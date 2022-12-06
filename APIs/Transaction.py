from requests.structures import CaseInsensitiveDict

from APIs import BaseRpcApi
from Configs import Constants
from Configs.Configs import ChainConfig
from Configs.Constants import BURNING_ADDR
from Drivers.Response import RPCResponseWithTxHash
from Helpers.Logging import config_logger
from Objects import BlockChainInfoBaseClass

logger = config_logger(__name__)


class TransactionRpc(BaseRpcApi):
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
        return TransactionDetail(self.rpc_connection.with_method("gettransactionbyhash").with_params([tx_id]).execute())

    def estimate_fee_prv(self, sender_private_key, receiver_payment_address, amount_prv, fee=0, privacy=0):
        return self.rpc_connection. \
            with_method("estimatefee"). \
            with_params([sender_private_key, {receiver_payment_address: amount_prv}, fee, privacy]). \
            execute()

    ###############
    # TOKEN SECTION
    ###############

    def init_custom_token(self, private_key, payment_address, symbol, amount, privacy=True, token_id="",
                          token_fee=0, token_tx_type=0, prv_fee=-1):
        return self.rpc_connection. \
            with_method("createandsendprivacycustomtokentransaction"). \
            with_params([private_key, None, prv_fee, 1,
                         {
                             "Privacy": privacy,
                             "TokenID": token_id,
                             "TokenName": f'{symbol}_{symbol}',
                             "TokenSymbol": symbol,
                             "TokenFee": token_fee,
                             "TokenTxType": token_tx_type,
                             "TokenAmount": amount,
                             "TokenReceivers": {
                                 payment_address: amount
                             }
                         }]).execute()

    def new_init_p_token(self, private_k, amount, token_name, token_symbol):
        return self.rpc_connection.with_method('createandsendtokeninittransaction'). \
            with_params([{"PrivateKey": private_k,
                          "TokenName": token_name,
                          "TokenSymbol": token_symbol,
                          "Amount": amount}]).execute()

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
                          "TokenReceivers": receiver_payment_key_amount_dict,
                          "TokenFee": token_fee
                      },
                      # "", token_privacy
                      ])
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

    def withdraw_centralize_token(self, private_key, token_id, amount_custom_token, tx_ver):
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
                                 Constants.BURNING_ADDR: amount_custom_token
                             },
                             "TokenFee": 0,
                             "TxVersion": tx_ver  # only mater with privacy v2, backward compatible with privacy v1
                         },
                         "", 0
                         ]). \
            execute()

    ###############
    # WITHDRAW REWARD
    ###############
    def withdraw_reward(self, private_key, payment_address, token_id, tx_fee=-1, tx_ver=2, version=2, privacy=1):
        return self.rpc_connection. \
            with_method("withdrawreward"). \
            with_params([private_key, {}, tx_fee, privacy,
                         {
                             "PaymentAddress": payment_address,
                             "TokenID": token_id,
                             "Version": version,
                             "TxVersion": tx_ver  # only mater with privacy v2, backward compatible with privacy v1
                         }
                         ]). \
            execute()

    def withdraw_reward_privacy_v2(self, private_key, payment_address, token_id="", tx_fee=-1, tx_ver=2, privacy=0):
        return self.rpc_connection. \
            with_method("withdrawreward"). \
            with_params([private_key, {}, tx_fee, privacy,
                         {
                             "PaymentAddress": payment_address,
                             "TokenID": token_id,
                             "TxVersion": tx_ver  # only mater with privacy v2, backward compatible with privacy v1
                         }
                         ]). \
            execute()

    def de_fragment_prv(self, private_key, min_bill=1000000000000000, tx_fee=-1, privacy=1):
        return self.rpc_connection. \
            with_method("defragmentaccount"). \
            with_params([private_key, min_bill, tx_fee, privacy]). \
            execute()

    def de_fragment_token(self, private_k, token_id, defrag_amount=0, privacy=True):
        """
        @param private_k:
        @param token_id:
        @param defrag_amount:
        @param privacy:True/False
        @return:
        """
        return self.rpc_connection.with_method('defragmentaccounttoken'). \
            with_params([private_k, {}, -1, 1,
                         {
                             "Privacy": privacy,
                             "TokenID": token_id,
                             "TokenName": "",
                             "TokenSymbol": "",
                             "TokenTxType": 1,
                             "TokenAmount": defrag_amount,
                             "TokenReceivers": {},
                             "TokenFee": 0
                         }, "", 1]).execute()

    def list_unspent_output_coins(self, private_key, token_id='', start_height=0):
        return self.rpc_connection. \
            with_method('listunspentoutputcoinsfromcache'). \
            with_params([0, 999999,  # privacy v2
                         [{"PrivateKey": private_key,
                           "StartHeight": start_height}],
                         token_id]). \
            execute()

    def list_output_coin(self, payment_k, token_id, **kwargs):
        """
        @param payment_k: mandatory parameter
        @param token_id:
        @param kwargs: ReadonlyKey or OTASecretKey (should not be both) must be specified
        @return:
        """
        kwargs = CaseInsensitiveDict(kwargs)
        read_only_k = kwargs.get("ReadonlyKey", "")
        ota_secret_key = kwargs.get("OTASecretKey", "")
        return self.rpc_connection.with_method("listoutputcoins"). \
            with_params([0, 999999,
                         [{
                             "PaymentAddress": payment_k,
                             "ReadonlyKey": read_only_k,
                             "OTASecretKey": ota_secret_key
                         }], token_id]).execute()

    def list_unspent_output_tokens(self, private_k, token_id, from_height):
        return self.rpc_connection. \
            with_method('listunspentoutputtokens'). \
            with_params([0, 999999, [{"PrivateKey": private_k,
                                      "StartHeight": from_height,
                                      "tokenID": token_id}]]) \
            .execute()

    def get_public_key_by_payment_key(self, payment_key):
        return self.rpc_connection. \
            with_method("getpublickeyfrompaymentaddress"). \
            with_params([payment_key]). \
            execute()

    # stake
    def create_and_send_staking_transaction(self, candidate_private_key, candidate_payment_key, candidate_validator_key,
                                            reward_receiver_payment_key, stake_amount=1750, auto_re_stake=True,
                                            tx_version=2, tx_fee=-1, tx_privacy=0):
        return self.rpc_connection. \
            with_method("createandsendstakingtransaction"). \
            with_params([candidate_private_key,
                         {BURNING_ADDR: stake_amount},
                         tx_fee, tx_privacy,
                         {
                             "StakingType": 63,
                             "CandidatePaymentAddress": candidate_payment_key,
                             "PrivateSeed": candidate_validator_key,
                             "RewardReceiverPaymentAddress": reward_receiver_payment_key,
                             "AutoReStaking": auto_re_stake,
                             "TxVersion": tx_version
                         }
                         ]). \
            execute()

    def create_and_send_stop_auto_staking_transaction(self, private_key, candidate_payment_key, validator_key):
        param = [private_key,
                 {BURNING_ADDR: 0},
                 10, 0,
                 {"StopAutoStakingType": 127,
                  "CandidatePaymentAddress": candidate_payment_key,
                  "PrivateSeed": validator_key}]
        return self.rpc_connection. \
            with_method('createandsendstopautostakingtransaction'). \
            with_params(param). \
            execute()

    def create_and_send_un_staking_transaction(self, private_key, candidate_payment_key, validator_key, tx_fee=-1):
        param = [private_key,
                 {BURNING_ADDR: 0},
                 tx_fee, 0,
                 {"UnStakingType": 210,
                  "CandidatePaymentAddress": candidate_payment_key,
                  "PrivateSeed": validator_key}]
        return self.rpc_connection. \
            with_method('createunstaketransaction'). \
            with_params(param). \
            execute()

    def get_reward_amount(self, validator_payment_key):
        return self.rpc_connection. \
            with_method('getrewardamount'). \
            with_params([validator_payment_key]). \
            execute()

    def create_convert_coin_ver1_to_ver2_transaction(self, private_key):
        return self.rpc_connection. \
            with_method('createconvertcoinver1tover2transaction'). \
            with_params([private_key, -1]). \
            execute()

    def create_convert_coin_ver1_to_ver2_tx_token(self, private_key, token_id, tx_fee=-1):
        return self.rpc_connection. \
            with_method('createconvertcoinver1tover2txtoken'). \
            with_params([private_key, token_id, tx_fee]). \
            execute()

    def get_transaction_by_receiver(self, payment_k, read_only_k):
        return self.rpc_connection. \
            with_method('gettransactionbyreceiver'). \
            with_params([{"PaymentAddress": payment_k,
                          "ReadonlyKey": read_only_k}]). \
            execute()

    def get_transaction_hash_by_receiver(self, payment_k):
        return self.rpc_connection. \
            with_method('gettransactionhashbyreceiver'). \
            with_params([payment_k]). \
            execute()

    def estimate_tx_fee(self, sender_private_k, receiver_payment_k, send_amount, fee=-1, privacy=1):
        # send_amount = str(send_amount)
        return self.rpc_connection. \
            with_method('estimatefee'). \
            with_params([sender_private_k, {receiver_payment_k: send_amount}, fee, privacy]). \
            execute()

    def create_tx(self, sender_private_k, receiver_payment_k, amount, fee=-1, privacy=1):
        return self.rpc_connection. \
            with_method('createtransaction'). \
            with_params([sender_private_k,
                         {receiver_payment_k: amount}, fee, privacy]). \
            execute()

    def send_prv_tx(self, proof):
        return self.rpc_connection. \
            with_method('sendtransaction'). \
            with_params([proof]). \
            execute()

    def send_token_tx(self, proof):
        return self.rpc_connection. \
            with_method('sendrawprivacycustomtokentransaction'). \
            with_params([proof]). \
            execute()

    def submit_key(self, key):
        """
        for privacy v2, must subscribe for caching and getting balance
        @param key: OTA private key or Private key
        @return:
        """
        return self.rpc_connection.with_method('submitkey').with_params([key]).execute()

    def submit_key_info(self, ota_key):
        return self.rpc_connection.with_method('getkeysubmissioninfo').with_params([ota_key]).execute()

    def submit_key_authorized(self, ota_key, access_token, block_height=0, re_index=False):
        """
        @param ota_key:
        @param access_token:
        @param block_height:
        @param re_index:
        @return:
        """
        return self.rpc_connection.with_method('authorizedsubmitkey'). \
            with_params([ota_key, access_token, block_height, re_index]).execute()

    def get_tx_by_receiver_v2(self, payment_k, read_only_k, token_id, from_index=0, to_index=500):
        return self.rpc_connection.with_method('gettransactionbyreceiverv2'). \
            with_params([{"PaymentAddress": payment_k,
                          "ReadonlyKey": read_only_k,
                          "TokenID": token_id,
                          "Skip": from_index,
                          "Limit": to_index}]).execute()

    def create_n_send_burn_tx_bsc(self, private_key,
                                  token_id, token_amount, remote_addr,
                                  prv_fee: dict = None, token_fee: dict = None, tx_fee=-1, tx_privacy=1):
        prv_tx = prv_fee if isinstance(prv_fee, dict) else {}
        token_tx = {**{BURNING_ADDR: token_amount}, **token_fee} if token_fee else {BURNING_ADDR: token_amount}
        return RPCResponseWithTxHash(self.rpc_connection.with_method("createandsendburningpbscfordeposittoscrequest").
                                     with_params([private_key, prv_tx, tx_fee, tx_privacy,
                                                  {"TokenID": token_id,
                                                   "TokenTxType": 1,
                                                   "TokenName": "",
                                                   "TokenSymbol": "",
                                                   "TokenAmount": token_amount,
                                                   "TokenReceivers": token_tx,
                                                   "RemoteAddress": remote_addr,
                                                   "Privacy": True,
                                                   "TokenFee": 0}, "", 0]).execute())


