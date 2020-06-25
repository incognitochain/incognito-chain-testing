import copy
from abc import ABC
from typing import List

from IncognitoChain.Configs.Constants import PORTAL_COLLATERAL_LIQUIDATE_PERCENT, \
    PORTAL_COLLATERAL_LIQUIDATE_TO_POOL_PERCENT, PBNB_ID, PBTC_ID, PRV_ID
from IncognitoChain.Helpers.Logging import INFO, DEBUG
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT


class PortalInfoObj(ABC):
    def __init__(self, dict_data=None):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data: dict = dict_data
        self.err = None
        self.SUT = SUT

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

    @classmethod
    def _extract_incognito_addr(cls, obj):
        from IncognitoChain.Objects.AccountObject import Account
        if type(obj) == str:
            addr = obj
        elif type(obj) == Account:
            addr = obj.incognito_addr
        elif type(obj) == CustodianInfo:
            addr = obj.get_incognito_addr()
        else:
            raise TypeError("Input must be incognito address (string), CustodianInfo or Account object")
        return addr


class CustodianInfo(PortalInfoObj):

    def __str__(self):
        # 'Custodian - bnb remote addr - btc remote add - total collateral - free collateral -
        # holding bnb - holding btc - lock bnb - lock btc - reward prv'
        s_inc_addr = s_bnb_addr = s_btc_addr = '-'
        total_col = free_col = hold_bnb = hold_btc = lock_bnb = lock_btc = reward_prv = 0
        try:
            s_inc_addr = l6(self.get_incognito_addr())
        except (KeyError, TypeError):
            pass
        try:
            s_bnb_addr = l6(self.get_remote_address(PBNB_ID))
        except (KeyError, TypeError):
            pass
        try:
            s_btc_addr = l6(self.get_remote_address(PBTC_ID))
        except (KeyError, TypeError):
            pass
        try:
            total_col = self.get_total_collateral()
        except (KeyError, TypeError):
            pass
        try:
            free_col = self.get_free_collateral()
        except (KeyError, TypeError):
            pass
        try:
            hold_bnb = self.get_holding_token_amount(PBNB_ID)
        except (KeyError, TypeError):
            pass
        try:
            hold_btc = self.get_holding_token_amount(PBTC_ID)
        except (KeyError, TypeError):
            pass
        try:
            lock_bnb = self.get_locked_collateral(PBNB_ID)
        except(KeyError, TypeError):
            pass
        try:
            lock_btc = self.get_locked_collateral(PBTC_ID)
        except (KeyError, TypeError):
            pass
        try:
            reward_prv = self.get_reward_amount(PRV_ID)
        except (KeyError, TypeError):
            pass
        return '%s : %6s/%6s %14s %14s %14s %14s %14s %14s %14s' % \
               (s_inc_addr, s_bnb_addr, s_btc_addr, total_col, free_col, hold_bnb, hold_btc, lock_bnb, lock_btc,
                reward_prv)

    def get_incognito_addr(self):
        try:
            return self.data['IncognitoAddress']  # this only exists in custodian pool
        except KeyError:
            return self.data['IncAddress']  # this only exists porting req

    def extract_new_info(self, portal_state_info, incognito_addr=None):
        portal_state_info: PortalStateInfo
        if incognito_addr is None:
            self.data = portal_state_info.get_custodian_info_in_pool(self.get_incognito_addr()).data
        else:
            self.data = portal_state_info.get_custodian_info_in_pool(incognito_addr).data
        return self

    def get_total_collateral(self):
        ret = self.data['TotalCollateral']
        return int(ret)

    def get_free_collateral(self):
        return int(self.data['FreeCollateral'])

    def get_holding_tokens(self):
        return self.data['HoldingPubTokens']

    def get_holding_token_amount(self, token_id):
        try:
            return int(self.get_holding_tokens()[token_id])
        except (KeyError, TypeError):
            DEBUG(f"{l6(token_id)} not found in HoldingPubTokens")
            return 0

    def get_locked_collateral(self, token_id=None):
        """

        :param token_id:
        :param none_equal_zero: set to false if you want to check if the the token is existed in LockedAmountCollateral
                or not
        :return: amount of locked collateral. If LockedAmountCollateral of token is not exist in data
                and none_equal_zero is true, then return 0, else return None
        """
        if token_id is None:
            ret = self.data['LockedAmountCollateral']
        else:
            try:
                ret = int(self.data['LockedAmountCollateral'][token_id])
            except (KeyError, TypeError):
                ret = 0
        return ret

    def get_remote_address(self, token=None):
        if token is None:
            return self.data['RemoteAddress']
        try:
            return self.data['RemoteAddresses'][token]
        except KeyError:
            return ""

    def get_reward_amount(self, token_id=None):
        if token_id is None:
            return self.data['RewardAmount']
        return int(self.data['RewardAmount'][token_id])

    def shall_i_be_liquidize_with_new_rate(self, token_id, new_tok_rate, new_prv_rate,
                                           additional_holding=0, additional_collateral=0):
        """

        :param new_tok_rate:
        :param new_prv_rate:
            when collateral <= liquidation_percent (120% by default) of token price in prv, collateral will be liquidize
        :param token_id: token to check, bnb or btc
        :param additional_collateral: in case you want to check the after more holding token added
        :param additional_holding: in case you want to check the after more holding token added
        :return:
        """
        prv_collateral_current = self.get_locked_collateral(token_id) + additional_collateral
        holding_token = self.get_holding_token_amount(token_id) + additional_holding

        if holding_token is None or holding_token == 0:
            return False
        holding_tok_in_prv_new_rate = PortalHelper.cal_portal_exchange_tok_to_prv(holding_token, new_tok_rate,
                                                                                  new_prv_rate)
        new_collateral = holding_tok_in_prv_new_rate * PORTAL_COLLATERAL_LIQUIDATE_PERCENT
        if prv_collateral_current <= new_collateral:
            return True
        return False

    def wait_my_lock_collateral_to_change(self, token_id, from_amount=None, check_rate=30, timeout=180):
        portal_state_info = self.SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
        my_new_status = portal_state_info.get_custodian_info_in_pool(self)

        if my_new_status is None:
            INFO("You're not even a custodian")
            return None
        if from_amount is None:
            collateral_before = my_new_status.get_locked_collateral(token_id)
        else:
            collateral_before = from_amount
        current_collateral = collateral_before
        time = 0
        while current_collateral == collateral_before:
            portal_state_info = self.SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
            my_new_status = portal_state_info.get_custodian_info_in_pool(self)
            if time >= timeout:
                INFO(f'Lock collateral does not change in the last {time}s')
                return 0
            WAIT(check_rate)
            time += check_rate
            current_collateral = my_new_status.get_locked_collateral(token_id)

        delta = current_collateral - collateral_before
        INFO(f'Lock collateral has change {delta}')
        return delta


