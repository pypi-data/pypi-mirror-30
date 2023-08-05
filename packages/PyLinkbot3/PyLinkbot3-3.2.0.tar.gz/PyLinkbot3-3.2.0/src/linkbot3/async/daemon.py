
import ribbonbridge as rb
import websockets

__daemon = None

@asyncio.coroutine
def get_daemon(uri):
    pass

class _DaemonProxy1(rb.Proxy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_protocol(self, protocol):
        self._protocol = protocol

    @asyncio.coroutine
    def rb_emit_to_server(self, bytestring):
        yield from self._protocol.send(bytestring)

class Daemon1():
    @classmethod
    @asyncio.coroutine
    def create(cls, uri):
        self = cls
        _dirname = os.path.dirname(os.path.realpath(__file__))
        self.proxy = _DaemonProxy1(os.path.join(_dirname, 'daemon_pb2.py'))
