from APIs import BaseRpcApi
from Objects.BeaconObject import BeaconBestStateDetailInfo


class SystemRpc(BaseRpcApi):
    def retrieve_beacon_block_by_height(self, beacon_height, level=2):
        return self.rpc_connection.with_method('retrievebeaconblockbyheight').with_params(
            [beacon_height, level]).execute()

    def retrieve_block_by_height(self, block_height, shard_id, level=1):
        """

        :param block_height:
        :param shard_id: shard id to retrieve data from
        :return:
        """
        return self.rpc_connection.with_method('retrieveblockbyheight').with_params(
            [block_height, shard_id, str(level)]).execute()

    def get_all_view_detail(self, chain_id):
        return self.rpc_connection.with_method('getallviewdetail').with_params([chain_id]).execute()

    def get_slashing_committee_detail(self, epoch):
        return self.rpc_connection.with_method('getslashingcommitteedetail').with_params([epoch]).execute()

    def get_slashing_committee(self, epoch):
        return self.rpc_connection.with_method('getslashingcommittee').with_params([epoch]).execute()

    def get_total_block(self, epoch):
        return self.rpc_connection.with_method('gettotalblockinepoch').with_params([epoch]).execute()

    def get_detail_blocks_of_epoch(self, shard_id, epoch):
        return self.rpc_connection.with_method('getdetailblocksofepoch').with_params([shard_id, epoch]).execute()

    def create_fork(self, block_fork_list, chain_id=1, num_of_branch=2, branch_tobe_continue=1):
        """

        @param block_list:
        @param num_of_branch:
        @param branch_tobe_continue:
        @param shard_id: number 1 to 7 : shard_id 1-7, 255: beacon
        @return:
        """
        payload = {
            "Type": 1,
            "Scene": {
                "Heights": block_fork_list,
                "Branchs": num_of_branch,
                "Chose": branch_tobe_continue
            },
            "CID": chain_id
        }
        return self.rpc_connection.set_payload(payload).execute()

    def get_mem_pool(self):
        return self.rpc_connection.with_method("getmempoolinfo").execute()

    def get_beacon_best_state_detail(self):
        return BeaconBestStateDetailInfo(self.rpc_connection.with_method('getbeaconbeststatedetail').
                                         with_params([]).execute())

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