class PortingReqInfo(PortalInfoObj):
    """
    response of "getportalportingrequestbykey"
             or "getportalportingrequestbyportingid"
             or "getportalreqptokenstatus"
    """

    def __str__(self):
        custodian_list = self.get_custodians()
        cust_short = {}
        for cust in custodian_list:
            cust_short[l6(cust.get_incognito_addr())] = l6(cust.get_remote_address())

        return f"""
            Porting id = {self.get_porting_id()},
            amount = {self.get_amount()},
            fee = {self.get_porting_fee()}
            custodian = {cust_short}"""

    def get_porting_req_by_tx_id(self, tx_id):
        INFO()
        INFO(f'Get porting req info, tx_id = {tx_id}')
        response = self.SUT.full_node.portal().get_portal_porting_req_by_key(tx_id)
        self.data = response.get_result('PortingRequest')
        return self

    def get_porting_req_by_porting_id(self, porting_id):
        self.data = self.SUT.full_node.portal().get_portal_porting_req_by_porting_id(porting_id).get_result(
            'PortingRequest')
        return self

    def get_porting_id(self):
        return self.data['UniquePortingID']

    def get_tx_req_id(self):
        return self.data['TxReqID']

    def get_porter_address(self):
        return self.data['PorterAddress']

    def get_custodians(self):
        custodian_info_list = self.data['Custodians']
        result = []
        for info in custodian_info_list:
            result.append(CustodianInfo(info))
        return result

    def get_custodian(self, custodian):
        """

        :param custodian: CustodianInfo or Account or incognito addr
        :return:
        """
        addr = self._extract_incognito_addr(custodian)

        custodian_list = self.get_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_porting_fee(self):
        return int(self.data['PortingFee'])

    def get_beacon_height(self):
        return int(self.data['BeaconHeight'])