class TransactionDetail(RPCResponseWithTxHash):
    class TxDetailProof(BlockChainInfoBaseClass):
        def _get_coin_list(self, coin_list_name):
            """

            @param coin_list_name: "InputCoins" or "OutputCoins"
            @return:
            """
            from Objects.CoinObject import TxOutPut
            raw_coins = self.dict_data[coin_list_name]
            list_coin_obj = []
            for raw in raw_coins:
                try:
                    coin_obj = TxOutPut(raw['CoinDetails'])
                except KeyError:
                    coin_obj = TxOutPut(raw)
                try:
                    coin_obj.dict_data['CoinDetailsEncrypted'] = raw['CoinDetailsEncrypted']
                except KeyError:
                    pass
                list_coin_obj.append(coin_obj)
            return list_coin_obj

        def get_input_coins(self):
            return self._get_coin_list('InputCoins')

        def get_output_coins(self):
            return self._get_coin_list('OutputCoins')

        def check_proof_privacy(self):
            input_coins = self.get_input_coins()
            for coin in input_coins:
                key = coin.get_public_key()
                value = coin.get_value()
                logger.info(f'Coin {key} value = {value}')
                if value != 0:
                    return False

            return True

    class MetaData(BlockChainInfoBaseClass):
        def get_type(self):
            return self.dict_data['Type']

        def get_sig(self):
            return self.dict_data['Sig']

        def get_payment_address(self):
            return self.dict_data['PaymentAddress']

        def get_payment_address_reward_receiver(self):
            return self.dict_data["RewardReceiverPaymentAddress"]

        def get_funder_payment_address(self):
            return self.dict_data["FunderPaymentAddress"]

        def get_amount(self):
            return self.dict_data['Amount']

    def get_block_hash(self):
        return self.get_result()['BlockHash']

    def get_block_height(self):
        """
        @return: shard block height NOT BEACON BLOCK HEIGHT
        """
        return self.get_result()['BlockHeight']

    def get_tx_size(self):
        return self.get_result()['TxSize']

    def get_index(self):
        return self.get_result()['Index']

    def get_shard_id(self):
        return self.get_result()['ShardID']

    def get_hash(self):
        return self.get_result()['Hash']

    def get_version(self):
        return self.get_result()['Version']

    def get_type(self):
        return self.get_result()['Type']

    def get_lock_time(self):
        return self.get_result()['LockTime']

    def get_fee(self):
        return self.get_result()['Fee']

    def get_image(self):
        return self.get_result()['Image']

    def is_privacy(self):
        return self.get_result()['IsPrivacy']

    def get_proof(self):
        return self.get_result()['Proof']

    def get_prv_proof_detail(self):
        """
        prv proof
        :return:
        """
        return TransactionDetail.TxDetailProof(self.get_result()['ProofDetail'])

    def get_input_coin_pub_key(self):
        return self.get_result()['InputCoinPubKey']

    def get_sig_pub_key(self):
        return self.get_result()['SigPubKey']

    def get_sig(self):
        return self.get_result()['Sig']

    def get_meta_data(self):
        return TransactionDetail.MetaData(self.get_result()['Metadata'])

    def get_custom_token_data(self):
        return self.get_result()['CustomTokenData']

    def get_privacy_custom_token_id(self):
        return self.get_result()['PrivacyCustomTokenID']

    def get_privacy_custom_token_name(self):
        return self.get_result()['PrivacyCustomTokenName']

    def get_privacy_custom_token_symbol(self):
        return self.get_result()['PrivacyCustomTokenSymbol']

    def get_privacy_custom_token_data(self):
        return self.get_result()['PrivacyCustomTokenData']

    def get_privacy_custom_token_proof_detail(self):
        """
        :return:
        """
        return TransactionDetail.TxDetailProof(self.get_result()['PrivacyCustomTokenProofDetail'])

    def is_privacy_custom_token(self):
        return self.get_result()['PrivacyCustomTokenIsPrivacy']

    def get_privacy_custom_token_fee(self):
        return self.get_result()['PrivacyCustomTokenFee']

    def is_in_mem_pool(self):
        in_mem_pool = True if self.get_result()["IsInMempool"] == 'true' else False
        return in_mem_pool

    def is_in_block(self):
        in_block = True if self.get_result()["IsInBlock"] == 'true' else False
        return in_block

    def get_info(self):
        return self.get_result()['Info']

    def get_tx_id(self):
        try:
            return self.get_result()['TxID']
        except KeyError:
            return self.get_hash()

    def __verify_privacy(self, privacy_flag, detail_proof, expected_privacy=True):
        version = ChainConfig.PRIVACY_VERSION
        privacy = privacy_flag and detail_proof.check_proof_privacy()
        if version == 2:
            logger.info(f'In v2, privacy is always enable')
            assert privacy, f'Expected privacy = True, actual = {privacy}'
        else:
            assert privacy == expected_privacy, f'Expected privacy = {expected_privacy} while actual = {privacy}'
        return self

    def verify_token_privacy(self, expected_privacy=True):
        logger.info(f'Check tx token privacy: {self.get_tx_id()}')
        detail_proof = self.get_privacy_custom_token_proof_detail()
        privacy = self.is_privacy_custom_token()
        logger.info(f'PrivacyCustomTokenIsPrivacy={privacy}')
        return self.__verify_privacy(privacy, detail_proof, expected_privacy)

    def verify_prv_privacy(self, expected_privacy=True):
        version = ChainConfig.PRIVACY_VERSION
        expected_privacy = bool(expected_privacy)
        logger.info(f'Check tx prv privacy v{version}: {self.get_tx_id()}')
        detail_proof = self.get_prv_proof_detail()
        privacy = self.is_privacy()
        logger.info(f'IsPrivacy={privacy}')
        return self.__verify_privacy(privacy, detail_proof, expected_privacy)

    def is_confirmed(self):
        return bool(self.get_block_hash() and self.get_hash())
