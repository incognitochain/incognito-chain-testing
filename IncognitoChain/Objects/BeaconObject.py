import copy
from IncognitoChain.Objects import BlockChainInfoBaseClass

class BeaconBestStateDetailInfo(BlockChainInfoBaseClass):

    def get_epoch(self):
        return self.data["Epoch"]

    def get_beacon_height(self):
        return self.data["BeaconHeight"]

    def get_beacon_proposer_index(self):
        return self.data["BeaconProposerIndex"]

    def get_current_random_number(self):
        return self.data["CurrentRandomNumber"]

    def get_current_random_time_stamp(self):
        return self.data["CurrentRandomTimeStamp"]

    def is_random_number(self):
        return self.data["IsGetRandomNumber"]

    def get_max_beacon_committee_size(self):
        return self.data["MaxBeaconCommitteeSize"]

    def get_min_beacon_committee_size(self):
        return self.data["MinBeaconCommitteeSize"]

    def get_max_shard_committee_size(self):
        return self.data["MaxShardCommitteeSize"]

    def get_min_shard_committee_size(self):
        return self.data["MinShardCommitteeSize"]

    def get_active_shard(self):
        return self.data["ActiveShards"]

    def get_shard_handle(self):
        return self.data["ShardHandle"]

    def get_best_shard_hash(self):
        raw_best_shard_hash_dict = self.data['BestShardHash']
        best_shard_hash_objs = []
        for k, v in raw_best_shard_hash_dict.items():
            best_shard_hash_data = {k: v}
            best_shard_hash_obj = _BestShardHashAndHeight(best_shard_hash_data)
            best_shard_hash_objs.append(best_shard_hash_obj)
        return best_shard_hash_objs

    def get_best_shard_height(self):
        raw_best_shard_height_dict = self.data['BestShardHeight']
        best_shard_height_objs = []
        for k, v in raw_best_shard_height_dict.items():
            best_shard_height_data = {k: v}
            best_shard_height_obj = _BestShardHashAndHeight(best_shard_height_data)
            best_shard_height_objs.append(best_shard_height_obj)
        return best_shard_height_objs

    def get_beacon_committee(self):
        raw_beacon_committee_list = self.data['BeaconCommittee']
        beacon_committee_objs = []
        for obj in raw_beacon_committee_list:
            pool_pair_obj = _BeaconCommitee(obj)
            beacon_committee_objs.append(pool_pair_obj)
        return beacon_committee_objs

    def get_shard_committee(self):
        raw_shard_committee_dict = self.data['ShardCommittee']
        shard_committee_objs = []
        for k, v in raw_shard_committee_dict.items():
            shard_commitee_data = {k: v}
            shard_committee_obj = _BeaconCommitee(shard_commitee_data)
            shard_committee_objs.append(shard_committee_obj)
        return shard_committee_objs

    def get_shard_pending_committee(self):
        raw_shard_committee_dict = self.data['ShardPendingValidator']
        shard_pending_committee_objs = []
        for k, v in raw_shard_committee_dict.items():
            shard_pending_commitee_data = {k: v}
            shard_pending_committee_obj = _BeaconCommitee(shard_pending_commitee_data)
            shard_pending_committee_objs.append(shard_pending_committee_obj)
        return shard_pending_committee_objs

    def get_auto_staking(self):
        raw_beacon_committee_list = self.data['AutoStaking']
        auto_staking_objs = []
        for obj in raw_beacon_committee_list:
            auto_staking_obj = _BeaconCommitee(obj)
            auto_staking_objs.append(auto_staking_obj)
        return auto_staking_objs

class _BeaconCommitee(BlockChainInfoBaseClass):
    """
    data sample:
     {
         "IncPubKey": "12DNFqDkW9bNwzVT8fxZd4y2XLz1PRe3jvbHMYgrp1wUBquWpz7",
         "MiningPubKey:
                {
                  "bls": ""1EF8XFyAYtrNrFMECSPENbxtktjJCJE8faXTdChqVuBMtQNVP2Dd9stFMXKDV8BPNPtmsogV3tLePBPrfAReLp5uWRQA9ngiEivmXFr1rg1wi5Pu31M9Giqhx94ZqgaTk854qUJEGhwXUmkEztw4GKYn7Zq24EDYXGzPK9R43iW1ysWzH5HqH"",
                  "dsa": "17MtmvoQhsppwCJtcuam6DHmEpSGTaK8kNNxCcXheL5apXMe3PH"
                }
     }
    """
    def __init__(self, raw_data):
        super(_BeaconCommitee, self).__init__(raw_data)
        raw_data = copy.copy(self.data)
        self._inc_public_key = raw_data['IncPubKey']
        self._bls = raw_data['MiningPubKey']['bls']
        self._dsa = raw_data['MiningPubKey']['dsa']

    def get_inc_public_key(self):
        return self._inc_public_key

    def get_bls(self):
        return self._bls

    def get_dsa(self):
        return self._dsa

class _BestShardHashAndHeight(BlockChainInfoBaseClass):
    """
    data sample:
    {
         "0": "58d858cd91d3301cc860d7c2557a244fba8a80a7baee7bfa621f7ab5078c56e2",
         "1": "b3ea51ab91e7d92b1d25cf9e170028dbbf7451c6293a96fcf5921a60c0fb1005",
         "2": "10dd582bc57dfd4251f39ad5fe39f55b5df89bd2f14cf561a643e3ca4e617bf1",
         "3": "c19ae2112f2e90b1af7ead7643ceb234f077b7e56c4670b5c591dfbac13651bf",
         "4": "271af42d2610920d6ec82449eb76c4841bcb1ad13d5e6df520a01b8726429e33",
         "5": "d83a96e01f6e0914b59f012b09e2d307c1961506b3fd38be7f8179dc076d4dc7",
         "6": "a700a0f610ffee7b7b53566dc912050c8d67ed943b6ad21891800395bbcb1b97",
         "7": "624ec47daeee5fba222022c6b74712b474963f8b8a22468c1bf07d833459b714",
     }
    or
    {
         "0": 123,
         "1": 234,
         "2": 132,
         "3": 4312,
         "4": 4123,
         "5": 3213,
         "6": 33111,
         "7": 22477,
     }
    """
    def __init__(self, raw_data):
        super(_BestShardHashAndHeight, self).__init__(raw_data)
        raw_data = copy.copy(self.data)
        self.index, self.info = raw_data.popitem()

    def get_shard_index(self):
        return self.index

    def get_shard_info(self):
        return self.info