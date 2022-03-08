import copy
import datetime
import json
import random
import re
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Union

from Configs import Constants
from Configs.Configs import ChainConfig, TestConfig
from Configs.Constants import PRV_ID, coin, PBNB_ID, PBTC_ID, Status, DAO_PRIVATE_K, BURNING_ADDR
from Drivers.IncCliWrapper import IncCliWrapper
from Drivers.NeighborChainCli import NeighborChainCli
from Drivers.Response import Response
from Helpers import TestHelper
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6, KeyExtractor
from Helpers.Time import WAIT, get_current_date_time
from Objects.CoinObject import CustomTokenBalanceResponse, TXOResponse
from Objects.PdexV3Objects import PdeV3State
from Objects.PortalObjects import RedeemReqInfo, PortalStateInfo

logger = config_logger(__name__)


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
        for key_type, value in self.key_info.items():
            if key_to_check in str(value):
                return key_type
        return False

    def __init__(self, private_key=None, payment_k=None, handler=None, **kwargs):
        """
        @param private_key: private key of this account,
         other keys will be generated automatically if payment_k is not specified
        @param payment_k: payment key of this account, if specified along with private key, other keys will not
         get generated and will be set to None
        @param handler: Node object, specify which chain this account belong to by specifying one node of the chain here
        (usually full node)
        @param kwargs:
        """
        self.key_info = {"PrivateKey": private_key,
                         "PublicKey": "",
                         "PaymentAddressV1": "",
                         "PaymentAddress": payment_k,
                         "ReadOnlyKey": "",
                         "OTAPrivateKey": "",
                         "MiningKey": "",
                         "MiningPublicKey": "",
                         "ValidatorPublicKey": "",
                         "ShardID": kwargs.get('shard')}
        self.remote_addr = {}
        self.cache = {Account._cache_bal: {},
                      Account._cache_nft_id: []}
        self.REQ_HANDLER = handler

        if private_key and not payment_k:  # generate all key from private key if there's privatekey but not paymentkey
            self.key_info = IncCliWrapper().key_info(self.private_key)

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

    @property
    def private_key(self):
        return self.key_info['PrivateKey']

    @property
    def payment_key_v1(self):
        return self.key_info['PaymentAddressV1']

    @property
    def payment_key(self):
        return self.key_info['PaymentAddress']

    @property
    def incognito_addr(self):  # just an alias for payment key
        return self.payment_key

    @property
    def validator_key(self):
        return self.key_info['MiningKey']

    @property
    def public_key(self):
        return self.key_info['PublicKey']

    @property
    def read_only_key(self):
        return self.key_info['ReadOnlyKey']

    @property
    def validator_public_key(self):
        return self.key_info['ValidatorPublicKey']

    @property
    def ota_k(self):
        return self.key_info['OTAPrivateKey']

    @property
    def committee_public_k(self):
        return self.key_info['MiningPublicKey']

    @property
    def shard(self):
        return self.key_info['ShardID']

    @property
    def nft_ids(self) -> List:
        return self.cache[Account._cache_nft_id]

    def save_nft_id(self, *nft_ids):
        for nft in nft_ids:
            self.nft_ids.append(nft) if nft not in self.nft_ids else None
        self.nft_ids.sort()
        return self

    def is_empty(self):
        if self.private_key is None:
            return True
        return False

    def attach_to_node(self, node):
        """
        Change request handler
        @param node: Node object
        @return:
        """
        self.REQ_HANDLER = node
        return self

    def __copy__(self):
        copy_obj = Account()

        copy_obj.key_info = self.key_info
        copy_obj.cache = self.cache
        copy_obj.remote_addr = self.remote_addr
        copy_obj.REQ_HANDLER = self.REQ_HANDLER
        return copy_obj

    def __deepcopy__(self, memo=None):
        copy_obj = Account()
        copy_obj.key_info = copy.deepcopy(self.key_info)
        copy_obj.cache = copy.deepcopy(self.cache)
        copy_obj.remote_addr = copy.deepcopy(self.remote_addr)
        copy_obj.REQ_HANDLER = self.REQ_HANDLER
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

    def __me(self):
        return f"(PrvK {self.private_key[-6:]})"

    def __to_me(self):
        return f"(PayK {self.payment_key[-6:]})"

    def clone(self):
        return self.__deepcopy__()

    def create_tx_proof(self, receiver, amount, fee=-1, privacy=1):
        resp = self.REQ_HANDLER.transaction().create_tx(self.private_key, receiver.payment_key, amount,
                                                        fee, privacy).expect_no_error()
        if resp.is_node_busy():
            return 'busy'
        return resp.get_created_proof()

    def calculate_shard_id(self):
        response = self.REQ_HANDLER.transaction().get_public_key_by_payment_key(self.payment_key)
        last_byte = response.get_result("PublicKeyInBytes")[-1]
        self.key_info['ShardID'] = last_byte % 8
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
        return CustomTokenBalanceResponse(response)

    def list_all_tx_output(self, token_id=PRV_ID):
        """

        @param token_id:
        @return:
        """
        response = self.REQ_HANDLER.transaction().list_output_coin(self.payment_key, token_id, OTASecretKey=self.ota_k)
        return TXOResponse(response)

    def list_utxo(self, token_id=PRV_ID, from_height=0):
        raw_response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key, token_id, from_height)
        return TXOResponse(raw_response)

    def print_utxo(self, token_id=None):
        """
        for @debug purpose
        @param token_id:
        @return:
        """
        if not token_id:
            print_data = f'+ {PRV_ID}'
            for c in self.list_utxo().get_coins():
                print_data += f'\n   {c}'

            for token in self.list_owned_custom_token().get_tokens_info():
                print_data += f'\n+ {token}'
                for c in self.list_utxo(token.get_token_id()).get_coins():
                    print_data += f'\n   {c}'
        else:
            print_data = f'\n+ {token_id}'
            for c in self.list_utxo(token_id).get_coins():
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

        logger.info(
            f'{self.__me()} Stake for {l6(validator.validator_key)} and reward: {l6(receiver_reward.payment_key)}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, validator.payment_key, validator.validator_key,
                                                receiver_reward.payment_key, stake_amount, auto_re_stake,
                                                TestConfig.TX_VER)

    def stake_and_reward_me(self, stake_amount=ChainConfig.STK_AMOUNT, auto_re_stake=True,
                            tx_version=TestConfig.TX_VER, tx_fee=-1, tx_privacy=0):
        """

        @return:
        """
        logger.info(f"Stake and reward me: {self.validator_key}")
        if not self.validator_key:
            raise Exception("Validator key is not specified")

        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, self.payment_key, self.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake, tx_version, tx_fee,
                                                tx_privacy)

    def stake_someone_reward_me(self, someone, stake_amount=ChainConfig.STK_AMOUNT, auto_re_stake=False,
                                tx_version=TestConfig.TX_VER, tx_fee=50):
        """

        @return:
        """
        logger.info(f'Stake {someone.validator_key} but reward me')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake, tx_version, tx_fee)

    def stake_someone_reward_him(self, someone, stake_amount=ChainConfig.STK_AMOUNT, auto_re_stake=True,
                                 tx_version=TestConfig.TX_VER):
        """

        @return:
        """
        logger.info(f'Stake and reward other: f{someone.validator_key}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                someone.payment_key, stake_amount, auto_re_stake, tx_version)

    def stk_stop_auto_staking(self, reward_receiver, validator):
        return self.REQ_HANDLER.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, reward_receiver.payment_key,
                                                          validator.validator_key)

    def stk_stop_auto_stake_me(self):
        logger.info('Stop auto stake me')
        return self.stk_stop_auto_staking(self, self)

    def stk_un_stake_tx(self, validator=None, tx_fee=50):
        if not validator:
            validator = self
        logger.info(f'Un-stake transaction for validator: {validator.validator_key}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_un_staking_transaction(self.private_key, validator.payment_key, validator.validator_key,
                                                   tx_fee).attach_to_node(self.REQ_HANDLER)

    def stk_stop_auto_stake_him(self, him):
        logger.info(f"Stop auto stake other: {him.validator_key}")
        return self.stk_stop_auto_staking(him, him)

    def stk_wait_till_i_am_committee(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        logger.info(f"Wait until {self.validator_key} become a committee, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_shard = beacon_bsd.is_he_a_committee(self)
            if staked_shard is False:
                self.REQ_HANDLER.wait_till_next_epoch(1, block_of_epoch=5)
            else:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                logger.info(f"Already a committee at epoch {e2}, block height {h}")
                return e2
            time_spent = (datetime.datetime.now() - time_start).seconds
        logger.info(f"Waited {time_spent}s but still not yet become committee")
        return None

    def stk_wait_till_i_am_in_waiting_next_random(self, check_cycle=ChainConfig.BLOCK_TIME,
                                                  timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        logger.info(f"Wait until {self.validator_key} exist in waiting next random, check every {check_cycle}s,"
                    f" timeout: {timeout}s")
        while timeout > check_cycle:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_in_waiting_4random = beacon_bsd.is_he_in_waiting_next_random(self)
            if staked_in_waiting_4random is False:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                logger.info(f"Already exists in waiting next random at epoch {e2}, block height {h}")
                return e2
        logger.info(f"Waited {t}s but still not yet exist in waiting next random")
        return None

    def stk_wait_till_i_am_in_shard_pending(self, timeout=ChainConfig.STK_WAIT_TIME_OUT, sfv3=False):
        logger.info(f"Wait until {self.validator_key} exist in shard pending, timeout: {timeout}s")
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
                        logger.info(f'Current height = {h} @ epoch = {e2}. '
                                    f'Wait {time_to_wait}s until epoch {e2} and B height {h + num_of_block_wait}')
                        WAIT(time_to_wait)
                    else:
                        self.REQ_HANDLER.wait_till_next_epoch(1, block_of_epoch=ChainConfig.RANDOM_TIME + 1)
                time_spent = (datetime.datetime.now() - time_start).seconds
            else:
                logger.info(f"Already exists in shard pending at epoch {e2}, block height {h}")
                return staked_shard, e2
        logger.info(f"Waited {time_spent}s but still not yet exist in shard pending")
        return

    def stk_wait_till_i_am_in_sync_pool(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        logger.info(f"Wait until {self.validator_key} exist in sync pool, timeout: {timeout}s")
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
                    logger.info(f'Current height = {h} @ epoch = {e2}. '
                                f'Wait {time_to_wait}s until epoch {e2} and B height {h + num_of_block_wait}')
                    WAIT(time_to_wait)
                else:
                    self.REQ_HANDLER.wait_till_next_epoch(1, block_of_epoch=ChainConfig.RANDOM_TIME + 1)
                time_spent = (datetime.datetime.now() - time_start).seconds
            else:
                logger.info(f"Already exists in shard pending at epoch {e2}, block height {h}")
                return staked_shard, e2
        logger.info(f"Waited {time_spent}s but still not yet exist in sync pool")
        return

    def stk_wait_till_i_am_out_of_autostaking_list(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        logger.info(f"Wait until {self.validator_key} does not exist in the autostaking list, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            if beacon_bsd.get_auto_staking_committees(self) is None:
                e2 = beacon_bsd.get_epoch()
                h = beacon_bsd.get_beacon_height()
                logger.info(f"Validator is out of autostaking list at epoch {e2}, block height {h}")
                return e2
            self.REQ_HANDLER.wait_till_next_epoch(1, block_of_epoch=5)
            time_spent = (datetime.datetime.now() - time_start).seconds
        logger.info(f"Waited {time_spent}s but still exist in the autostaking list")
        return None

    def stk_wait_till_i_am_swapped_out_of_committee(self, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        logger.info(f"Wait until {self.validator_key} no longer a committee, timeout: {timeout}s")
        time_start = datetime.datetime.now()
        time_spent = 0
        while timeout > time_spent:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            if not (beacon_bsd.is_he_a_committee(self) is False):  # is_he_a_committee returns False or shard number
                # (number which is not False) so must use this comparison to cover the case shard =0
                self.REQ_HANDLER.wait_till_next_epoch(1, block_of_epoch=5)
            else:
                e2 = beacon_bsd.get_epoch()
                logger.info(f"Swapped out of committee at epoch {e2}")
                return e2
            time_spent = (datetime.datetime.now() - time_start).seconds
        logger.info(f"Waited {time_spent}s but still a committee")
        return None

    def stk_wait_till_i_have_reward(self, token_id=None, check_cycle=120, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        if token_id is None:
            token_id = 'PRV'
        logger.info(
            f'Wait until {self.validator_key} has reward: {token_id}, check every {check_cycle}s, timeout: {timeout}s')
        while timeout > check_cycle:
            reward = self.stk_get_reward_amount(token_id)
            if reward is None:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.REQ_HANDLER.help_get_current_epoch()
                logger.info(f"Rewarded {reward} : {token_id} at epoch {e2}")
                return reward
        logger.info(f"Waited {t}s but still has no reward")
        return None

    def get_balance(self, token_id=PRV_ID, **kwargs):
        from_cache = kwargs.get('cache', False)
        if from_cache:
            bal = self.cache[Account._cache_bal].get(token_id, 0)
            logger.info(f"{self.__me()}, token id = {l6(token_id)}, bal from cache = {coin(bal, False)} ")
            return bal
        result = self.REQ_HANDLER.transaction().get_custom_token_balance(self.private_key, token_id)
        while True:
            try:
                error_msg = result.get_error_trace().get_message()
                if re.search(re.compile(r'{(.*)} not synced'), error_msg):
                    self.submit_key()
                    logger.warning(f'{error_msg}. Wait for {ChainConfig.BLOCK_TIME}s and retry')
                    WAIT(ChainConfig.BLOCK_TIME)
                    result = self.REQ_HANDLER.transaction().get_custom_token_balance(self.private_key, token_id)
                else:
                    break
            except Exception:
                break
        balance = result.get_result() if result.get_result() else 0
        self.cache[Account._cache_bal][token_id] = balance
        logger.info(f"{self.__me()}, token id = {l6(token_id)}, bal = {coin(balance, False)} ")
        return balance

    def get_assets(self):
        assets = {token.get_token_id(): token.get_token_amount() for token in
                  self.list_owned_custom_token().get_tokens_info()}
        assets[PRV_ID] = self.get_balance()
        return assets

    def sum_my_utxo(self, token_id=PRV_ID):
        try:
            return sum([t.get_value() for t in self.list_utxo(token_id).get_coins()])
        except IndexError:
            return 0

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
        log_msg = f'From: {self.__me()}. Sent {amount} prv to: {receiver_account.__to_me()}'
        try:
            log_msg += f', tx {response.get_tx_id()}'
        except TypeError:
            log_msg += f', \n    Err: {response.get_error_trace().get_message()}'
        logger.info(log_msg)
        return response

    def send_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1, token_id=PRV_ID):
        if token_id == PRV_ID:
            return self.send_prv_to_multi_account(dict_to_account_and_amount, fee, privacy)
        else:
            return self.send_token_multi_output(dict_to_account_and_amount, token_id, prv_fee=fee, prv_privacy=privacy)

    def send_prv_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1) -> Response:
        """

        @param dict_to_account_and_amount: a dictionary of {receiver Account : amount}
        @param fee:
        @param privacy:
        @return:
        """
        send_param = dict()
        logger.info(f"{self.__me()} sending prv to multiple accounts: --------------------------------------------- ")
        for acc, amount in dict_to_account_and_amount.items():
            logger.info(f'{amount} prv to shard {acc.shard} | {acc.__me()} | {acc.__to_me()}')
            send_param[acc.payment_key] = amount
        logger.info("---------------------------------------------------------------------------------- ")

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

        logger.info(f'Sending everything to {to_account}')
        # defrag account so that the custom fee = fee x 2 as below
        defrag = self.defragment_account()
        if defrag is not None:
            defrag.subscribe_transaction()
        balance = self.get_balance()
        fee, size = self.get_estimate_fee_and_size(to_account, balance - 100, privacy=privacy)
        logger.info(f'''EstimateFeeCoinPerKb = {fee}, EstimateTxSizeInKb = {size}''')
        if balance > 0:
            return self.send_prv_to(to_account, balance - 100, int(100 / (size + 1)),
                                    privacy).subscribe_transaction()

    def count_unspent_output_coins(self, token_id='', from_height=0):
        """
        count number of unspent coin

        @return: int
        """
        logger.info('Count unspent coin')

        response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key, token_id,
                                                                            from_height).get_result("Outputs")
        return len(response[self.private_key])

    def defragment_account(self, min_bill=1000000000000000):
        """
        check if account need to be defrag by count unspent coin,
            if count > 1 then defrag

        @return: Response object if need to defrag, None if not to
        """
        logger.info('Defrag account')

        if self.count_unspent_output_coins() > 1:
            return self.REQ_HANDLER.transaction().de_fragment_prv(self.private_key, min_bill)
        logger.info('No need to defrag!')
        return None

    def subscribe_cross_output_coin(self, timeout=120):
        logger.info(f'{self.__me()} Subscribe cross output coin')
        return self.REQ_HANDLER.subscription().subscribe_cross_output_coin_by_private_key(self.private_key, timeout)

    def subscribe_cross_output_token(self, timeout=120):
        logger.info(f'{self.__me()} Subscribe cross output token')
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
        logger.info(f'Init custom token to self: {self.payment_key}')

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
        logger.info(f'Init new token with name {token_name}')
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
            logger.info(f'{self.__me()} Contribute PRV, amount: {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_prv(self.private_key, self.payment_key, amount,
                                                         pair_id, TestConfig.TX_VER)
        else:
            logger.info(f'{self.__me()} Contribute token: {l6(token_id)}, amount = {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_token(self.private_key, self.payment_key, token_id,
                                                           amount, pair_id, TestConfig.TX_VER)

    def pde_contribute_v2(self, token_id, amount, pair_id):
        if token_id == PRV_ID:
            logger.info(f'{self.__me()} Contribute PRV V2, amount: {amount}, pair id = {pair_id}')

            return self.REQ_HANDLER.dex().contribute_prv_v2(self.private_key, self.payment_key, amount,
                                                            pair_id, TestConfig.TX_VER)
        else:
            logger.info(f'{self.__me()} Contribute token V2: {l6(token_id)}, amount = {amount}, pair id = {pair_id}')
            return self.REQ_HANDLER.dex().contribute_token_v2(self.private_key, self.payment_key, token_id,
                                                              amount, pair_id, TestConfig.TX_VER)

    def pde_withdraw_contribution(self, token_id_1, token_id_2, amount):
        logger.info(f'Withdraw PDE contribution {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution(self.private_key, self.payment_key,
                                                              token_id_1, token_id_2, amount, TestConfig.TX_VER)

    def pde_withdraw_contribution_v2(self, token_id_1, token_id_2, amount):
        logger.info(f'Withdraw PDE contribution v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution_v2(self.private_key, self.payment_key, token_id_1,
                                                                 token_id_2, amount)

    def pde_withdraw_reward_v2(self, token_id_1, token_id_2, amount):
        logger.info(f'Withdraw PDE reward v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
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
        logger.info(f'Sending {amount_custom_token} token {l6(token_id)} to {l6(receiver.payment_key)}')

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
        logger.info(f'Sending token {l6(token_id)} multi output')
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
        logger.info(f'Send custom token transaction to burning address')
        return self.REQ_HANDLER.transaction(). \
            send_custom_token_transaction(self.private_key, Constants.BURNING_ADDR, token_id, amount_custom_token,
                                          prv_fee=-1, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0)

    ########
    # BRIDGE
    ########
    def issue_centralize_token(self, receiver, token_id, token_name, amount):
        """
            initialize a new centralize token
            @return: Response Object
        """
        receiver = receiver.payment_key if isinstance(receiver, Account) else receiver
        logger.info(f'{self.__me()} issue {amount} of {token_id[-6:]} to {receiver[-6:]}')
        return self.REQ_HANDLER.bridge().issue_centralized_bridge_token(self.private_key, receiver, token_id,
                                                                        token_name, amount)

    def withdraw_centralize_token(self, token_id, amount_custom_token):
        """
        Withdraw token (this mean send token to burning address, but receive your token on ETH network)
        logger.info(f'Send custom token transaction')
        return Account.SYSTEM.transaction().\
            send_custom_token_transaction(self.private_key, Constants.burning_address, token_id, amount_custom_token,
                                          prv_fee=-1, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0)

        @param token_id: Token ID
        @param amount_custom_token: amount to withdraw
        @return: Response object
        """
        logger.info(f'Withdraw centralize token')
        return self.REQ_HANDLER.transaction().withdraw_centralize_token(self.private_key, token_id,
                                                                        amount_custom_token, TestConfig.TX_VER)

    def bsc_burn_for_deposit_req(self, token_id, token_amount, remote_addr,
                                 prv_fee: dict = None, token_fee: dict = None, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.transaction(). \
            create_n_send_burn_tx_bsc(self.private_key, token_id, token_amount, remote_addr, prv_fee, token_fee, tx_fee,
                                      tx_privacy)

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
        logger.info(f"{self.__to_me()}, {token_id[-6:]} reward = {coin(reward, False)}")
        return reward

    def stk_withdraw_reward_to(self, reward_receiver, token_id=PRV_ID, tx_fee=0, tx_version=TestConfig.TX_VER,
                               privacy=0):
        logger.info(f"Withdraw token reward {token_id} to {l6(reward_receiver.payment_key)}")
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
                logger.info(f"{contribution} belong to current user and waiting for PRV, so cannot use PRV to clean up")
            else:
                self.pde_contribute_v2(PRV_ID, 10, contribution.get_pair_id()).attach_to_node(self.REQ_HANDLER) \
                    .get_transaction_by_hash()

    def pde_wait_till_my_token_in_waiting_for_contribution(self, pair_id, token_id, timeout=100):
        logger.info(f"Wait until token {l6(token_id)} is in waiting for contribution")
        my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
            find_waiting_contribution_of_user(self, pair_id, token_id)
        while timeout >= 0:
            if my_waiting:  # not empty
                logger.info(f'Token {l6(token_id)} is found in contribution waiting list')
                return True
            timeout -= 10
            WAIT(10)
            my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
                find_waiting_contribution_of_user(self, pair_id, token_id)
        logger.info(f'Token {l6(token_id)} is NOT found in contribution waiting list')
        return False

    def pde_wait_till_my_token_out_waiting_for_contribution(self, pair_id, token_id, timeout=100):
        logger.info(f"Wait until token {l6(token_id)} is OUT of waiting for contribution")
        my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
            find_waiting_contribution_of_user(self, pair_id, token_id)
        while timeout >= 0:
            if not my_waiting:
                logger.info(f'Token {l6(token_id)} is NOT found in contribution waiting list')
                return True
            timeout -= 10
            WAIT(10)
            my_waiting = self.REQ_HANDLER.get_latest_pde_state_info(). \
                find_waiting_contribution_of_user(self, pair_id, token_id)
        logger.info(f'Token {l6(token_id)} is found in contribution waiting list')
        return False

    def pde_trade_token(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        logger.info(f'User {self.__to_me()}: '
                    f'Trade {sell_amount} of token {token_id_to_sell[-6:]} for {token_id_to_buy[-6:]} '
                    f'trading fee={trading_fee}')
        return self.REQ_HANDLER.dex().trade_token(self.private_key, self.payment_key, token_id_to_sell,
                                                  sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee,
                                                  tx_ver=TestConfig.TX_VER)

    def pde_trade_prv(self, amount_to_sell, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        logger.info(f'User {self.__to_me()}: '
                    f'Trade {amount_to_sell} of PRV for {token_id_to_buy[-6:]}')
        return self.REQ_HANDLER.dex().trade_prv(self.private_key, self.payment_key, amount_to_sell,
                                                token_id_to_buy, min_amount_to_buy, trading_fee, TestConfig.TX_VER)

    def pde_trade(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        if token_id_to_sell == PRV_ID:
            return self.pde_trade_prv(sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)
        else:
            return self.pde_trade_token(token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)

    def pde_trade_prv_v2(self, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        logger.info(f'User {self.__to_me()}: '
                    f'Trade {amount_to_sell} PRV for {l6(token_to_buy)} trading fee={trading_fee}, '
                    f'min acceptable={min_amount_to_buy}')
        return self.REQ_HANDLER.dex().trade_prv_v2(self.private_key, self.payment_key, amount_to_sell,
                                                   token_to_buy, trading_fee, min_amount_to_buy,
                                                   tx_ver=TestConfig.TX_VER)

    def pde_trade_token_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        logger.info(f'User {self.__to_me()}: '
                    f'Trade {amount_to_sell} of token {token_to_sell[-6:]} for {token_to_buy[-6:]} '
                    f'trading fee={trading_fee}, min acceptable={min_amount_to_buy}')
        return self.REQ_HANDLER.dex().trade_token_v2(self.private_key, self.payment_key, token_to_sell,
                                                     amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy,
                                                     tx_ver=TestConfig.TX_VER)

    def pde_trade_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        if token_to_sell == PRV_ID:
            return self.pde_trade_prv_v2(amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)
        else:
            return self.pde_trade_token_v2(token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)

    def pde3_add_order(self, token_sell, token_buy, pool_id, sell_amount, min_acceptable, nft_id=None,
                       tx_fee=-1, tx_privacy=1):
        nft_id = self.nft_ids[0] if not nft_id else nft_id
        logger.info(f"Adding order to order book\n   "
                    f"In pool {pool_id}\n   "
                    f"Selling {sell_amount} of {token_sell} to buy {token_buy}\n   "
                    f"Min acceptable: {min_acceptable}")
        return self.REQ_HANDLER.dex_v3() \
            .add_order(self.private_key, nft_id, token_sell, token_buy, pool_id, str(sell_amount),
                       str(min_acceptable), tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_order(self, pool_pair, order, nft_id, token_id_list, amount, tx_fee=-1, tx_privacy=1):
        if isinstance(pool_pair, PdeV3State.PoolPairData):
            pair_id = pool_pair.get_pool_pair_id()
        elif isinstance(pool_pair, str):
            pair_id = pool_pair
        else:
            raise RuntimeError(f"pool_pair param is {type(pool_pair)} ,not PdeV3State.PoolPairData or string")
        if isinstance(order, PdeV3State.PoolPairData.Order):
            order_id = order.get_id()
            order.get_nft_id()
        elif isinstance(order, str):
            order_id = order
        else:
            raise RuntimeError(f"order param is {type(order)} ,not PdeV3State.PoolPairData.Order or string")
        token_id_list = token_id_list if isinstance(token_id_list, list) else [token_id_list]
        logger.info(f"{self.__me()} nft: {nft_id[-6:]} Withdrawing {amount} from order {order_id}")
        return self.REQ_HANDLER.dex_v3().withdraw_order(self.private_key, pair_id, order_id, nft_id,
                                                        token_id_list, int(amount), tx_fee=tx_fee,
                                                        tx_privacy=tx_privacy)

    def pde3_trade(self, token_sell, token_buy, sell_amount, min_acceptable, trade_path, trading_fee,
                   use_prv_fee=True, tx_fee=-1, tx_privacy=1):
        trade_path = [trade_path] if isinstance(trade_path, str) else trade_path
        logger.info(
            f"PDE3 - {self.private_key[-6:]} request trading {sell_amount} of {token_sell[-6:]} for {token_buy[-6:]}, "
            f"PRV trading fee {use_prv_fee}, amount {trading_fee} via \n   {trade_path}")
        return self.REQ_HANDLER.dex_v3().trade(self.private_key, token_sell, token_buy, sell_amount, min_acceptable,
                                               trade_path, trading_fee, use_prv_fee,
                                               tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_make_raw_trade_tx(self, token_sell, token_buy, sell_amount, min_acceptable, trade_path, trading_fee,
                               use_prv_fee=True):
        return self.REQ_HANDLER.pde3_make_trade_tx(self.private_key, token_sell, token_buy, sell_amount,
                                                   min_acceptable, trade_path, trading_fee, use_prv_fee)

    def pde3_withdraw_lp_fee(self, receiver, pool_pair_id, nft_id, token_amount=1,
                             token_tx_type=1, token_fee=0, token_name="", token_symbol="",
                             burning_tx=None, tx_fee=-1, tx_privacy=1):
        payment_key = receiver.payment_key if isinstance(receiver, Account) else receiver
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_lp_fee(self.private_key, payment_key, token_amount, nft_id, pool_pair_id, nft_id,
                             token_tx_type, token_fee, token_name, token_symbol, burning_tx,
                             tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_stake(self, stake_amount, staking_pool_id, nft_id, tx_fee=-1, tx_privacy=1):
        nft_id = nft_id if nft_id else self.nft_ids[0]
        return self.REQ_HANDLER.dex_v3().stake(self.private_key, staking_pool_id, str(stake_amount), nft_id,
                                               tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_unstake(self, unstake_amount, staking_pool_id, nft_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .unstake(self.private_key, staking_pool_id, nft_id, str(unstake_amount), tx_fee=tx_fee,
                     tx_privacy=tx_privacy).attach_to_node(self.REQ_HANDLER)

    def pde3_withdraw_staking_reward_to(self, receiver, staking_pool_id, nft_id, token_id, tx_fee=-1, tx_privacy=1):
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_staking_reward(self.private_key, receiver.payment_key, staking_pool_id, nft_id, token_id,
                                     tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_staking_reward_to_me(self, staking_pool_id, nft_id, token_id, tx_fee=-1, tx_privacy=1):
        return self.pde3_withdraw_staking_reward_to(self, staking_pool_id, nft_id, token_id, tx_fee, tx_privacy)

    def pde3_add_liquidity(self, token_id, amount, amplifier, contribute_id, nft_id=None, pool_pair_id="", tx_fee=-1,
                           tx_privacy=1):
        nft_id = nft_id if nft_id else self.nft_ids[0]
        logger.info(f"Contributing {amount} of {token_id}\n\t"
                    f"NFT: {nft_id} | Amp: {amplifier} | contrib id: {contribute_id}")
        return self.REQ_HANDLER.dex_v3() \
            .add_liquidity(self.private_key, token_id, str(amount), str(amplifier), pool_pair_id, contribute_id, nft_id,
                           tx_fee=tx_fee, tx_privacy=tx_privacy)

    def pde3_withdraw_liquidity(self, pool, share_amount=None, nft_id=None, tx_fee=-1, tx_privacy=1):
        """
        @param pool: pool pair id or PoolPairData object
        @param share_amount: share amount to withdraw, leave None to withdraw all
        @param nft_id: NFT ID, leave None to use default NFT (self.nft_ids[0])
        @param tx_fee:
        @param tx_privacy:
        @return:
        """
        nft_id = nft_id if nft_id else self.nft_ids[0]
        if isinstance(pool, PdeV3State.PoolPairData):
            pair_id = pool.get_pool_pair_id()
            share_amount = pool.get_share(nft_id).amount if share_amount is None else share_amount
        else:
            pair_id = pool
            share_amount = self.REQ_HANDLER.pde3_get_state().get_pool_pair(id=pool).get_share(nft_id).amount \
                if share_amount is None else share_amount
        logger.info(f"PDE3 Withdraw liquidity, private k: {self.private_key[-6:]}, NFT ID {nft_id}\n   "
                    f"pair: {pair_id}\n   "
                    f"share amount withdraw: {share_amount}")
        return self.REQ_HANDLER.dex_v3() \
            .withdraw_liquidity(self.private_key, pair_id, nft_id, str(share_amount), tx_fee=tx_fee,
                                tx_privacy=tx_privacy)

    def pde3_mint_nft(self, amount=ChainConfig.Dex3.NFT_MINT_REQ, token_id=PRV_ID, tx_fee=-1, tx_privacy=1,
                      force=False):
        if not force:
            if self.nft_ids:
                logger.info(f"{self.__me()} Already have NFT ID(s), "
                            f"return the first one now and will not mint more: \n {self.nft_ids}")
                return self.nft_ids[0]
        logger.info(f"{self.__me()} request minting new PDEX NFT ID")
        response = self.REQ_HANDLER.dex_v3() \
            .mint_nft(self.private_key, amount, token_id, tx_fee=tx_fee, tx_privacy=tx_privacy)
        try:
            response.get_transaction_by_hash()
        except AssertionError:
            logger.error(f"{response.get_error_msg()}\n"
                         f"{response.get_error_trace().get_message()}\n"
                         f"{response.rpc_params().data}")
            return None
        except AttributeError as e:
            logger.error(f"{e}")
            return None

        wasted_time = 0
        while True:
            WAIT(ChainConfig.BLOCK_TIME)
            wasted_time += ChainConfig.BLOCK_TIME
            mint_status = self.REQ_HANDLER.dex_v3().get_mint_nft_status(response.get_tx_id())
            nft_id = mint_status.get_nft_id()
            if nft_id:
                logger.info(f"{self.__me()} New DEX NFT ID: {nft_id}")
                self.save_nft_id(nft_id)
                return nft_id
            if wasted_time > ChainConfig.BLOCK_TIME * 5:
                break
        if not nft_id:
            logger.info(f"{self.__me()} waited {wasted_time}s, but can't get new nft id after tx was confirmed")
            return None

    def pde3_get_my_nft_ids(self, pde_state=None, force=False):
        if not force and self.nft_ids:
            return self.nft_ids
        try:
            assert pde_state.get_nft_id() != {}
        except (AttributeError, AssertionError):
            pde_state = self.REQ_HANDLER.pde3_get_state(key_filter="NftIDs")
        try:
            all_my_custom_token = self.list_owned_custom_token().get_tokens_info()
        except Exception as e:
            logger.error(e)
            raise e
        self.nft_ids.clear()
        for token in all_my_custom_token:
            if pde_state.get_nft_id(token.get_token_id()):
                self.save_nft_id(token.get_token_id())
        logger.info(f"Get {self.private_key[-6:]} NFT id from pde state.\n   found: {self.nft_ids}")
        return self.nft_ids

    def pde3_clean_all_waiting_contribution(self, pde_state=None):
        pde_state = self.REQ_HANDLER.pde3_get_state() if pde_state is None else pde_state
        for contribution in pde_state.get_waiting_contribution():
            nft = ''
            for nft in pde_state.get_nft_id().keys():
                if nft != contribution.get_nft_id():
                    break
            self.pde3_add_liquidity(PRV_ID, 100, contribution.get_amplifier(), contribution.get_contribution_id(),
                                    nft, contribution.get_pool_pair_id()).get_transaction_by_hash()

    def pde3_modify_param(self, new_config: Union[dict, PdeV3State.Param], tx_fee=10, tx_privacy=0):
        new_config = new_config.get_configs() if isinstance(new_config, PdeV3State.Param) else new_config
        return self.REQ_HANDLER.dex_v3().modify_param(self.private_key, new_config, tx_fee=tx_fee,
                                                      tx_privacy=tx_privacy)

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
        logger.info(f'Wait for token {l6(token_id)} of {self.__me()} '
                    f'balance to change at least: {least_change_amount}. From {from_balance}')
        bal_new = None
        while timeout >= 0:
            bal_new = self.get_balance(token_id)
            change_amount = bal_new - from_balance
            if least_change_amount is None:  # just change, does not mater + or -
                if bal_new != from_balance:
                    logger.info(f'Balance token {l6(token_id)} of {self.__me()} changes: {change_amount}')
                    return bal_new
            elif least_change_amount >= 0:  # case balance increase
                if bal_new >= from_balance + least_change_amount:
                    logger.info(f'Balance token {l6(token_id)} of {self.__me()} changes: {change_amount}')
                    return bal_new
            else:  # case balance decrease
                if bal_new <= from_balance + least_change_amount:
                    logger.info(f'Balance token {l6(token_id)} of {self.__me()} changes: {change_amount}')
                    return bal_new
            WAIT(check_interval)
            timeout -= check_interval
        logger.info(f'Balance token {l6(token_id)} of {self.__me()} not change a bit')
        return bal_new

    #######
    # Portal
    #######
    def portal_create_exchange_rate(self, rate_dict: dict):
        logger.info()
        logger.info(f'Portal | User {self.__to_me()} | create rate')
        for key, value in rate_dict.items():  # convert dict value to string
            rate_dict[key] = str(value)
        return self.REQ_HANDLER.portal(). \
            create_n_send_portal_exchange_rates(self.private_key, self.payment_key, rate_dict)

    def portal_create_porting_request(self, token_id, amount, porting_fee=None, register_id=None):
        logger.info()
        logger.info(f'Portal | User {self.__to_me()} | create porting req | amount {coin(amount, False)}')
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
        logger.info()
        logger.info(f'Portal | Custodian {self.__to_me()} | '
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
        logger.info(f"{self.__to_me()} will take this redeem: {redeem_id}")
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
        logger.info()
        redeem_id = f"{l6(token_id)}_{get_current_date_time()}"
        logger.info(f'Portal | User (payment k) {self.__to_me()} | req redeem token |'
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
        logger.info(f'Portal | Custodian {self.__to_me()} | Withdraw collateral: {amount}')
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
        logger.info(f"Withdraw all collateral of {self.__to_me()}")
        my_custodian_info = psi.get_custodian_info_in_pool(self)
        if my_custodian_info is None:
            logger.info("I'm not even a custodian")
            return None
        my_free_collateral = my_custodian_info.get_free_collateral()
        if my_free_collateral == 0:
            logger.info('Current free collateral is 0, nothing to withdraw')
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
        logger.info()
        logger.info(f'Portal | User {self.__to_me()} | req for ported token')
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

    def portal_wait_my_lock_collateral_to_change(self, token_id, from_amount=None, check_interval=30, timeout=180):
        logger.info(f'Wait for my lock collateral change, {self.__to_me()}, token {l6(token_id)}')
        my_custodian_stat = self.portal_get_my_custodian_info()
        if my_custodian_stat is None:
            logger.info("You're not even a custodian")
            return None
        if from_amount is None:
            collateral_before = self.portal_get_my_custodian_info().get_locked_collateral(token_id)
        else:
            collateral_before = from_amount
        current_collateral = collateral_before
        wasted_time = 0
        while current_collateral == collateral_before:
            if wasted_time >= timeout:
                logger.info(f'Lock collateral does not change in the last {wasted_time}s')
                return 0
            WAIT(check_interval)
            wasted_time += check_interval
            current_collateral = self.portal_get_my_custodian_info().get_locked_collateral(token_id)

        delta = current_collateral - collateral_before
        logger.info(f'Lock collateral has change {delta}')
        return delta

    def portal_sum_my_waiting_porting_req_locked_collateral(self, token_id, portal_state_info=None):
        if portal_state_info is None:
            portal_state_info = self.REQ_HANDLER.get_latest_portal_state_info()

        sum_amount = portal_state_info.sum_collateral_porting_waiting(token_id, self)
        logger.info(f'{self.__to_me()} sum all waiting porting req collateral of token {l6(token_id)}: {sum_amount}')
        return sum_amount

    def portal_sum_my_matched_redeem_req_holding_token(self, token_id, portal_state_info=None):
        if portal_state_info is None:
            portal_state_info = self.REQ_HANDLER.get_latest_portal_state_info()

        sum_amount = portal_state_info.sum_holding_token_matched_redeem_req(token_id, self)
        logger.info(f'{self.__to_me()} sum all waiting redeem holding token of {l6(token_id)}: {sum_amount}')
        return sum_amount

    def portal_req_unlock_collateral(self, token_id, amount_redeem, redeem_id, proof):
        logger.info(f'{self.__to_me()} request unlock collateral: {l6(token_id)} {amount_redeem} {redeem_id}')
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
            convert_tx = self.REQ_HANDLER.transaction(). \
                create_convert_coin_ver1_to_ver2_tx_token(self.private_key, token_id, fee)
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
        logger.info(f"\n      TOP UP OTHERS'({len(receiver)} acc) TO {upper} (token {(l6(token_id))})\n{'=' * 80}")
        # there's a max number of output in "createandsendtransaction" rpc, so must split into small batch of output
        each, length, start = 20, len(receiver), 0
        mid = each
        keys = list(receiver.keys())
        wasted_time = 0
        while start < length:
            sub_keys = keys[start:mid]
            logger.info(f'Batch: {start}->{len(sub_keys)}')
            sub_receivers = {k: receiver[k] for k in sub_keys}
            send_tx = self.send_to_multi_account(sub_receivers, token_id=token_id)
            if send_tx.get_error_msg():
                # ideally should only retry if coin being used in another tx, but for now, just retry if there's any err
                logger.info(f'{send_tx.get_error_trace().get_message()}. Wait then retry')
                WAIT(retry_interval)
                wasted_time += retry_interval
                if wasted_time >= max_wait:
                    raise TimeoutError(f"Waited {wasted_time}s but cannot create send tx, "
                                       f"output coins appear to being used use in another tx")

            else:
                # tx should be succeed
                send_tx.expect_no_error().get_transaction_by_hash()
                start = mid
                mid += each
                wasted_time = 0

        # thread_pool = []
        for acc, amount in receiver.items():
            acc.wait_for_balance_change(token_id, from_balance=bal_receiver_b4_dict[acc])

    def submit_key(self, key_type='ota'):
        """
        @param key_type: private or ota
        @return:
        """
        key_type = key_type.lower()
        k_map = {'private': self.private_key, 'ota': self.ota_k}
        key = k_map.get(key_type)
        logger.info(f'Submit {key_type} key for indexing coin {l6(key)}')
        submit_response = self.REQ_HANDLER.transaction().submit_key(key)
        try:
            error = submit_response.get_error_trace().get_message()
        except AttributeError:
            error = None
        logger.error(error) if error else logger.info(submit_response.get_result())
        return self

    def submit_key_status(self):
        return self.REQ_HANDLER.transaction().submit_key_info(self.ota_k).get_result()

    def submit_key_authorize(self, from_height=0, re_index=False, access_token=ChainConfig.ACCESS_TOKEN):
        return self.REQ_HANDLER.transaction().submit_key_authorized(self.ota_k, access_token, from_height, re_index)

    @staticmethod
    def new():
        pass


class AccountGroup:
    def __get_acc_synchronous(self, keys):
        init_thread = []
        with ThreadPoolExecutor() as tpe:
            for key in keys:
                init_thread.append(tpe.submit(Account, key))

        for thread in init_thread:
            self.account_list.append(thread.result())
        return self

    def __init__(self, *accounts):
        self.mnemonic = None
        self.account_list: List[Account] = []
        list_key = []
        for acc in accounts:
            if isinstance(acc, Account):
                self.account_list.append(acc)
            elif isinstance(acc, str):
                list_key.append(acc)
            else:
                raise TypeError(f"List member must be an Account object or string (private key), "
                                f"got {type(acc)} instead ")
        self.__get_acc_synchronous(list_key)

    def load_from_list(self, _list):
        private_keys = []
        for item in _list:
            if isinstance(item, str):
                private_keys.append(item)
            elif isinstance(item, list):
                private_keys.append(item[0])
            else:
                raise TypeError(f"Each item of list must be a string or a list which first item is a string")
        return self.__get_acc_synchronous(private_keys)

    def load_from_file(self, file_path, num_of_key_to_load=None):
        with open(file_path) as file:
            lines = file.read().splitlines()
            if num_of_key_to_load:
                keys = []
                while num_of_key_to_load:
                    key = lines.pop(0)
                    if key:
                        keys.append(key)
                        num_of_key_to_load -= 1
            else:
                keys = [key for key in lines if key]
        self.__get_acc_synchronous(keys)
        return self

    def load_from_json_file(self, json_file_path):
        with open(json_file_path) as f:
            return self.load_from_list(json.load(f))

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
        logger.info(f'Find all accounts in shard {shard_number}')
        accounts_in_shard: List[Account] = []
        for account in self.account_list:
            if account.shard % ChainConfig.ACTIVE_SHARD == shard_number % ChainConfig.ACTIVE_SHARD:
                accounts_in_shard.append(account)

        return AccountGroup(*accounts_in_shard)

    def rm_accounts_in_shard(self, shard_id):
        for acc in self:
            if acc.shard == shard_id:
                self.remove(acc)
        return self

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

    def attach_to_node(self, node):
        for acc in self:
            acc.attach_to_node(node)
        return self

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

    def get_assets(self):
        thread_results = {}
        with ThreadPoolExecutor() as tpe:
            for acc in self:
                thread_results[acc] = tpe.submit(acc.get_assets)
        return {acc: thread.result() for acc, thread in thread_results.items()}

    def submit_key(self, key_type='ota'):
        to_submit = []
        wait_time, each_wait, max_wait = 0, 5, 300
        submit_statuses = {}
        logger.info(f"Getting key submit status...")
        with ThreadPoolExecutor() as tpe:
            for acc in self:
                t = tpe.submit(acc.submit_key_status)
                submit_statuses[acc] = t
        for acc, future in submit_statuses.items():
            if future.result() == Status.SubmitKey.NOT_SUBMITTED:
                to_submit.append(acc)
                wait_time += each_wait
        with ThreadPoolExecutor() as tpe:
            for acc in to_submit:
                tpe.submit(acc.submit_key, key_type)
        if wait_time:
            logger.info(f"Indexing is in progress, wait for {min(wait_time, max_wait)}!!!")
            WAIT(min(wait_time, max_wait))
        return self

    def convert_token_to_v2(self, token=PRV_ID, fee=-1):
        for acc in self.account_list:
            with ThreadPoolExecutor() as tpe:
                tpe.submit(acc.convert_token_to_v2, token, fee)

    def get_random_account(self):
        return self.account_list[random.randrange(len(self.account_list))]

    def pde3_mint_nft(self, amount=coin(1), token_id=PRV_ID, tx_fee=-1, tx_privacy=1, force=False):
        with ThreadPoolExecutor() as e:
            for acc in self:  # bug IC-1519
                time.sleep(0.3)
                e.submit(acc.pde3_mint_nft, amount, token_id, tx_fee, tx_privacy, force)
                # acc.pde3_mint_nft(amount, token_id, tx_fee, tx_privacy, force)
        return self

    def pde3_get_nft_ids(self, pde_state=None, force=False):
        pde_state = self[0].REQ_HANDLER.pde3_get_state(key_filter="NftIDs") if not pde_state else pde_state
        pde_state = self[0].REQ_HANDLER.pde3_get_state(key_filter="NftIDs") if pde_state.get_nft_id() == {} \
            else pde_state
        with ThreadPoolExecutor() as e:
            for acc in self:
                e.submit(acc.pde3_get_my_nft_ids, pde_state, force)
        return self

    def pde3_make_raw_trade_txs(self, token_sell, token_buy, trade_amount, min_acceptable, trade_path,
                                trade_fee):
        logger.info("Making multiple raw trade tx with same amount, fee, path...")
        futures = {}
        with ThreadPoolExecutor() as tpe:
            for acc in self:
                t = tpe.submit(acc.pde3_make_raw_trade_tx, token_sell, token_buy, trade_amount, min_acceptable,
                               trade_path, trade_fee)
                futures[acc] = t
        return {acc: t.result()[1] for acc, t in futures.items()}

    def get_shard_dispersion(self):
        dispersion = {}
        for acc in self:
            try:
                dispersion[acc.shard] += 1
            except KeyError:
                dispersion[acc.shard] = 1
        return dict(sorted(dispersion.items()))

    @staticmethod
    def gen_accounts(mnemonic=None, num_of_acc=1):
        acc_group = AccountGroup()
        if mnemonic:
            accounts_raw = IncCliWrapper().import_account(mnemonic, num_of_acc)
            acc_group.mnemonic = mnemonic
        else:
            acc_group.mnemonic, accounts_raw = IncCliWrapper().gen_account(num_of_acc)

        for raw_acc in accounts_raw:
            acc = Account()
            acc.key_info = raw_acc
            acc_group.append(acc)
        return acc_group


PORTAL_FEEDER = Account(ChainConfig.Portal.FEEDER_PRIVATE_K)
COIN_MASTER = Account(DAO_PRIVATE_K)
BLACK_HOLE = Account("", BURNING_ADDR)