class RedeemReqInfo(PortalInfoObj):

    def get_redeem_status_by_redeem_id(self, redeem_id):
        self.data = self.SUT.full_node.portal().get_portal_redeem_status(redeem_id).get_result()
        return self

    def get_req_matching_redeem_status(self, tx_id):
        self.data = self.SUT.full_node.portal().get_req_matching_redeem_status(tx_id).get_result()
        return self

    def get_redeem_matching_custodians(self):
        try:
            custodian_dict = self.data['MatchingCustodianDetail']
        except KeyError:
            custodian_dict = self.data['Custodians']

        custodian_obj_list = []
        for item in custodian_dict:
            cus = CustodianInfo(item)
            custodian_obj_list.append(cus)
        return custodian_obj_list

    def get_custodian(self, custodian):
        """

        :param custodian: CustodianInfo or Account or incognito addr
        :return:
        """
        addr = self._extract_incognito_addr(custodian)
        custodian_list = self.get_redeem_matching_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_redeem_amount(self):
        return int(self.data['RedeemAmount'])


class LiquidationPool(PortalInfoObj):
    """
    data sample:
     {
         "a1cd299965f5f6fe5e870709515d6cc2dc4254bf55184f6bdbd71383133bc421": {
            "Rates": {
               "b2655152784e8639fa19521a7035f331eea1f1e911b2f3200a507ebb4554387b": {
                  "CollateralAmount": 3291170,
                  "PubTokenAmount": 1000
               }
               "b832e5d3b1f01a4f0623f7fe91d6673461e1f5d37d91fe78c5c2e6183ff39696": {
                  "CollateralAmount": 234256,
                  "PubTokenAmount": 12000
               }
            }
         }
     }
    """
    _collateral = 'CollateralAmount'
    _token_amount = 'PubTokenAmount'
    _rates = 'Rates'
    _estimate = 'estimate'

    def __add__(self, other):
        sum_obj = LiquidationPool()

        my_tok_list = self._get_token_set()
        other_tok_list = other._get_token_set()
        tok_list = list(my_tok_list) + list(other_tok_list - my_tok_list)
        for tok in tok_list:
            sum_collateral = self.get_collateral_amount_of_token(tok) + other.get_collateral_amount_of_token(tok)
            sum_public_tok = self.get_public_token_amount_of_token(tok) + other.get_public_token_amount_of_token(tok)
            sum_obj.set_collateral_amount_of_token(tok, sum_collateral)
            sum_obj.set_public_token_amount_of_token(tok, sum_public_tok)
        return sum_obj

    def __sub__(self, other):
        sub_obj = LiquidationPool()

        my_tok_list = self._get_token_set()
        other_tok_list = other._get_token_set()
        tok_list = list(my_tok_list) + list(other_tok_list - my_tok_list)

        for tok in tok_list:
            sum_collateral = self.get_collateral_amount_of_token(tok) - other.get_collateral_amount_of_token(tok)
            sum_public_tok = self.get_public_token_amount_of_token(tok) - other.get_public_token_amount_of_token(tok)
            sub_obj.set_collateral_amount_of_token(tok, sum_collateral)
            sub_obj.set_public_token_amount_of_token(tok, sum_public_tok)
        return sub_obj

    def __eq__(self, other):
        my_data_copy = copy.deepcopy(self.data)
        _, my_rates = my_data_copy.popitem()

        other_data_copy = copy.deepcopy(other.data)
        _, other_rates = other_data_copy.popitem()
        return my_rates == other_rates

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_more_public_token(self, token_id, amount):
        new_amount = self.get_public_token_amount_of_token(token_id) + amount
        self.set_public_token_amount_of_token(token_id, new_amount)

    def add_more_collateral(self, token_id, amount):
        new_amount = self.get_collateral_amount_of_token(token_id) + amount
        self.set_collateral_amount_of_token(token_id, new_amount)

    def get_collateral_amount_of_token(self, token_id):
        rates = self.get_rate_of_token(token_id)
        return rates[LiquidationPool._collateral] if rates is not None else None

    def set_collateral_amount_of_token(self, token_id, amount):
        if type(self.data) is not dict:
            self.data = {LiquidationPool._estimate: {}}
            self.data[LiquidationPool._estimate][
                LiquidationPool._rates] = {}  # possible bug here since this dict level could contains 2 token_id here
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id] = {}

        try:
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id][LiquidationPool._collateral] = amount
        except KeyError:
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id] = {}
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id][LiquidationPool._collateral] = amount

        return self

    def get_public_token_amount_of_token(self, token_id):
        rates = self.get_rate_of_token(token_id)
        return rates[LiquidationPool._token_amount] if rates is not None else None

    def set_public_token_amount_of_token(self, token_id, amount):
        if type(self.data) is not dict:
            self.data = {LiquidationPool._estimate: {}}
            self.data[LiquidationPool._estimate][
                LiquidationPool._rates] = {}  # possible bug here since this dict level could contains 2 token_id here
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id] = {}

        try:
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id][
                LiquidationPool._token_amount] = amount
        except KeyError:
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id][
                LiquidationPool._token_amount] = amount
            self.data[LiquidationPool._estimate][LiquidationPool._rates][token_id][
                LiquidationPool._token_amount] = amount
        return self

    def get_rate_of_token(self, token_id):
        rates = self.get_rates()
        return None if rates is None else self.get_rates()[LiquidationPool._rates][token_id]

    def get_rates(self):
        if self.data == {}:
            return None
        clone = copy.deepcopy(self.data)
        _, rates = clone.popitem()
        return rates

    def get_pool_id(self):
        clone = copy.deepcopy(self.data)
        key, _ = clone.popitem()
        return key

    def _get_token_set(self):
        rates = self.get_rates()['Rates']
        tok_list = set()
        for token, _ in rates.items():
            tok_list.add(token)
        return tok_list


