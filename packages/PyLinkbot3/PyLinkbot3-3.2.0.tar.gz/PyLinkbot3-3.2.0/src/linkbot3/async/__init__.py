import asyncio
import functools
import importlib.util
import logging
import os
import ribbonbridge as rb
import sys
import traceback
import websockets

from . import peripherals
from .. import _util as util

from . import commontypes_pb2 as rbcommon

if sys.version_info < (3,4,4):
    asyncio.ensure_future = asyncio.async

__all__ = ['AsyncLinkbot', 'config', 'AsyncDaemon']

_dirname = os.path.dirname(os.path.realpath(__file__))

def load_pb2_file(filename):
    filepath = os.path.abspath(os.path.join(_dirname, filename))
    sys.path.append(os.path.dirname(filepath))

    basename = os.path.basename(filepath) 
    modulename = os.path.splitext(basename)[0]
    if sys.version_info >= (3,5):
        spec = importlib.util.spec_from_file_location(modulename,
                filepath)
        pb2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pb2)
        return pb2
    else:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(modulename, filepath).load_module()

class RpcProxy():
    def __init__(self, pb_module, logger_name='RBProxy'):
        self._members = {}
        self._pb_module = pb_module
        for key,value in pb_module.__dict__.items():
            try:
                if hasattr( value, 'In' ) and hasattr( value, 'Out', ):
                    self._members[key] = value
            except:
                pass
        self._requests = {}
        self._request_id = 0
        # self._event_handlers{ event_name i.e. dongleEvent : coroutine(DongleEvent) }
        self._event_handlers = {}
        self.logger=logging.getLogger(logger_name)

        # Add the connectEvent event handler
        self.on('connectEvent', self._connect_event)

    @asyncio.coroutine
    def _connect_event(self, payload):
        self.logger.info('Received connectEvent.')

    # Add a callback handler for Rpc events. For instance, for the daemon, one might do
    #    on("dongleEvent", coro)
    def on(self, name, coro = None):
        self._event_handlers[name] = coro

    def rb_get_args_obj(self, name):
        return getattr(self._members[name], 'In')()

    def __getattr__(self, name):
        logging.info('__getattr__')
        if name not in self._members:
            raise AttributeError('{} is not a method of this RPC proxy.'
                    .format(name))
        return functools.partial(self._handle_call, name)

    @asyncio.coroutine
    def _handle_call(self, procedure_name, pb2_obj=None, **kwargs):
        '''
        Handle a call.
        '''
        try:
            if not pb2_obj:
                pb2_obj = self._members[procedure_name].In()
                for k,v in kwargs.items():
                    setattr(pb2_obj, k, v)
            fut = asyncio.Future()
            self._requests[self._request_id] = fut
            
            user_fut = asyncio.Future()
            util.chain_futures(fut, user_fut, 
                    functools.partial(
                        self._convert_rpcReply,
                        procedure_name)
                    )

            # Serialize and send the message to the RPC server
            #result = yield from self._rpc.fire(procedure_name, pb2_obj.SerializeToString())
            self.logger.info('Scheduling call to: {}'.format(procedure_name))
            b = self.serialize(procedure_name, pb2_obj, self._request_id)
            yield from self.emit_to_server(b)
            self._request_id += 1

            return user_fut
        except Exception as e:
            logging.warning(traceback.format_exc())

    def _convert_rpcReply(self, rpc_name, rpcReply):
        # This function should turn rpcReply objects into an instantiation of
        # the child oneof object.
        try:
            return getattr(rpcReply, rpcReply.WhichOneof('arg'))
        except KeyError as e:
            self.logger.warning('Received unexpected reply. Current requests: {}'.format(self._requests.items()))

    @asyncio.coroutine
    def deliver(self, server_to_proxy):
        self.logger.info('RpcProxy.deliver()')
        try:
            method = server_to_proxy.WhichOneof('arg')
        except Exception as e:
            self.logger.warning('Could not parse server_to_proxy message; no "arg" member found. {}'.format(e))
            return

        self.logger.info('Parsed server->proxy message. SubMessage: {}'.format(server_to_proxy.WhichOneof('arg')))
        if method == "rpcReply":
            self._handle_rpc_reply(server_to_proxy.rpcReply)
        else:
            try:
                arg = getattr(server_to_proxy, method)
                yield from self._event_handlers[method](arg)
            except KeyError:
                self.logger.warning('Unhandled RPC Event: {}'.format(method))
            except:
                # FIXME
                self.logger.warning('Could not handle exception')
                raise

    def _handle_rpc_reply(self, rpc_reply):
        # If we receive rpcReply objects from the server, pass them to this function for processing.
        try:
            request_id = rpc_reply.requestId
            fut = self._requests.pop(request_id)
            fut.set_result( rpc_reply )
            self.logger.info('Handled rpc reply: {}'.format(request_id))
        except KeyError:
            self.logger.warning('Received spurious rpcReply with id: {}'.format(request_id))
        except:
            self.logger.warning(traceback.print_exc())

    def serialize(self, method_name, pb_in, request_id):
        '''
        This function should take an RPC "In" object and return the raw bytes
        that should be sent to the RPC server. For example, in the robot
        interface, pb_in might be an instance of "GetFormFactor.In". This
        function should return an object of type "bytearray" serialized from a
        ClientToRobot object.
        '''
        raise NotImplementedError('Required method not implemented.')

    @asyncio.coroutine
    def emit_to_server(self, bytestring):
        '''
        This function should take the "bytestring" argument and send it to the
        connected RPC server.
        '''
        raise NotImplementedError('Required method not implemented.')

