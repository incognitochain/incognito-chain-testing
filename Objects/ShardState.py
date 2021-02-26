from Objects import BlockChainInfoBaseClass
from Objects.BeaconObject import BeaconBestStateDetailInfo


class ShardBestStateDetailInfo(BlockChainInfoBaseClass):

    def get_block_hash(self):
        return self.data["BestBlockHash"]

    def get_beacon_hash(self):
        return self.data["BestBeaconHash"]

    def get_beacon_height(self):
        return self.data["BeaconHeight"]

    def get_shard_id(self):
        return self.data["ShardID"]

    def get_epoch(self):
        return self.data["Epoch"]

    def get_shard_height(self):
        return self.data["ShardHeight"]

    def get_max_shard_committee_size(self):
        return self.data["MaxShardCommitteeSize"]

    def get_min_shard_committee_size(self):
        return self.data["MinShardCommitteeSize"]

    def get_shard_proposer_inx(self):
        return self.data["ShardProposerIdx"]

    def get_shard_committee(self):
        """
        Function to get all committee in shard committee
        :return: a list of BeaconBestStateDetailInfo.Committee obj
        """
        obj_list = []
        committee_list_raw = self.data['ShardCommittee']  # get all committee in a shard
        for committee_raw in committee_list_raw:
            committee_obj = BeaconBestStateDetailInfo.Committee(committee_raw)
            obj_list.append(committee_obj)
        return obj_list

    def get_shard_pending_validator(self):
        """
        Function to get all committee in shard pending validator
        :return: list of BeaconBestStateDetailInfo.Committee obj
        """
        shard_pending_validator_objs = []
        shard_pending_validator_list_raw = self.data["ShardPendingValidator"]
        for obj in shard_pending_validator_list_raw:
            shard_pending_validator_obj = BeaconBestStateDetailInfo.Committee(obj)
            shard_pending_validator_objs.append(shard_pending_validator_obj)
        return shard_pending_validator_objs

    def get_cross_shard(self):
        """
        data sample:
        {
            "1": 60043,
            "2": 60044,
            "3": 59005,
            "4": 59007,
            "5": 57895,
            "6": 50080,
            "7": 59004,
        }
        """
        dict_obj = {}
        list_obj = []
        cross_shard_dict_raw = self.data["BestCrossShard"]
        for key, value in cross_shard_dict_raw.items():
            dict_obj.update({key: value})
            list_obj.append(dict_obj)
            dict_obj = {}
        return list_obj

    def get_staking_tx(self, committee_pub_k=None):
        """
        data sample:
        {
            "121VhftSAygpEJZ6i9jGkDy3b6YFqziMHFRQC6TvKTJcZWmy5a3U4KKpsEJLJ8zXsXpoDAQuqMHtjJk5Y52buC4qVvvRw2i6TbvHHFqpBdtfNqaepVfLPRvYB4CiUwLqjfh4R2Yf73YNhJ2MJJcDEsZ4U4QD7fDs3wiUi69WfcidqyYQpLaxU6RSDqLNkDQuosdaMF21xuX2w16DUxvZeyAsGQ8Z9d5AUCghWHTUAeH6tet9ZNaaXbZoSR2vktviitSrxYSXwpuR9JrfhXypxxgJBjeho2yZwTZTCrtqNsQDvrXC1KgK2XniKeeAiMs89ixQ4D3sVEUpvu9JPEiN4Kx7e64vcYh79RFq6qTkXFGLe2oZMqxutVmWGQfXGaSKCFstVU8zgwHLATU5tzvBEvJDRQKgPxcTQxhmqLqa8uLkPUwV": 1706e8bb73b4fd7ec0ed2ef8326a9a902754c5bf2762e6fb9960e678b088f0c6,
            "121VhftSAygpEJZ6i9jGkDy3b6YFqziMHFRQC6TvKTJcZWmy5a3U4KKpsEJLJ8zXsXpoDAQuqMHtjJk5Y52buC4qVvvRw2i6TbvHHFqpBdtfNqaepVfLPRvYB4CiUwLqjfh4R2Yf73YNhJ2MJJcDEsZ4U4QD7fDs3wiUi69WfcidqyYQpLaxU6RSDqLNkDQuosdaMF21xuX2w16DUxvZeyAsGQ8Z9d5AUCghWHTUAeH6tet9ZNaaXbZoSR2vktviitSrxYSXwpuR9JrfhXypxxgJBjeho2yZwTZTCrtqNsQDvrXC1KgK2XniKeeAiMs89ixQ4D3sVEUpvu9JPEiN4Kx7e64vcYh79RFq6qTkXFGLe2oZMqxutVmWGQfXGaSKCFstVU8zgwHLATU5tzvBEvJDRQKgPxcTQxhmqLqa8uLkPUwV": 1706e8bb73b4fd7ec0ed2ef8326a9a902754c5bf2762e6fb9960e678b088f0c6
        }
        """
        staking_tx_dict_raw = self.data["StakingTx"]
        if committee_pub_k is None:
            return staking_tx_dict_raw
        return staking_tx_dict_raw.get(committee_pub_k)

    def get_num_txns(self):
        return self.data["NumTxns"]

    def get_total_txns(self):
        return self.data["TotalTxns"]

    def get_total_txns_exclude_salary(self):
        return self.data["TotalTxnsExcludeSalary"]

    def get_active_shard(self):
        return self.data["ActiveShards"]

    def get_metric_block_height(self):
        return self.data["MetricBlockHeight"]


class ShardBestStateInfo(ShardBestStateDetailInfo):

    def get_shard_committee(self):
        """
        Function to get all committee public key in shard committee
        :return: all committee public key in shard committee
        """
        return self.data['ShardCommittee']

    def get_shard_pending_validator(self):
        """
        Function to get all committee public key in shard pending validator
        :return: all committee public key in shard pending validator
        """
        return self.data["ShardPendingValidator"]
