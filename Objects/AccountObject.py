import copy
import datetime
import random
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from Configs import Constants
from Configs.Configs import ChainConfig, TestConfig
from Configs.Constants import PRV_ID, coin, PBNB_ID, PBTC_ID, Status, DAO_PRIVATE_K
from Drivers.IncognitoKeyGen import get_key_set_from_private_k
from Drivers.NeighborChainCli import NeighborChainCli
from Drivers.Response import Response
from Helpers import TestHelper
from Helpers.Logging import INFO, INFO_HEADLINE, WARNING, ERROR
from Helpers.TestHelper import l6, KeyExtractor, ChainHelper
from Helpers.Time import WAIT, get_current_date_time
from Objects.CoinObject import TxOutPut, ListOwnedToken, ListPrvTXO
from Objects.PortalObjects import RedeemReqInfo, PortalStateInfo


class Account:
    _cache_custodian_inf = 'custodian_info'
    _cache_bal = 'bal'
    _cache_nft_id = 'nft_id'

    def set_remote_addr(self, addresses):
        """

        @param addresses:
            address list with following order: BNB, BTC. Set to None if you wish to leave the address empty
        @return:
        """
        support_token_list = [PBNB_ID, PBTC_ID]
        for token in support_token_list:
            self.remote_addr[token] = addresses.get(token)
        return self

    def get_remote_addr(self, token_id, address_type=None):
        if address_type is None:
            return self.remote_addr.get(token_id)
        else:
            try:
                return self.remote_addr.get(token_id).get(address_type)
            except (AttributeError, KeyError):
                return None

    def is_this_my_key(self, key_to_check):
        """
        @param key_to_check:
        @return: key type of the {key_key_to_check} or False if not found in this account
        """
        ktc_ver = self.check_payment_key_version(key_to_check)
        for attribute, value in self.__dict__.items():
            if "key" in attribute or "address" in attribute or "_k" in attribute:
                value_key_ver = self.check_payment_key_version(value)
                if ktc_ver != value_key_ver and ktc_ver != 0 and value_key_ver != 0:
                    key_to_check = self.convert_payment_k_to_v1(key_to_check) if ktc_ver == 2 else key_to_check
                    value = self.convert_payment_k_to_v1(value) if value_key_ver == 2 else value
                if key_to_check == value:
                    return attribute
        return False

    def __init__(self, private_key=None, payment_k=None, handler=None, **kwargs):
        """
        @param private_key: private key of this account,
         other keys will be generated automatically if payment_k is not specified
        @param payment_k: payment key of this account, if specified along with private key, other keys will not
         get generated and will be set to None
        @param handler: Node object, specify which chain this account belong to by specifying one node of the chain here
        (usually full node). If None, account is tied to default full node in specified test bed
        @param kwargs:
        """
        version = kwargs.get('version', TestConfig.KEY_VERSION)
        self.remote_addr = {}
        self.private_key = private_key
        self.payment_key = payment_k
        self.validator_key = \
            self.public_key = \
            self.read_only_key = \
            self.bls_public_k = \
            self.bridge_public_k = \
            self.mining_public_k = \
            self.ota_k = \
            self.view_k = \
            self.committee_public_k = None
        self.shard = kwargs.get('shard')
        self.cache = {Account._cache_bal: {},
                      Account._cache_nft_id: []}
        if handler:
            self.REQ_HANDLER = handler
        else:
            from Objects import IncognitoTestCase
            self.REQ_HANDLER = IncognitoTestCase.SUT()

        if private_key and not payment_k:  # generate all key from private key if there's privatekey but not paymentkey
            self.get_keys(version)

    def check_payment_key_version(self, key=None):
        """
        this not yet is the best solution to check key version, but it works for now. so... WTH!
        @param key:
        @return: 1 or 2. None if don't know what the key is.
        """
        key = key if key else self.payment_key
        if len(key) == 103:
            return 1
        if len(key) == 148:
            return 2
        return 0

    def get_keys(self, version, **kwargs):
        """
        generate all key from private key
        @param version: key version 1/2
        @param kwargs: private_key=xxx, default value: self.private_key
        @return:
        """
        private_key = kwargs.get('private_key', self.private_key)
        self.private_key, self.payment_key, self.public_key, self.read_only_key, self.validator_key, \
        self.bls_public_k, self.bridge_public_k, self.mining_public_k, self.committee_public_k, \
        self.view_k, self.ota_k, self.shard = \
            get_key_set_from_private_k(private_key, version)
        return self

    @property
    def incognito_addr(self):  # just an alias for payment key
        return self.payment_key

    @property
    def nft_ids(self) -> List:
        return self.cache[Account._cache_nft_id]

    def save_nft_id(self, nft_id):
        self.nft_ids.append(nft_id) if nft_id not in self.nft_ids else None
        return self

    def is_empty(self):
        if self.private_key is None:
            return True
        return False

    def req_to(self, handler):
        """
        Change request handler
        @param handler: Node object
        @return:
        """
        self.REQ_HANDLER = handler
        return self

    def __copy__(self):
        copy_obj = Account()

        copy_obj.private_key = self.private_key
        copy_obj.validator_key = self.validator_key
        copy_obj.payment_key = self.payment_key
        copy_obj.public_key = self.public_key
        copy_obj.read_only_key = self.read_only_key
        copy_obj.bls_public_k = self.bls_public_k
        copy_obj.bridge_public_k = self.bridge_public_k
        copy_obj.mining_public_k = self.mining_public_k
        copy_obj.committee_public_k = self.committee_public_k
        copy_obj.shard = self.shard
        copy_obj.cache = self.cache
        copy_obj.ota_k = self.ota_k
        return copy_obj

    def __deepcopy__(self, memo=None):
        copy_obj = Account()

        copy_obj.private_key = copy.deepcopy(self.private_key)
        copy_obj.validator_key = copy.deepcopy(self.validator_key)
        copy_obj.payment_key = copy.deepcopy(self.payment_key)
        copy_obj.public_key = copy.deepcopy(self.public_key)
        copy_obj.read_only_key = copy.deepcopy(self.read_only_key)
        copy_obj.bls_public_k = copy.deepcopy(self.bls_public_k)
        copy_obj.bridge_public_k = copy.deepcopy(self.bridge_public_k)
        copy_obj.mining_public_k = copy.deepcopy(self.mining_public_k)
        copy_obj.committee_public_k = copy.deepcopy(self.committee_public_k)
        copy_obj.shard = copy.deepcopy(self.shard)
        copy_obj.cache = copy.deepcopy(self.cache)
        copy_obj.ota_k = copy.deepcopy(self.ota_k)
        return copy_obj

    def __eq__(self, other):
        if self.payment_key == other.payment_key:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # for using Account object as 'key' in dictionary
        return int(str(self.private_key).encode('utf8').hex(), 16)

    def clone(self):
        return self.__deepcopy__()

    def convert_payment_address_to_version(self, version=1):
        self.payment_key = get_key_set_from_private_k(self.private_key, version)[1]
        return self

    def create_tx_proof(self, receiver, amount, fee=-1, privacy=1):
        resp = self.REQ_HANDLER.transaction().create_tx(self.private_key, receiver.payment_key, amount,
                                                        fee, privacy).expect_no_error()
        if resp.is_node_busy():
            return 'busy'
        return resp.get_created_proof()

    def calculate_shard_id(self):
        if not self.payment_key:
            self.find_payment_key()
        if not self.public_key:
            self.find_public_key()
        response = self.REQ_HANDLER.transaction().get_public_key_by_payment_key(self.payment_key)
        last_byte = response.get_result("PublicKeyInBytes")[-1]
        self.shard = last_byte % 8
        return self.shard

    def __str__(self):
        string = f'Shard = {self.shard}\n' + \
                 f'Private key = {self.private_key}\n' + \
                 f'Payment key = {self.payment_key}'
        if self.read_only_key:
            string += f'\nRead only key = {self.read_only_key}'
        if self.validator_key:
            string += f'\nValidator key = {self.validator_key}'
        if self.public_key:
            string += f'\nPublic key = {self.public_key}'
        try:
            balance_prv = self.cache['balance_prv']
            string += f'\nBalance = {balance_prv}'
        except KeyError:
            pass
        return f'{string}\n'

    def find_payment_key(self, force=False):
        """
        find payment address from private key

        @return:
        """
        if not force:
            if self.payment_key is not None:
                return self.payment_key

        tx = self.REQ_HANDLER.transaction().list_custom_token_balance(self.private_key)
        self.payment_key = tx.get_result('PaymentAddress')
        return self.payment_key

    def find_public_key(self, force=False):
        """

        @return:
        """
        if not force and self.public_key:
            return self.public_key

        tx = self.REQ_HANDLER.transaction().get_public_key_by_payment_key(self.payment_key)
        self.public_key = tx.get_result('PublicKeyInBase58Check')
        return self.public_key

    def get_estimate_fee_and_size(self, receiver, amount, fee=-1, privacy=1):
        r = self.REQ_HANDLER.transaction().estimate_tx_fee(self.private_key, receiver.payment_key, amount, fee, privacy)
        estimate_fee_coin_perkb = int(r.get_result('EstimateFeeCoinPerKb'))
        estimate_txsize_inKb = int(r.get_result('EstimateTxSizeInKb'))
        return estimate_fee_coin_perkb, estimate_txsize_inKb

    def list_owned_custom_token(self):
        """
        @return: OwnedTokenListInfo
        """
        response = self.REQ_HANDLER.transaction().list_custom_token_balance(self.private_key)
        return ListOwnedToken(response)

    def list_all_tx_output(self, token_id=PRV_ID):
        """

        @param token_id:
        @return:
        """
        response = self.REQ_HANDLER.transaction().list_output_coin(self.payment_key, self.read_only_key, token_id)
        return ListPrvTXO(response)

    def list_unspent_coin(self, token_id=PRV_ID, from_height=0):
        raw_response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key, token_id, from_height)
        return ListPrvTXO(raw_response)

    def list_unspent_token(self, token_id=None, from_height=0):
        obj_coins = []
        token_list = [] if token_id is None else [token_id]
        if not token_id:
            for token_info in self.list_owned_custom_token():
                token_list.append(token_info.get_token_id())

        for token in token_list:
            raw_response = self.REQ_HANDLER.transaction(). \
                list_unspent_output_tokens(self.private_key, token, from_height).expect_no_error()
            raw_coins = raw_response.get_result('Outputs')[self.private_key]
            for raw_coin in raw_coins:
                obj_coins.append(TxOutPut(raw_coin))
        return obj_coins

    def print_all_unspent_coin(self, token_id=None):
        """
        for @debug purpose
        @param token_id:
        @return:
        """
        if not token_id:
            print_data = f'+ {PRV_ID}'
            for c in self.list_unspent_coin():
                print_data += f'\n   {c}'

            for token in self.list_owned_custom_token():
                print_data += f'\n+ {token}'
                for c in self.list_unspent_coin(token.get_token_id()):
                    print_data += f'\n   {c}'
        else:
            print_data = f'\n+ {token_id}'
            for c in self.list_unspent_coin(token_id):
                print_data += f'\n   {c}'
        print(print_data)

    def stake(self, validator=None, receiver_reward=None, stake_amount=ChainConfig.STK_AMOUNT, auto_re_stake=True):
        """

        @param validator: account_object. if None then validator = the stake
        @param receiver_reward: account_object. if None then receiver_reward = the stake
        @param stake_amount: str. if None then stake_amount = 1750PRV
        @param auto_re_stake: bool
        @return:
        """
        if not validator:
            validator = self
        if not receiver_reward:
            receiver_reward = self
        if not receiver_reward.payment_key:
            receiver_reward.find_payment_key()
        if not validator.validator_key:
            raise Exception("Validator key is not specified")

        INFO(
            f'{l6(self.private_key)} Stake for {l6(validator.validator_key)} and reward: {l6(receiver_reward.payment_key)}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, validator.payment_key, validator.validator_key,
                                                receiver_reward.payment_key, stake_amount, auto_re_stake,
                                                TestConfig.TX_VER)

    def stake_and_reward_me(self, stake_amount=ChainConfig.STK_AMOUNT, auto_re_stake=True,
                            tx_version=TestConfig.TX_VER):
        """

        @return:
        """
        INFO(f"Stake and reward me: {self.validator_key}")
        if not self.payment_key:
            self.find_payment_key()
        if not self.public_key:
            self.find_public_key()
        if not self.validator_key:
            raise Exception("Validator key is not specified")

        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, self.payment_key, self.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake, tx_version)

    def stake_someone_reward_me(self, someone, stake_amount=None, auto_re_stake=False, tx_version=TestConfig.TX_VER):
        """

        @return:
        """
        INFO(f'Stake {someone.validator_key} but reward me')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake, tx_version)

    def stake_someone_reward_him(self, someone, stake_amount=None, auto_re_stake=True, tx_version=TestConfig.TX_VER):
        """

        @return:
        """
        INFO(f'Stake and reward other: f{someone.validator_key}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                someone.payment_key, stake_amount, auto_re_stake, tx_version)

    def stk_stop_auto_staking(self, reward_receiver, validator):
        return self.REQ_HANDLER.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, reward_receiver.payment_key,
                                                          validator.validator_key)

    def stk_stop_auto_stake_me(self):
        INFO('Stop auto stake me')
        return self.stk_stop_auto_staking(self, self)

    def stk_un_stake_tx(self, validator=None):
        if not validator:
            validator = self
        INFO(f'Un-stake transaction for validator: {validator.validator_key}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_un_staking_transaction(self.private_key, validator.payment_key, validator.validator_key)

    def stk_stop_auto_stake_him(self, him):
        INFO(f"Stop auto stake other: {him.validator_key}")
        return self.stk_stop_auto_staking(him, him)

    def stk_wait_till_i_am_committee(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        INFO(f"Wait until {self.validator_key} become a committee, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_shard = beacon_bsd.is_he_a_committee(self)
            if staked_shard is False:
                ChainHelper.wait_till_next_epoch(1, block_of_epoch=5)
            else:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                INFO(f"Already a committee at epoch {e2}, block height {h}")
                return e2
            time_spent = (datetime.datetime.now() - time_start).seconds
        INFO(f"Waited {time_spent}s but still not yet become committee")
        return None

    def stk_wait_till_i_am_in_waiting_next_random(self, check_cycle=ChainConfig.BLOCK_TIME,
                                                  timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        INFO(
            f"Wait until {self.validator_key} exist in waiting next random, check every {check_cycle}s, timeout: {timeout}s")
        while timeout > check_cycle:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_in_waiting_4random = beacon_bsd.is_he_in_waiting_next_random(self)
            if staked_in_waiting_4random is False:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                INFO(f"Already exists in waiting next random at epoch {e2}, block height {h}")
                return e2
        INFO(f"Waited {t}s but still not yet exist in waiting next random")
        return None

    def stk_wait_till_i_am_in_shard_pending(self, timeout=ChainConfig.STK_WAIT_TIME_OUT, sfv3=False):
        INFO(f"Wait until {self.validator_key} exist in shard pending, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        block_per_epoch = ChainConfig.BLOCK_PER_EPOCH
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_shard = beacon_bsd.is_he_in_shard_pending(self)
            e2 = beacon_bsd.get_epoch()
            h = beacon_bsd.get_beacon_height()
            if staked_shard is False:
                if sfv3:
                    WAIT(ChainConfig.BLOCK_TIME)
                else:
                    index_height = h % block_per_epoch
                    if index_height <= ChainConfig.RANDOM_TIME:
                        num_of_block_wait = ChainConfig.RANDOM_TIME - index_height
                        time_to_wait = ChainConfig.get_epoch_n_block_time(0, num_of_block_wait)
                        INFO(f'Current height = {h} @ epoch = {e2}. '
                             f'Wait {time_to_wait}s until epoch {e2} and B height {h + num_of_block_wait}')
                        WAIT(time_to_wait)
                    else:
                        ChainHelper.wait_till_next_epoch(1, block_of_epoch=ChainConfig.RANDOM_TIME + 1)
                time_spent = (datetime.datetime.now() - time_start).seconds
            else:
                INFO(f"Already exists in shard pending at epoch {e2}, block height {h}")
                return staked_shard, e2
        INFO(f"Waited {time_spent}s but still not yet exist in shard pending")
        return

    def stk_wait_till_i_am_in_sync_pool(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        INFO(f"Wait until {self.validator_key} exist in sync pool, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        block_per_epoch = ChainConfig.BLOCK_PER_EPOCH
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_shard = beacon_bsd.is_he_in_sync_pool(self)
            e2 = beacon_bsd.get_epoch()
            h = beacon_bsd.get_beacon_height()
            if staked_shard is False:
                index_height = h % block_per_epoch
                if index_height <= ChainConfig.RANDOM_TIME:
                    num_of_block_wait = ChainConfig.RANDOM_TIME - index_height
                    time_to_wait = ChainConfig.get_epoch_n_block_time(0, num_of_block_wait)
                    INFO(f'Current height = {h} @ epoch = {e2}. '
                         f'Wait {time_to_wait}s until epoch {e2} and B height {h + num_of_block_wait}')
                    WAIT(time_to_wait)
                else:
                    ChainHelper.wait_till_next_epoch(1, block_of_epoch=ChainConfig.RANDOM_TIME + 1)
                time_spent = (datetime.datetime.now() - time_start).seconds
            else:
                INFO(f"Already exists in shard pending at epoch {e2}, block height {h}")
                return staked_shard, e2
        INFO(f"Waited {time_spent}s but still not yet exist in sync pool")
        return

    def stk_wait_till_i_am_out_of_autostaking_list(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        INFO(f"Wait until {self.validator_key} does not exist in the autostaking list, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            if beacon_bsd.get_auto_staking_committees(self) is None:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                INFO(f"Validator is out of autostaking list at epoch {e2}, block height {h}")
                return e2
            ChainHelper.wait_till_next_epoch(1, block_of_epoch=5)
            time_spent = (datetime.datetime.now() - time_start).seconds
        INFO(f"Waited {time_spent}s but still exist in the autostaking list")
        return None

    def stk_wait_till_i_am_swapped_out_of_committee(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        INFO(f"Wait until {self.validator_key} no longer a committee, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            if not (beacon_bsd.is_he_a_committee(self) is False):  # is_he_a_committee returns False or shard number
                # (number which is not False) so must use this comparison to cover the case shard =0
                ChainHelper.wait_till_next_epoch(1, block_of_epoch=5)
            else:
                e2 = beacon_bsd.get_epoch()
                INFO(f"Swapped out of committee at epoch {e2}")
                return e2
            time_spent = (datetime.datetime.now() - time_start).seconds
        INFO(f"Waited {time_spent}s but still a committee")
        return None

    def stk_wait_till_i_have_reward(self, token_id=None, check_cycle=120, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        if token_id is None:
            token_id = 'PRV'
        INFO(f'Wait until {self.validator_key} has reward: {token_id}, check every {check_cycle}s, timeout: {timeout}s')
        while timeout > check_cycle:
            reward = self.stk_get_reward_amount(token_id)
            if reward is None:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.REQ_HANDLER.help_get_current_epoch()
                INFO(f"Rewarded {reward} : {token_id} at epoch {e2}")
                return reward
        INFO(f"Waited {t}s but still has no reward")
        return None

    def get_balance(self, token_id=PRV_ID, **kwargs):
        from_cache = kwargs.get('cache', False)
        if from_cache:
            bal = self.cache[Account._cache_bal].get(token_id, 0)
            INFO(f"Private k = {l6(self.private_key)}, token id = {l6(token_id)}, bal from cache = {coin(bal, False)} ")
            return bal
        result = self.REQ_HANDLER.transaction().get_custom_token_balance(self.private_key, token_id)
        while True:
            try:
                error_msg = result.get_error_trace().get_message()
                if re.search(re.compile(r'{(.*)} not synced'), error_msg):
                    self.submit_key()
                    WARNING(f'{error_msg}. Wait for {ChainConfig.BLOCK_TIME}s and retry')
                    WAIT(ChainConfig.BLOCK_TIME)
                    result = self.REQ_HANDLER.transaction().get_custom_token_balance(self.private_key, token_id)
                else:
                    break
            except:
                break
        balance = result.get_result() if result.get_result() else 0
        self.cache[Account._cache_bal][token_id] = balance
        INFO(f"Private k = {l6(self.private_key)}, token id = {l6(token_id)}, bal = {coin(balance, False)} ")
        return balance

    def send_public_token(self, token_id, amount, receiver, password=None, memo=None):
        """

        @param token_id:
        @param amount:
        @param receiver: Account or remote address
        @param password:
        @param memo:
        @return:
        """
        cli = NeighborChainCli.new(token_id)
        receiver_remote_addr = receiver.get_remote_addr(token_id) if type(receiver) is Account else receiver
        return cli.send_to(self.get_remote_addr(token_id), receiver_remote_addr, amount, password,
                           memo)

    def send_public_token_multi(self, token_id, receiver_amount_dict, password=None, memo=None):
        cli = NeighborChainCli.new(token_id)
        return cli.send_to_multi(self.get_remote_addr(token_id), receiver_amount_dict, password, memo)

    def send_prv_to(self, receiver_account, amount, fee=-1, privacy=1) -> Response:
        """
        send amount_prv of prv to to_account. by default fee=-1 and privacy=1

        @param receiver_account:
        @param amount:
        @param fee: default = auto
        @param privacy: default = privacy on
        @return: Response object
        """
        response = self.REQ_HANDLER.transaction(). \
            send_transaction(self.private_key, {receiver_account.payment_key: amount}, fee, privacy)
        log_msg = f'From: {l6(self.private_key)}. Sent {amount} prv to: {l6(receiver_account.payment_key)}'
        try:
            log_msg += f', tx {response.get_tx_id()}'
        except TypeError:
            log_msg += f', \n    Err: {response.get_error_trace().get_message()}'
        INFO(log_msg)
        return response

    def send_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1, token_id=PRV_ID):
        if token_id == PRV_ID:
            return self.send_prv_to_multi_account(dict_to_account_and_amount, fee, privacy)
        else:
            return self.send_token_multi_output(dict_to_account_and_amount, token_id, prv_fee=fee, prv_privacy=privacy)

    def send_prv_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1):
        """

        @param dict_to_account_and_amount: a dictionary of {receiver Account : amount}
        @param fee:
        @param privacy:
        @return:
        """
        send_param = dict()
        INFO(f"{l6(self.private_key)} sending prv to multiple accounts: --------------------------------------------- ")
        for acc, amount in dict_to_account_and_amount.items():
            INFO(f'{amount} prv to (shard|private_k|payment_k) {acc.shard}|{l6(acc.private_key)}|{l6(acc.payment_key)}')
            send_param[acc.payment_key] = amount
        INFO("---------------------------------------------------------------------------------- ")

        return self.REQ_HANDLER.transaction(). \
            send_transaction(self.private_key, send_param, fee, privacy)

    def send_coin(self, receiver_amount_dict, fee, privacy, token=PRV_ID, **kwargs):
        # todo: merge all send coin/token methods into this if possible
        pass

    def send_all_prv_to(self, to_account, privacy=1):
        """
        send all prv to another account

        @param to_account:
        @param privacy:
        @return:
        """

        INFO(f'Sending everything to {to_account}')
        # defrag account so that the custom fee = fee x 2 as below
        defrag = self.defragment_account()
        if defrag is not None:
            defrag.subscribe_transaction()
        balance = self.get_balance()
        fee, size = self.get_estimate_fee_and_size(to_account, balance - 100, privacy=privacy)
        INFO(f'''EstimateFeeCoinPerKb = {fee}, EstimateTxSizeInKb = {size}''')
        if balance > 0:
            return self.send_prv_to(to_account, balance - 100, int(100 / (size + 1)),
                                    privacy).subscribe_transaction()

    def count_unspent_output_coins(self, token_id='', from_height=0):
        """
        count number of unspent coin

        @return: int
        """
        INFO('Count unspent coin')

        response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key, token_id,
                                                                            from_height).get_result("Outputs")
        return len(response[self.private_key])

    def defragment_account(self, min_bill=1000000000000000):
        """
        check if account need to be defrag by count unspent coin,
            if count > 1 then defrag

        @return: Response object if need to defrag, None if not to
        """
        INFO('Defrag account')

        if self.count_unspent_output_coins() > 1:
            return self.REQ_HANDLER.transaction().de_fragment_prv(self.private_key, min_bill)
        INFO('No need to defrag!')
        return None

    def subscribe_cross_output_coin(self, timeout=120):
        INFO(f'{l6(self.private_key)} Subscribe cross output coin')
        return self.REQ_HANDLER.subscription().subscribe_cross_output_coin_by_private_key(self.private_key, timeout)

    def subscribe_cross_output_token(self, timeout=120):
        INFO(f'{l6(self.private_key)} Subscribe cross output token')
        return self.REQ_HANDLER.subscription().subscribe_cross_custom_token_privacy_by_private_key(
            self.private_key, timeout)

    def init_custom_token(self, amount, token_symbol=None, receiver=None):
        """
        Init custom token to self payment address

        @param receiver:
        @param token_symbol:
        @param amount
        @return:
        """
        receiver = self.payment_key if receiver is None else KeyExtractor.incognito_addr(receiver)
        token_symbol = TestHelper.make_random_word(15, 20) if not token_symbol else token_symbol
        INFO(f'Init custom token to self: {self.payment_key}')

        return self.REQ_HANDLER.transaction().init_custom_token(self.private_key, receiver, token_symbol, amount)

    def init_custom_token_new_flow(self, amount, token_name=None, token_symbol=None):
        """
        init token with new flow
        @param amount:
        @param token_name:
        @param token_symbol:
        @return:
        """
        token_name = f"random_{TestHelper.make_random_word()}" if not token_name else token_name
        token_symbol = f"random_{TestHelper.make_random_word()}" if not token_symbol else token_symbol
        INFO(f'Init new token with name {token_name}')
        return self.REQ_HANDLER.transaction().new_init_p_token(self.private_key, amount, token_name, token_symbol)

    def pde_contribute_pair(self, pair_dict):
        """
        @param pair_dict: a dictionary of {token_id: amount}
        @return: the 2 contribute txs
        """
        token1, token2 = list(pair_dict.keys())
        amount1, amount2 = list(pair_dict.values())
        pair_id = f'pde_{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
        tx1 = self.pde_contribute(token1, amount1, pair_id).expect_no_error().subscribe_transaction()
        tx2 = self.pde_contribute(token2, amount2, pair_id).expect_no_error().subscribe_transaction()
        return tx1, tx2

    def pde_contribute(self, token_id, amount, pair_id):
        if token_id == PRV_ID:
            INFO(f'{l6(self.private_key)} Contribute PRV, amount: {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_prv(self.private_key, self.payment_key, amount,
                                                         pair_id, TestConfig.TX_VER)
        else:
            INFO(f'{l6(self.private_key)} Contribute token: {l6(token_id)}, amount = {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_token(self.private_key, self.payment_key, token_id,
                                                           amount, pair_id, TestConfig.TX_VER)

    def pde_contribute_v2(self, token_id, amount, pair_id):
        if token_id == PRV_ID:
            INFO(f'{l6(self.private_key)} Contribute PRV V2, amount: {amount}, pair id = {pair_id}')

            return self.REQ_HANDLER.dex().contribute_prv_v2(self.private_key, self.payment_key, amount,
                                                            pair_id, TestConfig.TX_VER)
        else:
            INFO(f'{l6(self.private_key)} Contribute token V2: {l6(token_id)}, amount = {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_token_v2(self.private_key, self.payment_key, token_id,
                                                              amount, pair_id, TestConfig.TX_VER)

    def pde_withdraw_contribution(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE contribution {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution(self.private_key, self.payment_key,
                                                              token_id_1, token_id_2, amount, TestConfig.TX_VER)

    def pde_withdraw_contribution_v2(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE contribution v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution_v2(self.private_key, self.payment_key, token_id_1,
                                                                 token_id_2, amount)

    def pde_withdraw_reward_v2(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE reward v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdraw_reward_v2(self.private_key, self.payment_key, token_id_1,
                                                         token_id_2, amount, TestConfig.TX_VER)

    def pde_contribute_pair_v2(self, pair_dict: dict):
        """
        @param pair_dict: a dictionary of {token_id: amount}
        @return: the two contribute tx
        """
        token1, token2 = list(pair_dict.keys())
        amount1, amount2 = list(pair_dict.values())
        pair_id = f'pde_{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
        tx1 = self.pde_contribute_v2(token1, amount1, pair_id).expect_no_error().subscribe_transaction()
        tx2 = self.pde_contribute_v2(token2, amount2, pair_id).expect_no_error().subscribe_transaction()
        return tx1, tx2

    def send_token_to(self, receiver, token_id, amount_custom_token,
                      prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0):
        """
        Send token to receiver (custom token only, not prv)

        @param prv_privacy:
        @param prv_amount:
        @param receiver: Account
        @param token_id:
        @param amount_custom_token:
        @param prv_fee:
        @param token_fee:
        @param token_privacy:
        @return: Response object
        """
        INFO(f'Sending {amount_custom_token} token {l6(token_id)} to {l6(receiver.payment_key)}')

        return self.REQ_HANDLER.transaction(). \
            send_custom_token_transaction(self.private_key, receiver.payment_key, token_id, amount_custom_token,
                                          prv_fee, token_fee, prv_amount, prv_privacy, token_privacy)

    def send_token_multi_output(self, receiver_token_amount_dict, token_id, prv_fee=0, token_fee=0, prv_privacy=0,
                                token_privacy=0):
        """
        sending token multi output, default fee is PRV-auto (-1) and default privacy is PRV-true (1)
        @param receiver_token_amount_dict:
        @param token_id:
        @param prv_fee:
        @param token_fee:
        @param prv_privacy:
        @param token_privacy:
        @return:
        """
        INFO(f'Sending token {l6(token_id)} multi output')
        prv_fee = -1 if prv_fee == 0 and token_fee == 0 else prv_fee
        prv_privacy = 1 if prv_privacy == 0 and token_privacy == 0 else prv_privacy
        payment_key_amount_dict = {}
        for acc in receiver_token_amount_dict.keys():
            payment_key_amount_dict[acc.payment_key] = receiver_token_amount_dict[acc]
        return self.REQ_HANDLER.transaction(). \
            send_custom_token_multi_output(self.private_key, payment_key_amount_dict, token_id, prv_fee, token_fee,
                                           prv_privacy, token_privacy)

    def burn_token(self, token_id, amount_custom_token):
        """
        Burning token (this mean send token to burning address)
        @param token_id: Token ID
        @param amount_custom_token: amount to burn
        @return: Response object
        """
        INFO(f'Send custom token transaction to burning address')
        return self.REQ_HANDLER.transaction(). \
            send_custom_token_transaction(self.private_key, Constants.BURNING_ADDR, token_id, amount_custom_token,
                                          prv_fee=-1, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0)

    ########
    # BRIDGE
    ########
    def issue_centralize_token(self, token_id, token_name, amount):
        """
            initialize a new centralize token
            @return: Response Object
        """
        return self.REQ_HANDLER.bridge().issue_centralized_bridge_token(DAO_PRIVATE_K, self.payment_key, token_id,
                                                                        token_name, amount)

    def withdraw_centralize_token(self, token_id, amount_custom_token):
        """
        Withdraw token (this mean send token to burning address, but receive your token on ETH network)
        INFO(f'Send custom token transaction')
        return Account.SYSTEM.transaction().\
            send_custom_token_transaction(self.private_key, Constants.burning_address, token_id, amount_custom_token,
                                          prv_fee=-1, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0)

        @param token_id: Token ID
        @param amount_custom_token: amount to withdraw
        @return: Response object
        """
        INFO(f'Withdraw centralize token')
        return self.REQ_HANDLER.transaction().withdraw_centralize_token(self.private_key, token_id,
                                                                        amount_custom_token, TestConfig.TX_VER)

    ########
    # Stake
    ########

    def stk_get_reward_amount(self, token_id=PRV_ID):
        """
        @param token_id: token id to get reward, set as '*' to get all token reward in a dictionary
        @return: reward amount of token
        """
        result = self.REQ_HANDLER.transaction().get_reward_amount(self.payment_key).get_result()
        result[PRV_ID] = result.pop('PRV')
        if token_id == '*':
            return result
        else:
            reward = result.get(token_id, 0)
        INFO(f"Payment key = {l6(self.payment_key)}, {token_id[-6:]} reward = {coin(reward, False)}")
        return reward

    def stk_withdraw_reward_to(self, reward_receiver, token_id=PRV_ID, tx_fee=0, tx_version=TestConfig.TX_VER,
                               privacy=0):
        INFO(f"Withdraw token reward {token_id} to {l6(reward_receiver.payment_key)}")
        if ChainConfig.PRIVACY_VERSION == 1:
            return self.REQ_HANDLER.transaction(). \
                withdraw_reward(self.private_key, reward_receiver.payment_key, token_id, tx_fee, tx_version, privacy)
        if ChainConfig.PRIVACY_VERSION == 2:
            return self.REQ_HANDLER.transaction(). \
                withdraw_reward_privacy_v2(self.private_key, reward_receiver.payment_key, token_id, -1, tx_version,
                                           privacy)
        raise RuntimeError('Can not detect privacy version to use the correct withdraw rpc')

    def stk_withdraw_reward_to_me(self, token_id=PRV_ID, tx_fee=0, tx_version=TestConfig.TX_VER, privacy=0):
        return self.stk_withdraw_reward_to(self, token_id, tx_fee, tx_version, privacy)

    #######
    # DEX
    #######
    def pde_clean_all_waiting_contribution(self, pde_state=None):
        pde_state = self.REQ_HANDLER.get_latest_pde_state_info() if pde_state is None else pde_state
        waiting_contributions = pde_state.get_waiting_contributions()
        for contribution in waiting_contributions:
            if contribution.get_contributor_address() == self.payment_key and contribution.get_token_id() != PRV_ID:
                INFO(f"{contribution} belong to current user and waiting for PRV, so cannot use PRV to clean up")
            else:
                self.pde_contribute(PRV_ID, 100,
                                    contribution.get_pair_id()).subscribe_transaction()

    def pde_wait_till_my_token_in_waiting_for_contribution(self, pair_id, token_id, timeout=100):
        INFO(f"Wait until token {l6(token_id)} is in waiting for contribution")
        my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
            find_waiting_contribution_of_user(self, pair_id, token_id)
        while timeout >= 0:
            if my_waiting:  # not empty
                INFO(f'Token {l6(token_id)} is found in contribution waiting list')
                return True
            timeout -= 10
            WAIT(10)
            my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
                find_waiting_contribution_of_user(self, pair_id, token_id)
        INFO(f'Token {l6(token_id)} is NOT found in contribution waiting list')
        return False

    def pde_wait_till_my_token_out_waiting_for_contribution(self, pair_id, token_id, timeout=100):
        INFO(f"Wait until token {l6(token_id)} is OUT of waiting for contribution")
        my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
            find_waiting_contribution_of_user(self, pair_id, token_id)
        while timeout >= 0:
            if not my_waiting:
                INFO(f'Token {l6(token_id)} is NOT found in contribution waiting list')
                return True
            timeout -= 10
            WAIT(10)
            my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
                find_waiting_contribution_of_user(self, pair_id, token_id)
        INFO(f'Token {l6(token_id)} is found in contribution waiting list')
        return False

    def pde_trade_token(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {sell_amount} of token {token_id_to_sell[-6:]} for {token_id_to_buy[-6:]} '
             f'trading fee={trading_fee}')
        return self.REQ_HANDLER.dex().trade_token(self.private_key, self.payment_key, token_id_to_sell,
                                                  sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee,
                                                  tx_ver=TestConfig.TX_VER)

    def pde_trade_prv(self, amount_to_sell, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} of PRV for {token_id_to_buy[-6:]}')
        return self.REQ_HANDLER.dex().trade_prv(self.private_key, self.payment_key, amount_to_sell,
                                                token_id_to_buy, min_amount_to_buy, trading_fee, TestConfig.TX_VER)

    def pde_trade(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        if token_id_to_sell == PRV_ID:
            return self.pde_trade_prv(sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)
        else:
            return self.pde_trade_token(token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)

    def pde_trade_prv_v2(self, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} PRV for {l6(token_to_buy)} trading fee={trading_fee}, '
             f'min acceptable={min_amount_to_buy}')
        return self.REQ_HANDLER.dex().trade_prv_v2(self.private_key, self.payment_key, amount_to_sell,
                                                   token_to_buy, trading_fee, min_amount_to_buy,
                                                   tx_ver=TestConfig.TX_VER)

    def pde_trade_token_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} of token {token_to_sell[-6:]} for {token_to_buy[-6:]} trading fee={trading_fee} '
             f'min acceptable={min_amount_to_buy}')
        return self.REQ_HANDLER.dex().trade_token_v2(self.private_key, self.payment_key, token_to_sell,
                                                     amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy,
                                                     tx_ver=TestConfig.TX_VER)

    def pde_trade_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        if token_to_sell == PRV_ID:
            return self.pde_trade_prv_v2(amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)
        else:
            return self.pde_trade_token_v2(token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)

    def pde3_add_order(self, nft_id, token_sell, pool_id, sell_amount, min_acceptable,
                       tx_fee=-1, tx_privacy=1):
        INFO(f"Adding order to order book\n"
             f"In pool {pool_id}\n"
             f"Selling {sell_amount} of {token_sell}\n"
             f"Min acceptable: {min_acceptable}")
        return self.REQ_HANDLER.dex_v3().add_order(self.private_key, nft_id, token_sell, pool_id, str(sell_amount),
                                                   str(min_acceptable), tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_order(self, token_id, amount, nft_id, pair_id, order_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3().withdraw_order(self.private_key, token_id, amount, nft_id, pair_id,
                                                        order_id, tx_fee, tx_privacy)

    def pde3_trade(self, token_sell, token_buy, sell_amount, min_acceptable, trade_path, trading_fee=100,
                   use_prv_fee=True, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3().trade(self.private_key, token_sell, token_buy, sell_amount, min_acceptable,
                                               trade_path, trading_fee, use_prv_fee, tx_fee, tx_privacy)

    def pde3_withdraw_lp_fee(self, receiver, token_amount, token_id, pool_pair_id, nft_id,
                             token_tx_type=1, token_fee=0, token_name="", token_symbol=0,
                             burning_tx=None, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_lp_fee(self.private_key, receiver.payment_key, token_amount, token_id, pool_pair_id, nft_id,
                             token_tx_type, token_fee, token_name, token_symbol, burning_tx, tx_fee, tx_privacy)

    def pde3_stake(self, stake_amount, staking_pool_id, nft_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .stake(self.private_key, staking_pool_id, stake_amount, nft_id, tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_unstake(self, unstake_amount, staking_pool_id, nft_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .unstake(self.private_key, staking_pool_id, nft_id, unstake_amount, tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_staking_reward_to(self, receiver, staking_pool_id, nft_id, token_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_staking_reward(self.private_key, receiver.payment_key, staking_pool_id, nft_id, token_id,
                                     tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_staking_reward_to_me(self, staking_pool_id, nft_id, token_id, tx_fee=-1, tx_privacy=1):
        return self.pde3_withdraw_staking_reward_to(self, staking_pool_id, nft_id, token_id, tx_fee=-1, tx_privacy=1)

    def pde3_add_liquidity(self, token_id, amount, amplifier, contribute_id, nft_id=None, pool_pair_id="", tx_fee=-1,
                           tx_privacy=1):
        nft_id = nft_id if nft_id else self.nft_ids[0]
        INFO(f"Contributing {amount} of {token_id}\n\t"
             f"NFT: {nft_id} | Amp: {amplifier}")
        return self.REQ_HANDLER.dex_v3() \
            .add_liquidity(self.private_key, token_id, str(amount), str(amplifier), pool_pair_id, contribute_id, nft_id,
                           tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_liquidity(self, share_amount, pool_pair_id, nft_id=None, tx_fee=-1, tx_privacy=1):
        nft_id = nft_id if nft_id else self.nft_ids[0]
        INFO(f"PDE3 Withdraw liquidity, private k: {self.private_key[-6:]}, NFTID {nft_id}\n\t"
             f"pair: {pool_pair_id}")
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_liquidity(self.private_key, pool_pair_id, nft_id, share_amount, tx_fee=tx_fee,
                                tx_privacy=tx_privacy)

    def pde3_mint_nft(self, amount=coin(1), token_id=PRV_ID, tx_fee=-1, tx_privacy=1, force=False):
        if not force:
            if self.nft_ids:
                INFO(f"{self.private_key[-6:]} Already have NFT ID(s), "
                     f"return the first one now and will not mint more: \n {self.nft_ids}")
                return self.nft_ids[0]
        response = self.REQ_HANDLER.dex_v3() \
            .mint_nft(self.private_key, amount, token_id, tx_fee=tx_fee, tx_privacy=tx_privacy)
        tx_detail = response.get_transaction_by_hash()
        wasted_time = 0
        while True:
            WAIT(ChainConfig.BLOCK_TIME)
            wasted_time += ChainConfig.BLOCK_TIME
            mint_status = self.REQ_HANDLER.dex_v3().get_mint_nft_status(response.get_tx_id())
            nft_id = mint_status.get_nft_id()
            if nft_id:
                INFO(f"{self.private_key[-6:]} New DEX NFT ID: {nft_id}")
                return nft_id
            if wasted_time > ChainConfig.BLOCK_TIME * 5:
                break
        if not nft_id:
            INFO(f'Waited {wasted_time}s, but cant get new nft id after tx was confirmed')
            return None

    def pde3_get_my_nft_ids(self, pde_state=None):
        all_my_custom_token = self.list_owned_custom_token()
        pde_state = self.REQ_HANDLER.get_pde3_state() if not pde_state else pde_state
        for token in all_my_custom_token.__iter__():
            if pde_state.get_nft_id(token.get_token_id()):
                self.save_nft_id(token.get_token_id())
        INFO(f"Get {self.private_key[-6:]} NFT id from pde state.\n   found: {self.nft_ids}")
        return self.nft_ids

    def wait_for_balance_change(self, token_id=PRV_ID, from_balance=None, least_change_amount=1, check_interval=10,
                                timeout=100):
        """
        @param token_id:
        @param from_balance:
        @param least_change_amount: change at least this amount of token
        @param check_interval:
        @param timeout:
        @return: new balance
        """
        if from_balance is None:
            from_balance = self.get_balance(token_id)
            WAIT(check_interval)
            timeout -= check_interval
        INFO(f'Wait for token {l6(token_id)} of {l6(self.private_key)} '
             f'balance to change at least: {least_change_amount}. From {from_balance}')
        bal_new = None
        while timeout >= 0:
            bal_new = self.get_balance(token_id)
            change_amount = bal_new - from_balance
            if least_change_amount is None:  # just change, does not mater + or -
                if bal_new != from_balance:
                    INFO(f'Balance token {l6(token_id)} of {l6(self.private_key)} changes: {change_amount}')
                    return bal_new
            elif least_change_amount >= 0:  # case balance increase
                if bal_new >= from_balance + least_change_amount:
                    INFO(f'Balance token {l6(token_id)} of {l6(self.private_key)} changes: {change_amount}')
                    return bal_new
            else:  # case balance decrease
                if bal_new <= from_balance + least_change_amount:
                    INFO(f'Balance token {l6(token_id)} of {l6(self.private_key)} changes: {change_amount}')
                    return bal_new
            WAIT(check_interval)
            timeout -= check_interval
        INFO(f'Balance token {l6(token_id)} of {l6(self.private_key)} not change a bit')
        return bal_new

    #######
    # Portal
    #######
    def portal_create_exchange_rate(self, rate_dict: dict):
        INFO()
        INFO(f'Portal | User {l6(self.payment_key)} | create rate')
        for key, value in rate_dict.items():  # convert dict value to string
            rate_dict[key] = str(value)
        return self.REQ_HANDLER.portal(). \
            create_n_send_portal_exchange_rates(self.private_key, self.payment_key, rate_dict)

    def portal_create_porting_request(self, token_id, amount, porting_fee=None, register_id=None):
        INFO()
        INFO(f'Portal | User {l6(self.payment_key)} | create porting req | amount {coin(amount, False)}')
        if porting_fee is None:
            beacon_height = self.REQ_HANDLER.help_get_beacon_height()
            porting_fee = self.REQ_HANDLER.portal().get_porting_req_fees(
                token_id, amount, beacon_height).get_result(token_id)
            porting_fee = 1 if porting_fee == 0 else porting_fee
        if register_id is None:
            now = get_current_date_time("%d%m%y_%H%M%S")
            register_id = f"{l6(token_id)}_{now}"

        return self.REQ_HANDLER.portal(). \
            create_n_send_reg_porting_public_tokens(
            self.private_key, self.payment_key, token_id, amount, burn_fee=porting_fee, port_fee=porting_fee,
            register_id=register_id)

    def portal_add_collateral(self, collateral, ptoken, remote_addr=None):
        INFO()
        INFO(f'Portal | Custodian {l6(self.payment_key)} | '
             f'Add collateral to become custodian: {coin(collateral, False)}')
        remote_addr = self.get_remote_addr(ptoken) if remote_addr is None else remote_addr
        return self.REQ_HANDLER.portal().create_n_send_tx_with_custodian_deposit(
            self.private_key, self.payment_key, collateral, {ptoken: remote_addr})

    def portal_make_me_custodian(self, collateral, ptoken, remote_addr=None):
        """
        just an alias of add_collateral
        """
        remote_addr = self.get_remote_addr(ptoken) if remote_addr is None else remote_addr
        return self.portal_add_collateral(collateral, ptoken, remote_addr)

    def portal_let_me_take_care_this_redeem(self, redeem_id, do_assert=True):
        INFO(f"{l6(self.payment_key)} will take this redeem: {redeem_id}")
        req_tx = self.REQ_HANDLER.portal().create_n_send_tx_with_req_matching_redeem(self.private_key,
                                                                                     self.payment_key,
                                                                                     redeem_id)
        req_tx.subscribe_transaction()
        info = RedeemReqInfo()
        info.get_req_matching_redeem_status(req_tx.get_tx_id())

        if do_assert:
            assert info.get_status() == Status.Portal.CustodianReqMatchingStatus.ACCEPT, \
                f'Req matching status is {info.get_status()}'
        return req_tx

    def portal_req_redeem_my_token(self, token_id, redeem_amount, redeem_fee=None, privacy=True):
        INFO()
        redeem_id = f"{l6(token_id)}_{get_current_date_time()}"
        INFO(f'Portal | User (payment k) {l6(self.payment_key)} | req redeem token |'
             f' ID: {redeem_id} | Amount: {redeem_amount} | token: {l6(token_id)}')

        beacon_height = self.REQ_HANDLER.help_get_beacon_height()

        if redeem_fee is None:
            redeem_fee = self.REQ_HANDLER.portal().get_porting_req_fees(token_id, redeem_amount,
                                                                        beacon_height).get_result(
                token_id)
        return self.REQ_HANDLER.portal(). \
            create_n_send_tx_with_redeem_req(self.private_key, self.payment_key, self.get_remote_addr(token_id),
                                             token_id, redeem_amount, redeem_fee, redeem_id, privacy)

    def portal_withdraw_my_collateral(self, amount):
        INFO(f'Portal | Custodian {l6(self.payment_key)} | Withdraw collateral: {amount}')
        return self.REQ_HANDLER.portal().create_n_send_custodian_withdraw_req(self.private_key,
                                                                              self.payment_key,
                                                                              amount)

    def portal_withdraw_my_all_free_collateral(self, psi=None):
        """

        @param psi: PortalStateInfo
        @return: Response if current total collateral > 0, None if = 0
        """
        if psi is None:
            psi = self.REQ_HANDLER.get_latest_portal_state_info()
        INFO(f"Withdraw all collateral of {l6(self.payment_key)}")
        my_custodian_info = psi.get_custodian_info_in_pool(self)
        if my_custodian_info is None:
            INFO("I'm not even a custodian")
            return None
        my_free_collateral = my_custodian_info.get_free_collateral()
        if my_free_collateral == 0:
            INFO('Current free collateral is 0, nothing to withdraw')
            return None
        return self.portal_withdraw_my_collateral(my_free_collateral)

    def portal_req_ported_ptoken(self, porting_id, token_id, amount, proof):
        """

        @param porting_id:
        @param token_id:
        @param amount:
        @param proof:
        @return:
        """
        INFO()
        INFO(f'Portal | User {l6(self.payment_key)} | req for ported token')
        return self.REQ_HANDLER.portal().create_n_send_tx_with_req_ptoken(self.private_key,
                                                                          self.payment_key,
                                                                          porting_id, token_id, amount,
                                                                          proof)

    def portal_get_my_custodian_info(self, psi: PortalStateInfo = None, **kwargs):
        """

        @param psi: PortalStateInfo
        @return CustodianInfo or None:
        """
        cache = kwargs.get("cache", False)
        if psi is None:
            if cache:
                return self.cache[Account._cache_custodian_inf]
            psi = self.REQ_HANDLER.get_latest_portal_state_info()
        return psi.get_custodian_info_in_pool(self)

    def portal_wait_my_lock_collateral_to_change(self, token_id, from_amount=None, check_rate=30, timeout=180):
        INFO(f'Wait for my lock collateral change, {l6(self.payment_key)}, token {l6(token_id)}')
        my_custodian_stat = self.portal_get_my_custodian_info()
        if my_custodian_stat is None:
            INFO("You're not even a custodian")
            return None
        if from_amount is None:
            collateral_before = self.portal_get_my_custodian_info().get_locked_collateral(token_id)
        else:
            collateral_before = from_amount
        current_collateral = collateral_before
        time = 0
        while current_collateral == collateral_before:
            if time >= timeout:
                INFO(f'Lock collateral does not change in the last {time}s')
                return 0
            WAIT(check_rate)
            time += check_rate
            current_collateral = self.portal_get_my_custodian_info().get_locked_collateral(token_id)

        delta = current_collateral - collateral_before
        INFO(f'Lock collateral has change {delta}')
        return delta

    def portal_sum_my_waiting_porting_req_locked_collateral(self, token_id, portal_state_info=None):
        if portal_state_info is None:
            portal_state_info = self.REQ_HANDLER.get_latest_portal_state_info()

        sum_amount = portal_state_info.sum_collateral_porting_waiting(token_id, self)
        INFO(f'{l6(self.payment_key)} sum all waiting porting req collateral of token {l6(token_id)}: {sum_amount}')
        return sum_amount

    def portal_sum_my_matched_redeem_req_holding_token(self, token_id, portal_state_info=None):
        if portal_state_info is None:
            portal_state_info = self.REQ_HANDLER.get_latest_portal_state_info()

        sum_amount = portal_state_info.sum_holding_token_matched_redeem_req(token_id, self)
        INFO(f'{l6(self.payment_key)} sum all waiting redeem holding token of {l6(token_id)}: {sum_amount}')
        return sum_amount

    def portal_req_unlock_collateral(self, token_id, amount_redeem, redeem_id, proof):
        INFO(f'{l6(self.payment_key)} request unlock collateral: {l6(token_id)} {amount_redeem} {redeem_id}')
        return self.REQ_HANDLER.portal(). \
            create_n_send_tx_with_req_unlock_collateral(self.private_key, self.payment_key, token_id, amount_redeem,
                                                        redeem_id, proof)

    def portal_withdraw_reward(self, token_id=PRV_ID):
        return self.REQ_HANDLER.portal(). \
            create_n_send_tx_with_req_withdraw_reward_portal(self.private_key, self.payment_key, token_id)

    def portal_get_prv_from_liquidation_pool(self, token_id, token_amount):
        return self.REQ_HANDLER.portal().create_n_send_redeem_liquidation_exchange_rates(
            self.private_key, self.payment_key, token_amount, token_id)

    def portal_get_my_reward(self, token=None):
        result = self.REQ_HANDLER.portal().get_portal_reward(self.incognito_addr)
        if token is None:
            rewards = result.get_result()
            rewards = {} if rewards is None else rewards
            return rewards
        try:
            reward = result.get_result(token)
            reward = 0 if reward is None else reward
            return reward
        except KeyError:
            return 0

    def convert_payment_k_to_v1(self, key=None):
        key = key if key else self.payment_key
        return self.REQ_HANDLER.util_rpc().convert_payment_k_to_v1(key).get_result()

    def convert_token_to_v2(self, token_id=PRV_ID, fee=-1):
        if token_id == PRV_ID:
            convert_tx = self.REQ_HANDLER.transaction().create_convert_coin_ver1_to_ver2_transaction(self.private_key)
        else:
            convert_tx = self.REQ_HANDLER.transaction().create_convert_coin_ver1_to_ver2_tx_token(self.private_key,
                                                                                                  token_id, fee)
        return convert_tx

    def top_up_if_lower_than(self, account, lower, upper, token_id=PRV_ID, retry_interval=30, max_wait=180):
        """
        todo: under construction
        @param max_wait:
        @param retry_interval:
        @param account: Account or list of Account or AccountGroup
        @param upper: desired balance of receivers
        @param lower: top up if lower than this
        @param token_id: default: PRV
        @param retry_interval: amount of time to wait (in each tx)
                to retry in case out put coin is being used in another transaction
        @param max_wait: max time to wait (in each tx) if retry keep failing
        @return:
        """
        if isinstance(account, Account):
            account = AccountGroup(account)
        elif isinstance(account, list):
            account = AccountGroup(*account)
        lower = int(lower)
        upper = int(upper)
        receiver = {}
        bal_receiver_b4_dict = account.get_balance(token_id)

        for acc, balance in bal_receiver_b4_dict.items():
            if balance <= lower:
                top_up_amount = upper - balance
                if top_up_amount > 0:
                    receiver[acc] = top_up_amount
        if len(receiver) == 0:
            return None

        INFO_HEADLINE(f"TOP UP OTHERS'({len(receiver)} acc) TO {upper} (token {(l6(token_id))})")

        # there's a max number of output in "createandsendtransaction" rpc, so must split into small batch of output
        each, length, start = 20, len(receiver), 0
        mid = each
        keys = list(receiver.keys())
        wasted_time = 0
        while start < length:
            sub_keys = keys[start:mid]
            INFO(f'Batch: {start}->{len(sub_keys)}')
            sub_receivers = {k: receiver[k] for k in sub_keys}
            send_tx = self.send_to_multi_account(sub_receivers, token_id=token_id)
            if send_tx.get_error_msg():
                # ideally should only retry if coin being used in another tx, but for now, just retry if there's any err
                INFO(f'{send_tx.get_error_trace().get_message()}. Wait then retry')
                WAIT(retry_interval)
                wasted_time += retry_interval
                if wasted_time >= max_wait:
                    raise TimeoutError(f"Waited {wasted_time}s but cannot create send tx, "
                                       f"output coins appear to being used use in another tx")

            else:
                # tx should be succeed
                send_tx.expect_no_error().subscribe_transaction()
                start = mid
                mid += each
                wasted_time = 0

        # thread_pool = []
        for acc, amount in receiver.items():
            acc.wait_for_balance_change(token_id, from_balance=bal_receiver_b4_dict[acc])

    def submit_key(self, key_type='private'):
        """
        @param key_type: private or ota
        @return:
        """
        key_type = key_type.lower()
        if key_type == 'private':
            key = self.private_key
        elif key_type == 'ota':
            key = self.ota_k
        else:
            key = None
        INFO(f'Submit {key_type} key for indexing coin {l6(key)}')
        submit_response = self.REQ_HANDLER.transaction().submit_key(key)
        try:
            error = submit_response.get_error_trace().get_message()
        except AttributeError:
            error = None
        ERROR(error) if error else INFO(submit_response.get_result())
        return self

    def submit_key_authorize(self, from_height=0, re_index=False, access_token=ChainConfig.ACCESS_TOKEN):
        return self.REQ_HANDLER.transaction().submit_key_authorized(self.ota_k, access_token, from_height, re_index)


class AccountGroup:
    def __init__(self, *accounts):
        for acc in accounts:
            if type(acc) is not Account:
                raise TypeError(f"List member must be an Account object, got {type(acc)} instead ")
        self.account_list: List[Account] = list(accounts)

    def __len__(self):
        return len(self.account_list)

    def __iter__(self):
        self.__current_index = 0
        return iter(self.account_list)

    def __next__(self):
        if self.__current_index >= len(self.account_list):
            raise StopIteration
        else:
            self.__current_index += 1
            return self[self.__current_index]

    def __getitem__(self, item):
        return self.account_list[item]

    def __deepcopy__(self, memo=None):
        copy_acc_group = AccountGroup()
        copy_acc_group.account_list = copy.deepcopy(self.account_list, memo)
        return copy_acc_group

    def clone(self):
        return self.__deepcopy__()

    def convert_payment_address_to_version(self, version=2):
        for acc in self:
            acc.convert_payment_address_to_version(version)
        return self

    def remove(self, obj):
        self.account_list.remove(obj)

    def append(self, acc_obj):
        self.account_list.append(acc_obj)

    def get_accounts_in_shard(self, shard_number: int):
        """
        iterate through accounts in account_list, check if they're in the same shard_number

        @param shard_number: shard id to check
        @return: list of Account which is in the same shard_number
        """
        INFO(f'Find all accounts in shard {shard_number}')
        accounts_in_shard: List[Account] = []
        for account in self.account_list:
            if account.shard % ChainConfig.ACTIVE_SHARD == shard_number % ChainConfig.ACTIVE_SHARD:
                accounts_in_shard.append(account)

        return AccountGroup(*accounts_in_shard)

    def find_account_by_key(self, key):
        """
        @param key: any kind of key (private, payment, public, committee ...)
        @return: Account object or None if not found
        """
        for acc in self.account_list:
            if acc.is_this_my_key(key):
                return acc

    def __add__(self, other):
        if type(other) is AccountGroup:  # add 2 AccountGroup
            return AccountGroup(*(self.account_list + other.account_list))
        elif type(other) is list:  # add AccountGroup with list of accounts
            return AccountGroup(*(self.account_list + other))
        elif type(other) is Account:
            self.account_list.append(other)
            return AccountGroup(*self.account_list)
        raise TypeError(f'Not support adding type {type(other)} with {__class__} ')

    def change_req_handler(self, HANDLER):
        for acc in self:
            acc.req_to(HANDLER)

    def find_the_richest(self, token_id=PRV_ID):
        all_bal = self.get_balance(token_id)
        return max(self, key=lambda acc: all_bal[acc])

    def get_balance(self, token_id=PRV_ID):
        """
        @param token_id:
        @return: dict of {Account: balance(int)}
        """
        balance_result = {}
        with ThreadPoolExecutor() as executor:
            for acc in self.account_list:
                thread = executor.submit(acc.get_balance, token_id)
                balance_result[acc] = thread
        for acc, thread in balance_result.items():
            balance_result[acc] = thread.result()
        return balance_result

    def submit_key(self, key_type='private'):
        for acc in self.account_list:
            with ThreadPoolExecutor() as tpe:
                tpe.submit(acc.submit_key, key_type)
        return self

    def convert_token_to_v2(self, token=PRV_ID, fee=-1):
        for acc in self.account_list:
            with ThreadPoolExecutor() as tpe:
                tpe.submit(acc.convert_token_to_v2, token, fee)

    def get_random_account(self):
        return self.account_list[random.randrange(len(self.account_list))]

    def pde3_mint_nft(self):
        with ThreadPoolExecutor() as e:
            for acc in self:
                e.submit(acc.pde3_mint_nft)
        return self

    def pde3_get_nft_ids(self):
        with ThreadPoolExecutor() as e:
            pde_state = self[0].REQ_HANDLER.get_pde3_state()
            for acc in self:
                e.submit(acc.pde3_get_my_nft_ids, pde_state)
        return self


def get_accounts_in_shard(shard_number: int, account_list=None):
    """ @deprecated
    iterate through accounts in account_list, check if they're in the same shard_number

    @param shard_number: shard id to check
    @param account_list: account list to check, by default it's TestData
    @return: list of Account which is in the same shard_number
    """
    if account_list is None:
        from Objects.IncognitoTestCase import ACCOUNTS
        account_list = ACCOUNTS
    if type(account_list) is AccountGroup:
        return account_list.get_accounts_in_shard(shard_number)
    else:
        return AccountGroup(*account_list).get_accounts_in_shard(shard_number)


PORTAL_FEEDER = Account(ChainConfig.Portal.FEEDER_PRIVATE_K, handler="nomad")
COIN_MASTER = Account(DAO_PRIVATE_K, handler="nomad")
