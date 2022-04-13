from APIs import BaseRpcApi


class PortalV4Rpc(BaseRpcApi):
    def create_n_send_deposit_tx(self, private_k, token_id, deposit_private_k, deposit_pub_k, deposit_index,
                                 shielding_proof, receiver="", signature="",
                                 main_tx_receiver=None, tx_fee=-1, tx_privacy=0):
        return self.rpc_connection.with_method("createandsenddeposittxwithdepositkey").with_params([
            private_k, main_tx_receiver, tx_fee, tx_privacy,
            {
                "TokenID": token_id,
                "ShieldingProof": shielding_proof,
                "DepositPrivateKey": deposit_private_k,
                "DepositPubKey": deposit_pub_k,
                "DepositKeyIndex": deposit_index,
                "Receiver": receiver,
                "Signature": signature
            }]).execute()

    def get_deposit_tx_by_pub_keys(self, pub_k_list):
        return self.rpc_connection.with_method("getdeposittxsbypubkeys").with_params([{
            "DepositPubKeys": pub_k_list}]).execute()

    def has_ot_deposit_pub_keys(self, deposit_pub_k_list):
        return self.rpc_connection.with_method("hasotdepositpubkeys").with_params([{
            "DepositPubKeys": deposit_pub_k_list}]).execute()

    def get_next_ot_reposit_k(self, private_k, token_id):
        return self.rpc_connection.with_method("getnextotdepositkey").with_params([{
            "PrivateKey": private_k, "TokenID": token_id}]).execute()

    def gen_ot_deposit_key(self, private_k, index, token_id):
        return self.rpc_connection.with_method("generateotdepositkey").with_params([{
            "PrivateKey": private_k, "TokenID": token_id, "Index": index}]).execute()

    def gen_ota_receiver(self, payment_k):
        return self.rpc_connection.with_method("generateotareceiver").with_params([payment_k]).execute()

    def sign_receiver(self, signing_k, ota_receiver):
        return self.rpc_connection.with_method("signreceiver").with_params([{
            "SigningKey": signing_k, "Receiver": ota_receiver}]).execute()

    def generate_deposit_address(self, payment_key, token_id, deposit_pub_k):
        return self.rpc_connection.with_method("generatedepositaddress").with_params([{
            "IncAddressStr": payment_key, "DepositPubKey": deposit_pub_k, "TokenID": token_id}]).execute()
