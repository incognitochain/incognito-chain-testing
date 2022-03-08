import json
from abc import abstractmethod

from Configs.Constants import PRV_ID
from Drivers.Response import RPCResponseBase
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6, KeyExtractor
from Objects import BlockChainInfoBaseClass

logger = config_logger(__name__)


class InstructionType:
    PDE3_TRADE = "285"


class BeaconBestStateBase(RPCResponseBase):
    def get_block_hash(self):
        return self.get_result("BestBlockHash")

    def get_previous_block_hash(self):
        return self.get_result("PreviousBestBlockHash")

    def get_epoch(self):
        return self.get_result("Epoch")

    def get_beacon_height(self):
        return self.get_result("BeaconHeight")

    def get_beacon_proposer_index(self):
        return self.get_result("BeaconProposerIndex")

    def get_current_random_number(self):
        return self.get_result("CurrentRandomNumber")

    def get_current_random_time_stamp(self):
        return self.get_result("CurrentRandomTimeStamp")

    def get_max_beacon_committee_size(self):
        return self.get_result("MaxBeaconCommitteeSize")

    def get_min_beacon_committee_size(self):
        return self.get_result("MinBeaconCommitteeSize")

    def get_max_shard_committee_size(self):
        return self.get_result("MaxShardCommitteeSize")

    def get_min_shard_committee_size(self):
        return self.get_result("MinShardCommitteeSize")

    def get_active_shard(self):
        return self.get_result("ActiveShards")

    def get_shard_handle(self):
        return self.get_result("ShardHandle")

    def get_missing_signature(self):
        pass

    def get_missing_signature_penalty(self):
        pass

    def get_best_shard_height(self, shard_number=None):
        if shard_number is not None:
            return self.get_result('BestShardHeight')[str(shard_number)]
        else:
            return self.get_result('BestShardHeight')

    def get_candidate_beacon_waiting_current_random(self):
        # TODO: Will update after getting the data
        return self.get_result("CandidateBeaconWaitingForCurrentRandom")

    def get_candidate_beacon_waiting_next_random(self):
        # TODO: Will update after getting the data
        return self.get_result("CandidateBeaconWaitingForNextRandom")

    def get_reward_receiver(self):
        return self.get_result("RewardReceiver")

    @abstractmethod
    def print_committees(self):
        pass

    @abstractmethod
    def get_beacon_committee(self):
        pass

    @abstractmethod
    def get_beacon_pending_validator(self):
        pass

    @abstractmethod
    def get_shard_committees(self, shard_num=None, validator_number=None):
        pass

    @abstractmethod
    def get_shard_pending_validator(self, shard_num=None, validator_number=None):
        pass

    @abstractmethod
    def get_auto_staking_committees(self, account=None):
        pass

    @abstractmethod
    def is_he_a_committee(self, account):
        pass

    @abstractmethod
    def get_candidate_shard_waiting_current_random(self):
        pass

    @abstractmethod
    def get_candidate_shard_waiting_next_random(self):
        pass


