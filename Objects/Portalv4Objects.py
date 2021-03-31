from typing import List
from Helpers.Logging import INFO, DEBUG, INFO_HEADLINE, ERROR
from Helpers.Time import WAIT
from Objects import BlockChainInfoBaseClass


class PortalV4InfoBase(BlockChainInfoBaseClass):
    def get_status(self):
        return self.data['Status']

    def get_token_id(self):
        return self.data['TokenID']

    def get_amount(self):
        return int(self.data['Amount'])

    def is_none(self):
        if self.data is None:
            return True
        return False

    def get_shield_req_status(self, tx_id, retry=True):
        INFO(f'Get shield req info, tx_id = {tx_id}')
        from Objects.IncognitoTestCase import SUT
        response = SUT().portalv4().get_portal_shield_status(tx_id)
        self.data = response.get_result()
        if self.is_none() and retry:
            WAIT(40)
            response = SUT().portalv4().get_portal_shield_status(tx_id)
        return response.get_result('Status')

    def get_unshield_req_status(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        INFO(f'Get unshield req info, tx_id = {tx_id}')
        response = SUT().portalv4().get_unsheild_status(tx_id)
        self.data = response.get_result()
        if self.is_none() and retry:
            WAIT(20)
            response = SUT().portalv4().get_unsheild_status(tx_id)
        return response.get_result('Status')

    def get_raw_btc_transaction(self, batch_id):
        INFO(f'Get raw transaction with batch req info, batch_id = {batch_id}')
        from Objects.IncognitoTestCase import SUT
        response = SUT().portalv4().get_signed_raw_transaction(batch_id)
        return response.get_result("SignedTx")

    def get_submit_proof_confirm_status(self, txhash, retry= True):
        INFO(f'Get submit proof confirm info, tx_id = {txhash}')
        from Objects.IncognitoTestCase import SUT
        response = SUT().portalv4().get_portal_submit_confirm_status(txhash)
        self.data = response.get_result()
        if self.is_none() and retry:
            WAIT(20)
            response = SUT().portalv4().get_portal_submit_confirm_status(txhash)
        return response.get_result("Status")

    def get_replace_fee_status(self, txhash, retry = True):
        from Objects.IncognitoTestCase import SUT
        response = SUT().portalv4().get_replace_fee_status(txhash)
        self.data = response.get_result()
        if self.is_none() and retry:
            WAIT(20)
            response = SUT().portalv4().get_replace_fee_status(txhash)
        return response.get_result("Status")

    def get_raw_replace_fee_btc_transaction(self, txhash):
        INFO(f'Get raw replace fee transaction with replace fee  info, replace_fee_ = {txhash}')
        from Objects.IncognitoTestCase import SUT
        response = SUT().portalv4().get_signed_raw_replace_fee_transaction(txhash)
        return response.get_result("SignedTx")


class Portalv4StateInfo(PortalV4InfoBase):
    class UTXO(PortalV4InfoBase):
        def __str__(self):
            return "key= %s, WalletAddress= %s, TxHash= %s OutputAmount= %s" % (
                self.get_key(), self.get_wallet_addr(), self.get_tx_hash(), self.get_output_amt())

        def __eq__(self, other):
            return self.data == other.data

        def __ne__(self, other):
            return self.data != other.data

        def get_key(self):
            return list(self.data.keys())[0]

        def get_wallet_addr(self):
            try:
                return list(self.data.values())[0]['WalletAddress']  # this only exists in UTXO
            except KeyError:
                return list(self.data.values())[0]['WalletAddress']  # this only exists  UTXO

        def get_tx_hash(self):
            try:
                return list(self.data.values())[0]['TxHash']  # this only exists in UTXO
            except KeyError:
                return list(self.data.values())[0]['TxHash']  # this only exists UTXO

        def get_output_amt(self):
            return int(list(self.data.values())[0]['OutputAmount'])

        def get_output_idx(self):
            return int(list(self.data.values())[0]['OutputIdx'])

    class UnshieldRequest(PortalV4InfoBase):
        def get_unshield_id(self):
            return self.data["UnshieldID"]

        def get_amount(self):
            return int(self.data["Amount"])

        def get_remote_address(self):
            return self.data["RemoteAddress"]

        def get_beacon_height(self):
            return int(self.data["BeaconHeight"])

    class Batch(PortalV4InfoBase):
        def __str__(self):
            return "Batch_id= %s" % (
                self.get_batch_id())

        def get_batch_id(self):
            return self.data["BatchID"]

        def get_list_unshield_req(self):
            return list(self.data["UnshieldsID"])

        def get_external_fee(self):
            return self.data["ExternalFees"]

        def get_last_fee(self):
            data_raw = self.get_external_fee().items()
            data = sorted(data_raw, reverse=True)
            return int(data[0][1])

        def get_last_beacon_height_fee(self):
            data_raw = self.get_external_fee().items()
            data = sorted(data_raw, reverse=True)
            return int(data[0][0])

        def get_beacon_height(self):
            data_fee = self.data["ExternalFees"]
            becon_height = int(data_fee.key())
            return becon_height

        def get_list_utxo_in_batch(self):
            list_utxo = []
            data_raw = self.data["UTXOs"]
            key, value = list(self.data["UTXOs"].items())[0]
            if data_raw is None:
                return list_utxo
            else:
                for i in value:
                    data = {key: i}
                    utxo = Portalv4StateInfo.UTXO(data)
                    list_utxo.append(utxo)
            return list_utxo

        def compare_list_utxo_in_batch(self, list_utxo):
            result = False
            src_utxo = self.get_list_utxo_in_batch()
            src_utxo.sort(key=lambda utxo: (utxo.get_output_amt(), utxo.get_tx_hash()), reverse=True)
            list_utxo.sort(key=lambda utxo: (utxo.get_output_amt(), utxo.get_tx_hash()), reverse=True)
            if len(src_utxo) != len(list_utxo):
                return result
            else:
                for i in range(len(src_utxo)):
                    if (
                            src_utxo[i].get_output_idx() == list_utxo[i].get_output_idx()
                            and src_utxo[i].get_tx_hash() == list_utxo[i].get_tx_hash()
                    ):
                        result = True
                    else:
                        return False
            return result

    def get_list_utxo(self, token_id) -> List[UTXO]:
        utxo_list = []
        req_data_raw = self.data["UTXOs"][token_id]
        if req_data_raw is None:
            return utxo_list
        else:
            for key, req_utxo_raw in req_data_raw.items():
                data_ = {key: req_utxo_raw}
                req = Portalv4StateInfo.UTXO(data_)
                utxo_list.append(req)
        return utxo_list

    def find_utxo_by_txHash_amount(self, token_id, tx_hash, output_amout):
        result = False
        utxo_list = self.get_list_utxo(token_id)
        if utxo_list is None:
            return result
        else:
            for i in utxo_list:
                if i.get_tx_hash() == tx_hash and i.get_output_amt() == output_amout:
                    result = True
        return result

    def sum_output_amount_all_utxo(self, token_id):
        sum_output = 0
        utxo_list = self.get_list_utxo(token_id)
        if utxo_list is None:
            return sum_output
        else:
            for i in utxo_list:
                sum_output += i.get_output_amt()
        return sum_output

    def pick_utxo(self, token_id, total_unshield):
        from TestCases.PortalV4 import TINY_UTXO_AMT
        tmp_amount = int(total_unshield / 10)
        list_result = []
        list_utxo = self.get_list_utxo(token_id)
        if list_utxo is None:
            return None
        list_utxo.sort(key=lambda utxo: (-utxo.get_output_amt(), utxo.get_key()))
        for i in list_utxo:
            tmp_amount -= i.get_output_amt()
            if tmp_amount <= 0:
                list_result.append(i)
                break
            else:
                list_result.append(i)
        if len(list_utxo) > 2 and len(list_utxo) > len(list_result) and list_utxo[-1].get_output_amt() <= TINY_UTXO_AMT:
            list_result.append(list_utxo[-1])
            return list_result
        else:
            return list_result

    def get_list_unshield_waiting(self, token_id) -> List[UnshieldRequest]:
        list_unshield = []
        req_data_raw = self.data["WaitingUnshieldRequests"][token_id]
        if req_data_raw is None:
            return list_unshield
        else:
            for req in req_data_raw.values():
                unshield_req = Portalv4StateInfo.UnshieldRequest(req)
                list_unshield.append(unshield_req)
        return list_unshield

    def find_unshield_in_waiting_by_id(self, token_id, unshield_id):
        result = False
        list_unshield = self.get_list_unshield_waiting(token_id)
        if list_unshield is None:
            return result
        else:
            for i in list_unshield:
                if i.get_unshield_id() == unshield_id:
                    result = True
        return result

    def get_list_batch_unshield(self, token_id) -> List[Batch]:
        list_batch = []
        req_data_raw = self.data["ProcessedUnshieldRequests"][token_id]
        if req_data_raw is None:
            return list_batch
        else:
            for req in req_data_raw.values():
                batch_req = Portalv4StateInfo.Batch(req)
                list_batch.append(batch_req)
        return list_batch

    def find_batch_id_by_unshield_id(self, token_id, unshield_id):
        result = ""
        list_batch = self.get_list_batch_unshield(token_id)
        for i in list_batch:
            list_unshield_id = i.get_list_unshield_req()
            if unshield_id in list_unshield_id:
                return i.get_batch_id()
        return result

    def get_batch_with_batch_id(self, token_id, batch_id):
        list_batch = self.get_list_batch_unshield(token_id)
        for i in list_batch:
            if i.get_batch_id() == batch_id:
                return i
        return None

    def get_last_beacon_height_replace_fee(self, token_id, batch_id):
        batch_obj = self.get_batch_with_batch_id(token_id, batch_id)
        return int(batch_obj.get_last_beacon_height_fee())

    def get_last_fee(self, token_id, batch_id):
        batch_obj = self.get_batch_with_batch_id(token_id, batch_id)
        return int(batch_obj.get_last_fee())
