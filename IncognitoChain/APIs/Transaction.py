from IncognitoChain.Configs import Constants
from IncognitoChain.Configs.Constants import burning_address, prv_token_id
from IncognitoChain.Drivers import Connections


class TransactionRpc:
    def __init__(self, url):
        self.rpc_connection = Connections.RpcConnection(url=url)

    def send_transaction(self, sender_private_key, dict_payment_address_amount_prv, fee=-1, privacy=1):
        """
        3rd param: -1 => auto estimate fee; >0 => fee * transaction size (KB)
        4th param: 0 => no privacy ; 1 => privacy
        """
        return self.rpc_connection. \
            with_method("createandsendtransaction"). \
            with_params([sender_private_key, dict_payment_address_amount_prv, fee, privacy]). \
            execute()

    def get_balance(self, private_key):
        return self.rpc_connection. \
            with_method("getbalancebyprivatekey"). \
            with_params([private_key]). \
            execute()

    def get_tx_by_hash(self, tx_id):
        return self.rpc_connection. \
            with_method("gettransactionbyhash"). \
            with_params([tx_id]). \
            execute()

    def estimate_fee_prv(self, sender_private_key, receiver_payment_address, amount_prv, fee=0, privacy=0):
        return self.rpc_connection. \
            with_method("estimatefee"). \
            with_params([sender_private_key, {receiver_payment_address: amount_prv}, fee, privacy]). \
            execute()

    ###############
    # TOKEN SECTION
    ###############

    def init_custom_token(self, private_key, payment_address, symbol, amount, prv_fee=-1):
        return self.rpc_connection. \
            with_method("createandsendprivacycustomtokentransaction"). \
            with_params([private_key, None, prv_fee, 1,
                         {
                             "Privacy": True,
                             "TokenID": "",
                             "TokenName": symbol + "_" + symbol,
                             "TokenSymbol": symbol,
                             "TokenFee": 0,
                             "TokenTxType": 0,
                             "TokenAmount": amount,
                             "TokenReceivers": {
                                 payment_address: amount
                             }
                         }
                         ]). \
            execute()

    def send_custom_token_transaction(self, sender_private_key, receiver_payment_address, token_id, amount_custom_token,
                                      prv_fee=0, token_fee=0, prv_amount=0, prv_privacy=0, token_privacy=0):
        """
        Can be use to send not only custom token but also PRV, can also send both at the same time

        :param sender_private_key:
        :param receiver_payment_address:
        :param token_id:
        :param amount_custom_token:
        :param prv_fee: using prv to pay for fee
        :param token_fee: using custom token to pay for fee
        :param prv_amount: amount of prv to be sent
        :param prv_privacy:
        :param token_privacy:
        :return: Response Object
        """
        param = [sender_private_key]
        if prv_amount == 0:
            param.append(None)
        else:
            param.append({receiver_payment_address: prv_amount})

        param.extend([prv_fee,
                      prv_privacy,
                      {
                          "Privacy": True,
                          "TokenID": token_id,
                          "TokenName": "",
                          "TokenSymbol": "",
                          "TokenTxType": 1,
                          "TokenAmount": 0,
                          "TokenReceivers": {
                              receiver_payment_address: amount_custom_token
                          },
                          "TokenFee": token_fee
                      },
                      "", token_privacy])
        return self.rpc_connection. \
            with_method("createandsendprivacycustomtokentransaction"). \
            with_params(param). \
            execute()

    def send_custom_token_multi_output(self, sender_private_key, receiver_payment_key_amount_dict: dict, token_id,
                                       prv_fee=0, token_fee=0, prv_privacy=0, token_privacy=0):
        param = [sender_private_key, None]
        param.extend([prv_fee,
                      prv_privacy,
                      {
                          "Privacy": True,
                          "TokenID": token_id,
                          "TokenName": "",
                          "TokenSymbol": "",
                          "TokenTxType": 1,
                          "TokenAmount": 0,
                          "TokenReceivers":
                              receiver_payment_key_amount_dict
                          ,
                          "TokenFee": token_fee
                      },
                      "", token_privacy])
        return self.rpc_connection.with_method('createandsendprivacycustomtokentransaction').with_params(param). \
            execute()

    def get_custom_token_balance(self, private_key, token_id):
        return self.rpc_connection. \
            with_method("getbalanceprivacycustomtoken"). \
            with_params([private_key, token_id]). \
            execute()

    def list_custom_token_balance(self, private_key):
        return self.rpc_connection. \
            with_method("getlistprivacycustomtokenbalance"). \
            with_params([private_key]). \
            execute()

    def estimate_fee_token(self, sender_private_key, receiver_payment_address, token_id, amount_custom_token,
                           prv_fee=0, token_fee=0):
        return self.rpc_connection. \
            with_method("estimatefee"). \
            with_params([sender_private_key, None, prv_fee, 1,
                         {
                             "Privacy": True,
                             "TokenID": token_id,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenTxType": 1,
                             "TokenAmount": 0,
                             "TokenReceivers": {
                                 receiver_payment_address: amount_custom_token
                             },
                             "TokenFee": token_fee
                         },
                         "", 0
                         ]). \
            execute()

    def withdraw_centralize_token(self, private_key, token_id, amount_custom_token):
        return self.rpc_connection. \
            with_method("createandsendcontractingrequest"). \
            with_params([private_key, None, -1, 0,
                         {
                             "Privacy": True,
                             "TokenID": token_id,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenTxType": 1,
                             "TokenAmount": amount_custom_token,
                             "TokenReceivers": {
                                 Constants.burning_address: amount_custom_token
                             },
                             "TokenFee": 0
                         },
                         "", 0
                         ]). \
            execute()

    ###############
    # WITHDRAW REWARD
    ###############
    def withdraw_reward(self, private_key, payment_address, token_id=None):
        if token_id is None:
            token_id = prv_token_id
        return self.rpc_connection. \
            with_method("withdrawreward"). \
            with_params([private_key, 0, 0, 0,
                         {
                             "PaymentAddress": payment_address,
                             "TokenID": token_id
                         }
                         ]). \
            execute()

    def get_reward_prv(self, payment_address):
        return self.rpc_connection. \
            with_method("getrewardamount"). \
            with_params([payment_address]). \
            execute()

    def get_reward_token(self, payment_address):
        return self.rpc_connection. \
            with_method("getrewardamount"). \
            with_params([payment_address]). \
            execute()

    def get_reward_specific_token(self, payment_address):
        return self.rpc_connection. \
            with_method("getrewardamount"). \
            with_params([payment_address]). \
            execute()

    def check_reward_specific_token(self, payment_address):
        return self.rpc_connection. \
            with_method("getrewardamount"). \
            with_params([payment_address]). \
            execute()

    def defragment_account(self, private_key, min_bill=1000000000000000):
        return self.rpc_connection. \
            with_method("defragmentaccount"). \
            with_params([private_key, min_bill, -1, 0]). \
            execute()

    def list_unspent_output_coins(self, private_key):
        return self.rpc_connection. \
            with_method('listunspentoutputcoins'). \
            with_params([0,
                         999999,
                         [
                             {
                                 "PrivateKey": private_key
                             }
                         ],
                         ""
                         ]). \
            execute()

    def get_public_key_by_payment_key(self, payment_key):
        return self.rpc_connection. \
            with_method("getpublickeyfrompaymentaddress"). \
            with_params([payment_key]). \
            execute()

    # stake
    def create_and_send_staking_transaction(self, candidate_private_key, candidate_payment_key, candidate_validator_key,
                                            reward_receiver_payment_key, stake_amount=None, auto_re_stake=True):
        if stake_amount is None:
            stake_amount = 1750000000000
        return self.rpc_connection. \
            with_method("createandsendstakingtransaction"). \
            with_params([candidate_private_key,
                         {burning_address: stake_amount},
                         2, 0,
                         {
                             "StakingType": 63,
                             "CandidatePaymentAddress": candidate_payment_key,
                             "PrivateSeed": candidate_validator_key,
                             "RewardReceiverPaymentAddress": reward_receiver_payment_key,
                             "AutoReStaking": auto_re_stake
                         }
                         ]). \
            execute()

    def create_and_send_stop_auto_staking_transaction(self, private_key, candidate_payment_key, validator_key):
        param = [private_key,
                 {burning_address: 0},
                 10, 0,
                 {"StopAutoStakingType": 127,
                  "CandidatePaymentAddress": candidate_payment_key,
                  "PrivateSeed": validator_key}]
        return self.rpc_connection. \
            with_method('createandsendstopautostakingtransaction'). \
            with_params(param). \
            execute()

    def get_reward_amount(self, validator_payment_key):
        return self.rpc_connection. \
            with_method('getrewardamount'). \
            with_params([validator_payment_key]). \
            execute()
