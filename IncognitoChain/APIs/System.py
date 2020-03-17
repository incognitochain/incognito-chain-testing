from IncognitoChain.Drivers.Connections import RpcConnection


class SystemRpc:
    def __init__(self, url):
        self.rpc_connection = RpcConnection(url=url)
        self._cache = {}

    def retrieve_block_by_height(self, block_height, shard_id):
        """

        :param block_height:
        :param shard_id: shard id to retrieve data from
        :return:
        """
        level = '1'
        return self.rpc_connection.with_method('retrieveblockbyheight').with_params(
            [block_height, shard_id, level]).execute()

    def get_mem_pool(self):
        return self.rpc_connection.with_method("getmempoolinfo").execute()

    def get_beacon_best_state_detail(self, refresh_cache=True):
        if refresh_cache:
            beacon_best_state_detail = self.rpc_connection.with_method('getbeaconbeststatedetail').with_params(
                []).execute()
            self._cache['getbeaconbeststatedetail'] = beacon_best_state_detail
        else:
            try:
                beacon_best_state_detail = self._cache['getbeaconbeststatedetail']
            except KeyError:
                beacon_best_state_detail = self.rpc_connection.with_method('getbeaconbeststatedetail').with_params(
                    []).execute()
        return beacon_best_state_detail

    def remove_tx_in_mem_pool(self, tx_id):
        return self.rpc_connection.with_method('removetxinmempool').with_params([tx_id]).execute()

    # HELPERS ###############
    def help_clear_mem_pool(self):
        list_tx = self.get_mem_pool().get_result('ListTxs')
        for tx in list_tx:
            self.remove_tx_in_mem_pool(tx['TxID'])

    def help_count_shard_committee(self, refresh_cache=False):
        best = self.get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        return len(shard_committee_list)

    def help_count_committee_in_shard(self, shard_id, refresh_cache=False):
        best = self.get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        shard_committee = shard_committee_list[f'{shard_id}']
        return len(shard_committee)

    def help_get_current_epoch(self, refresh_cache=True):
        beacon_best_state = self.get_beacon_best_state_detail(refresh_cache)
        return beacon_best_state.get_result('Epoch')

    def help_get_beacon_height_in_best_state_detail(self, refresh_cache=True):
        beacon_best_state = self.get_beacon_best_state_detail(refresh_cache)
        return beacon_best_state.get_result('BeaconHeight')
