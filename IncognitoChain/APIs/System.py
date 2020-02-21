from IncognitoChain.Drivers.Connections import RpcConnection


class SystemRpc:
    def __init__(self, url):
        self.rpc_connection = RpcConnection(url=url)

    def retrieve_block_by_height(self, block_height, shard_id):
        level = '1'
        return self.rpc_connection.with_method('retrieveblockbyheight').with_params(
            [block_height, shard_id, level]).execute()

    def get_mem_pool(self):
        return self.rpc_connection.with_method("getmempoolinfo").execute()
