import copy
import json

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects import BlockChainInfoBaseClass
from IncognitoChain.Objects.AccountObject import Account


class BeaconBestStateDetailInfo(BlockChainInfoBaseClass):
    class Committee(BlockChainInfoBaseClass):
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
            super(BeaconBestStateDetailInfo.Committee, self).__init__(raw_data)
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

    def print_committees(self):
        all_committee_in_all_shard_dict = self.get_shard_committees()
        for key, value in all_committee_in_all_shard_dict.items():
            for info in value:
                public_key = info.get_inc_public_key()
                shard_id = self.is_he_a_committee(public_key)
                for auto_staking in self.get_auto_staking_committees():
                    if auto_staking.get_inc_public_key() == public_key:
                        auto_staking_info = self.is_this_committee_auto_stake(public_key)
                validator_number = len(value)
                INFO(f"{l6(public_key)} - {shard_id} - {validator_number} - {auto_staking_info}")

    def get_block_hash(self):
        return self.data["BestBlockHash"]

    def get_previous_block_hash(self):
        return self.data["PreviousBestBlockHash"]

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
            beacon_committee_obj = BeaconBestStateDetailInfo.Committee(obj)
            beacon_committee_objs.append(beacon_committee_obj)
        return beacon_committee_objs

    def get_beacon_pending_validator(self):
        raw_beacon_pending_validator_list = self.data['BeaconPendingValidator']
        beacon_pending_validator_objs = []
        for obj in raw_beacon_pending_validator_list:
            beacon_pending_validator_obj = BeaconBestStateDetailInfo.Committee(obj)
            beacon_pending_validator_objs.append(beacon_pending_validator_obj)
        return beacon_pending_validator_objs

    def get_shard_committees(self, shard_num=None, validator_number=None):
        """

        :param shard_num:
        :param validator_number:
        :return: Return one BeaconBestStateDetailInfo.Committee obj shard_num and validator_num are specified
        Return list of BeaconBestStateDetailInfo.Committee obj if only shard_num is specify
        Return dict of {shard_num: BeaconBestStateDetailInfo.Committee} obj if only shard_num and validator_num are specify
        """
        obj_list = []
        committee_dict_raw = self.data['ShardCommittee']  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_raw = committee_dict_raw[str(shard_num)][validator_number]
            committee_obj = BeaconBestStateDetailInfo.Committee(committee_raw)
            return committee_obj
        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_list_raw = committee_dict_raw[str(shard_num)]
            for committee_raw in committee_list_raw:
                committee_obj = BeaconBestStateDetailInfo.Committee(committee_raw)
                obj_list.append(committee_obj)
            return obj_list
        elif shard_num is None and validator_number is None:
            dict_objs = {}
            list_objs = []
            for key, value in committee_dict_raw.items():
                for info in value:
                    obj = BeaconBestStateDetailInfo.Committee(info)
                    list_objs.append(obj)
                dict_objs.update({key: list_objs})
                list_objs = []
            return dict_objs
        else:
            return

    def get_shard_pending_validator(self, shard_num=None, validator_number=None):
        obj_list = []
        committee_dict_raw = self.data['ShardPendingValidator']  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_raw = committee_dict_raw[str(shard_num)][validator_number]
            committee_obj = BeaconBestStateDetailInfo.Committee(committee_raw)
            return committee_obj
        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_list_raw = committee_dict_raw[str(shard_num)]
            for committee_raw in committee_list_raw:
                committee_obj = BeaconBestStateDetailInfo.Committee(committee_raw)
                obj_list.append(committee_obj)
            return obj_list
        elif shard_num is None and validator_number is None:
            dict_objs = {}
            list_objs = []
            for key, value in committee_dict_raw.items():
                for info in value:
                    obj = BeaconBestStateDetailInfo.Committee(info)
                    list_objs.append(obj)
                dict_objs.update({key: list_objs})
                list_objs = []
            return dict_objs
        else:
            return

    def get_auto_staking_committees(self, auto_staking_number=None):
        auto_staking_objs = []
        raw_auto_staking_list_raw = self.data['AutoStaking']

        if auto_staking_number is not None:  # get a specific committee auto staking
            auto_staking_raw = raw_auto_staking_list_raw[(auto_staking_number)]
            auto_staking_obj = BeaconBestStateDetailInfo.Committee(auto_staking_raw)
            return auto_staking_obj
        elif auto_staking_number is None:  # get all committee auto staking
            for auto_staking_raw in raw_auto_staking_list_raw:
                auto_staking_obj = BeaconBestStateDetailInfo.Committee(auto_staking_raw)
                auto_staking_objs.append(auto_staking_obj)
            return auto_staking_objs

    def is_he_a_committee(self, account):
        """
        Function to find shard committee number by using Account or public key
        :param account: Account obj or public key
        :return: shard committee number
        """
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

    def get_candidate_shard_waiting_current_random(self):
        """
        Function to get candidate shard waiting current random
        :return: a list candidate shard waiting current random objs
        """
        candidate_shard_waiting_current_random_objs = []
        candidate_shard_waiting_current_random_list_raw = self.data['CandidateShardWaitingForCurrentRandom']
        for obj in candidate_shard_waiting_current_random_list_raw:
            candidate_shard_waiting_current_random_obj = BeaconBestStateDetailInfo.Committee(obj)
            candidate_shard_waiting_current_random_objs.append(candidate_shard_waiting_current_random_obj)
        return candidate_shard_waiting_current_random_objs

    # TODO: Will update after getting the data
    def get_candidate_beacon_waiting_current_random(self):
        return self.data["CandidateBeaconWaitingForCurrentRandom"]

    def get_candidate_beacon_waiting_next_random(self):
        return self.data["CandidateBeaconWaitingForNextRandom"]

    def get_candidate_shard_waiting_next_random(self):
        """
        Function to get candidate shard waiting next random
        :return: a list candidate shard waiting next random objs
        :return:
        """
        candidate_shard_waiting_next_random_objs = []
        candidate_shard_waiting_next_random_list_raw = self.data['CandidateShardWaitingForNextRandom']
        for obj in candidate_shard_waiting_next_random_list_raw:
            candidate_shard_waiting_next_random_obj = BeaconBestStateDetailInfo.Committee(obj)
            candidate_shard_waiting_next_random_objs.append(candidate_shard_waiting_next_random_obj)
        return candidate_shard_waiting_next_random_objs

    def get_reward_receiver(self):
        return self.data["RewardReceiver"]

    def get_current_shard_committee_size(self, shard_number):
        committee_list_in_shard = self.get_shard_committees(shard_number)
        return len(committee_list_in_shard)


