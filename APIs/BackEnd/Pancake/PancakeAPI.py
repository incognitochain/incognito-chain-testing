from APIs.BackEnd import BackEndApiWithAuth
from Drivers import ResponseBase
from Objects import BlockChainInfoBaseClass


class PanCakeIntegrationAPI(BackEndApiWithAuth):
    def get_tokens(self):
        return GetTokensResponse(self.get("trade/tokens"))

    def estimate_trade_fee(self, wallet_address, token_sell, token_buy, sell_amount):
        return GetEstimateTradeFeeResponse(self.post("trade/estimate-fees", {"WalletAddress": wallet_address,
                                                                             "SrcTokens": token_sell,
                                                                             "DestTokens": token_buy,
                                                                             "SrcQties": str(sell_amount)}))

    def submit_trade(self, sell_amount, expected_amount, est_id, burn_tx, wallet_addr, src_token, dest_token,
                     trade_path, fee_selection=2, fee_level=1, is_native=True):
        return self.post("trade/submit-trading-tx", {
            "ID": est_id,
            "BurnTx": burn_tx,
            "WalletAddress": wallet_addr,
            "SrcTokens": src_token,
            "DestTokens": dest_token,
            "IsNative": is_native,
            "Path": trade_path,
            "UserFeeSelection": fee_selection,
            "UserFeeLevel": fee_level,
            "ExpectedOutputAmount": str(expected_amount),
            "SrcQties": str(sell_amount)
        })

    def get_history(self, wallet_address):
        return GetHistoryResponse(self.get(f"trade/history?filter[wallet_address]={wallet_address}"))

    def get_history_detail(self, trade_id):
        return GetHistoryDetailResponse(self.get(f"trade/history/{trade_id}"))


class GetTokensResponse(ResponseBase):
    class TokensInfo(BlockChainInfoBaseClass):
        def token_id(self):
            return self.dict_data.get("ID")

        def contract_id(self):
            return self.dict_data.get("ContractID")

        def name(self):
            return self.dict_data.get("Name")

        def symbol(self):
            return self.dict_data.get("Symbol")

        def decimals(self):
            return self.dict_data.get("Decimals")

        def p_decimals(self):
            return self.dict_data.get("PDecimals")

        def protocol(self):
            return self.dict_data.get("Protocol")

        def price_prv(self):
            return self.dict_data.get("PricePrv")

        def is_verify(self):
            return self.dict_data.get("Verify")

        def __str__(self):
            return f"{self.symbol()} - {self.token_id()} - {self.contract_id()}"

    def get_tokens(self, **by):
        all_token_info = [GetTokensResponse.TokensInfo(info) for info in self.get_result()]
        by_contract = by.get("contract")
        by_name = by.get("name")
        by_symbol = by.get("symbol")
        filtered_result = []
        for tok_inf in all_token_info:
            include = True
            if by_contract:
                include = include and by_contract == tok_inf.contract_id()
            if by_symbol:
                include = include and by_symbol == tok_inf.symbol()
            if by_name:
                include = include and by_name in tok_inf.name()
            if include:
                filtered_result.append(tok_inf)


class GetEstimateTradeFeeResponse(ResponseBase):
    def id(self):
        return self.get_result("ID")

    def fee_address(self):
        return self.get_result("FeeAddress")

    def sign_address(self) -> str:
        return self.get_result("SignAddress")

    def token_fee(self, level=None):
        if level:
            return self.get_result("TokenFees").get(f"Level{level}")
        return self.get_result("TokenFees")

    def prv_fee(self, level=None):
        if level:
            return self.get_result("PrivacyFees").get(f"Level{level}")
        return self.get_result("PrivacyFees")


class HistoryEntry(BlockChainInfoBaseClass):
    def id(self):
        return self.dict_data.get("id")

    def user_id(self):
        return self.dict_data.get("userID")

    def wallet_address(self):
        return self.dict_data.get("walletAddress")

    def sell_token(self):
        return self.dict_data.get("sellTokenId")

    def buy_token(self):
        return self.dict_data.get("buyTokenId")

    def src_symbol(self):
        return self.dict_data.get("srcSymbol")

    def dest_symbol(self):
        return self.dict_data.get("destSymbol")

    def src_contract_addr(self):
        return self.dict_data.get("srcContractAddress")

    def dest_contract_addr(self):
        return self.dict_data.get("destContractAddress")

    def amount(self):
        return self.dict_data.get("amount")

    def mint_accept(self):
        return self.dict_data.get("mintAccept")

    def amount_out(self):
        return self.dict_data.get("amountOut")

    def trading_path(self):
        return self.dict_data.get("tradingPath")

    def is_native(self):
        return self.dict_data.get("isNative")

    def status_code(self):
        return self.dict_data.get("statusCode")

    def status_detail(self):
        return self.dict_data.get("statusDetail")

    def user_fee_amount(self):
        return self.dict_data.get("userFeeAmount")

    def user_fee_lvl(self):
        return self.dict_data.get("userFeeLevel")

    def request_tx(self):
        return self.dict_data.get("requestTx")

    def submit_proof_tx(self):
        return self.dict_data.get("submitProofTx")

    def execute_swap_tx(self):
        return self.dict_data.get("executeSwapTx")

    def withdraw_tx(self):
        return self.dict_data.get("withdrawTx")

    def mint_tx(self):
        return self.dict_data.get("mintTx")

    def request_time(self):
        return self.dict_data.get("requestime")

    def response_txs(self):
        return self.dict_data.get("respondTxs")


class GetHistoryResponse(ResponseBase):
    def get_histories(self, **by):
        return [HistoryEntry(data) for data in self.get_result("History")]


class GetHistoryDetailResponse(ResponseBase, HistoryEntry):
    @property
    def dict_data(self):
        return self.get_result()
