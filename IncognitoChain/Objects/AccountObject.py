import copy
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from IncognitoChain.Configs import Constants
from IncognitoChain.Configs.Constants import PRV_ID, coin, PBNB_ID, PBTC_ID, Status, DAO_PRIVATE_K, \
    ChainConfig
from IncognitoChain.Drivers.IncognitoKeyGen import get_key_set_from_private_k
from IncognitoChain.Drivers.NeighborChainCli import NeighborChainCli
from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE, WARNING
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT, get_current_date_time
from IncognitoChain.Objects.CoinObject import Coin
from IncognitoChain.Objects.PortalObjects import RedeemReqInfo, PortalStateInfo


class Account:
    class RemoteAddress:
        def __init__(self, data=None):
            data = {} if data is None else data
            self.data: dict = data

    _cache_custodian_inf = 'custodian_info'
    _cache_bal_prv = 'balance_prv'
    _cache_bal_tok = 'balance_token'

    def set_remote_addr(self, *addresses):
        """

        :param addresses:
            address list with following order: BNB, BTC. Set to None if you wish to leave the address empty
        :return:
        """
        support_token_list = [PBNB_ID, PBTC_ID]
        for token, address in zip(support_token_list, addresses):
            self.remote_addr.data[token] = address
        return self

    def get_remote_addr(self, token_id):
        try:
            return self.remote_addr.data[token_id]
        except KeyError:
            return None

    def is_this_my_key(self, key_to_check):
        """
        @param key_to_check:
        @return: key type of the {key_key_to_check} or None if not found in this account
        """
        for key_type, value in self.__dict__.items():
            if "key" in key_type or "address" in key_type or "_k" in key_type:
                if key_to_check == value:
                    return key_type
        return False

    def __init__(self, private_key=None, payment_k=None, nomad=False, **kwargs):
        """

        @param private_key: private key of this account,
         other keys will be generated automatically if payment_k is not specified
        @param payment_k: payment key of this account, if specified along with private key, other keys will not
         get generated and will be set to None
        @param nomad: True = not yet tie this account to a Chain.
            False: tie this account to the configured Chain (from command line arg or from config.py file)
        @param kwargs:
        """
        self.remote_addr = Account.RemoteAddress()

        if private_key is not None:
            if payment_k is not None:
                self.private_key = private_key
                self.payment_key = self.incognito_addr = payment_k
                self.validator_key = self.public_key = self.read_only_key = self.bls_public_k = self.bridge_public_k = \
                    self.mining_public_k = self.committee_public_k = self.shard = None
                try:
                    self.shard = kwargs['shard']
                except KeyError:
                    self.shard = None
            else:
                private_k, payment_k, public_k, read_only_k, validator_k, bls_public_k, \
                bridge_public_k, mining_public_k, committee_public_k, shard_id = get_key_set_from_private_k(private_key)

                self.private_key = private_k
                self.validator_key = validator_k
                self.payment_key = self.incognito_addr = payment_k
                self.public_key = public_k
                self.read_only_key = read_only_k
                self.bls_public_k = bls_public_k
                self.bridge_public_k = bridge_public_k
                self.mining_public_k = mining_public_k
                self.committee_public_k = committee_public_k
                self.shard = int(shard_id)
        else:
            self.private_key = None

        self.cache = {}
        if nomad:
            from IncognitoChain.Objects.NodeObject import Node
            self.REQ_HANDLER = Node()
        else:
            from IncognitoChain.Objects import IncognitoTestCase
            self.REQ_HANDLER = IncognitoTestCase.SUT()

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
        copy_obj.incognito_addr = self.incognito_addr
        copy_obj.public_key = self.public_key
        copy_obj.read_only_key = self.read_only_key
        copy_obj.bls_public_k = self.bls_public_k
        copy_obj.bridge_public_k = self.bridge_public_k
        copy_obj.mining_public_k = self.mining_public_k
        copy_obj.committee_public_k = self.committee_public_k
        copy_obj.shard = self.shard
        copy_obj.cache = self.cache
        return copy_obj

    def __deepcopy__(self, memo={}):
        copy_obj = Account()

        copy_obj.private_key = copy.deepcopy(self.private_key)
        copy_obj.validator_key = copy.deepcopy(self.validator_key)
        copy_obj.payment_key = copy.deepcopy(self.payment_key)
        copy_obj.incognito_addr = copy.deepcopy(self.incognito_addr)
        copy_obj.public_key = copy.deepcopy(self.public_key)
        copy_obj.read_only_key = copy.deepcopy(self.read_only_key)
        copy_obj.bls_public_k = copy.deepcopy(self.bls_public_k)
        copy_obj.bridge_public_k = copy.deepcopy(self.bridge_public_k)
        copy_obj.mining_public_k = copy.deepcopy(self.mining_public_k)
        copy_obj.committee_public_k = copy.deepcopy(self.committee_public_k)
        copy_obj.shard = copy.deepcopy(self.shard)
        copy_obj.cache = copy.deepcopy(self.cache)
        return copy_obj

    def __eq__(self, other):
        if self.payment_key == other.payment_key:
            return True
        return False

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        return True

    def __hash__(self):
        # for using Account object as 'key' in dictionary
        return int(str(self.private_key).encode('utf8').hex(), 16)

    def create_tx_proof(self, receiver, amount, fee=-1, privacy=1):
        resp = self.REQ_HANDLER.transaction().create_tx(self.private_key, receiver.payment_key, amount,
                                                        fee, privacy).expect_no_error()
        if resp.is_node_busy():
            return 'busy'
        return resp.get_created_proof()

    def calculate_shard_id(self):
        if self.payment_key is None:
            self.find_payment_key()
        if self.public_key is None:
            self.find_public_key()
        response = self.REQ_HANDLER.transaction().get_public_key_by_payment_key(self.payment_key)
        last_byte = response.get_result("PublicKeyInBytes")[-1]
        self.shard = last_byte % ChainConfig.ACTIVE_SHARD
        return self.shard

    def __str__(self):
        string = f'Shard = {self.shard}\n' + \
                 f'Private key = {self.private_key}\n' + \
                 f'Payment key = {self.payment_key}'
        if self.read_only_key is not None:
            string += f'\nRead only key = {self.read_only_key}'
        if self.validator_key is not None:
            string += f'\nValidator key = {self.validator_key}'
        if self.public_key is not None:
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

        :return:
        """
        if not force:
            if self.payment_key is not None:
                return self.payment_key

        tx = self.REQ_HANDLER.transaction().list_custom_token_balance(self.private_key)
        self.payment_key = tx.get_result('PaymentAddress')
        return self.payment_key

    def find_public_key(self, force=False):
        """

        :return:
        """
        if not force:
            if self.public_key is not None:
                return self.public_key

        tx = self.REQ_HANDLER.transaction().get_public_key_by_payment_key(self.payment_key)
        self.public_key = tx.get_result('PublicKeyInBase58Check')
        return self.public_key

    def get_estimate_fee_and_size(self, receiver, amount, fee=-1, privacy=1):
        r = self.REQ_HANDLER.transaction().estimate_tx_fee(self.private_key, receiver.payment_key, amount, fee, privacy)
        estimate_fee_coin_perkb = int(r.get_result('EstimateFeeCoinPerKb'))
        estimate_txsize_inKb = int(r.get_result('EstimateTxSizeInKb'))
        return estimate_fee_coin_perkb, estimate_txsize_inKb

    def get_token_balance(self, token_id):
        """
        get balance by token_id

        :param token_id:
        :return:
        """

        result = self.REQ_HANDLER.transaction().get_custom_token_balance(self.private_key, token_id). \
            expect_no_error().get_result()
        balance = result if result is not None else 0

        self.cache[f'{Account._cache_bal_tok}_{token_id}'] = balance
        INFO(f"Private k = {l6(self.private_key)}, token id = {l6(token_id)}, bal = {coin(balance, False)} ")
        return balance

    def get_all_custom_token_balance(self):
        """

        :return: example
        [
            {
                "Name": "",
                "Symbol": "",
                "Amount": 430,
                "TokenID": "6abd698ea7ddd1f98b1ecaaddab5db0453b8363ff092f0d8d7d4c6b1155fb693",
                "TokenImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaQAAAGkAQMAAABEgsN2AAAABlBMVEXw8PBwrhrnsOZhAAAAn0lEQVR4nOzaOwoCMRSGUa1cRpaqS3UZqVS4WFxMEDGZB8P5qhkmZ+q/yEmSJK3R+Rnd4qXEc6UoiqIoiqKopVT++Fa52v6OoiiKoiiKouaoTtc4cv92hKIoiqIoiqLGVUlz9dGqS56zn7uXoiiKoiiKokaUJEmStFWdBZv7ffdSFEVRFEVR1F9qzzdaKYqiKIqiqKMqSZI0uVcAAAD//xeb0J2XU8SMAAAAAElFTkSuQmCC",
                "IsPrivacy": true,
                "IsBridgeToken": true
            }
        ]
        """
        return self.REQ_HANDLER.transaction().list_custom_token_balance(self.private_key). \
            get_result('ListCustomTokenBalance')

    def list_unspent_coin(self):
        raw_response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key)
        raw_coins = raw_response.get_result('Outputs')[self.private_key]
        obj_coins = []
        for raw_coin in raw_coins:
            obj_coins.append(Coin(raw_coin))
        return obj_coins

    def list_unspent_token(self):
        custom_token_bal_raw = self.get_all_custom_token_balance()
        obj_coins = []
        for bal in custom_token_bal_raw:
            tok_id = bal['TokenID']
            raw_response = self.REQ_HANDLER.transaction(). \
                list_unspent_output_tokens(self.private_key, tok_id).expect_no_error()
            raw_coins = raw_response.get_result('Outputs')[self.private_key]
            for raw_coin in raw_coins:
                obj_coins.append(Coin(raw_coin))
        return obj_coins

    def stake(self, validator=None, receiver_reward=None, stake_amount=None, auto_re_stake=True):
        """

        @param validator: account_object. if None then validator = the stake
        @param receiver_reward: account_object. if None then receiver_reward = the stake
        @param stake_amount: str. if None then stake_amount = 1750PRV
        @param auto_re_stake: bool
        @return:
        """
        if validator is None:
            validator = self
        if receiver_reward is None:
            receiver_reward = self
        if receiver_reward.payment_key is None:
            receiver_reward.find_payment_key()
        if validator.validator_key is None:
            raise Exception("Validator key is not specified")

        INFO(
            f'{l6(self.private_key)} Stake for {l6(validator.validator_key)} and reward other: {l6(receiver_reward.payment_key)}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, validator.payment_key,
                                                validator.validator_key,
                                                receiver_reward.payment_key, stake_amount, auto_re_stake)

    def stake_and_reward_me(self, stake_amount=None, auto_re_stake=True):
        """

        :return:
        """
        INFO(f"Stake and reward me: {self.validator_key}")
        if self.payment_key is None:
            self.find_payment_key()
        if self.public_key is None:
            self.find_public_key()
        if self.validator_key is None:
            raise Exception("Validator key is not specified")

        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, self.payment_key, self.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake)

    def stake_someone_reward_me(self, someone, stake_amount=None):
        """

        :return:
        """
        INFO(f'Stake {someone.validator_key} but reward me')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                self.payment_key, stake_amount)

    def stake_someone_reward_him(self, someone, stake_amount=None, auto_re_stake=True):
        """

        :return:
        """
        INFO(f'Stake and reward other: f{someone.validator_key}')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                someone.payment_key, stake_amount, auto_re_stake)

    def stk_un_stake_me(self):
        INFO('Un-stake me')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, self.payment_key, self.validator_key)

    def stk_un_stake_tx(self):
        INFO('Un-stake transaction')
        return self.REQ_HANDLER.transaction(). \
            create_and_send_un_staking_transaction(self.private_key, self.payment_key, self.validator_key)

    def stk_un_stake_him(self, him):
        INFO(f"Un-stake other: {him.validator_key}")
        return self.REQ_HANDLER.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, him.payment_key, him.validator_key)

    def stk_wait_till_i_am_committee(self, check_cycle=120, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        INFO(f"Wait until {self.validator_key} become a committee, check every {check_cycle}s, timeout: {timeout}s")
        while timeout > check_cycle:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            staked_shard = beacon_bsd.is_he_a_committee(self)
            if staked_shard is False:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.REQ_HANDLER.help_get_current_epoch()
                h = self.REQ_HANDLER.help_get_beacon_height_in_best_state_detail()
                INFO(f"Already a committee at epoch {e2}, block height {h}")
                return e2
        INFO(f"Waited {t}s but still not yet become committee")
        return None

    def stk_wait_till_i_am_swapped_out_of_committee(self, check_cycle=120, timeout=ChainConfig.STK_WAIT_TIME_OUT):
        t = timeout
        INFO(f"Wait until {self.validator_key} no longer a committee, check every {check_cycle}s, timeout: {timeout}s")
        while timeout > check_cycle:
            beacon_bsd = self.REQ_HANDLER.get_beacon_best_state_detail_info()
            if not (beacon_bsd.is_he_a_committee(self) is False):  # is_he_a_committee returns False or shard number
                # (number which is not False) so must use this comparision to cover the cases
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.REQ_HANDLER.help_get_current_epoch()
                INFO(f"Swapped out of committee at epoch {e2}")
                return e2
        INFO(f"Waited {t}s but still a committee")
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

    def get_token_balance_cache(self, token_id):
        try:
            return self.cache[f'{Account._cache_bal_tok}_{token_id}']
        except KeyError:
            return None

    def get_prv_balance(self):
        """
        get account's prv balance, by default it will ask the full node.
        when the shard_id is specify, then it will on that shard
        if shard if = -1, it will ask for the balance on it own shard

        :return:
        """

        # from privacy v2, must subscribe with private key to get balance, hence the code below
        get_bal_res = self.REQ_HANDLER.transaction().get_balance(self.private_key)
        while True:
            if get_bal_res.get_error_trace():
                error_msg = get_bal_res.get_error_trace().get_message()
                if 'Subscribed to OTA key to view all coins' in error_msg or \
                        "OTA Key indexing is in progress" in error_msg:
                    WARNING(f'{error_msg}. Wait for {ChainConfig.BLOCK_TIME}s and retry')
                    WAIT(ChainConfig.BLOCK_TIME)
                    get_bal_res = self.REQ_HANDLER.transaction().get_balance(self.private_key)
                else:
                    break
            else:
                break

        balance = get_bal_res.expect_no_error().get_result()
        INFO(f"Private k = {l6(self.private_key)}, prv bal = {coin(balance, False)}")
        self.cache['balance_prv'] = balance
        return balance

    def get_prv_balance_cache(self):
        try:
            return self.cache[Account._cache_bal_prv]
        except KeyError:
            return None

    def send_public_token(self, token_id, amount, receiver, password=None, memo=None):
        """

        :param token_id:
        :param amount:
        :param receiver: Account or remote address
        :param password:
        :param memo:
        :return:
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

        :param receiver_account:
        :param amount:
        :param fee: default = auto
        :param privacy: default = privacy on
        :return: Response object
        """
        INFO(f'From: {l6(self.private_key)}. Send {amount} prv to: {l6(receiver_account.payment_key)}')

        return self.REQ_HANDLER.transaction(). \
            send_transaction(self.private_key, {receiver_account.payment_key: amount}, fee, privacy)

    def send_prv_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1):
        """

        :param dict_to_account_and_amount: a dictionary of {receiver account : amount}
        :param fee:
        :param privacy:
        :return:
        """
        send_param = dict()
        INFO(f"{l6(self.private_key)} sending prv to multiple accounts: --------------------------------------------- ")
        for account, amount in dict_to_account_and_amount.items():
            INFO(f'{amount} prv to {account}')
            send_param[account.payment_key] = amount
        INFO("---------------------------------------------------------------------------------- ")

        return self.REQ_HANDLER.transaction(). \
            send_transaction(self.private_key, send_param, fee, privacy)

    def send_all_prv_to(self, to_account, privacy=1):
        """
        send all prv to another account

        :param to_account:
        :param privacy:
        :return:
        """

        INFO(f'Sending everything to {to_account}')
        # defrag account so that the custom fee = fee x 2 as below
        defrag = self.defragment_account()
        if defrag is not None:
            defrag.subscribe_transaction()
        balance = self.get_prv_balance()
        fee, size = self.get_estimate_fee_and_size(to_account, balance - 100, privacy=privacy)
        INFO(f'''EstimateFeeCoinPerKb = {fee}, EstimateTxSizeInKb = {size}''')
        if balance > 0:
            return self.send_prv_to(to_account, balance - 100, int(100 / (size + 1)),
                                    privacy).subscribe_transaction()

    def count_unspent_output_coins(self):
        """
        count number of unspent coin

        :return: int
        """
        INFO('Count unspent coin')

        response = self.REQ_HANDLER.transaction().list_unspent_output_coins(self.private_key).get_result(
            "Outputs")
        return len(response[self.private_key])

    def defragment_account(self, min_bill=1000000000000000):
        """
        check if account need to be defrag by count unspent coin,
            if count > 1 then defrag

        :return: Response object if need to defrag, None if not to
        """
        INFO('Defrag account')

        if self.count_unspent_output_coins() > 1:
            return self.REQ_HANDLER.transaction().de_fragment_prv(self.private_key, min_bill)
        INFO('No need to defrag!')
        return None

    def subscribe_cross_output_coin(self, timeout=120):
        INFO(f'{l6(self.private_key)} Subscribe cross output coin')
        return self.REQ_HANDLER.subscription().subscribe_cross_output_coin_by_private_key(
            self.private_key,
            timeout)

    def subscribe_cross_output_token(self, timeout=120):
        INFO(f'{l6(self.private_key)} Subscribe cross output token')
        return self.REQ_HANDLER.subscription().subscribe_cross_custom_token_privacy_by_private_key(
            self.private_key,
            timeout)

    def init_custom_token_self(self, token_symbol, amount):
        """
        Init custom token to self payment address

        :param token_symbol:
        :param amount
        :return:
        """
        INFO(f'Init custom token to self: {self.payment_key}')

        return self.REQ_HANDLER.transaction().init_custom_token(self.private_key, self.payment_key,
                                                                token_symbol,
                                                                amount)

    def init_custom_token_to(self, account, symbol, amount):
        """
        Init custom token to other account's payment address

        :param account:
        :param symbol:
        :param amount
        :return:
        """
        INFO(f'Init custom token to: {account.payment_key}')

        return self.REQ_HANDLER.transaction().init_custom_token(self.private_key, account.payment_key,
                                                                symbol,
                                                                amount)

    def pde_contribute(self, token_id, amount, pair_id):
        if token_id == PRV_ID:
            return self.pde_contribute_prv(amount, pair_id)
        else:
            return self.pde_contribute_token(token_id, amount, pair_id)

    def pde_contribute_v2(self, token_id, amount, pair_id):
        if token_id == PRV_ID:
            return self.pde_contribute_prv_v2(amount, pair_id)
        else:
            return self.pde_contribute_token_v2(token_id, amount, pair_id)

    def pde_contribute_token(self, contribute_token_id, amount, contribution_pair_id):
        INFO(f'{l6(self.private_key)} Contribute token: {l6(contribute_token_id)}, amount = {amount}, '
             f'pair id = {contribution_pair_id}')

        return self.REQ_HANDLER.dex().contribute_token(self.private_key, self.payment_key,
                                                       contribute_token_id,
                                                       amount, contribution_pair_id)

    def pde_contribute_token_v2(self, contribute_token_id, amount, contribution_pair_id):
        INFO(f'{l6(self.private_key)} Contribute token V2: {l6(contribute_token_id)}, amount = {amount}, '
             f'pair id = {contribution_pair_id}')

        return self.REQ_HANDLER.dex().contribute_token_v2(self.private_key, self.payment_key,
                                                          contribute_token_id,
                                                          amount, contribution_pair_id)

    def pde_contribute_prv(self, amount, contribution_pair_id):
        INFO(f'{l6(self.private_key)} Contribute PRV, amount: {amount}, pair id = {contribution_pair_id}')

        return self.REQ_HANDLER.dex().contribute_prv(self.private_key, self.payment_key, amount,
                                                     contribution_pair_id)

    def pde_contribute_prv_v2(self, amount, contribution_pair_id):
        INFO(f'{l6(self.private_key)} Contribute PRV V2, amount: {amount}, pair id = {contribution_pair_id}')

        return self.REQ_HANDLER.dex().contribute_prv_v2(self.private_key, self.payment_key, amount,
                                                        contribution_pair_id)

    def pde_withdraw_contribution(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE contribution {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution(self.private_key, self.payment_key,
                                                              token_id_1,
                                                              token_id_2, amount)

    def pde_withdraw_contribution_v2(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE contribution v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdrawal_contribution_v2(self.private_key, self.payment_key,
                                                                 token_id_1,
                                                                 token_id_2, amount)

    def pde_withdraw_reward_v2(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw PDE reward v2 {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.REQ_HANDLER.dex().withdraw_reward_v2(self.private_key, self.payment_key, token_id_1,
                                                         token_id_2, amount)

    def pde_contribute_pair_v2(self, rate_dict: dict):
        tokens = list(rate_dict.keys())
        token1 = tokens[0]
        token2 = tokens[1]
        pair_id = f'pde_{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
        tx1 = self.pde_contribute_v2(token1, tokens[token1], pair_id).expect_no_error().subscribe_transaction()
        tx2 = self.pde_contribute_v2(token2, tokens[token2], pair_id).expect_no_error().subscribe_transaction()
        return tx1, tx2

    def send_token_to(self, receiver, token_id, amount_custom_token,
                      prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0):
        """
        Send token to receiver (custom token only, not prv)

        :param prv_privacy:
        :param prv_amount:
        :param receiver: Account
        :param token_id:
        :param amount_custom_token:
        :param prv_fee:
        :param token_fee:
        :param token_privacy:
        :return: Response object
        """
        INFO(f'Sending {amount_custom_token} token {l6(token_id)} to {l6(receiver.payment_key)}')

        return self.REQ_HANDLER.transaction().send_custom_token_transaction(self.private_key,
                                                                            receiver.payment_key,
                                                                            token_id, amount_custom_token,
                                                                            prv_fee,
                                                                            token_fee, prv_amount,
                                                                            prv_privacy,
                                                                            token_privacy)

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
        return self.REQ_HANDLER.transaction().send_custom_token_multi_output(self.private_key,
                                                                             payment_key_amount_dict,
                                                                             token_id,
                                                                             prv_fee, token_fee,
                                                                             prv_privacy, token_privacy)

    def burn_token(self, token_id, amount_custom_token):
        """
        Burning token (this mean send token to burning address)

        :param token_id: Token ID
        :param amount_custom_token: amount to burn
        :return: Response object
        """
        INFO(f'Send custom token transaction to burning address')
        return self.REQ_HANDLER.transaction().send_custom_token_transaction(self.private_key,
                                                                            Constants.BURNING_ADDR,
                                                                            token_id,
                                                                            amount_custom_token,
                                                                            prv_fee=-1,
                                                                            token_fee=0, prv_amount=0,
                                                                            prv_privacy=0,
                                                                            token_privacy=0)

    ########
    # BRIDGE
    ########
    def issue_centralize_token(self, token_id, token_name, amount):
        """
            initialize a new centralize token

            :return: Response Object

        """
        return self.REQ_HANDLER.bridge().issue_centralized_bridge_token(self.payment_key, token_id,
                                                                        token_name, amount)

    def withdraw_centralize_token(self, token_id, amount_custom_token):
        """
        Withdraw token (this mean send token to burning address, but receive your token on ETH network)
        INFO(f'Send custom token transaction')
        return Account.SYSTEM.transaction().send_custom_token_transaction(self.private_key,
                                                                                Constants.burning_address,
                                                                                token_id, amount_custom_token,
                                                                                prv_fee=-1,
                                                                                token_fee=0, prv_amount=0,
                                                                                prv_privacy=0,
                                                                                token_privacy=0)

        :param token_id: Token ID
        :param amount_custom_token: amount to withdraw
        :return: Response object
        """
        INFO(f'Withdraw centralize token')
        return self.REQ_HANDLER.transaction().withdraw_centralize_token(self.private_key, token_id,
                                                                        amount_custom_token)

    ########
    # Stake
    ########

    def stk_get_reward_amount(self, token_id=PRV_ID):
        """
        @return: reward amount of token
        """
        result = self.REQ_HANDLER.transaction().get_reward_amount(self.payment_key)
        try:
            if token_id == PRV_ID:
                reward = result.get_result("PRV")
            else:
                reward = result.get_result(token_id)
            reward = 0 if reward is None else reward
            return reward
        except KeyError:
            return 0

    def stk_get_reward_amount_all_token(self):
        """

        :return:
        """
        try:
            return self.REQ_HANDLER.transaction().get_reward_amount(self.payment_key).get_result()
        except KeyError:
            return None

    def stk_withdraw_reward_to(self, reward_receiver, token_id=PRV_ID):
        INFO(f"Withdraw token reward {token_id} to {l6(reward_receiver.payment_key)}")
        if ChainConfig.PRIVACY_VERSION == 1:
            return self.REQ_HANDLER.transaction().withdraw_reward(self.private_key, reward_receiver.payment_key,
                                                                  token_id)
        if ChainConfig.PRIVACY_VERSION == 2:
            return self.REQ_HANDLER.transaction().withdraw_reward_privacy_v2(self.private_key,
                                                                             reward_receiver.payment_key, token_id)
        raise BaseException('Can not detect privacy version to use the correct withdraw rpc')

    def stk_withdraw_reward_to_me(self, token_id=PRV_ID):
        return self.stk_withdraw_reward_to(self, token_id)

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
                                                  sell_amount,
                                                  token_id_to_buy, min_amount_to_buy, trading_fee)

    def pde_trade_prv(self, amount_to_sell, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} of PRV for {token_id_to_buy[-6:]}')
        return self.REQ_HANDLER.dex().trade_prv(self.private_key, self.payment_key, amount_to_sell,
                                                token_id_to_buy,
                                                min_amount_to_buy, trading_fee)

    def pde_trade(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        if token_id_to_sell == PRV_ID:
            return self.pde_trade_prv(sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)
        else:
            return self.pde_trade_token(token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee)

    def pde_trade_prv_v2(self, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} of PRV for {l6(token_to_buy)} trading fee={trading_fee}')
        return self.REQ_HANDLER.dex().trade_prv_v2(self.private_key, self.payment_key, amount_to_sell,
                                                   token_to_buy, trading_fee, min_amount_to_buy)

    def pde_trade_token_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        INFO(f'User {l6(self.payment_key)}: '
             f'Trade {amount_to_sell} of token {token_to_sell[-6:]} for {token_to_buy[-6:]} trading fee={trading_fee}')
        return self.REQ_HANDLER.dex().trade_token_v2(self.private_key, self.payment_key, token_to_sell,
                                                     amount_to_sell,
                                                     token_to_buy, trading_fee, min_amount_to_buy)

    def pde_trade_v2(self, token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy=1):
        if token_to_sell == PRV_ID:
            return self.pde_trade_prv_v2(amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)
        else:
            return self.pde_trade_token_v2(token_to_sell, amount_to_sell, token_to_buy, trading_fee, min_amount_to_buy)

    def wait_for_balance_change(self, token_id=PRV_ID, from_balance=None, least_change_amount=1, check_interval=10,
                                timeout=100):
        """

        :param token_id:
        :param from_balance:
        :param least_change_amount: change at least this amount of token
        :param check_interval:
        :param timeout:
        :return: new balance
        """
        INFO(f'Wait for token {l6(token_id)} of {l6(self.private_key)} '
             f'balance to change at least: {least_change_amount}. From {from_balance}')
        if from_balance is None:
            from_balance = self.get_token_balance(token_id)
            WAIT(check_interval)
            timeout -= check_interval
        bal_new = None
        while timeout >= 0:
            bal_new = self.get_token_balance(token_id)
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

        :param psi: PortalStateInfo
        :return: Response if current total collateral > 0, None if = 0
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

        :param porting_id:
        :param token_id:
        :param amount:
        :param proof:
        :return:
        """
        INFO()
        INFO(f'Portal | User {l6(self.payment_key)} | req for ported token')
        return self.REQ_HANDLER.portal().create_n_send_tx_with_req_ptoken(self.private_key,
                                                                          self.payment_key,
                                                                          porting_id, token_id, amount,
                                                                          proof)

    def portal_get_my_custodian_info(self, psi: PortalStateInfo = None):
        """

        :param psi: PortalStateInfo
        :return CustodianInfo or None:
        """
        if psi is None:
            psi = self.REQ_HANDLER.get_latest_portal_state_info()
        return psi.get_custodian_info_in_pool(self)

    def portal_get_my_custodian_info_cache(self):
        return self.cache[Account._cache_custodian_inf]

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

    def convert_prv_to_v2(self):
        return self.REQ_HANDLER.transaction().create_convert_coin_ver1_to_ver2_transaction(
            self.private_key)

    def convert_token_to_v2(self, token_id):
        return self.REQ_HANDLER.transaction().create_convert_coin_ver1_to_ver2_tx_token(self.private_key,
                                                                                        token_id)

    def top_him_up_token_to_amount_if(self, token_id, if_lower_than, top_up_to_amount, accounts_list):
        """

        :param token_id:
        :param if_lower_than: top up if current balance is equal or lower this number
        :param top_up_to_amount:
        :param accounts_list: Account or list of Account
        :return:
        """
        INFO_HEADLINE(f"TOP UP OTHERS' TOKEN {l6(token_id)} TO {top_up_to_amount}")

        if type(accounts_list) is Account:
            accounts_list = [accounts_list]
        receiver = {}
        threads_bal_b4 = {}
        with ThreadPoolExecutor() as exc:
            for acc in accounts_list:
                thread = exc.submit(acc.get_token_balance, token_id)
                threads_bal_b4[acc] = thread

        for acc, thread in threads_bal_b4.items():
            bal = thread.result()
            if bal <= if_lower_than:
                top_up_amount = top_up_to_amount - bal
                if top_up_amount > 0:
                    receiver[acc] = top_up_amount
        if len(receiver) == 0:
            return None

        send_tx = self.send_token_multi_output(receiver, token_id, prv_fee=-1)
        send_tx.expect_no_error()
        send_tx.subscribe_transaction()

        with ThreadPoolExecutor() as executor:
            for acc in receiver.keys():
                executor.submit(acc.wait_for_balance_change, token_id, from_balance=threads_bal_b4[acc].result())

        return send_tx

    def top_him_up_prv_to_amount_if(self, if_lower_than, top_up_to_amount, accounts_list):
        """

        :param if_lower_than: top up if current balance is equal or lower this number
        :param top_up_to_amount:
        :param accounts_list: Account or list of Account
        :return:
        """
        # breakpoint()
        INFO_HEADLINE(f"TOP UP OTHERS' PRV TO {top_up_to_amount}")
        if type(accounts_list) is Account:
            accounts_list = [accounts_list]
        receiver = {}
        threads = {}
        with ThreadPoolExecutor() as exc:
            for acc in accounts_list:
                thread = exc.submit(acc.get_prv_balance)
                threads[acc] = thread

        for acc, thread in threads.items():
            bal = thread.result()
            if bal <= if_lower_than:
                top_up_amount = top_up_to_amount - bal
                if top_up_amount > 0:
                    receiver[acc] = top_up_amount
        if len(receiver) == 0:
            return None

        # there's a max number of output in "createandsendtransaction" rpc, so must split into small batch of output
        each, length, start = 20, len(receiver), 0
        mid = each
        keys = list(receiver.keys())
        while start < length:
            sub_keys = keys[start:mid]
            sub_receivers = {k: receiver[k] for k in sub_keys}
            send_tx = self.send_prv_to_multi_account(sub_receivers)
            send_tx.expect_no_error()
            send_tx.subscribe_transaction()
            start = mid
            mid += each

        # thread_pool = []
        for acc, amount in receiver.items():
            acc.wait_for_balance_change(from_balance=acc.get_prv_balance_cache())

    def submit_key(self):
        self.REQ_HANDLER.transaction().submit_key(self.private_key).expect_no_error()
        WAIT(ChainConfig.BLOCK_TIME)
        return self


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

    def __deepcopy__(self, memodict={}):
        copy_acc_group = AccountGroup()
        copy_acc_group.account_list = copy.deepcopy(self.account_list)
        return copy_acc_group

    def remove(self, obj):
        self.account_list.remove(obj)

    def append(self, acc_obj):
        self.account_list.append(acc_obj)

    def get_accounts_in_shard(self, shard_number: int):
        """
        iterate through accounts in account_list, check if they're in the same shard_number

        :param shard_number: shard id to check
        :return: list of Account which is in the same shard_number
        """
        INFO(f'Find all accounts in shard {shard_number}')
        accounts_in_shard: List[Account] = []
        for account in self.account_list:
            if account.shard == shard_number:
                accounts_in_shard.append(account)

        return AccountGroup(*accounts_in_shard)

    def find_account_by_public_k(self, key):
        for acc in self.account_list:
            if acc.public_key == key:
                return acc

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

    def change_req_handler(self, HANDLER):
        for acc in self:
            acc.req_to(HANDLER)

    def find_the_richest(self, token_id=PRV_ID):
        the_richest = self[0]
        for acc in self[1:]:
            if acc.get_token_balance(token_id) > the_richest.get_token_balance(token_id):
                the_richest = acc
        return the_richest


def get_accounts_in_shard(shard_number: int, account_list=None):
    """ @deprecated
    iterate through accounts in account_list, check if they're in the same shard_number

    :param shard_number: shard id to check
    :param account_list: account list to check, by default it's TestData
    :return: list of Account which is in the same shard_number
    """
    if account_list is None:
        from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
        account_list = ACCOUNTS
    if type(account_list) is AccountGroup:
        return account_list.get_accounts_in_shard(shard_number)
    else:
        return AccountGroup(*account_list).get_accounts_in_shard(shard_number)


PORTAL_FEEDER = Account(ChainConfig.Portal.FEEDER_PRIVATE_K)
COIN_MASTER = Account(DAO_PRIVATE_K)