class BeaconBestStateDetailInfo(BeaconBestStateBase):
    class Committee(BlockChainInfoBaseClass):
        """
        data sample:
         {
             "IncPubKey": "12DNFqDkW9bNwzVT8fxZd4y2XLz1PRe3jvbHMYgrp1wUBquWpz7",
             "MiningPubKey:
                    {
                      "bls": ""1EF8XFyAYtrNrFMECSPENbxtktjJCJE8faXTdChqVuBMtQNVP2Dd9stFMXKDV8BPNPtmsogV3tLePBPrfAReLp5uW
                      RQA9ngiEivmXFr1rg1wi5Pu31M9Giqhx94ZqgaTk854qUJEGhwXUmkEztw4GKYn7Zq24EDYXGzPK9R43iW1ysWzH5HqH"",
                      "dsa": "17MtmvoQhsppwCJtcuam6DHmEpSGTaK8kNNxCcXheL5apXMe3PH"
                    }
         }
        """

        def get_inc_public_key(self):
            return self.dict_data['IncPubKey']

        def get_bls(self):
            return self.dict_data['MiningPubKey']['bls']

        def get_dsa(self):
            return self.dict_data['MiningPubKey']['dsa']

        def is_auto_staking(self):
            """@return: True/False/None"""
            return self.dict_data.get('IsAutoStake')

        def __eq__(self, other):
            # !! ATTENTION. not compare auto staking info
            return self.get_inc_public_key() == other.get_inc_public_key() and \
                   self.get_bls() == other.get_bls() and \
                   self.get_dsa() == other.get_dsa()

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            string = f'IncPubKey = {self.get_inc_public_key} - IsAutoStake = {self.is_auto_staking}\n'
            return string

    def print_committees(self):
        all_committee_in_all_shard_dict = self.get_shard_committees()
        for shard_id, committee_list in all_committee_in_all_shard_dict.items():
            for i in range(len(committee_list)):
                committee = committee_list[i]
                logger.info(f"{l6(committee.get_inc_public_key())} - shard{shard_id}.{i} - "
                            f"AutoStake {committee.is_auto_staking()}")

    def is_random_number(self):
        return self.get_result("IsGetRandomNumber")

    def get_best_shard_hash(self, shard_number):
        return self.get_result('BestShardHash')[str(shard_number)]

    def get_beacon_committee(self):
        raw_beacon_committee_list = self.get_result('BeaconCommittee')
        beacon_committee_objs = []
        for obj in raw_beacon_committee_list:
            beacon_committee_obj = BeaconBestStateDetailInfo.Committee(obj)
            beacon_committee_objs.append(beacon_committee_obj)
        return beacon_committee_objs

    def get_beacon_pending_validator(self):
        raw_beacon_pending_validator_list = self.get_result('BeaconPendingValidator')
        return self._parse_raw_list_to_shard_committee_list(raw_beacon_pending_validator_list)

    def get_shard_committees(self, shard_num=None, validator_number=None):
        """

        :param shard_num:
        :param validator_number:
        :return: Return one BeaconBestStateDetailInfo.Committee obj shard_num and validator_num are specified
        Return [BeaconBestStateDetailInfo.Committee] obj if only shard_num is specify
        Return {shard_num: BeaconBestStateDetailInfo.Committee} obj if only shard_num and validator_num are specify
        """
        committee_dict_raw = self.get_result('ShardCommittee')  # get all committee in all shar

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_raw = committee_dict_raw[str(shard_num)][validator_number]
            return self._parse_raw_list_to_shard_committee_list([committee_raw])[0]
        if shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_list_raw = committee_dict_raw[str(shard_num)]
            return self._parse_raw_list_to_shard_committee_list(committee_list_raw)
        if shard_num is None and validator_number is None:
            dict_objs = {}
            for shard_id, committee_list_raw in committee_dict_raw.items():
                dict_objs[shard_id] = self._parse_raw_list_to_shard_committee_list(committee_list_raw)
            return dict_objs

    def get_shard_pending_validator(self, shard_num=None, validator_number=None):
        committee_dict_raw = self.get_result('ShardPendingValidator')  # get all pending validator in all shar

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_raw = committee_dict_raw[str(shard_num)][validator_number]
            return self._parse_raw_list_to_shard_committee_list([committee_raw])[0]
        if shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_list_raw = committee_dict_raw[str(shard_num)]
            return self._parse_raw_list_to_shard_committee_list(committee_list_raw)
        if shard_num is None and validator_number is None:
            dict_objs = {}
            for shard, raw_list in committee_dict_raw.items():
                dict_objs[shard] = self._parse_raw_list_to_shard_committee_list(raw_list)
            return dict_objs

    def get_syncing_validators(self, shard_num=None, validator_number=None):
        validators_dict_raw = self.get_result().get('SyncingValidator')  # get all syncing validators in all shard
        if validators_dict_raw is None:
            return
        if shard_num is not None and validator_number is not None:  # get a specific validator
            validator_raw = validators_dict_raw[str(shard_num)][validator_number]
            return self._parse_raw_list_to_shard_committee_list([validator_raw])[0]
        if shard_num is not None and validator_number is None:  # get all validators in a shard
            try:
                committee_list_raw = validators_dict_raw[str(shard_num)]
            except KeyError:
                committee_list_raw = []
            return self._parse_raw_list_to_shard_committee_list(committee_list_raw)
        if shard_num is None and validator_number is None:
            dict_objs = {}
            for shard, raw_list in validators_dict_raw.items():
                dict_objs[shard] = self._parse_raw_list_to_shard_committee_list(raw_list)
            return dict_objs

    def _parse_raw_list_to_shard_committee_list(self, raw_data_list):
        """
        @param raw_data_list: list of ShardCommittee raw data
        @return:
        """
        object_list = []
        for datum in raw_data_list:
            try:
                _ = datum['IsAutoStake']
                o = BeaconBestStateDetailInfo.Committee(datum)
            except KeyError:
                pub_k = datum['IncPubKey']
                datum['IsAutoStake'] = self._get_auto_staking_committee_raw(pub_k)
                o = BeaconBestStateDetailInfo.Committee(datum)
            object_list.append(o)
        return object_list

    def _get_auto_staking_committee_raw(self, public_key):
        raw_auto_staking_data = self.get_result('AutoStaking')
        for raw_datum in raw_auto_staking_data:
            pub_k_of_datum = raw_datum['IncPubKey']
            if pub_k_of_datum == public_key:
                return raw_datum['IsAutoStake']

    def get_auto_staking_committees(self, account=None):
        """
        get auto staking status of a user or get list of all user with their staking status
        @param account: optional, Account object or public key (string)
        @return: list of BeaconBestStateDetailInfo.Committee or True/False/None if account is specified.
        None means committee is not auto staking list
        """
        acc_pub_key = KeyExtractor.inc_public_k(account) if account is not None else None
        auto_staking_objs = []
        raw_auto_staking_list_raw = self.get_result('AutoStaking')
        for raw_data in raw_auto_staking_list_raw:
            auto_staking_obj = BeaconBestStateDetailInfo.Committee(raw_data)
            if auto_staking_obj.get_inc_public_key() == acc_pub_key:
                # logger.info(f"{l6(acc_pub_key)} (public key) auto-staking is {auto_staking_obj.is_auto_staking()}")
                return auto_staking_obj.is_auto_staking()
            auto_staking_objs.append(auto_staking_obj)

        if account is not None:
            logger.info(f"{l6(acc_pub_key)} (public key) not found in auto-staking list")
            return None
        return auto_staking_objs

    def get_staking_tx(self, account=None):
        """
        get staking transaction of a user or get list of all user with their staking transaction
        @param account: optional, Account object or public key (string) or BeaconBestStateDetailInfo.Committee
        @return:
        """
        staking_tx_dict = self.get_result('StakingTx')
        if account is None:
            return staking_tx_dict
        else:
            acc_pub_key = KeyExtractor.inc_public_k(account)

        for key, tx in staking_tx_dict.items():
            if key == acc_pub_key:
                logger.info(f"{l6(acc_pub_key)} (public key) staking tx_id is {tx}")
                return tx
        logger.info(f"{l6(acc_pub_key)} (public key) not found staking tx_id")
        return None

    def get_missing_signature(self, account=None):
        """
        get missing signature of a user or get list of all user with their missing signature
        @param account: optional, Account object or public key (string) or BeaconBestStateDetailInfo.Committee
        @return:
        """
        missing_signature_dict = self.get_result('MissingSignature')
        if account is None:
            return missing_signature_dict
        else:
            acc_pub_key = KeyExtractor.inc_public_k(account)

        for key, count_signature in missing_signature_dict.items():
            if key == acc_pub_key:
                try:
                    total = count_signature["ActualTotal"]
                except KeyError:
                    total = count_signature["Total"]
                missing = count_signature["Missing"]
                # logger.info(f"Count signature of {l6(acc_pub_key)} (public key) - Total: {total} - Missing: {missing}")
                return total, missing
        logger.info(f"Missing Signature of {l6(acc_pub_key)} (public-key) not found")

    def get_missing_signature_penalty(self, account=None):
        """
        get missing signature of a user or get list of all user with their missing signature
        @param account: optional, Account object or public key (string) or BeaconBestStateDetailInfo.Committee
        @return:
        """
        missing_signature_penalty_dict = self.get_result('MissingSignaturePenalty')
        if account is None:
            return missing_signature_penalty_dict
        else:
            acc_pub_key = KeyExtractor.inc_public_k(account)

        for key, count_signature in missing_signature_penalty_dict.items():
            if key == acc_pub_key:
                total = count_signature["Total"]
                missing = count_signature["Missing"]
                logger.info(f"Count signature of {l6(acc_pub_key)} (public key) - Total: {total} - Missing: {missing}")
                return total, missing
        logger.info(f"Missing Signature Penalty of {l6(acc_pub_key)} (public-key) not found")

    def is_he_a_committee(self, account):
        """
        Function to find shard committee number by using Account or public key
        :param account: Account obj or public key
        :return: shard committee number or False if not a committee
        """
        from Objects.AccountObject import Account
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
                    logger.debug(f" IS committee @ B height {self.get_beacon_height()}: "
                                 f"pub_key = {public_key} : shard {shard_number}")
                    return shard_number
        logger.debug(f"NOT committee @ B height {self.get_beacon_height()}: pub_key = {public_key}")
        return False

    def is_he_in_shard_pending(self, account):
        from Objects.AccountObject import Account
        if type(account) == str:
            public_key = account
        elif type(account) == Account:
            public_key = account.public_key
        else:
            public_key = ''

        number_of_shards = self.get_active_shard()
        for shard_number in range(0, number_of_shards):
            shard_pending = self.get_shard_pending_validator(shard_number)
            for committee in shard_pending:
                if committee.get_inc_public_key() == public_key:
                    logger.debug(f" IS in shard pending: pub_key = {public_key} : shard {shard_number}")
                    return shard_number
        logger.debug(f"NOT exist in shard pending: pub_key = {public_key}")
        return False

    def is_he_in_sync_pool(self, account):
        from Objects.AccountObject import Account
        if type(account) == str:
            public_key = account
        elif type(account) == Account:
            public_key = account.public_key
        else:
            public_key = ''

        number_of_shards = self.get_active_shard()
        for shard_number in range(0, number_of_shards):
            shard_pending = self.get_syncing_validators(shard_number)
            for committee in shard_pending:
                if committee.get_inc_public_key() == public_key:
                    logger.debug(f" IS committee in sync pool: pub_key = {public_key} : shard {shard_number}")
                    return shard_number
        logger.debug(f"NOT exist in sync pool: pub_key = {public_key}")
        return False

    def is_he_in_waiting_next_random(self, account):
        from Objects.AccountObject import Account
        if type(account) == str:
            public_key = account
        elif type(account) == Account:
            public_key = account.public_key
        else:
            public_key = ''

        waiting_next_random = self.get_candidate_shard_waiting_next_random()
        for committee in waiting_next_random:
            if committee.get_inc_public_key() == public_key:
                logger.debug(f" IS validator in shard waiting next random: pub_key = {public_key}")
                return True
        logger.debug(f"NOT exist in shard waiting next random: pub_key = {public_key}")
        return False

    def where_is_he(self, account):
        position = "not any list"
        in_random = self.is_he_in_waiting_next_random(account)
        in_shard_sync_pool = self.is_he_in_sync_pool(account)
        in_shard_pending = self.is_he_in_shard_pending(account)
        in_shard_comm = self.is_he_a_committee(account)
        if in_random:
            position = "Waiting"
        elif in_shard_sync_pool is not False:
            position = f"Sync pool shard {in_shard_sync_pool}"
        elif in_shard_pending is not False:
            position = f"Pending shard {in_shard_pending}"
        elif in_shard_comm is not False:
            position = f"Committee shard {in_shard_comm}"
        logger.info(f"Public k {account.public_key[-6:]} is in {position} @ {self.get_beacon_height()}")
        return position

    def get_candidate_shard_waiting_current_random(self):
        """
        Function to get candidate shard waiting current random
        :return: a list candidate shard waiting current random objs
        """
        candidate_shard_waiting_current_random_list_raw = self.get_result('CandidateShardWaitingForCurrentRandom')
        return self._parse_raw_list_to_shard_committee_list(candidate_shard_waiting_current_random_list_raw)

    def get_candidate_shard_waiting_next_random(self):
        """
        Function to get candidate shard waiting next random
        :return: a list candidate shard waiting next random objs
        :return:
        """
        candidate_shard_waiting_next_random_list_raw = self.get_result('CandidateShardWaitingForNextRandom')
        return self._parse_raw_list_to_shard_committee_list(candidate_shard_waiting_next_random_list_raw)

    def get_current_shard_committee_size(self, shard_number):
        committee_list_in_shard = self.get_shard_committees(shard_number)
        return len(committee_list_in_shard)