class BeaconBlock(BlockChainInfoBaseClass):
    INST_TYPE_DAO = 'dev'
    INST_TYPE_SHARD = 'shard'
    INST_TYPE_BEACON = 'beacon'
    INST_TYPE_PORTAL = 'portal'

    class ShardState(BlockChainInfoBaseClass):
        class BlockInfo(BlockChainInfoBaseClass):
            def get_height(self):
                return self.data['Height']

            def get_hash(self):
                return self.data['Hash']

            def get_cross_shard(self):
                return self.data['CrossShard']

        def get_blocks_info(self):
            info_list = []
            for raw_info in self.data:
                info = BeaconBlock.ShardState.BlockInfo(raw_info)
                info_list.append(info)
            return info_list

        def get_smallest_block_height(self):
            info_list = self.get_blocks_info()
            list_len = len(info_list)
            smallest_block_height = self.get_blocks_info()[0]

            if list_len == 1:
                return smallest_block_height.get_height()

            for info in info_list:
                if info.get_height() < smallest_block_height.get_height():
                    smallest_block_height = info

            return smallest_block_height.get_height()

        def get_biggest_block_height(self):
            info_list = self.get_blocks_info()
            list_len = len(info_list)
            biggest_block_height = self.get_blocks_info()[0]

            if list_len == 1:
                return biggest_block_height.get_height()

            for info in info_list:
                if info.get_height() > biggest_block_height.get_height():
                    biggest_block_height = info

            return biggest_block_height.get_height()

    class BeaconInstruction(BlockChainInfoBaseClass):
        """
        example 1:
        [
           "39",
           "0",
           "beaconRewardInst",
           "{\"BeaconReward\":{\"0000000000000000000000000000000000000000000000000000000000000004\":855000000},\"PayToPublicKey\":\"1TdgrfUkGoRu365bCPoaYpXn3ceCFvG9ts4xMgPhxq8MPZwW3i\"}"
        ]

        example 2:
        [
            "42",
            "0",
            "devRewardInst",
            "{\"IncDAOReward\":{\"0000000000000000000000000000000000000000000000000000000000000004\":760000000}}"
        ]

        example 3:
        [
            "43",
            "0",
            "shardRewardInst",
            "{\"ShardReward\":{\"0000000000000000000000000000000000000000000000000000000000000004\":1800000000},\"Epoch\":898}"
        ]
        """

        class InstructionDetail(BlockChainInfoBaseClass):
            def __str__(self):
                pass  # todo

            def _get_reward_dict(self):
                return self.data[self.get_type()]

            def get_type(self):
                keys = self.data.keys()
                for k in keys:
                    if "Reward" in k:
                        return k
                return None

            def get_rewarded_token(self):  # return a list of token id to receive as reward
                reward_dict = self._get_reward_dict()
                token_list = []
                for token in reward_dict.keys:
                    token_list.append(token)
                return token_list

            def get_reward_amount(self, token_id=None):
                # return amount reward of a token, or a dict of {token: reward amount ...}
                if token_id is None:
                    token_id = PRV_ID
                return self._get_reward_dict()[token_id]

            def get_public_k_to_pay_to(self):
                return self.data['PayToPublicKey']

            def get_epoch(self):
                return self.data['Epoch']

            def get_shard_id(self):
                return self.data['ShardID']

            def get_txs_fee(self):
                return self.data['TxsFee']

            def get_shard_block_height(self):
                return self.data['ShardBlockHeight']

        def __str__(self):
            return self.data

        def get_num_1(self):
            return self.data[0]

        def get_num_2(self):
            return self.data[1]

        def get_instruction_type(self):
            index_2 = self.data[2]
            if "Inst" in index_2:
                return self.data[2]
            return ''

        def get_instruction_detail(self):
            if self.get_instruction_type() == '':  # instruction has no type
                inst_dict_raw = json.loads(self.data[2])
            else:
                inst_dict_raw = json.loads(self.data[3])

            inst_detail_obj = BeaconBlock.BeaconInstruction.InstructionDetail(inst_dict_raw)

            return inst_detail_obj

    def get_hash(self):
        return self.data["Hash"]

    def get_height(self):
        return self.data['Height']

    def get_validation_data(self):
        return self.data["ValidationData"]

    def get_block_producer(self):
        return self.data["BlockProducer"]

    def get_consensus_type(self):
        return self.data["ConsensusType"]

    def get_version(self):
        return self.data["Version"]

    def get_epoch(self):
        return self.data["Epoch"]

    def get_round(self):
        return self.data["Round"]

    def get_time(self):
        return self.data["Time"]

    def get_previous_block_hash(self):
        return self.data["PreviousBlockHash"]

    def get_next_block_hash(self):
        return self.data["NextBlockHash"]

    def get_size(self):
        return self.data["Size"]

    def get_shard_states(self, shard_id=None):
        dict_raw_shard_state = self.data["ShardStates"]
        shard_state_list_obj = []
        for _id, state in dict_raw_shard_state.items():
            shard_state_obj = BeaconBlock.ShardState(state)
            if shard_id is not None and _id == str(shard_id):
                return shard_state_obj
            elif shard_id is None:
                shard_state_list_obj.append(shard_state_obj)

    def get_instructions(self, inst_type=None):
        list_raw_inst = self.data["Instructions"]
        list_obj_inst = []
        for raw_inst in list_raw_inst:
            obj_inst = BeaconBlock.BeaconInstruction(raw_inst)
            list_obj_inst.append(obj_inst)

        if inst_type is None:
            return list_obj_inst

        list_obj_inst_w_type = []
        for inst in list_obj_inst:
            if inst_type in inst.get_instruction_type():
                list_obj_inst_w_type.append(inst)

        return list_obj_inst_w_type

    def get_transaction_reward_from_instruction(self, token=None):
        """

        :param token:
        :return:
        :type: dict {'beacon': amount,
                    'DAO': amount,
                    shard_id: amount,
                    ...}
        """
        RESULT = {}
        token = PRV_ID if token is None else token
        INFO(f'GET reward info, epoch {self.get_epoch() - 1}, height {self.get_height()}, token {l6(token)}')
        beacon_reward_inst = self.get_instructions(BeaconBlock.INST_TYPE_BEACON)
        DAO_reward_inst = self.get_instructions(BeaconBlock.INST_TYPE_DAO)
        shard_reward_inst = self.get_instructions(BeaconBlock.INST_TYPE_SHARD)

        # get shard reward first
        for inst in shard_reward_inst:
            shard_id = inst.get_num_2()
            amount = inst.get_instruction_detail().get_reward_amount(token)
            RESULT[str(shard_id)] = amount
        # get beacon reward
        sum_beacon_reward = 0
        for inst in beacon_reward_inst:
            amount = inst.get_instruction_detail().get_reward_amount(token)
            sum_beacon_reward += amount
        RESULT['beacon'] = sum_beacon_reward
        # get DAO reward
        DAO_amount = DAO_reward_inst[0].get_instruction_detail().get_reward_amount()
        RESULT['DAO'] = DAO_amount

        return RESULT