class Daemon(RpcProxy):
    def __init__(self):
        super().__init__(load_pb2_file('daemon_pb2.py'), 'DaemonProxy')

    def serialize(self, method_name, pb_in, request_id):
        request = self._pb_module.RpcRequest()
        getattr(request, method_name).CopyFrom(pb_in)
        request.requestId = request_id
        c_to_d = self._pb_module.ClientToDaemon()
        c_to_d.rpcRequest.CopyFrom(request)
        return c_to_d.SerializeToString()

    def set_io(self, io):
        self.protocol = io
        # Start the in-pump
        self.__pump_handle = asyncio.ensure_future(self.pump())

    @asyncio.coroutine
    def emit_to_server(self, bytestring):
        # This override requires the "protocol" field to be set, and expects it
        # to be an asyncio Protocol object
        yield from self.protocol.send(bytestring)

    @asyncio.coroutine
    def pump(self):
        '''
        Pass all data from underlying transport to this function.
        '''
        logging.info('Daemon in-pump starting...')
        while True:
            try:
                msg = yield from self.protocol.recv()
                if msg is None:
                    continue
                logging.info('Daemon in-pump received message...')
                daemon_to_client = self._pb_module.DaemonToClient()
                daemon_to_client.ParseFromString(msg)
                logging.info('Daemon in-pump received message... delivering...')
                yield from self.deliver(daemon_to_client)
            except asyncio.CancelledError:
                logging.warning('Daemon consumer received asyncio.CancelledError')
                return
            except websockets.exceptions.ConnectionClosed:
                logging.info('Daemon consumer connection closed.')
                return
            except Exception as e:
                logging.warning('Unhandled exception! {}'.format(traceback.format_exc()))
                raise

def config(**kwargs):
    ''' Configure linkbot module settings

        :param use_sfp: default:False Use WebSockets daemon communication transport, or the old SFP transport?
        :type use_sfp: bool
        :param daemon_hostport: default:'localhost:42000' Location of the linkbotd daemon.
        :type daemon_hostport: string
        :param timeout: default: 30 (seconds)
        :type timeout: float
    '''
    my_config = util.Config()
    if 'use_sfp' in kwargs:
        use_sfp = kwargs['use_sfp']
        if use_sfp:
            use_websockets = False
        else:
            use_websockets = True
        my_config.use_websockets = use_websockets

    if 'daemon_hostport' in kwargs:
        daemon_host = kwargs['daemon_hostport']
        my_config.daemon_host = daemon_host

    if 'timeout' in kwargs:
        timeout = kwargs['timeout']
        my_config.timeout = timeout