class BeaconBestStateInfo(BeaconBestStateBase):
    def print_committees(self):
        # todo: implement later
        pass

    def get_beacon_pending_validator(self):
        # todo: implement later
        pass

    def is_he_a_committee(self, account):
        """

        @param account:
        @return: shard id if found, False if not
        """
        for shard_id, committee_pub_k_list in self.get_shard_committees().items():
            if account.committee_public_k in committee_pub_k_list:
                logger.info(f'(comm pub k) {l6(account.committee_public_k)} is a committee of shard {shard_id}')
                return shard_id
        logger.info(f'(comm pub k) {l6(account.committee_public_k)} is NOT a committee of any shard')
        return False

    def is_in_shard_pending_list(self, account):
        """

        @param account:
        @return: shard id if found, False if not
        """
        for shard_id, pending_list in self.get_shard_pending_validator().items():
            if account.committee_public_k in pending_list:
                logger.info(f'(comm pub k) {l6(account.committee_public_k)} is in shard {shard_id} pending list')
                return shard_id
        logger.info(f'(comm pub k) {l6(account.committee_public_k)} is NOT in pending list of any shard')
        return False

    def get_beacon_committee(self):
        return self.get_result('BeaconCommittee')

    def get_candidate_shard_waiting_next_random(self):
        candidate_shard_waiting_next_random_list_raw = self.get_result('CandidateShardWaitingForNextRandom')
        return candidate_shard_waiting_next_random_list_raw

    def get_candidate_shard_waiting_current_random(self):
        candidate_shard_waiting_current_random_list_raw = self.get_result('CandidateShardWaitingForCurrentRandom')
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
        committee_dict_raw = self.get_result('ShardCommittee')  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_public_key = committee_dict_raw[str(shard_num)][validator_number]
            return committee_public_key

        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_public_key_list = committee_dict_raw[str(shard_num)]
            return committee_public_key_list

        elif shard_num is None and validator_number is None:  # get all committee in all shard
            committee_public_key_dict = self.get_result('ShardCommittee')
            return committee_public_key_dict

    def get_current_shard_committee_size(self, shard_id):
        return len(self.get_shard_committees(shard_id))

    def get_auto_staking_committees(self, account=None):
        """
        Function to get auto staking committee
        :param account: Account obj or committee_public_k
        :return: a dict {committee_public_k: true/false} if account is None.
         If account not none, return True/False if account is found in the list.
         Return None if account not exist in the list
        """
        auto_staking_dict_raw = self.get_result('AutoStaking')

        if account is None:  # get all committee auto staking
            return auto_staking_dict_raw
        else:
            committee_public_k = KeyExtractor.committee_public_k(account)
        # get a committee auto staking
        for key, value in auto_staking_dict_raw.items():
            if committee_public_k == key:
                logger.info(f'(comm pub k) {l6(committee_public_k)} auto staking is {value}')
                return value
        logger.info(f'(comm pub k) {l6(committee_public_k)} is not found in auto staking list')
        return None

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
        committee_dict_raw = self.get_result('ShardPendingValidator')  # get all committee in all shard

        if shard_num is not None and validator_number is not None:  # get a specific committee
            committee_public_key = committee_dict_raw[str(shard_num)][validator_number]
            return committee_public_key

        elif shard_num is not None and validator_number is None:  # get all committee in a shard
            committee_public_key_list = committee_dict_raw[str(shard_num)]
            return committee_public_key_list

        elif shard_num is None and validator_number is None:  # get all committee in all shard
            committee_public_key_dict = self.get_result('ShardPendingValidator')
            return committee_public_key_dict

    def get_syncing_validators(self, shard_num=None, validator_number=None):
        """
        Function to get committee in shard pending validator
        :param shard_num: shard id
        :param validator_number: position of validator in shard pending validator
        :return:
        Return a committee public key that shard_num and validator_num are specified
        Return list of committee public key if only shard_num is specify
        Return dict of {shard_num: list of committee public key} if only shard_num and validator_num are specify
        """
        validators_dict_raw = self.get_result().get('SyncingValidator')  # get all validators in all shard

        if shard_num is not None and validator_number is not None:  # get a specific validator
            committee_public_key = validators_dict_raw[str(shard_num)][validator_number]
            return committee_public_key

        elif shard_num is not None and validator_number is None:  # get all validators in a shard
            committee_public_key_list = validators_dict_raw[str(shard_num)]
            return committee_public_key_list

        elif shard_num is None and validator_number is None:  # get all validators in all shard
            committee_public_key_dict = validators_dict_raw
            return committee_public_key_dict

    def get_staking_tx(self, account=None):
        """
        get staking transaction of a user or get list of all user with their staking transaction
        @param account: optional, Account obj or committee_public_k
        @return:
        """
        staking_tx_dict = self.get_result('StakingTx')
        if account is None:
            return staking_tx_dict
        else:
            acc_committee_pub_key = KeyExtractor.committee_public_k(account)

        for key, tx in staking_tx_dict.items():
            if key == acc_committee_pub_key:
                logger.info(f"{l6(acc_committee_pub_key)} (public key) staking tx_id is {tx}")
                return tx
        logger.info(f"{l6(acc_committee_pub_key)} (public key) not found staking tx_id")
        return None

    def get_missing_signature(self, account=None):
        """
        get missing signature of a user or get list of all user with their missing signature
        @param account: optional, Account obj or committee_public_k
        @return:
        """
        missing_signature_dict = self.get_result('MissingSignature')
        if account is None:
            return missing_signature_dict
        else:
            acc_committee_pub_key = KeyExtractor.committee_public_k(account)

        for key, count_signature in missing_signature_dict.items():
            if key == acc_committee_pub_key:
                try:
                    total = count_signature["Total"]
                except KeyError:
                    total = count_signature["ActualTotal"]
                missing = count_signature["Missing"]
                logger.info(
                    f"Count signature of {l6(acc_committee_pub_key)} (public k) - Total: {total} - Missing: {missing}")
                return total, missing
        logger.info(f"Missing Signature of {l6(acc_committee_pub_key)} (public-key) not found")

    def get_missing_signature_penalty(self, account=None):
        """
        get missing signature of a user or get list of all user with their missing signature
        @param account: optional, Account obj or committee_public_k
        @return:
        """
        missing_signature_penalty_dict = self.get_result('MissingSignaturePenalty')
        if account is None:
            return missing_signature_penalty_dict
        else:
            acc_committee_pub_key = KeyExtractor.committee_public_k(account)

        for key, count_signature in missing_signature_penalty_dict.items():
            if key == acc_committee_pub_key:
                total = count_signature["Total"]
                missing = count_signature["Missing"]
                logger.info(
                    f"Count signature of {l6(acc_committee_pub_key)} (public k) - Total: {total} - Missing: {missing}")
                return total, missing
        logger.info(f"Missing Signature Penalty of {l6(acc_committee_pub_key)} (public k) not found")

    def get_number_of_shard_block(self, shard_id=None):
        raw_data = self.get_result("NumberOfShardBlock")
        if shard_id is not None:
            return raw_data[str(shard_id)]
        return raw_data