class BeaconBestStateInfo(BeaconBestStateDetailInfo):

    def get_beacon_committee(self):
        return self.data['BeaconCommittee']

    def get_candidate_shard_waiting_next_random(self):
        candidate_shard_waiting_next_random_list_raw = self.data['CandidateShardWaitingForNextRandom']
        return candidate_shard_waiting_next_random_list_raw

    def get_candidate_shard_waiting_current_random(self):
        candidate_shard_waiting_current_random_list_raw = self.data['CandidateShardWaitingForCurrentRandom']
        return candidate_shard_waiting_current_random_list_raw

    def get_shard_committees(self, shard_num=None, validator_number=None):
        """
        Function to get shard committee
        :param shard_num: shard id
        :param validator_number: position of validator in shard committee
        :return:
        Return a committee public key that shard_num and validator_num are specified
        Return list of committee public key if only shard_num is specify
        Return dict of {shard_num: list of committee public key} if only shard_num and validator_num are specify
        """
        committee_dict_raw = self.data['ShardCommittee']  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_public_key = committee_dict_raw[str(shard_num)][validator_number]
            return committee_public_key

        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_public_key_list = committee_dict_raw[str(shard_num)]
            return committee_public_key_list

        elif shard_num is None and validator_number is None:  # get all committee in all shard
            committee_public_key_dict = self.data['ShardCommittee']
            return committee_public_key_dict

    def get_auto_staking_committees(self, committee_public_key=None):
        """
        Function to get auto staking committee
        :param committee_public_key: committee public key of account
        :return: a dict if committee public key is None
        """
        auto_staking_dict_raw = self.data['AutoStaking']

        if committee_public_key is None:  # get all committee auto staking
            return auto_staking_dict_raw

        elif committee_public_key is not None:  # get a committee auto staking
            for key, value in auto_staking_dict_raw.items():
                if committee_public_key == key:
                    return value

    def get_shard_pending_validator(self, shard_num=None, validator_number=None):
        """
        Function to get committee in shard pending validator
        :param shard_num: shard id
        :param validator_number: position of validator in shard pending validator
        :return:
        Return a committee public key that shard_num and validator_num are specified
        Return list of committee public key if only shard_num is specify
        Return dict of {shard_num: list of committee public key} if only shard_num and validator_num are specify
        """
        committee_dict_raw = self.data['ShardPendingValidator']  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_public_key = committee_dict_raw[str(shard_num)][validator_number]
            return committee_public_key

        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_public_key_list = committee_dict_raw[str(shard_num)]
            return committee_public_key_list

        elif shard_num is None and validator_number is None:  # get all committee in all shard
            committee_public_key_dict = self.data['ShardPendingValidator']
            return committee_public_key_dict