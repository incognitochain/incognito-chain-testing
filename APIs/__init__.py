from Drivers import Connections

unspecified = "unspecified"


class BaseRpcApi:
    def __init__(self, url):
        self.rpc_connection = Connections.RpcConnection(url=url)
