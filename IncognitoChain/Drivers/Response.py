import json
import re
from builtins import Exception

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Objects.PortalObjects import PortalStateInfo
from IncognitoChain.Objects.TransactionObjects import TransactionDetail


class Response:
    def __init__(self, response, more_info=None):
        self.response = response
        self.more_info = more_info
        if more_info is not None:
            Log.DEBUG(more_info)
        Log.DEBUG(self.__str__())

    def __str__(self):
        return f'\n{json.dumps(self.data(), indent=3)}'

    def expect_no_error(self):
        assert self.get_error_msg() is None, self.get_error_trace().get_message()
        return True

    def expect_error(self):
        assert self.get_error_msg() is not None, 'Found no error while expect one'
        return True

    def data(self):
        if type(self.response) is str:
            return json.loads(self.response)  # response from WebSocket
        return json.loads(self.response.text)  # response from rpc

    def params(self):
        return Params(self.data()["Params"])

    def size(self):
        if self.response is str:  # response from WebSocket
            return len(self.response)
        return len(self.response.content)  # response from rpc

    def response_time(self):
        if self.response is str:  # response from WebSocket
            return None
        return self.response.elapsed.total_seconds()  # response from rpc

    def is_success(self):
        if self.data()['Error'] is None:
            return True
        return False

    def get_error_trace(self):
        if self.data()['Error'] is None:
            return ''
        return StackTrace(self.data()['Error']['StackTrace'][0:512])

    def get_error_msg(self):
        if self.data()['Error'] is None:
            return None
        return self.data()['Error']['Message']

    def find_in_result(self, string):
        for k, v in self.data()["Result"].items():
            if k == str(string):
                return True
        return False

    def get_result(self, string=None):
        try:
            if string is None:
                return self.data()['Result']
            return self.data()['Result'][string]
        except(KeyError, TypeError):
            return None

    def get_tx_id(self):
        return self.get_result("TxID")

    def get_beacon_height(self):
        return self.get_result("BeaconHeight")

    def get_pde_pool_pairs(self):
        return self.get_result("PDEPoolPairs")

    def get_pde_share(self):
        return self.get_result("PDEShares")

    def get_token_id_1_str(self):
        return self.get_result("TokenID1Str")

    def get_token_id_2_str(self):
        return self.get_result("TokenID2Str")

    def get_token_id(self):
        return self.get_result("TokenID")

    def get_returned_1_amount(self):
        return self.get_result("Returned1Amount")

    def get_returned_2_amount(self):
        return self.get_result("Returned2Amount")

    def get_contributed_1_amount(self):
        return self.get_result("Contributed1Amount")

    def get_contributed_2_amount(self):
        return self.get_result("Contributed2Amount")

    def get_fee(self):
        try:
            return self.get_result('Result')['Fee']
        except (KeyError, TypeError):
            return self.get_result('Fee')

    def get_tx_size(self):
        try:
            return self.get_result()['TxSize']
        except (KeyError, TypeError):
            return self.get_result('Result')['TxSize']

    def get_privacy(self):
        return self.get_result("IsPrivacy")

    def get_custom_token_privacy(self):
        return self.get_result("PrivacyCustomTokenIsPrivacy")

    def get_balance(self):
        return self.get_result()

    def get_block_height(self):
        return self.get_result("BlockHeight")

    def get_tx_hashes(self):
        # for retrieveblockbyheight database v1
        ret = self.get_result("TxHashes")
        if ret is None:
            # for retrieveblockbyheight database v2
            ret = self.get_result()[0]["TxHashes"]
        return ret

    def get_list_txs(self):
        return self.get_result("ListTxs")

    def get_block_hash(self):
        return self.get_result("BlockHash")

    def get_shard_id(self):
        return self.get_result('ShardID')

    # !!!!!!!! Next actions base on response
    def subscribe_transaction(self, tx_id=None):
        """
        Subscribe transaction by txid

        :param tx_id: if not specified, use tx id from self
        :return: Response Object
        """
        if tx_id is None:
            tx_id = self.get_tx_id()
        INFO(f'Subscribe to transaction tx_id = {tx_id}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        return SUT.full_node.subscription().subscribe_pending_transaction(tx_id)

    def subscribe_transaction_obj(self, tx_id=None):
        """
        Subscribe transaction by txid

        :param tx_id: if not specified, use tx id from self
        :return: TransactionDetail Object
        """
        if tx_id is None:
            tx_id = self.get_tx_id()
        INFO(f'Subscribe to transaction tx_id = {tx_id}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        from IncognitoChain.Objects.TransactionObjects import TransactionDetail
        tx = SUT.full_node.subscription().subscribe_pending_transaction(tx_id)
        return TransactionDetail(tx.get_result('Result'))

    def get_proof_detail_input_coin_value_prv(self):
        try:
            return self.get_result('ProofDetail')['InputCoins'][0]['CoinDetails']['Value']
        except TypeError:
            return None

    def get_portal_state_info_obj(self):
        return PortalStateInfo(self.get_result())

    def is_prv_privacy(self):
        return self.is_prv_privacy_v2()

    def is_prv_privacy_v2(self):
        """
        check if prv transaction is privacy or not

        :return: True = privacy, False = no privacy
        """
        tx_info = self.get_transaction_by_hash()
        value = int(tx_info.get_result('ProofDetail')['InputCoins'][0]['Value'])
        privacy = tx_info.get_privacy()
        if not privacy:
            raise Exception("Transaction PRV v2 must always have privacy")
        INFO(f'Checking PRV v2 privacy. isPrivacy = {tx_info.get_privacy()}, input coin value = {value}')
        return value == 0

    def is_prv_privacy_v1(self):
        """
        check if prv transaction is privacy or not

        :return: True = privacy, False = no privacy
        """
        result = self.get_transaction_by_hash()
        value = result.get_proof_detail_input_coin_value_prv()
        INFO(f'Checking PRV v1 privacy. isPrivacy = {result.get_privacy()}, input coin value = {value}')
        return result.get_privacy() and result.get_proof_detail_input_coin_value_prv() == 0

    def get_proof_detail_input_coin_value_custom_token(self):
        try:
            return self.get_result('PrivacyCustomTokenProofDetail')['InputCoins'][0]['CoinDetails']['Value']
        except TypeError:
            return None

    def is_token_privacy(self):
        return self.is_token_privacy_v2()

    def is_token_privacy_v2(self):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        tx_info = SUT.full_node.transaction().get_tx_by_hash(self.get_tx_id())
        value = int(tx_info.get_result('PrivacyCustomTokenProofDetail')['InputCoins'][0]['Value'])
        privacy = tx_info.get_custom_token_privacy()
        if not privacy:
            raise Exception("Transaction token v2 must always have privacy")
        INFO(f'Checking tok v2 privacy. isPrivacy = {tx_info.get_custom_token_privacy()}, input coin value = {value}')
        return value == 0

    def is_token_privacy_v1(self):
        """
        check if token transaction is privacy or  not

        :return: True = privacy, False = no privacy
        """
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        result = SUT.full_node.transaction().get_tx_by_hash(self.get_tx_id())
        value = result.get_proof_detail_input_coin_value_custom_token()
        INFO(f'Checking tok v1 privacy. isPrivacy = {result.get_custom_token_privacy()}, input coin value = {value}')
        return result.get_custom_token_privacy() and value == 0

    def is_transaction_v2(self):
        stack_trace_msg = self.get_error_trace().get_message()
        if 'error calling MarshalJSON for type *transaction.TxTokenVersion2' in stack_trace_msg:
            INFO('Transaction v2 no longer support paying fee with token')
            return True

    def get_transaction_by_hash(self):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        return SUT.full_node.transaction().get_tx_by_hash(self.get_tx_id())

    def get_mem_pool_transactions_id_list(self) -> list:
        hashes = self.get_list_txs()
        if hashes is None:
            return []
        tx_id_list = list()
        for entry in hashes:
            tx_id_list.append(entry['TxID'])
        return tx_id_list

    def get_tx_proof(self):
        """
        :return: tx proof from the response it self
        """
        return self.get_result('Proof')

    def get_tx_object(self):
        return TransactionDetail(self.get_result())


class StackTrace:
    def __init__(self, stack_string):
        self.stack_string = stack_string

    def __str__(self):
        return self.stack_string

    def get_error_codes(self):
        code_list = re.findall("(-[0-9]\\w+: )", self.stack_string)
        return ''.join([str(elem) for elem in code_list])

    def get_message(self):
        try:
            i_start = len(self.get_error_codes())
            i_end = str.index(self.stack_string, 'github.com')
            return str(self.stack_string[i_start:i_end])
        except ValueError:
            return str(self.stack_string)

    def get_estimated_fee(self):
        return re.search("fee=(.*)", self.stack_string).group(1)


class Params:
    def __init__(self, data):
        self.data = data

    def get_beacon_height(self):
        return int(self.data[0]["BeaconHeight"])

    def get_portal_redeem_req_id(self):
        return self.data[4]["UniqueRedeemID"]

    def get_portal_register_id(self):
        return self.data[4]['UniqueRegisterId']

    def get_portal_porting_fee(self):
        return int(self.data[4]['PortingFee'])

    def get_portal_register_amount(self):
        return int(self.data[4]['RegisterAmount'])

    def get_portal_redeem_amount(self):
        return int(self.data[4]['TokenAmount'])

    def get_portal_redeem_fee(self):
        return int(self.data[4]['RedeemFee'])
