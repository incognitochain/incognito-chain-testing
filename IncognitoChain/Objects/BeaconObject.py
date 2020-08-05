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
            beacon_committee_obj = _Committee(obj)
            beacon_committee_objs.append(beacon_committee_obj)
        return beacon_committee_objs

    def get_beacon_pending_validator(self):
        raw_beacon_pending_validator_list = self.data['BeaconPendingValidator']
        beacon_pending_validator_objs = []
        for obj in raw_beacon_pending_validator_list:
            beacon_pending_validator_obj = _Committee(obj)
            beacon_pending_validator_objs.append(beacon_pending_validator_obj)
        return beacon_pending_validator_objs

    def get_shard_committees(self, shard_num=None, validator_number=None):
        obj_list = []
        committee_list_raw = self.data['ShardCommittee']  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_raw = committee_list_raw[str(shard_num)][validator_number]
            committee_obj = _Committee(committee_raw)
            return committee_obj
        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_list_raw = committee_list_raw[str(shard_num)]
        elif shard_num is None and validator_number is None:
            pass  # get all committee in all shard
        else:
            return

        for committee_raw in committee_list_raw:
            committee_obj = _Committee(committee_raw)
            obj_list.append(committee_obj)

        return obj_list

    def _get_shard_pending_validator(self):
        return self.data['ShardPendingValidator']

    def get_shard_pending_validator(self, shard_num, validator_number):
        return _Committee(self._get_shard_pending_validator()[str(shard_num)][validator_number])

    def get_auto_staking_committees(self, auto_staking_number=None):
        auto_staking_objs = []
        raw_auto_staking_list_raw = self.data['AutoStaking']

        if auto_staking_number is not None:  # get a specific committee auto staking
            auto_staking_raw = raw_auto_staking_list_raw[(auto_staking_number)]
            auto_staking_obj = _Committee(auto_staking_raw)
            return auto_staking_obj
        elif auto_staking_number is None:  # get all committee auto staking
            for auto_staking_raw in raw_auto_staking_list_raw:
                auto_staking_obj = _Committee(auto_staking_raw)
                auto_staking_objs.append(auto_staking_obj)
            return auto_staking_objs

    def is_he_a_committee(self, account):
        """
        Function to find shard committee number by using Account or public key
        :param account: Account obj or public key
        :return: shard committee number
        """
        from IncognitoChain.Objects.AccountObject import Account
        if type(account) == str:
            public_key = account
        elif type(account) == Account:
            public_key = account.public_key
        else:
            public_key = ''

        number_of_shards = self.get_active_shard()
        for shard_number in range(0, number_of_shards):
            committees_in_shard = self.get_shard_committees(shard_number)
            for committee in committees_in_shard:
                if committee.get_inc_public_key() == public_key:
                    return shard_number
        return False

    def is_this_committee_auto_stake(self, account):
        """
        Function to check committee auto stake by using Account or public key
        :param account: Account obj or public key
        :return: True if it matches, else False
        """
        from IncognitoChain.Objects.AccountObject import Account
        if type(account) == str:
            public_key = account
        elif type(account) == Account:
            public_key = account.public_key
        else:
            public_key = ''

        committees_auto_staking = self.get_auto_staking_committees()
        for committee in committees_auto_staking:
            if committee.get_inc_public_key() == public_key:
                return committee.is_auto_staking()
        return

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

    def get_current_shard_committee_size(self, shard_number):
        committee_list_in_shard = self.get_shard_committees(shard_number)
        return len(committee_list_in_shard)


class _Committee(BlockChainInfoBaseClass):
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
        super(_Committee, self).__init__(raw_data)
        raw_data = copy.copy(self.data)
        self._inc_public_key = raw_data['IncPubKey']
        self._bls = raw_data['MiningPubKey']['bls']
        self._dsa = raw_data['MiningPubKey']['dsa']
        self._auto_staking = raw_data['IsAutoStake'] if "IsAutoStake" in raw_data else None

    def get_inc_public_key(self):
        return self._inc_public_key

    def get_bls(self):
        return self._bls

    def get_dsa(self):
        return self._dsa

    def is_auto_staking(self):
        return self._auto_staking
