from Drivers.Connections import RpcConnection


class SystemRpc:
    def __init__(self, url):
        self.rpc_connection = RpcConnection(url=url)

    def retrieve_beacon_block_by_height(self, beacon_height, level=2):
        return self.rpc_connection.with_method('retrievebeaconblockbyheight').with_params(
            [beacon_height, level]).execute()

    def retrieve_block_by_height(self, block_height, shard_id):
        """

        :param block_height:
        :param shard_id: shard id to retrieve data from
        :return:
        """
        level = '1'
        return self.rpc_connection.with_method('retrieveblockbyheight').with_params(
            [block_height, shard_id, level]).execute()

    def get_all_view_detail(self, shard_id):
        return self.rpc_connection.with_method('getallviewdetail').with_params([shard_id]).execute()

    def get_mem_pool(self):
        return self.rpc_connection.with_method("getmempoolinfo").execute()

    def get_beacon_best_state_detail(self):
        return self.rpc_connection.with_method('getbeaconbeststatedetail').with_params([]).execute()

    def get_beacon_best_state(self):
        return self.rpc_connection. \
            with_method("getbeaconbeststate"). \
            with_params([]). \
            execute()

    def remove_tx_in_mem_pool(self, tx_id):
        return self.rpc_connection.with_method('removetxinmempool').with_params([tx_id]).execute()

    def get_block_chain_info(self):
        return self.rpc_connection.with_method('getblockchaininfo').with_params([]).execute()

    def get_reward_amount_by_epoch(self, shard_id, epoch):
        return self.rpc_connection.with_method('getrewardamountbyepoch'). \
            with_params([shard_id, epoch]). \
            execute()

    def get_shard_best_state_detail(self, shard_id):
        return self.rpc_connection.with_method('getshardbeststatedetail').with_params([shard_id]).execute()

    def get_shard_best_state(self, shard_id):
        return self.rpc_connection.with_method('getshardbeststate').with_params([shard_id]).execute()

    def get_committee_state(self, beacon_height):
        # according to dev, parameter must be [beacon_height, ""],
        # otherwise it would cause the node panic and crash, this should be a bug
        return self.rpc_connection.with_method("getcommitteestate").with_params([beacon_height, ""]).execute()
