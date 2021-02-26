from APIs import BaseRpcApi


class ExploreRpc(BaseRpcApi):
    def list_privacy_custom_token(self):
        return self.rpc_connection. \
            with_method('listprivacycustomtoken'). \
            with_params([]). \
            execute()

    def list_privacy_custom_token_by_shard(self, shard_id):
        return self.rpc_connection. \
            with_method('listprivacycustomtokenbyshard'). \
            with_params([shard_id]). \
            execute()

    def privacy_custom_token(self, token_id):
        return self.rpc_connection. \
            with_method('privacycustomtoken'). \
            with_params([token_id]). \
            execute()

    def get_list_privacy_custom_token_balance(self, private_key):
        return self.rpc_connection. \
            with_method('getlistprivacycustomtokenbalance'). \
            with_params([private_key]). \
            execute()

    def get_balance_privacy_custom_token(self, private_key, token_id):
        return self.rpc_connection. \
            with_method('getbalanceprivacycustomtoken'). \
            with_params([private_key, token_id]). \
            execute()

    def get_reward_feature(self, epoch, feature_name='portal'):  # only portal feature for now
        return self.rpc_connection.with_method('getrewardfeature'). \
            with_params([{
            "FeatureName": feature_name,
            "Epoch": str(epoch)}]).execute()
