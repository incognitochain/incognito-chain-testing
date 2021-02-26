from APIs import BaseRpcApi


class UtilsRpc(BaseRpcApi):
    def convert_payment_k_to_v1(self, key):
        return self.rpc_connection.with_method("convertpaymentaddress").with_params([key]).execute()
