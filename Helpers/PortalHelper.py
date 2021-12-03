from Configs.Configs import ChainConfig
from Configs.Constants import Status
from Helpers.Logging import config_logger
from Helpers.TestHelper import to_num

logger = config_logger(__name__)


class PortalMath:

    @staticmethod
    def cal_lock_collateral(token_amount, token_rate, prv_rate):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        estimated_lock_collateral = int(
            int(token_amount * ChainConfig.Portal.COLLATERAL_PERCENT) * token_rate // prv_rate)
        logger(f'''Calculating lock collateral: 
            token amount: {token_amount}, 
            token rate:   {token_rate}, 
            prv rate:     {prv_rate},
            lock amount:  {estimated_lock_collateral} 
        -------------------------------------------------------------------''')
        return estimated_lock_collateral

    @staticmethod
    def cal_portal_exchange_tok_to_prv(token_amount, token_rate, prv_rate):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        return token_amount * token_rate // prv_rate

    @staticmethod
    def cal_portal_exchange_prv_to_tok(prv_amount, prv_rate, token_rate):
        prv_amount, prv_rate, token_rate = to_num(prv_amount, prv_rate, token_rate)
        return prv_amount * prv_rate // token_rate

    @staticmethod
    def cal_portal_portal_fee(token_amount, token_rate, prv_rate, fee_rate=0.0001):
        token_amount, token_rate, prv_rate = to_num(token_amount, token_rate, prv_rate)
        return round(token_amount * fee_rate * token_rate / prv_rate)  # fee = 0.01%

    @staticmethod
    def cal_liquidate_rate(percent, token_rate, prv_rate, change_token_rate=False):
        """
        @param percent:
        @param token_rate:
        @param prv_rate:
        @param change_token_rate: if true, return new token rate. otherwise , return new prv rate
        @return:
        """

        new_prv_rate = (percent * prv_rate) // ChainConfig.Portal.COLLATERAL_PERCENT
        new_tok_rate = (ChainConfig.Portal.COLLATERAL_PERCENT * token_rate) // percent

        if change_token_rate:
            logger.info(f'Current token rate {token_rate}, new rate {new_tok_rate}')
            return int(new_tok_rate)
        else:
            logger.info(f'Current prv rate {prv_rate}, new rate {new_prv_rate}')
            return int(new_prv_rate)

    @staticmethod
    def cal_rate_to_match_collateral_percent(percent, token_holding, prv_collateral, current_tok_rate,
                                             current_prv_rate, rate_return='token'):
        """

        @param current_tok_rate:
        @param current_prv_rate:
        @param percent:
        @param token_holding:
        @param prv_collateral:
        @param rate_return: select new rate to return, PRV or token
        @return:
        """

        new_prv_rate = int(current_tok_rate * percent * token_holding / prv_collateral)
        new_tok_rate = int(prv_collateral * current_prv_rate / percent / token_holding)

        if rate_return == 'token':
            logger.info(f'Current token rate {current_tok_rate}, new rate {new_tok_rate}')
            return int(new_tok_rate)
        else:
            logger.info(f'Current prv rate {current_prv_rate}, new rate {new_prv_rate}')
            return int(new_prv_rate)

    @staticmethod
    def cal_rate_to_liquidate_collateral(token_holding, prv_collateral, current_tok_rate,
                                         current_prv_rate, new_rate='token',
                                         liquidate_percent=ChainConfig.Portal.COLLATERAL_LIQUIDATE_PERCENT):
        """

        @param liquidate_percent:
        @param token_holding:
        @param prv_collateral:
        @param current_tok_rate:
        @param current_prv_rate:
        @param new_rate: 'token' or 'prv', to indicate which of the new rate you want to get
        @return:
        """
        if new_rate == 'token':
            return PortalMath.cal_rate_to_match_collateral_percent(
                liquidate_percent, token_holding, prv_collateral, current_tok_rate, current_prv_rate)
        else:
            return PortalMath.cal_rate_to_match_collateral_percent(
                liquidate_percent, token_holding, prv_collateral, current_tok_rate, current_prv_rate,
                rate_return='prv')

    @staticmethod
    def cal_liquidation_amount_of_collateral(holding_token, holding_token_of_waiting_redeem, rate_token, rate_prv):
        """
        @param rate_prv:
        @param rate_token:
        @param holding_token: of custodian
        @param holding_token_of_waiting_redeem: of custodian
        @return: (sum_holding * 1.05 * ratePubToken) / ratePRV
        """
        sum_holding = holding_token + holding_token_of_waiting_redeem
        return int(sum_holding * 1.05 * rate_token / rate_prv)

    @staticmethod
    def check_custodian_deposit_tx_status(tx_id, expected='accept'):
        from Objects.PortalObjects import DepositTxInfo

        info = DepositTxInfo()
        info.get_deposit_info(tx_id)
        if expected.lower() == "accept":
            assert info.get_status() == Status.Portal.DepositStatus.ACCEPT
        else:
            assert info.get_status() == Status.Portal.DepositStatus.REJECTED

    @staticmethod
    def cal_liquidation_of_porting(porting_amount, current_token_rate, current_prv_rate):
        porting_amount_in_new_prv_rate = PortalMath.cal_portal_exchange_tok_to_prv(porting_amount, current_token_rate,
                                                                                   current_prv_rate)

        estimate_lock_collateral = PortalMath.cal_lock_collateral(porting_amount, current_token_rate,
                                                                  current_prv_rate)
        estimated_liquidated_collateral = int(
            ChainConfig.Portal.COLLATERAL_LIQUIDATE_TO_POOL_PERCENT * porting_amount_in_new_prv_rate)
        return_collateral = estimate_lock_collateral - estimated_liquidated_collateral
        return int(estimated_liquidated_collateral), int(return_collateral)

    @staticmethod
    def cal_token_amount_from_collateral(collateral, token_rate, prv_rate):
        prv_equivalent = collateral // ChainConfig.Portal.COLLATERAL_PERCENT
        return int(PortalMath.cal_portal_exchange_prv_to_tok(prv_equivalent, prv_rate, token_rate))


class PortalV2Math:
    pass


class PortalV3Math:
    """
    Portal v3 helper:
    base token: token which use as collateral
    """

    @staticmethod
    def cal_lock_collateral(token_amount, token_rate, token_base_rate):
        pass

    @staticmethod
    def cal_portal_exchange_tok_to_base_tok(token_amount, token_rate, token_base_rate):
        pass

    @staticmethod
    def cal_portal_exchange_base_tok_to_tok(prv_amount, token_base_rate, token_rate):
        pass

    @staticmethod
    def cal_portal_portal_fee(token_amount, token_rate, token_base_rate, fee_rate=ChainConfig.Portal.FEE_RATE):
        pass

    @staticmethod
    def cal_liquidate_rate(percent, token_rate, token_base_rate, change_token_rate=False):
        """
        @param percent:
        @param token_rate:
        @param token_base_rate:
        @param change_token_rate: if true, return new token rate. otherwise , return new prv rate
        @return:
        """
        pass

    @staticmethod
    def cal_rate_to_match_collateral_percent(percent, token_holding, collateral_amount, current_tok_rate,
                                             current_tok_base_rate, rate_return='token'):
        """

        @param current_tok_rate:
        @param current_tok_base_rate:
        @param percent:
        @param token_holding:
        @param collateral_amount:
        @param rate_return: select new rate to return, base (token) or token
        @return:
        """
        pass

    @staticmethod
    def cal_rate_to_liquidate_collateral(token_holding, collateral_amount,
                                         current_tok_rate, current_tok_base_rate, new_rate='token',
                                         liquidate_percent=ChainConfig.Portal.COLLATERAL_LIQUIDATE_PERCENT):
        """

        @param liquidate_percent:
        @param token_holding:
        @param collateral_amount:
        @param current_tok_rate:
        @param current_tok_base_rate:
        @param new_rate: 'token' or 'base', to indicate which of the new rate you want to get
        @return:
        """
        pass

    @staticmethod
    def cal_liquidation_amount_of_collateral(holding_token, holding_token_of_waiting_redeem, rate_token,
                                             rate_token_base):
        """
        @param rate_token_base:
        @param rate_token:
        @param holding_token: of custodian
        @param holding_token_of_waiting_redeem: of custodian
        @return: (sum_holding * 1.05 * ratePubToken) / ratePRV
        """
        pass

    @staticmethod
    def cal_liquidation_of_porting(porting_amount, current_token_rate, current_token_base_rate):
        pass

    @staticmethod
    def cal_token_amount_from_collateral(collateral, token_rate, token_base_rate):
        pass