class PTokenReqInfo(PortalInfoObj):
    def get_ptoken_req_by_tx_id(self, tx_id):
        self.data = self.SUT.full_node.portal().get_portal_req_ptoken_status(tx_id).get_result()
        return self


class PortalStateInfo(PortalInfoObj):
    def get_custodian_pool(self) -> List[CustodianInfo]:
        custodian_pool = self.data['CustodianPool']
        custodian_list = [CustodianInfo(value) for key, value in custodian_pool.items()]
        return custodian_list

    def get_custodian_info_in_pool(self, custodian_info):
        """

        :param custodian_info: incognito address or CustodianInfo obj
        :return:
        """
        addr = self._extract_incognito_addr(custodian_info)
        pool = self.get_custodian_pool()
        for custodian in pool:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_portal_rate(self, token_id=None):
        if token_id is None:
            return self.data['FinalExchangeRatesState']['Rates']
        else:
            return int(self.data['FinalExchangeRatesState']['Rates'][token_id]['Amount'])

    def print_rate(self):
        rate = self.get_portal_rate()
        print(f'    ===== Rates =====    ')
        rate_short = {}
        for k, v in rate.items():
            rate_short[k] = v
            print(f'   {l6(k)} : {v}')
        return rate_short

    def get_porting_waiting_req(self, token_id=None) -> List[PortingReqInfo]:
        req_list = []
        req_data_raw = self.data['WaitingPortingRequests']
        for req_raw in req_data_raw.values():
            req = PortingReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)
        return req_list

    def get_redeem_waiting_req(self, token_id=None) -> List[RedeemReqInfo]:
        req_list = []
        req_data_raw = self.data['WaitingRedeemRequests']
        for req_raw in req_data_raw.values():
            req = RedeemReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)
        return req_list

    def get_redeem_matched_req(self, token_id=None) -> List[RedeemReqInfo]:
        req_list = []
        req_data_raw = self.data['MatchedRedeemRequests']
        for req_raw in req_data_raw.values():
            req = RedeemReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)
        return req_list

    def get_liquidation_pool(self) -> LiquidationPool:
        pool_data = self.data['LiquidationPool']
        return LiquidationPool(pool_data)

    def help_get_highest_free_collateral_custodian(self):
        custodian_pool = self.get_custodian_pool()
        highest_free_collateral_custodian_info = custodian_pool[0]
        for info in custodian_pool:
            if info.get_free_collateral() > highest_free_collateral_custodian_info.get_free_collateral():
                highest_free_collateral_custodian_info = info

        return highest_free_collateral_custodian_info

    def sum_locked_collateral_of_token(self, token_id):
        sum_locked_collateral = 0
        custodians = self.get_custodian_pool()
        if custodians is None:
            return 0
        for custodian in custodians:
            incr = custodian.get_locked_collateral(token_id)
            sum_locked_collateral += incr
        return sum_locked_collateral

    def sum_holding_token_matched_redeem_req(self, token_id, custodian_account):
        sum_holding = 0
        if custodian_account is None:
            waiting_redeem_reqs = self.get_redeem_matched_req(token_id)
        else:
            waiting_redeem_reqs = self.find_all_matched_redeem_req_of_custodian(token_id, custodian_account)

        if waiting_redeem_reqs is None:
            return 0
        for req in waiting_redeem_reqs:
            custodians_of_req = req.get_redeem_matching_custodians()
            if custodians_of_req is not None:
                for custodian in custodians_of_req:
                    holding = custodian.get_holding_token_amount(token_id)
                    holding = 0 if holding is None else holding
                    sum_holding += holding
        return sum_holding

    def sum_holding_of_token(self, token_id):
        sum_holding = 0
        custodians = self.get_custodian_pool()
        if custodians is None:
            return 0
        for custodian in custodians:
            incr = custodian.get_holding_token_amount(token_id)
            incr = incr if incr is not None else 0
            sum_holding += incr
        return sum_holding

    def sum_collateral_porting_waiting(self, token_id, custodian=None):
        sum_collateral = 0
        if custodian is None:
            porting_waiting_reqs = self.get_porting_waiting_req(token_id)
        else:
            porting_waiting_reqs = self.find_all_wait_porting_req_of_custodian(token_id, custodian)

        if porting_waiting_reqs is None:
            return 0
        for req in porting_waiting_reqs:
            custodians_of_req = req.get_custodians()
            for custodian in custodians_of_req:
                sum_collateral += custodian.get_locked_collateral()
        return sum_collateral

    def sum_holding_token_waiting_redeem_req(self, token_id, custodian_account=None):
        sum_holding = 0
        if custodian_account is None:
            waiting_redeem_reqs = self.get_redeem_waiting_req(token_id)
        else:
            waiting_redeem_reqs = self.find_all_wait_redeem_req_of_custodian(token_id, custodian_account)

        if waiting_redeem_reqs is None:
            return 0
        for req in waiting_redeem_reqs:
            custodians_of_req = req.get_redeem_matching_custodians()
            if custodians_of_req is not None:
                for custodian in custodians_of_req:
                    sum_holding += custodian.get_holding_token_amount(token_id)
        return sum_holding

    def find_custodians_will_be_liquidate_with_new_rate(self, token_id, new_token_rate, new_prv_rate):
        custodians = self.get_custodian_pool()
        liquidating_list = []
        for custodian in custodians:
            if custodian.shall_i_be_liquidize_with_new_rate(token_id, new_token_rate, new_prv_rate):
                liquidating_list.append(custodian)
        return liquidating_list

    def estimate_liquidation_pool(self, token_id, new_token_rate, new_prv_rate) -> LiquidationPool:
        liquidating_custodian = self.find_custodians_will_be_liquidate_with_new_rate(token_id, new_token_rate,
                                                                                     new_prv_rate)
        estimate_liquidate_pool = LiquidationPool()
        estimate_liquidate_pool.set_public_token_amount_of_token(token_id, 0)
        estimate_liquidate_pool.set_collateral_amount_of_token(token_id, 0)
        if not liquidating_custodian:  # liquidate_custodian is empty
            return estimate_liquidate_pool

        for custodian in liquidating_custodian:
            my_holding_token = custodian.get_holding_token_amount(token_id)
            liquidated_collateral, _ = self.estimate_liquidation_of_custodian(custodian, token_id, new_token_rate,
                                                                              new_prv_rate)

            estimate_liquidate_pool.add_more_public_token(token_id, my_holding_token)
            estimate_liquidate_pool.add_more_collateral(token_id, liquidated_collateral)

        return estimate_liquidate_pool

    def find_all_wait_porting_req_of_custodian(self, token_id, custodian_account):
        porting_waiting_req = self.get_porting_waiting_req(token_id)
        return PortalStateInfo._find_all_req_of_custodian_in_req_list(custodian_account, porting_waiting_req)

    def find_all_wait_redeem_req_of_custodian(self, token_id, custodian_account):
        redeem_waiting_req = self.get_redeem_waiting_req(token_id)
        return PortalStateInfo._find_all_req_of_custodian_in_req_list(custodian_account, redeem_waiting_req)

    def find_all_matched_redeem_req_of_custodian(self, token_id, custodian_account):
        redeem_matched_req = self.get_redeem_matched_req(token_id)
        return PortalStateInfo._find_all_req_of_custodian_in_req_list(custodian_account, redeem_matched_req)

    def find_lowest_free_collateral_custodian(self):
        pool = self.get_custodian_pool()
        custodian_min_free_collateral = pool[0]
        for custodian in pool:
            if custodian.get_free_collateral() < custodian_min_free_collateral.get_free_collateral():
                custodian_min_free_collateral = custodian

        return custodian_min_free_collateral

    @staticmethod
    def _find_all_req_of_custodian_in_req_list(custodian_account, req_list):
        result = []
        for req in req_list:
            if req.get_custodian(custodian_account) is not None:
                result.append(req)
        return result

    def estimate_liquidation_of_custodian(self, custodian, token_id, new_token_rate, new_prv_rate,
                                          additional_holding=0, additional_collateral=0):
        """
        Estimate liquidate collateral and return collateral of custodian
        :param additional_collateral:
        :param additional_holding:
        :param custodian:a CustodianInfo, Account object or incognito addr of custodian
        :param token_id:
        :param new_token_rate:
        :param new_prv_rate:
        :return:
        """
        my_holding_token = custodian.get_holding_token_amount(token_id)
        lock_collateral_minus_waiting_porting = \
            self._lock_collateral_minus_waiting_porting_of_custodian(custodian, token_id) + additional_collateral

        waiting_redeem_holding_tok = \
            self.sum_holding_token_waiting_redeem_req(token_id, custodian.get_incognito_addr())
        sum_holding_tok = my_holding_token + waiting_redeem_holding_tok + additional_holding

        holding_token_in_prv_new_rate = PortalHelper.cal_portal_exchange_tok_to_prv(sum_holding_tok, new_token_rate,
                                                                                    new_prv_rate)
        estimated_liquidated_collateral = int(
            PORTAL_COLLATERAL_LIQUIDATE_TO_POOL_PERCENT * holding_token_in_prv_new_rate)
        if lock_collateral_minus_waiting_porting > estimated_liquidated_collateral:
            collateral_return_to_custodian = lock_collateral_minus_waiting_porting - estimated_liquidated_collateral
            liquidate_amount = estimated_liquidated_collateral
        else:
            collateral_return_to_custodian = 0
            liquidate_amount = lock_collateral_minus_waiting_porting
        return liquidate_amount, collateral_return_to_custodian

    def _lock_collateral_minus_waiting_porting_of_custodian(self, custodian, token_id):
        sum_waiting_porting_collateral = self.sum_collateral_porting_waiting(token_id, custodian)
        return custodian.get_locked_collateral(token_id) - sum_waiting_porting_collateral


