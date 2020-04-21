import copy
import re
from typing import List

from IncognitoChain.Configs import Constants
from IncognitoChain.Configs.Constants import prv_token_id
from IncognitoChain.Helpers.Logging import INFO, WARNING
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT


class Account:

    def __init__(self, private_key=None, payment_key=None, shard=None,
                 validator_key=None, public_key=None, read_only_key=None):
        self.private_key = private_key
        self.validator_key = validator_key
        self.payment_key = payment_key
        self.public_key = public_key
        self.read_only_key = read_only_key
        self.shard = shard
        self.cache = {}
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.__SUT = SUT

    def __copy__(self):
        copy_obj = Account(self.private_key,
                           self.payment_key,
                           self.shard,
                           self.validator_key,
                           self.public_key,
                           self.read_only_key)
        copy_obj.cache = self.cache
        return copy_obj

    def __deepcopy__(self, memo={}):
        copy_obj = Account(copy.deepcopy(self.private_key),
                           copy.deepcopy(self.payment_key),
                           copy.deepcopy(self.shard),
                           copy.deepcopy(self.validator_key),
                           copy.deepcopy(self.public_key),
                           copy.deepcopy(self.read_only_key))

        copy_obj.prv_balance_cache = copy.deepcopy(self.cache)
        return copy_obj

    def __eq__(self, other):
        if self.private_key == other.private_key:
            return True
        return False

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        return True

    def __hash__(self):
        # for using Account object as 'key' in dictionary
        return int(str(self.private_key).encode('utf8').hex(), 16)

    def calculate_shard_id(self):
        if self.payment_key is None:
            self.find_payment_key()
        if self.public_key is None:
            self.find_public_key()
        response = self.__SUT.full_node.transaction().get_public_key_by_payment_key(self.payment_key)
        last_byte = response.get_result("PublicKeyInBytes")[-1]
        self.shard = last_byte % 8
        return self.shard

    def from_json(self, json_string):
        self.public_key = json_string.get('public')
        self.private_key = json_string.get('private')
        self.payment_key = json_string.get('payment')
        self.read_only_key = json_string.get('read')
        self.validator_key = json_string.get('validator')
        self.shard = json_string.get('shard')
        return self

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

    def _where_am_i(self, a_list: list):
        """
        find index of self in a_list of account

        :param a_list:
        :return: if self is in a_list then return index of self in the list or else return -1
        """
        for account in a_list:
            if self.__eq__(account):
                return a_list.index(account)
        return -1

    def find_payment_key(self, force=False):
        """
        find payment address from private key

        :return:
        """
        if not force:
            if self.payment_key is not None:
                return self.payment_key

        tx = self.__SUT.full_node.transaction().list_custom_token_balance(self.private_key)
        self.payment_key = tx.get_result('PaymentAddress')
        return self.payment_key

    def find_public_key(self, force=False):
        """

        :return:
        """
        if not force:
            if self.public_key is not None:
                return self.public_key

        tx = self.__SUT.full_node.transaction().get_public_key_by_payment_key(self.payment_key)
        self.public_key = tx.get_result('PublicKeyInBase58Check')
        return self.public_key

    def get_token_balance(self, token_id, shard_id=None):
        """
        get balance by token_id

        :param token_id:
        :param shard_id: when = None, will ask full_node. When = -1, ask on its own shard, or else will ask on shard_id
        :return:
        """

        if shard_id is None:
            where_to_ask = self.__SUT.full_node.transaction()
        elif shard_id == -1:
            where_to_ask = self.__SUT.shards[self.shard].get_representative_node().transaction()
        else:
            where_to_ask = self.__SUT.shards[shard_id].get_representative_node().transaction()
        balance = where_to_ask.get_custom_token_balance(self.private_key, token_id).get_result()

        self.cache[f'balance_token_{token_id}'] = balance
        INFO(f"Token Bal = {balance}, private key = {l6(self.private_key)}, token id = {l6(token_id)}")
        return balance

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

        return self.__SUT.full_node.transaction(). \
            create_and_send_staking_transaction(self.private_key, self.payment_key, self.validator_key,
                                                self.payment_key, stake_amount, auto_re_stake)

    def stake_someone_reward_me(self, someone, stake_amount=None):
        """

        :return:
        """
        INFO(f'Stake {someone.validator_key} but reward me')
        return self.__SUT.full_node.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                self.payment_key, stake_amount)

    def stake_someone_reward_him(self, someone, stake_amount=None, auto_re_stake=True):
        """

        :return:
        """
        INFO(f'Stake and reward other: f{someone.validator_key}')
        return self.__SUT.full_node.transaction(). \
            create_and_send_staking_transaction(self.private_key, someone.payment_key, someone.validator_key,
                                                someone.payment_key, stake_amount, auto_re_stake)

    def un_stake_me(self):
        INFO('Un-stake me')
        return self.__SUT.full_node.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, self.payment_key, self.validator_key)

    def un_stake_him(self, him):
        INFO(f"Un-stake other: {him.validator_key}")
        return self.__SUT.full_node.transaction(). \
            create_and_send_stop_auto_staking_transaction(self.private_key, him.payment_key, him.validator_key)

    def wait_till_i_am_committee(self, check_cycle=120, timeout=1000):
        t = timeout
        INFO(f"Wait until {self.validator_key} become a committee, check every {check_cycle}s, timeout: {timeout}s")
        while timeout > check_cycle:
            if self.am_i_a_committee() is False:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.__SUT.full_node.system_rpc().help_get_current_epoch()
                h = self.__SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=False)
                INFO(f"Promoted to committee at epoch {e2}, block height {h}")
                return e2
        INFO(f"Waited {t}s but still not yet become committee")
        return None

    def wait_till_i_am_swapped_out_of_committee(self, check_cycle=120, timeout=1000):
        t = timeout
        INFO(f"Wait until {self.validator_key} no longer a committee, check every {check_cycle}s, timeout: {timeout}s")
        while timeout > check_cycle:
            if not (self.am_i_a_committee() is False):  # am_i_a_committee returns False or shard number
                # (number which is not False) so must use this comparision to cover the cases
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.__SUT.full_node.system_rpc().help_get_current_epoch()
                INFO(f"Swapped out of committee at epoch {e2}")
                return e2
        INFO(f"Waited {t}s but still a committee")
        return None

    def wait_till_i_have_reward(self, token_id=None, check_cycle=120, timeout=1000):
        t = timeout
        if token_id is None:
            token_id = 'PRV'
        INFO(f'Wait until {self.validator_key} has reward: {token_id}, check every {check_cycle}s, timeout: {timeout}s')
        while timeout > check_cycle:
            reward = self.get_reward_amount(token_id)
            if reward is None:
                WAIT(check_cycle)
                timeout -= check_cycle
            else:
                e2 = self.__SUT.full_node.system_rpc().help_get_current_epoch()
                INFO(f"Rewarded {reward} : {token_id} at epoch {e2}")
                return reward
        INFO(f"Waited {t}s but still has no reward")
        return None

    def get_token_balance_cache(self, token_id):
        try:
            return self.cache[f'balance_token_{token_id}']
        except KeyError:
            return None

    def get_prv_balance(self, shard_id=None):
        """
        get account's prv balance, by default it will ask the full node.
        when the shard_id is specify, then it will on that shard
        if shard if = -1, it will ask for the balance on it own shard

        :param shard_id:
        :return:
        """
        if shard_id is None:
            balance = self.__SUT.full_node.transaction().get_balance(self.private_key).get_balance()
        else:
            if shard_id == -1:
                shard_to_ask = self.shard
            else:
                shard_to_ask = shard_id
            balance = self.__SUT.shards[shard_to_ask].get_representative_node().transaction().get_balance(
                self.private_key).get_balance()
        INFO(f"Prv bal = {balance}, private key = {l6(self.private_key)}")
        self.cache['balance_prv'] = balance
        return balance

    def get_prv_balance_cache(self):
        return self.cache['balance_prv']

    def send_prv_to(self, receiver_account, amount, fee=-1, privacy=1, shard_id=-1):
        """
        send amount_prv of prv to to_account. by default fee=-1 and privacy=1

        :param shard_id: if = -1 then fullnode will handle the transaction.
         otherwise shard with id = {shard_id} will handle the request
        :param receiver_account:
        :param amount:
        :param fee: default = auto
        :param privacy: default = privacy on
        :return: Response object
        """
        INFO(f'''
                From: {self.private_key}
                Send {amount} prv 
                To: {receiver_account.payment_key}''')

        return self.__SUT.get_request_handler(shard_id).transaction(). \
            send_transaction(self.private_key, {receiver_account.payment_key: amount}, fee, privacy)

    def send_prv_to_multi_account(self, dict_to_account_and_amount: dict, fee=-1, privacy=1):
        """

        :param dict_to_account_and_amount: a dictionary of {receiver account : amount}
        :param fee:
        :param privacy:
        :return:
        """
        send_param = dict()
        INFO("Sending prv to multiple accounts: ------------------------------------------------ ")
        for account, amount in dict_to_account_and_amount.items():
            INFO(f'{amount} prv to {account}')
            send_param[account.payment_key] = amount
        INFO("---------------------------------------------------------------------------------- ")

        return self.__SUT.full_node.transaction(). \
            send_transaction(self.private_key, send_param, fee, privacy)

    def send_all_prv_to(self, to_account, privacy=0):
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
        if balance > 0:
            return self.send_prv_to(to_account, balance - 200, 100, privacy).subscribe_transaction()

    def count_unspent_output_coins(self):
        """
        count number of unspent coin

        :return: int
        """
        INFO('Count unspent coin')

        response = self.__SUT.full_node.transaction().list_unspent_output_coins(self.private_key).get_result("Outputs")
        return len(response[self.private_key])

    def defragment_account(self):
        """
        check if account need to be defrag by count unspent coin,
            if count > 1 then defrag

        :return: Response object if need to defrag, None if not to
        """
        INFO('Defrag account')

        if self.count_unspent_output_coins() > 1:
            return self.__SUT.full_node.transaction().defragment_account(self.private_key)
        INFO('No need to defrag!')
        return None

    def subscribe_cross_output_coin(self, timeout=180):
        INFO('Subscribe output coin')
        return self.__SUT.full_node.subscription().subscribe_cross_output_coin_by_private_key(self.private_key, timeout)

    def subscribe_cross_output_token(self, timeout=180):
        INFO('Subscribe cross output token')
        return self.__SUT.full_node.subscription().subscribe_cross_custom_token_privacy_by_private_key(self.private_key,
                                                                                                       timeout)

    def init_custom_token_self(self, token_symbol, amount):
        """
        Init custom token to self payment address

        :param token_symbol:
        :param amount
        :return:
        """
        INFO(f'Init custom token to self: {self.payment_key}')

        return self.__SUT.full_node.transaction().init_custom_token(self.private_key, self.payment_key, token_symbol,
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

        return self.__SUT.full_node.transaction().init_custom_token(self.private_key, account.payment_key, symbol,
                                                                    amount)

    def contribute_token(self, contribute_token_id, amount, contribution_pair_id):
        INFO(f'Contribute token: {contribute_token_id[-6:]}, amount = {amount}, pair id = {contribution_pair_id}')

        return self.__SUT.full_node.dex().contribute_token(self.private_key, self.payment_key, contribute_token_id,
                                                           amount,
                                                           contribution_pair_id)

    def contribute_prv(self, amount, contribution_pair_id):
        INFO(f'Contribute PRV, amount: {amount}, pair id = {contribution_pair_id}')

        return self.__SUT.full_node.dex().contribute_prv(self.private_key, self.payment_key, amount,
                                                         contribution_pair_id)

    def withdraw_contribution(self, token_id_1, token_id_2, amount):
        INFO(f'Withdraw contribution {l6(token_id_1)}-{l6(token_id_2)}, amount = {amount}')
        return self.__SUT.full_node.dex().withdrawal_contribution(self.private_key, self.payment_key, token_id_1,
                                                                  token_id_2, amount)

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

        return self.__SUT.full_node.transaction().send_custom_token_transaction(self.private_key, receiver.payment_key,
                                                                                token_id, amount_custom_token, prv_fee,
                                                                                token_fee, prv_amount, prv_privacy,
                                                                                token_privacy)

    def send_token_multi_output(self, receiver_token_amount_dict, token_id, prv_fee=0, token_fee=0, prv_privacy=0,
                                token_privacy=0):
        INFO(f'Sending token multi output')
        payment_key_amount_dict = {}
        for acc in receiver_token_amount_dict.keys():
            payment_key_amount_dict[acc.payment_key] = receiver_token_amount_dict[acc]
        return self.__SUT.full_node.transaction().send_custom_token_multi_output(self.private_key,
                                                                                 payment_key_amount_dict, token_id,
                                                                                 prv_fee, token_fee,
                                                                                 prv_privacy, token_privacy)

    def am_i_a_committee(self, refresh_cache=True):
        """

        :return: shard id of which this account is a committee, if not a committee in any shard, return False
        """
        best = self.__SUT.full_node.system_rpc().get_beacon_best_state_detail(refresh_cache=refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        shard_id = 0
        for i in range(0, len(shard_committee_list)):
            committees_in_shard = shard_committee_list[f'{i}']
            for committee in committees_in_shard:
                if self.public_key is None:
                    self.find_public_key()

                if committee['IncPubKey'] == self.public_key:
                    INFO(f"You {self.validator_key} are a committee in shard {shard_id}")
                    return shard_id
            shard_id += 1
        INFO(f"{self.validator_key} is NOT a committee")
        return False

    def am_i_stake(self):
        pass

    def burn_token(self, token_id, amount_custom_token):
        """
        Burning token (this mean send token to burning address)

        :param token_id: Token ID
        :param amount_custom_token: amount to burn
        :return: Response object
        """
        INFO(f'Send custom token transaction to burning address')
        return self.__SUT.full_node.transaction().send_custom_token_transaction(self.private_key,
                                                                                Constants.burning_address, token_id,
                                                                                amount_custom_token, prv_fee=-1,
                                                                                token_fee=0, prv_amount=0,
                                                                                prv_privacy=0, token_privacy=0)

    ########
    # BRIDGE
    ########
    def withdraw_centralize_token(self, token_id, amount_custom_token):
        """
        Withdraw token (this mean send token to burning address, but receive your token on ETH network)
        INFO(f'Send custom token transaction')
        return self.__SUT.full_node.transaction().send_custom_token_transaction(self.private_key,
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
        return self.__SUT.full_node.transaction().withdraw_centralize_token(self.private_key, token_id,
                                                                            amount_custom_token)

    ########
    # Stake
    ########

    def get_reward_amount(self, token_id=None):
        """
        when @token_id is None, return PRV reward amount
        :return:
        """
        result = self.__SUT.full_node.transaction().get_reward_amount(self.payment_key)
        try:
            if token_id is None:
                return result.get_result("PRV")
            else:
                return result.get_result(token_id)
        except KeyError:
            return None

    def get_reward_amount_all_token(self):
        """

        :return:
        """
        try:
            return self.__SUT.full_node.transaction().get_reward_amount(self.payment_key).get_result()
        except KeyError:
            return None

    def withdraw_reward_to(self, reward_receiver, token_id=None):
        INFO(f"""Withdraw token reward {token_id}
            to {reward_receiver.payment_key}""")
        return self.__SUT.full_node.transaction().withdraw_reward(self.private_key, reward_receiver.payment_key,
                                                                  token_id)

    def withdraw_reward_to_me(self, token_id=None):
        return self.withdraw_reward_to(self, token_id)

    #######
    # DEX
    #######
    def is_my_token_waiting_for_contribution(self, token_id):
        INFO(f"Check if {token_id[-6:]} init by {self.payment_key[-6:]} is waiting for contribution ")
        pde_state = self.__SUT.full_node.help_get_current_pde_status()
        waiting_contribution_list = str(pde_state.get_result()['WaitingPDEContributions']).split(
            'waitingpdecontribution')

        for contribution in waiting_contribution_list:
            if re.search(token_id, str(contribution)):
                if re.search(self.payment_key, str(contribution)):
                    INFO(f'{token_id[-6:]} was init by {self.payment_key[-6:]} and waiting for contribution')
                    return True
        WARNING("payment address and token id NOT found")
        return False

    def wait_till_my_token_in_waiting_for_contribution(self, token_id, timeout=100):
        INFO(f"Wait until token {token_id[-6:]} is in waiting for contribution")
        result = self.is_my_token_waiting_for_contribution(token_id)
        while timeout >= 0:
            if result:
                INFO(f'Token {token_id[-6:]} is found in contribution waiting list')
                return result
            timeout -= 10
            WAIT(10)
            result = self.is_my_token_waiting_for_contribution(token_id)
        INFO(f'Token {token_id[-6:]} is NOT found in contribution waiting list')
        return result

    def wait_till_my_token_out_waiting_for_contribution(self, token_id, timeout=100):
        INFO(f"Wait until token {token_id[-6:]} is OUT of waiting for contribution")
        result = self.is_my_token_waiting_for_contribution(token_id)
        while timeout >= 0:
            if not result:
                INFO(f'Token {token_id[-6:]} is NOT found in contribution waiting list')
                return result
            timeout -= 10
            WAIT(10)
            result = self.is_my_token_waiting_for_contribution(token_id)
        INFO(f'Token {token_id[-6:]} is found in contribution waiting list')
        return result

    def wait_for_balance_change(self, token_id=prv_token_id, current_balance=None, change_amount=None, pool_time=10,
                                timeout=100):
        INFO(f'Wait for token: {token_id[-6:]} balance to change, amount: {change_amount}')
        if current_balance is None:
            current_balance = self.get_token_balance(token_id)
            WAIT(pool_time)
            timeout -= pool_time

        while timeout >= 0:
            bal_2 = self.get_token_balance(token_id)
            if change_amount is None:
                if bal_2 != current_balance:
                    INFO(f'Balance is changed: {bal_2 - current_balance}')
                    return bal_2
            else:
                if bal_2 == current_balance + change_amount:
                    INFO(f'Balance changes with {change_amount}')
                    return bal_2
            WAIT(pool_time)
            timeout -= pool_time
        INFO('Balance not change a bit')
        return bal_2

    def trade_token(self, token_id_to_sell, sell_amount, token_id_to_buy, min_amount_to_buy, trading_fee=0):
        INFO(f'Trade {sell_amount} of token {token_id_to_sell[-6:]} for {token_id_to_buy[-6:]}')
        return self.__SUT.full_node.dex().trade_token(self.private_key, self.payment_key, token_id_to_sell, sell_amount,
                                                      token_id_to_buy, min_amount_to_buy, trading_fee)

    def trade_prv(self, amount_to_sell, token_id_to_buy, min_amount_to_buy):
        INFO(f'Trade {amount_to_sell} of PRV for {token_id_to_buy[-6:]}')
        return self.__SUT.full_node.dex().trade_prv(self.private_key, self.payment_key, amount_to_sell, token_id_to_buy,
                                                    min_amount_to_buy)

    def get_my_current_pde_share(self, token_id_1, token_id_2):
        """

        :param token_id_1: token id to get share part
        :param token_id_2:
        :return: list of token 1 share
        """
        INFO(f"Get PDE share of me: payment key: {l6(token_id_1)}")
        pde_status = self.__SUT.full_node.help_get_current_pde_status()
        beacon_height = pde_status.params().get_beacon_height()
        INFO(f"Checking pdeshare {l6(token_id_2)}-{l6(token_id_1)} or {l6(token_id_1)}-{l6(token_id_2)}")
        share_key_1_2 = f'pdeshare-{beacon_height}-{token_id_2}-{token_id_1}-{self.payment_key}'
        share_key_2_1 = f'pdeshare-{beacon_height}-{token_id_1}-{token_id_2}-{self.payment_key}'
        share_response = pde_status.get_pde_share()
        try:
            INFO(f'Finding pdeshare-{beacon_height}-{l6(token_id_1)}-{l6(token_id_2)}-{l6(self.payment_key)}')
            return share_response[share_key_1_2]
        except KeyError:
            INFO('Not found')
        try:
            INFO(f'Finding pdeshare-{beacon_height}-{l6(token_id_2)}-{l6(token_id_1)}-{l6(self.payment_key)}')
            return share_response[share_key_2_1]
        except KeyError:
            INFO('Not found')
        return None


def get_accounts_in_shard(shard_number: int, account_list=None) -> List[Account]:
    """
    iterate through accounts in account_list, check if they're in the same shard_number

    :param shard_number: shard id to check
    :param account_list: account list to check, by default it's TestData
    :return: list of Account which is in the same shard_number
    """
    if account_list is None:
        from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
        account_list = ACCOUNTS
    INFO(f'Find all accounts in shard {shard_number}')
    accounts_in_shard: List[Account] = []
    for account in account_list:
        if account.shard == shard_number:
            accounts_in_shard.append(account)
    return accounts_in_shard


def find_0_balance_accounts(token_id=None, account_list=None) -> List[Account]:
    """
    find all account in account_list which prv balance = 0

    :param token_id:
    :param account_list: Default is TestData
    :return:  Account list
    """
    if account_list is None:
        from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
        account_list = ACCOUNTS

    zero_balance_list: List[Account] = []
    INFO(f'Find all account which balance = 0, Token id = {token_id}')
    for account in account_list:
        if token_id is None:
            balance = account.get_prv_balance()
        else:
            balance = account.get_token_balance(token_id).get_result()

        if balance == 0:
            zero_balance_list.append(account)

    return zero_balance_list


def find_same_shard_accounts_with(account: Account, account_list=None):
    """
    find all accounts which is in the same shard with param:account bellow

    :param account:
    :param account_list:
    :return: Account list
    """
    if account_list is None:
        from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
        account_list = ACCOUNTS

    same_shard_list: List[Account] = []
    INFO(f"Find all accounts which is in the same shard with input account: {account}")
    for account_in_list in account_list:
        if account_in_list is not account:
            if account_in_list.shard == account.shard:
                same_shard_list.append(account_in_list)
    return same_shard_list
