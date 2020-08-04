from IncognitoChain.Objects import BlockChainInfoBaseClass

class BeaconBestStateDetailObj(BlockChainInfoBaseClass):

    def get_epoch(self):
        return int(self.data["Epoch"])

    def get_beacon_height(self):
        return int(self.data["BeaconHeight"])

    def get_beacon_proposer_index(self):
        return int(self.data["BeaconProposerIndex"])

    def get_current_random_number(self):
        return int(self.data["CurrentRandomNumber"])

    def get_current_random_time_stamp(self):
        return int(self.data["CurrentRandomTimeStamp"])

    def is_random_number(self):
        return self.data["IsGetRandomNumber"]

    def get_max_beacon_committee_size(self):
        return int(self.data["MaxBeaconCommitteeSize"])

    def get_min_beacon_committee_size(self):
        return int(self.data["MinBeaconCommitteeSize"])

    def get_max_shard_committee_size(self):
        return int(self.data["MaxShardCommitteeSize"])

    def get_min_shard_committee_size(self):
        return int(self.data["MinShardCommitteeSize"])

    def get_active_shard(self):
        return int(self.data["ActiveShards"])

    def get_shard_handle(self):
        return self.data["ShardHandle"]

class BestShardHashAndHeightInfo(BeaconBestStateDetailObj):

    def get_best_shard_hash_dict(self):
        return self.data['BestShardHash']

    def get_shard_hash_string(self, shard_number):
        return self.get_best_shard_hash_dict()[str(shard_number)]

    def get_best_shard_height_dict(self):
        return self.data['BestShardHeight']

    def get_shard_height_int(self, shard_number):
        return self.get_best_shard_height_dict()[str(shard_number)]

class BeaconCommitteesInfo(BeaconBestStateDetailObj):

    def get_beacon_committees_list(self):
        return self.data['BeaconCommittee']

    def get_beacon_committee_dict(self, beacon_number):
        return self.get_beacon_committees_list()[beacon_number]

    def get_beacon_pending_validator(self):
        return self.data['BeaconPendingValidator'] #

    def get_candidate_beacon_waiting_for_current_random(self):
        return self.data['CandidateBeaconWaitingForCurrentRandom'] #

    def get_candidate_beacon_waiting_for_next_random(self):
        return self.data['CandidateBeaconWaitingForNextRandom'] #

class ShardPendingValidatorAndCommitteeInfo(BeaconBestStateDetailObj):

    def get_shard_committees_dict(self):
        return self.data['ShardCommittee']

    def get_shard_committee_list(self, shard_committee_number):
        return self.get_shard_committees_dict()[str(shard_committee_number)]

    def get_shard_pending_validators_dict(self):
        return self.data['ShardPendingValidator']

    def get_shard_pending_validator_list(self, shard_pending_number):
        return self.get_shard_pending_validators_dict()[str(shard_pending_number)]

    def get_candidate_shard_waiting_for_current_random(self):
        return self.data['CandidateShardWaitingForCurrentRandom'] #

    def get_candidate_shard_waiting_for_next_random(self):
        return self.data['CandidateShardWaitingForNextRandom'] #

    def get_reward_receiver(self):
        return self.data['RewardReceiver'] #

    def get_last_cross_shard_state(self):
        return self.data['LastCrossShardState'] #

class AutoStakingInfo(BeaconBestStateDetailObj):

    def get_auto_staking_list(self):
        return self.data['AutoStaking']

    def get_auto_staking_number_dict(self, staking_number):
        return self.get_auto_staking_list()[staking_number]