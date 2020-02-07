from typing import List

from IncognitoChain.Helpers.Logging import INFO


class Account:

    def __init__(self, private_key=None, payment_key=None, shard=None,
                 validator_key=None, public_key=None, read_only_key=None):
        self.private_key = private_key
        self.validator_key = validator_key
        self.payment_key = payment_key
        self.public_key = public_key
        self.read_only_key = read_only_key
        self.shard = shard

    def __eq__(self, other):
        if self.private_key == other.private_key:
            return True
        return False

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        return True

    def from_json(self, json_string):
        self.public_key = json_string.get('public')
        self.private_key = json_string.get('private')
        self.payment_key = json_string.get('payment')
        self.read_only_key = json_string.get('read')
        self.validator_key = json_string.get('validator')
        self.shard = json_string.get('shard')
        return self

    def __str__(self):
        return f'Shard = {self.shard}\n' + \
               f'Private key = {self.private_key}\n' + \
               f'Payment key = {self.payment_key}\n' + \
               f'Read only key = {self.read_only_key}\n' + \
               f'Validator key = {self.validator_key}\n' + \
               f'Public key = {self.public_key}\n'

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

    def get_token_balance(self, token_id, shard_id=None):
        """
        get balance by token_id
        :param token_id:
        :param shard_id: default = None, if not specified, will ask full_node. or else, will ask on shard_id
        :return:
        """
        INFO(f'Get token balance, token id = {token_id}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        if shard_id is None:
            return SUT.full_node.transaction().get_custom_token_balance(self.private_key, token_id)
        if shard_id is None:
            shard_to_ask = self.shard
        else:
            shard_to_ask = shard_id
        return SUT.shards[shard_to_ask].get_representative_node().transaction().get_custom_token_balance(
            self.private_key, token_id)

    def get_prv_balance(self, shard_id=None):
        """
        get account's prv balance, by default it will ask the full node.
        when the shard_id is specify, then it will on that shard
        if shard if = -1, it will ask for the balance on it own shard
        :param shard_id:
        :return:
        """
        INFO("Get prv balance")
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        if shard_id is None:
            balance = SUT.full_node.transaction().get_balance(self.private_key).get_balance()
        else:
            if shard_id == -1:
                shard_to_ask = self.shard
            else:
                shard_to_ask = shard_id
            balance = SUT.shards[shard_to_ask].get_representative_node().transaction().get_balance(
                self.private_key).get_balance()
        INFO(f"Balance = {balance}")
        return balance

    def send_prv_to(self, receiver_account, amount, fee=-1, privacy=1):
        """
        send amount_prv of prv to to_account. by default fee=-1 and privacy=1
        :param receiver_account:
        :param amount:
        :param fee:
        :param privacy:
        :return:
        """
        INFO(f'Sending {amount} prv to {receiver_account}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        return SUT.full_node.transaction(). \
            send_transaction(self.private_key, receiver_account.payment_key, amount, fee, privacy)

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
        return self.send_prv_to(to_account, balance - 200, 100, privacy)

    def count_unspent_output_coins(self):
        """
        count number of unspent coin
        :return: int
        """
        INFO('Count unspent coin')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        response = SUT.full_node.transaction().list_unspent_output_coins(self.private_key).get_result("Outputs")
        return len(response[self.private_key])

    def defragment_account(self):
        """
            check if account need to be defrag by count unspent coin
            if count > 1 then defrag
        :return: Response object if need to defrag, None if not to
        """
        INFO('Defrag account')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        if self.count_unspent_output_coins() > 1:
            return SUT.full_node.transaction().defragment_account(self.private_key)
        INFO('No need to defrag!')
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