class _DaemonProxy(rb.Proxy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_protocol(self, protocol):
        self._protocol = protocol

    @asyncio.coroutine
    def rb_emit_to_server(self, bytestring):
        yield from self._protocol.send(bytestring)

class _AsyncLinkbot(RpcProxy):
    @classmethod
    @asyncio.coroutine
    def create(cls, serial_id):
        my_config = util.Config()

        if serial_id is None:
            serial_id = my_config.linkbot

        logging.info('Creating async Linkbot handle to ID:{}'.format(serial_id))
        logger=logging.getLogger('RBProxy.'+serial_id)
        self = cls(load_pb2_file('daemon_pb2.py').robot__pb2, 'RobotProxy')

        serial_id = serial_id.upper()
        self._serial_id = serial_id
        self._loop = asyncio.get_event_loop()

        self.__daemon = Daemon()

        self.__daemon.on('receive', self.on_receive)

        if my_config.use_websockets:
            self.__log('Creating Websocket connection to daemon...')
            protocol = yield from websockets.connect(
                    'ws://'+my_config.daemon_host[0]+':'+my_config.daemon_host[1], loop=self._loop)
        else:
            import sfp
            self.__log('Creating tcp connection to daemon...')
            (transport, protocol) = yield from sfp.client.connect(
                    my_config.daemon_host[0], my_config.daemon_host[1], loop=self._loop)

        self.__log('Daemon TCP connection established.')
        protocol.connection_lost = self.__connection_closed

        self.__daemon.set_io(protocol)
        self._daemon_protocol = protocol
        '''
        self.__log('Initiating daemon handshake...')
        yield from asyncio.sleep(0.5)
        yield from self.__daemon.rb_connect()
        self.__log('Daemon handshake finished.')
        '''

        #yield from asyncio.sleep(0.5)
        self.__log('Resolving serial id: ' + serial_id)
        args = self.__daemon._pb_module.addRobotRefs.In()
        _serial_id = args.serialIds.add()
        _serial_id.value = serial_id
        result_fut = yield from self.__daemon.addRobotRefs(args)
        self.__log('Waiting for addRobotRefs result...')
        status_result = yield from result_fut
        self.__log('Waiting for addRobotRefs result...done')
        try:
            assert(status_result.status == self.__daemon._pb_module.OK)
        except:
            self.__log('Received unexpected status from daemon: {}'.format(repr(status)))
            raise
        return self

    @asyncio.coroutine
    def disconnect(self):
        yield from self._linkbot_protocol.close()
        yield from self._daemon_protocol.close()

    def close(self):
        self._linkbot_protocol.close()
        self.__linkbot_consumer_handle.cancel()

    def __connection_closed(self, exc):
        ''' Called when the connection is closed from the other end.
           
            :param exc: An exception or "None"
        '''
        if exc:
            self.__log('Remote closed connection: '+str(exc), 'warning')
        else:
            self.__log('Remote closed connection gracefully.')
        self.rb_close()

    def serialize(self, method_name, pb_in, request_id):
        request = self._pb_module.RpcRequest()
        getattr(request, method_name).CopyFrom(pb_in)
        request.requestId = request_id
        c_to_r = self._pb_module.ClientToRobot()
        c_to_r.rpcRequest.CopyFrom(request)
        return c_to_r

    @asyncio.coroutine
    def emit_to_server(self, client_to_robot):
        self.__log('emit_to_server')
        transmit = self.__daemon.rb_get_args_obj('transmit')
        transmit.destination.value = self._serial_id
        transmit.payload.CopyFrom(client_to_robot)
        self.__log('robot emitting "transmit" message to daemon...')
        try:
            fut = yield from self.__daemon.transmit( transmit )
        except:
            self.__log(traceback.print_exc())
        self.__log('robot emitting "transmit" message to daemon...done')
        yield from fut

    @asyncio.coroutine
    def on_receive(self, receive_transmission):
        self.__log('_AsyncLinkbot received data from robot!')
        if receive_transmission.HasField('payload'):
            yield from self.deliver(receive_transmission.payload)

    def __log(self, msg, logtype='info'):
        getattr(logging, logtype)(self._serial_id + ': ' + msg)

class AsyncLinkbot():
    @classmethod
    @asyncio.coroutine
    def create(cls, serial_id):
        """ Create a new asynchronous Linkbot object.

        :param serial_id: The robot to connect to
        :type serial_id: str
        :returns: AsyncLinkbot() object.
        """
        try:
            self = cls()
            self._proxy = yield from asyncio.wait_for( _AsyncLinkbot.create(serial_id), 
                                                  util.DEFAULT_TIMEOUT )
            form_factor_fut = yield from self._proxy.getFormFactor()
            form_factor = yield from form_factor_fut
            logging.info('Got form factor: {}'.format(form_factor))
            if form_factor.value == 0:
                self._motor_mask = 0x05
            elif form_factor.value == 1:
                self._motor_mask = 0x03
            elif form_factor.value == 2:
                self._motor_mask = 0x07
            else:
                raise Exception('Unknown form factor')
            self._proxy.form_factor = form_factor.value
            self.rb_add_broadcast_handler = self._proxy.on
            self.close = self._proxy.close
            self.enableButtonEvent = self._proxy.enableButtonEvent
            self._accelerometer = yield from peripherals.Accelerometer.create(self)
            self._battery = yield from peripherals.Battery.create(self)
            self._button = yield from peripherals.Button.create(self)
            self._buzzer = yield from peripherals.Buzzer.create(self)
            self._eeprom_obj = yield from peripherals.Eeprom.create(self)
            self._led = yield from peripherals.Led.create(self)
            self._motors = yield from peripherals.Motors.create(self)
            self._twi = yield from peripherals.Twi.create(self)
            self._serial_id = serial_id

            # Enable joint events
            yield from self._proxy.enableJointEvent(enable=True)
            self._proxy.on('jointEvent', self.__joint_event)
            self._proxy.on('debugMessageEvent',
                    self.__debug_message_event)
            return self
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(
                'Timed out trying to connect to remote robot. Please ensure '
                'that the remote robot is on and not currently connected to '
                'another computer.' )

    @asyncio.coroutine
    def disconnect(self):
        yield from self._proxy.disconnect()

    @property
    def accelerometer(self):
        """
        The Linkbot accelerometer.

        See :class:`linkbot3.async.peripherals.Accelerometer`.
        """
        return self._accelerometer

    @property
    def battery(self):
        """
        The Linkbot battery.

        Access the Linkbot's battery voltage. See
        :class:`linkbot3.async.peripherals.Battery`
        """
        return self._battery

    @property
    def buttons(self):
        """
        Access to the Linkbot's buttons. 

        See :class:`linkbot3.async.peripherals.Button`.
        """
        return self._button

    @property
    def buzzer(self):
        """
        Access to the Linkbot's buzzer.

        See :class:`linkbot3.async.peripherals.Buzzer`.
        """
        return self._buzzer

    @property
    def _eeprom(self):
        """
        Access the robot's EEPROM memory.

        Warning: Improperly accessing the robot's EEPROM memory may yield
        unexpected results. The robot uses EEPROM memory to store information
        such as its serial ID, calibration data, etc.
        """
        return self._eeprom_obj

    @property
    def led(self):
        """
        The Linkbot multicolor LED.

        See :class:`linkbot3.async.peripherals.Led`.
        """
        return self._led

    @property
    def motors(self):
        """
        The motors of the Linkbot.

        See :class:`linkbot3.async.peripherals.Motors` . To access individual motors, you may do:

            AsyncLinkbot.motors[0].is_moving()

        or similar. Also see :class:`linkbot3.async.peripherals.Motor`
        """
        return self._motors

    @property
    def twi(self):
        """
        Access the I2C two-wire interface of the Linkbot.

        See :class:`linkbot3.async.peripherals.Twi` .
        """
        return self._twi

    @asyncio.coroutine
    def reboot(self):
        result_fut = yield from self._proxy.reboot({})
        return result_fut

    @asyncio.coroutine
    def version(self):
        '''
        Get the firmware version

        :returns: asyncio.Future with result (major, minor, patch)
        :rtype: asyncio.Future with result type: (int, int, int)
        '''
        def conv(payload):
            return (payload.major, payload.minor, payload.patch)

        fut = yield from self._proxy.getFirmwareVersion()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=conv)
        return user_fut

    @asyncio.coroutine
    def form_factor(self):
        '''
        Get the robot's self-identified form factor

        :returns: asyncio.Future with result int
        :rtype: asyncio.Future with result type: int
        '''
        def conv(payload):
            return payload.value

        fut = yield from self._proxy.getFormFactor()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=conv)
        return user_fut

    @asyncio.coroutine
    def set_peripherals_reset(self, peripheral_mask, mask=0xff):
        '''
        Specify which peripherals to reset when the robot is disconnected.

        Values should be "1<<Linkbot.MOTOR1 | 1<<Linkbot.LED", etc. Valid peripheral_mask values are:

        Linkbot.MOTOR1
        Linkbot.MOTOR2
        Linkbot.MOTOR3
        Linkbot.LED
        Linkbot.BUZZER
        '''
        args_obj = self._proxy.rb_get_args_obj('setResetOnDisconnect')
        args_obj.peripheralResetMask = peripheral_mask
        args_obj.mask = mask
        fut = yield from self._proxy.setResetOnDisconnect(args_obj)
        return fut
    
    @asyncio.coroutine    
    def __joint_event(self, payload):
        # Update the motor states
        self.motors[payload.joint].state = payload.event

    @asyncio.coroutine
    def __debug_message_event(self, payload):
        logging.warning('Received DEBUG message from robot {}: {}'
                .format(self._serial_id, payload.bytestring))