class BeaconBlock(BlockChainInfoBaseClass):
    INST_TYPE_DAO = 'devRewardInst'
    INST_TYPE_SHARD = 'shardRewardInst'
    INST_TYPE_BEACON = 'beaconRewardInst'
    INST_TYPE_PORTAL = 'portal'

    class ShardState(BlockChainInfoBaseClass):
        class BlockInfo(BlockChainInfoBaseClass):
            def get_height(self):
                return self.dict_data['Height']

            def get_hash(self):
                return self.dict_data['Hash']

            def get_cross_shard(self):
                return self.dict_data['CrossShard']

        def get_blocks_info(self):
            return [BeaconBlock.ShardState.BlockInfo(raw_info) for raw_info in self.dict_data]

        def get_smallest_block_height(self):
            return min([info.get_height() for info in self.get_blocks_info()])

        def get_biggest_block_height(self):
            return max([info.get_height() for info in self.get_blocks_info()])

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
                return self.dict_data[self.get_type()]

            def get_type(self):
                keys = self.dict_data.keys()
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
                """
                @param token_id: default = PRV_ID
                @return: return reward amount of token_id, 0 if not found
                """
                if token_id is None:
                    token_id = PRV_ID
                try:
                    return self._get_reward_dict()[token_id]
                except KeyError:
                    return 0

            def get_public_k_to_pay_to(self):
                return self.dict_data['PayToPublicKey']

            def get_epoch(self):
                return self.dict_data['Epoch']

            def get_shard_id(self):
                return self.dict_data['ShardID']

            def get_txs_fee(self):
                return self.dict_data['TxsFee']

            def get_shard_block_height(self):
                return self.dict_data['ShardBlockHeight']

        def __str__(self):
            return json.dumps(self.dict_data, indent=3)

        def get_num_1(self):
            return self.dict_data[0]

        def get_num_2(self):
            return self.dict_data[1]

        def get_instruction_description(self):
            try:
                inst_type = self.dict_data[2]
                if "Inst" in inst_type:  # beaconRewardInst, devRewardInst, shardRewardInst, portalRewardInst
                    return inst_type
            except IndexError:
                inst_type = self.dict_data[0]

            if type(inst_type) is str:  # unstake, return, swap_shard
                return inst_type

            return ''

        def get_instruction_detail(self):
            if self.get_instruction_description() == '':  # instruction has no type
                inst_dict_raw = json.loads(self.dict_data[2])
            else:
                inst_dict_raw = json.loads(self.dict_data[3])

            inst_detail_obj = BeaconBlock.BeaconInstruction.InstructionDetail(inst_dict_raw)

            return inst_detail_obj

        def get_instruction_type(self):
            return self.dict_data[0]

    def get_hash(self):
        return self.dict_data["Hash"]

    def get_height(self):
        return self.dict_data['Height']

    def get_validation_data(self):
        return self.dict_data["ValidationData"]

    def get_block_producer(self):
        return self.dict_data["BlockProducer"]

    def get_consensus_type(self):
        return self.dict_data["ConsensusType"]

    def get_version(self):
        return self.dict_data["Version"]

    def get_epoch(self):
        return self.dict_data["Epoch"]

    def get_round(self):
        return self.dict_data["Round"]

    def get_time(self):
        return self.dict_data["Time"]

    def get_previous_block_hash(self):
        return self.dict_data["PreviousBlockHash"]

    def get_next_block_hash(self):
        return self.dict_data["NextBlockHash"]

    def get_size(self):
        return self.dict_data["Size"]

    def get_shard_states(self, shard_id=None):
        """
        @param shard_id:
        @return: state of shard_id or dict {shard_id: state}
        """
        if shard_id is not None:
            try:
                return BeaconBlock.ShardState(self.dict_data["ShardStates"][str(shard_id)])
            except KeyError:
                logger.debug(f"Not found shard state of shard {shard_id} in beacon block {self.get_height()}")
                return None
        else:
            return {shard: BeaconBlock.ShardState(raw) for shard, raw in self.dict_data["ShardStates"].items()}

    def get_instructions(self, inst_type=None):
        list_raw_inst = self.dict_data["Instructions"]
        list_obj_inst = []
        for raw_inst in list_raw_inst:
            obj_inst = BeaconBlock.BeaconInstruction(raw_inst)
            list_obj_inst.append(obj_inst)

        if inst_type is None:
            return list_obj_inst

        list_obj_inst_w_type = []
        for inst in list_obj_inst:
            if inst_type in inst.get_instruction_description():
                list_obj_inst_w_type.append(inst)

        return list_obj_inst_w_type

    def get_pde3_trade_instructions(self):
        list_raw_inst = self.dict_data["Instructions"]
        list_inst_obj = []
        for raw_inst in list_raw_inst:
            if raw_inst[0] == "285":
                list_inst_obj.append(BeaconBlock.BeaconInstruction(raw_inst))
        return list_inst_obj

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
        logger.info(f'GET reward info, epoch {self.get_epoch() - 1}, height {self.get_height()}, token {l6(token)}')
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
        DAO_amount = DAO_reward_inst[0].get_instruction_detail().get_reward_amount(token)
        RESULT['DAO'] = DAO_amount

        return RESULT

    def sum_all_reward(self):
        all_inst = self.get_transaction_reward_from_instruction()
        sum_reward = 0
        for key, value in all_inst.items():
            sum_reward += value
        return sum_reward

    def is_tx_in_instructions(self, tx_id):
        instructions = self.get_instructions()
        for inst in instructions:
            if tx_id in json.dumps(inst.dict_data):
                return True
        return False
