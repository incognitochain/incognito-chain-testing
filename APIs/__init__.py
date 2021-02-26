from Drivers import Connections


class BaseRpcApi:
    def __init__(self, url):
        self.rpc_connection = Connections.RpcConnection(url=url)