class AsyncDaemon(_DaemonProxy):
    @classmethod
    @asyncio.coroutine
    def create(cls):
        my_config = util.Config()

        self = cls(os.path.join(_dirname, 'daemon_pb2.py'))

        if my_config.use_websockets:
            #self.__log('Creating Websocket connection to daemon...')
            protocol = yield from websockets.connect(
                    'ws://'+my_config.daemon_host[0]+':'+my_config.daemon_host[1])
        else:
            #self.__log('Creating tcp connection to daemon...')
            (transport, protocol) = yield from sfp.client.connect(
                    my_config.daemon_host[0], my_config.daemon_host[1])
        
        self.set_protocol(protocol)
        self.consumer = asyncio.ensure_future(self.__consumer(protocol))
        yield from self.rb_connect()

        return self

    @asyncio.coroutine
    def cycle(self, seconds):
        args = self.rb_get_args_obj('cycleDongle')
        args.seconds = seconds
        result_fut = yield from self.cycleDongle(args)
        return result_fut

    @asyncio.coroutine
    def reboot(self):
        result_fut = yield from self.reboot({})
        return result_fut

    @asyncio.coroutine
    def ping(self, destinations = [], peripheral_reset_mask = 0x1f):
        args = self.rb_get_args_obj('sendRobotPing')
        for d in destinations:
            serial_id_obj = args.destinations.add()
            serial_id_obj.value = d
        args.peripheralResetMask = peripheral_reset_mask
        result_fut = yield from self.sendRobotPing(args)
        return result_fut

    @asyncio.coroutine
    def __consumer(self, protocol):
        while True:
            try:
                msg = yield from protocol.recv()
                if msg is None:
                    continue
            except asyncio.CancelledError:
                logging.warning('Daemon consumer received asyncio.CancelledError')
                return
            except websockets.exceptions.ConnectionClosed:
                logging.info('Connection Closed.')
                return
            yield from self.rb_deliver(msg)