class UnlockCollateralReqInfo(PortalInfoObj):
    def get_unlock_collateral_req_stat(self, tx_id):
        self.data = self.SUT.full_node.portal().get_portal_req_unlock_collateral_status(tx_id).get_result()

    def get_unlock_amount(self):
        return int(self.data['UnlockAmount'])


class DepositTxInfo(PortalInfoObj):
    _amount = 'DepositedAmount'

    def get_deposit_info(self, tx_id):
        self.data = self.SUT.full_node.portal().get_portal_custodian_deposit_status(tx_id).get_result()
        return self

    def get_deposited_amount(self):
        return self.data[DepositTxInfo._amount]


class CustodianWithdrawTxInfo(PortalInfoObj):
    _info = 'CustodianWithdraw'
    _payment_addr = 'PaymentAddress'
    _remain_free_collateral = 'RemainCustodianFreeCollateral'

    def get_custodian_withdraw_info_by_tx(self, tx_id):
        self.data = self.SUT.full_node.portal().get_custodian_withdraw_by_tx_id(tx_id). \
            get_result()[CustodianWithdrawTxInfo._info]
        return self

    def get_payment_addr(self):
        return self.data[CustodianWithdrawTxInfo._payment_addr]

    def get_remain_free_collateral(self):
        return self.data[CustodianWithdrawTxInfo._remain_free_collateral]


class RewardWithdrawTxInfo(PortalInfoObj):
    _CustodianAddressStr = 'CustodianAddressStr'
    _RewardAmount = 'RewardAmount'
    _TxReqID = 'TxReqID'

    def get_reward_info_by_tx_id(self, tx_id):
        self.data = self.SUT.full_node.portal().get_request_withdraw_portal_reward_status(tx_id).get_result()
        return self

    def get_custodian_addr_str(self):
        return self.data[RewardWithdrawTxInfo._CustodianAddressStr]

    def get_reward_amount(self):
        return self.data[RewardWithdrawTxInfo._RewardAmount]

    def get_tx_req_id(self):
        return self.data[RewardWithdrawTxInfo._TxReqID]
