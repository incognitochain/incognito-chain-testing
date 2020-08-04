import copy
from IncognitoChain.Objects import BlockChainInfoBaseClass

class BeaconBestStateDetailInfo(BlockChainInfoBaseClass):

    def get_block_hash(self):
        return self.data["BestBlockHash"]

    def get_previous_block_hash(self):
        return self.data["get_previous_block_hash"]

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

    def get_best_shard_hash(self, shard_number):
        return self.data['BestShardHash'][str(shard_number)]

    def get_best_shard_height(self, shard_number):
        return self.data['BestShardHeight'][str(shard_number)]

    def get_beacon_committee(self):
        raw_beacon_committee_list = self.data['BeaconCommittee']
        beacon_committee_objs = []
        for obj in raw_beacon_committee_list:
            beacon_committee_obj = _BeaconCommittee(obj)
            beacon_committee_objs.append(beacon_committee_obj)
        return beacon_committee_objs

    def get_beacon_pending_validator(self):
        raw_beacon_pending_validator_list = self.data['BeaconPendingValidator']
        beacon_pending_validator_objs = []
        for obj in raw_beacon_pending_validator_list:
            beacon_pending_validator_obj = _BeaconCommittee(obj)
            beacon_pending_validator_objs.append(beacon_pending_validator_obj)
        return beacon_pending_validator_objs

    def _get_shard_committee(self):
        return self.data['ShardCommittee']

    def get_shard_committee(self, shard_num, validator_number):
        return _BeaconCommittee(self._get_shard_committee()[str(shard_num)][validator_number])

    def _get_shard_pending_validator(self):
        return self.data['ShardPendingValidator']

    def get_shard_pending_validator(self, shard_num, validator_number):
        return _BeaconCommittee(self._get_shard_pending_validator()[str(shard_num)][validator_number])

    def get_auto_staking(self):
        raw_auto_staking_list = self.data['AutoStaking']
        auto_staking_objs = []
        for obj in raw_auto_staking_list:
            auto_staking_obj = _AutoStaking(obj)
            auto_staking_objs.append(auto_staking_obj)
        return auto_staking_objs

    # TODO: Will update after getting the data
    def get_candidate_shard_waiting_current_random(self):
        return self.data["CandidateShardWaitingForCurrentRandom"]

    def get_candidate_beacon_waiting_current_random(self):
        return self.data["CandidateBeaconWaitingForCurrentRandom"]

    def get_candidate_beacon_waiting_next_random(self):
        return self.data["CandidateBeaconWaitingForNextRandom"]

    def get_candidate_shard_waiting_next_random(self):
        return self.data["CandidateShardWaitingForNextRandom"]

    def get_reward_receiver(self):
        return self.data["RewardReceiver"]

class _BeaconCommittee(BlockChainInfoBaseClass):
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
        super(_BeaconCommittee, self).__init__(raw_data)
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

class _AutoStaking(_BeaconCommittee):
    def __init__(self, raw_data):
        super(_AutoStaking, self).__init__(raw_data)
        raw_data = copy.copy(self.data)
        self.is_auto_stake = raw_data["IsAutoStake"]