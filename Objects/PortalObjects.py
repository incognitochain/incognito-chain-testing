import copy
import random
from typing import List

from Configs.Configs import ChainConfig
from Configs.Constants import PBNB_ID, PBTC_ID, PRV_ID, Status
from Helpers.Logging import config_logger
from Helpers.PortalHelper import PortalMath
from Helpers.TestHelper import l6, KeyExtractor
from Helpers.Time import WAIT
from Objects import BlockChainInfoBaseClass

logger = config_logger(__name__)


class _PortalInfoBase(BlockChainInfoBaseClass):

    def get_status(self):
        return self.dict_data['Status']

    def get_token_id(self):
        return self.dict_data['TokenID']

    def get_amount(self):
        return int(self.dict_data['Amount'])

    def is_none(self):
        if self.dict_data is None:
            return True
        return False


class PortingReqInfo(_PortalInfoBase):
    """
    response of "getportalportingrequestbykey"
             or "getportalportingrequestbyportingid"
             or "getportalreqptokenstatus"
    """

    def __str__(self):
        custodian_list = self.get_custodians()
        cust_short = ''
        for cust in custodian_list:
            cust_short += "%s/%s/%s/%s " % (
                l6(cust.get_incognito_addr()), l6(cust.get_remote_address()), cust.get_amount(),
                cust.get_locked_collateral())
        cust_short = cust_short.strip()

        return "id= %s, amount= %s, fee= %s custodian= %s" % (
            self.get_porting_id(), self.get_amount(), self.get_porting_fee(), cust_short)

    def get_porting_req_by_tx_id(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        logger.info()
        logger.info(f'Get porting req info, tx_id = {tx_id}')
        response = SUT().portal().get_portal_porting_req_by_key(tx_id)
        if self.is_none() and retry:
            WAIT(40)
            response = SUT().portal().get_portal_porting_req_by_key(tx_id)
        self.data = response.get_result('PortingRequest')
        return self

    def get_porting_req_by_porting_id(self, porting_id):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_portal_porting_req_by_porting_id(porting_id).get_result(
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
            result.append(PortalStateInfo.CustodianInfo(info))
        return result

    def get_custodian(self, custodian):
        """

        @param custodian: CustodianInfo or Account or incognito addr
        @return: CustodianInfo or None
        """
        addr = KeyExtractor.incognito_addr(custodian)

        custodian_list = self.get_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_porting_fee(self):
        return int(self.data['PortingFee'])

    def get_beacon_height(self):
        return int(self.data['BeaconHeight'])


class RedeemReqInfo(_PortalInfoBase):
    def __str__(self):
        custodian_list = self.get_redeem_matching_custodians()
        cust_short = ''
        for cust in custodian_list:
            cust_short += "%s/%s/%s " % (
                l6(cust.get_incognito_addr()), l6(cust.get_remote_address()), cust.get_amount())
        cust_short = cust_short.strip()

        return "id= %s, requester= %s, amount= %s, fee= %s, b height= %s, custodian: %s" % (
            self.get_redeem_id(), l6(self.get_requester()), self.get_redeem_amount(), self.get_redeem_fee(),
            self.get_beacon_height(), cust_short)

    def get_redeem_id(self):
        return self.data['UniqueRedeemID']

    def get_redeem_fee(self):
        return self.data['RedeemFee']

    def get_requester(self):
        try:
            return self.data['RedeemerAddress']
        except KeyError:
            return self.data['RedeemerRemoteAddress']

    def get_redeem_status_by_redeem_id(self, redeem_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_portal_redeem_status(redeem_id).get_result()
        if self.is_none() and retry:
            WAIT(40)
            self.data = SUT().portal().get_portal_redeem_status(redeem_id).get_result()
        return self

    def get_req_matching_redeem_status(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_req_matching_redeem_status(tx_id).get_result()
        if self.is_none() and retry:
            WAIT(40)
            self.data = SUT().portal().get_req_matching_redeem_status(tx_id).get_result()
        return self

    def get_redeem_matching_custodians(self):
        try:
            custodian_dict = self.data['MatchingCustodianDetail']
        except KeyError:
            custodian_dict = self.data['Custodians']

        custodian_obj_list = []
        for item in custodian_dict:
            cus = PortalStateInfo.CustodianInfo(item)
            custodian_obj_list.append(cus)
        return custodian_obj_list

    def get_custodian(self, custodian):
        """

        @param custodian: CustodianInfo or Account or incognito addr
        @return:
        """
        addr = KeyExtractor.incognito_addr(custodian)
        custodian_list = self.get_redeem_matching_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_redeem_amount(self):
        return int(self.data['RedeemAmount'])

    def get_beacon_height(self):
        try:
            return int(self.data['BeaconHeight'])
        except:
            pass


class RedeemMatchingInfo(_PortalInfoBase):
    def get_matching_amount(self):
        return self.data['MatchingAmount']

    def get_redeem_id(self):
        return self.data['RedeemID']

    def get_custodian_inc_addr(self):
        return self.data['CustodianAddressStr']

    def is_accepted(self):
        return self.get_status() == Status.Portal.RedeemMatchingStatus.ACCEPT

    def is_rejected(self):
        return self.get_status() == Status.Portal.RedeemMatchingStatus.REJECTED

    def get_matching_info_by_tx(self, tx_id):
        from Objects.IncognitoTestCase import SUT
        response = SUT().portal().get_req_matching_redeem_status(tx_id)
        if response.get_result() is None:  # retry after 40s if nothing return
            WAIT(10)
            response = SUT().portal().get_req_matching_redeem_status(tx_id)

        self.data = response.get_result()
        return self


class PTokenReqInfo(_PortalInfoBase):

    def get_ptoken_req_by_tx_id(self, tx_id):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_portal_req_ptoken_status(tx_id).get_result()
        return self


class PortalStateInfo(_PortalInfoBase):
    class CustodianInfo(_PortalInfoBase):

        def __str__(self):
            # 'Custodian - bnb remote addr - btc remote add - total collateral - free collateral -
            # holding bnb - holding btc - lock bnb - lock btc - reward prv'
            s_inc_addr = s_bnb_addr = s_btc_addr = '-'
            total_col = free_col = hold_bnb = hold_btc = lock_bnb = lock_btc = reward_prv = '-'
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
            try:
                ret = self.data['TotalCollateral']
                return int(ret)
            except TypeError as e:
                logger.error(f'{e}')
                return 0

        def get_free_collateral(self):
            return int(self.data['FreeCollateral'])

        def get_holding_tokens(self):
            return self.data['HoldingPubTokens']

        def get_holding_token_amount(self, token_id):
            try:
                return int(self.get_holding_tokens()[token_id])
            except (KeyError, TypeError):
                logger.debug(f"{l6(token_id)} not found in HoldingPubTokens")
                return 0

        def get_locked_collateral(self, token_id=None):
            """

            @param token_id:
            @return: amount of locked collateral of a token if token_id is specified. If token id is not specified,
                return a dictionary of {token_id: locked amount}
            """
            if token_id is None:
                all_collateral = self.data['LockedAmountCollateral']
                ret = {} if all_collateral is None else all_collateral
            else:
                try:
                    token_collateral = int(self.data['LockedAmountCollateral'][token_id])
                    ret = 0 if token_collateral is None else token_collateral
                except (KeyError, TypeError):
                    logger.debug('Not found LockedAmountCollateral in data, locked collateral not exist')
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

        def wait_my_lock_collateral_to_change(self, token_id, from_amount=None, check_rate=30, timeout=180):
            from Objects.IncognitoTestCase import SUT
            portal_state_info = SUT().get_latest_portal_state_info()
            my_new_status = portal_state_info.get_custodian_info_in_pool(self)

            if my_new_status is None:
                logger.info("You're not even a custodian")
                return None
            if from_amount is None:
                collateral_before = my_new_status.get_locked_collateral(token_id)
            else:
                collateral_before = from_amount
            current_collateral = collateral_before
            time = 0
            while current_collateral == collateral_before:
                portal_state_info = SUT().get_latest_portal_state_info()
                my_new_status = portal_state_info.get_custodian_info_in_pool(self)
                if time >= timeout:
                    logger.info(f'Lock collateral does not change in the last {time}s')
                    return 0
                WAIT(check_rate)
                time += check_rate
                current_collateral = my_new_status.get_locked_collateral(token_id)

            delta = current_collateral - collateral_before
            logger.info(f'Lock collateral has change {delta}')
            return delta

    class LiquidationPool(_PortalInfoBase):
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
            sum_obj = PortalStateInfo.LiquidationPool()

            my_tok_list = self._get_token_set()
            other_tok_list = other._get_token_set()
            tok_list = list(my_tok_list) + list(other_tok_list - my_tok_list)
            for tok in tok_list:
                sum_collateral = self.get_collateral_amount_of_token(tok) + other.get_collateral_amount_of_token(tok)
                sum_public_tok = self.get_public_token_amount_of_token(tok) + other.get_public_token_amount_of_token(
                    tok)
                sum_obj.set_collateral_amount_of_token(tok, sum_collateral)
                sum_obj.set_public_token_amount_of_token(tok, sum_public_tok)
            return sum_obj

        def __sub__(self, other):
            sub_obj = PortalStateInfo.LiquidationPool()

            my_tok_list = self._get_token_set()
            other_tok_list = other._get_token_set()
            tok_list = list(my_tok_list) + list(other_tok_list - my_tok_list)

            for tok in tok_list:
                sum_collateral = self.get_collateral_amount_of_token(tok) - other.get_collateral_amount_of_token(tok)
                sum_public_tok = self.get_public_token_amount_of_token(tok) - other.get_public_token_amount_of_token(
                    tok)
                sub_obj.set_collateral_amount_of_token(tok, sum_collateral)
                sub_obj.set_public_token_amount_of_token(tok, sum_public_tok)
            return sub_obj

        def __eq__(self, other):
            my_data_copy = copy.deepcopy(self.data)
            _, my_rates = my_data_copy.popitem()

            other_data_copy = copy.deepcopy(other.tok_info_obj_list)
            _, other_rates = other_data_copy.popitem()
            return my_rates == other_rates

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            ret = ""
            for token in self._get_token_set():
                ret += "token= %s, amount= %s, collateral = %s\n" % (
                    l6(token), self.get_public_token_amount_of_token(token), self.get_collateral_amount_of_token(token))
            return ret.strip('\n')

        def add_more_public_token(self, token_id, amount):
            new_amount = self.get_public_token_amount_of_token(token_id) + amount
            self.set_public_token_amount_of_token(token_id, new_amount)

        def add_more_collateral(self, token_id, amount):
            new_amount = self.get_collateral_amount_of_token(token_id) + amount
            self.set_collateral_amount_of_token(token_id, new_amount)

        def get_collateral_amount_of_token(self, token_id):
            try:
                rates = self.get_rate_of_token(token_id)
                return rates[PortalStateInfo.LiquidationPool._collateral] if rates is not None else 0
            except KeyError:
                return 0

        def set_collateral_amount_of_token(self, token_id, amount):
            if type(self.data) is not dict:
                self.data = {PortalStateInfo.LiquidationPool._estimate: {}}
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates] = {}
                # possible bug here since this dict level could contains 2 token_id here

                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][
                    token_id] = {}

            try:
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][token_id][
                    PortalStateInfo.LiquidationPool._collateral] = amount
            except KeyError:
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][
                    token_id] = {}
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][token_id][
                    PortalStateInfo.LiquidationPool._collateral] = amount

            return self

        def get_public_token_amount_of_token(self, token_id):
            try:
                rates = self.get_rate_of_token(token_id)
                return rates[PortalStateInfo.LiquidationPool._token_amount] if rates is not None else 0
            except KeyError:
                return 0

        def set_public_token_amount_of_token(self, token_id, amount):
            if type(self.data) is not dict:
                self.data = {PortalStateInfo.LiquidationPool._estimate: {}}
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates] = {}
                # possible bug here since this dict level could contains 2 token_id here
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][
                    token_id] = {}

            try:
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][token_id][
                    PortalStateInfo.LiquidationPool._token_amount] = amount
            except KeyError:
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][token_id][
                    PortalStateInfo.LiquidationPool._token_amount] = amount
                self.data[PortalStateInfo.LiquidationPool._estimate][PortalStateInfo.LiquidationPool._rates][token_id][
                    PortalStateInfo.LiquidationPool._token_amount] = amount
            return self

        def get_rate_of_token(self, token_id):
            rates = self.get_rates()
            return None if rates is None else self.get_rates()[PortalStateInfo.LiquidationPool._rates][token_id]

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
            tok_list = set()
            if self.get_rates() is None:
                return tok_list
            rates = self.get_rates()['Rates']
            for token, _ in rates.items():
                tok_list.add(token)
            return tok_list

    def get_custodian_pool(self) -> List[CustodianInfo]:
        custodian_pool = self.dict_data['CustodianPool']
        custodian_list = [PortalStateInfo.CustodianInfo(value) for key, value in custodian_pool.items()]
        return custodian_list

    def get_custodian_info_in_pool(self, custodian_info):
        """

        @param custodian_info: incognito address, Account, or CustodianInfo obj
        @return:
        """
        addr = KeyExtractor.incognito_addr(custodian_info)
        pool = self.get_custodian_pool()
        for custodian in pool:
            if custodian.get_incognito_addr() == addr:
                return custodian
        return None

    def get_portal_rate(self, token_id=None):
        try:
            if token_id is None:
                return self.dict_data['FinalExchangeRatesState']['Rates']
            else:
                return int(self.dict_data['FinalExchangeRatesState']['Rates'][token_id]['Amount'])
        except KeyError:
            logger.error(f'Cannot find portal rate of token {token_id}, assume rate = 0')
            return 0

    def print_rate(self):
        rate = self.get_portal_rate()
        print(f'    ===== Rates =====    ')
        for k, _ in rate.items():
            print(f'   {l6(k)} : {self.get_portal_rate(k)}')

    def print_state(self):
        wait_porting = self.get_porting_waiting_req()
        wait_redeems = self.get_redeem_waiting_req()
        match_redeems = self.get_redeem_matched_req()
        pool = self.get_custodian_pool()
        rate: dict = self.get_portal_rate()
        liquidate = self.get_liquidation_pool()
        logger.info(f'!!!!! ===== Portal state summary ===== !!!!!')
        logger.info("Wait porting requests")
        for req in wait_porting:
            logger.info(req)
        logger.info('Waiting redeem requests')
        for req in wait_redeems:
            logger.info(req)

        logger.info('Matched redeem requests')
        for req in match_redeems:
            logger.info(req)

        logger.info(f'Custodian Pool')
        logger.info("%6s : %6s/%6s %14s %14s %14s %14s %14s %14s %14s" %
             ('addr', 'bnb', 'btc', 'total col', 'free col', 'hold bnb', 'hold btc', 'lock bnb',
              'lock btc', 'reward prv'))
        for cus in pool:
            logger.info(cus)

        if rate is not None:
            logger.info(f'Portal rate')
            for k, _ in rate.items():
                logger.info(f'   {l6(k)} : {self.get_portal_rate(k)}')

        logger.info(f'Liquidation pool \n\t\t {liquidate}')

        logger.info('--------------- End summary -----------------')

    def get_porting_waiting_req(self, token_id=None) -> List[PortingReqInfo]:
        req_list = []
        req_data_raw = self.dict_data['WaitingPortingRequests']
        for req_raw in req_data_raw.values():
            req = PortingReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)
        return req_list

    def get_redeem_waiting_req(self, token_id=None) -> List[RedeemReqInfo]:
        req_list = []
        req_data_raw = self.dict_data['WaitingRedeemRequests']
        for req_raw in req_data_raw.values():
            req = RedeemReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)
        return req_list

    def get_redeem_matched_req(self, token_id=None, custodian=None) -> List[RedeemReqInfo]:
        req_list = []
        req_data_raw = self.dict_data['MatchedRedeemRequests']
        for req_raw in req_data_raw.values():
            req = RedeemReqInfo(req_raw)
            if token_id is not None and req.get_token_id() == token_id:
                req_list.append(req)
            else:
                req_list.append(req)

        if custodian is not None:  # find matching req which belong to custodian
            req_tok_addr = []
            inc_addr = KeyExtractor.incognito_addr(custodian)
            for req in req_list:
                cus_of_req = req.get_custodian(custodian)
                if cus_of_req is not None:
                    if cus_of_req.get_incognito_addr() == inc_addr:
                        req_tok_addr.append(req)
            return req_tok_addr

        return req_list

    def get_liquidation_pool(self) -> LiquidationPool:
        pool_data = self.dict_data['LiquidationPool']
        return PortalStateInfo.LiquidationPool(pool_data)

    def help_get_highest_free_collateral_custodian(self):
        custodian_pool = self.get_custodian_pool()
        highest_custodian = custodian_pool[0]
        for info in custodian_pool:
            if info.get_free_collateral() > highest_custodian.get_free_collateral():
                highest_custodian = info

        return highest_custodian

    def help_get_highest_holding_token_custodian(self, token_id):
        custodian_pool = self.get_custodian_pool()
        highest_custodian = custodian_pool[0]
        for info in custodian_pool:
            if info.get_holding_token_amount(token_id) > highest_custodian.get_holding_token_amount(token_id):
                highest_custodian = info
        return highest_custodian

    def help_sort_custodian_by_holding_token_desc(self, token_id):
        return self.get_custodian_pool().sort(key=lambda custodian: self.get_custodian_info_in_pool(
            custodian).get_holding_token_amount(token_id))

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
            if self.will_custodian_be_liquidated_with_new_rate(custodian, token_id, new_token_rate, new_prv_rate):
                liquidating_list.append(custodian)
        return liquidating_list

    def estimate_liquidation_pool_with_new_rate(self, token_id, new_token_rate, new_prv_rate) -> LiquidationPool:
        liquidating_custodian = self.find_custodians_will_be_liquidate_with_new_rate(token_id, new_token_rate,
                                                                                     new_prv_rate)
        estimate_liquidate_pool = PortalStateInfo.LiquidationPool()
        estimate_liquidate_pool.set_public_token_amount_of_token(token_id, 0)
        estimate_liquidate_pool.set_collateral_amount_of_token(token_id, 0)
        if not liquidating_custodian:  # liquidate_custodian is empty
            return estimate_liquidate_pool

        for custodian in liquidating_custodian:
            my_holding_token = custodian.get_holding_token_amount(token_id)
            liquidated_collateral, _ = self. \
                estimate_liquidation_of_custodian_with_new_rate(custodian, token_id, new_token_rate, new_prv_rate)

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

    def find_custodian_with_holding_token_amount(self, token_id, holding_amount):
        """
        @param token_id:
        @param holding_amount:
        @return: CustodianInfo who holds specific <holding_amount> of <token_id>
        """
        pool = self.get_custodian_pool()
        for custodian in pool:
            if custodian.get_holding_token_amount(token_id) == holding_amount:
                return custodian
        return None

    def find_custodian_hold_more_than_amount(self, token_id, holding_amount):
        """

        @param token_id:
        @param holding_amount:
        @return: List of CustodianInfo who holds <token_id> with amount > <holding_amount>
        """
        pool = self.get_custodian_pool()
        list_custodian = []
        for custodian in pool:
            if custodian.get_holding_token_amount(token_id) > holding_amount:
                list_custodian.append(custodian)
        return list_custodian

    def get_a_random_custodian(self, token=None):
        """
        get a random custodian in pool
        @param token: if specified return custodian who holding 'token' > 0
        @return:
        """
        custodian_pool = self.get_custodian_pool()
        random_index = random.randrange(0, len(custodian_pool))
        if token is not None:
            for i in range(0, 10):
                if custodian_pool[random_index].get_holding_token_amount(token) > 0:
                    break
                random_index = random.randrange(0, len(custodian_pool))
        return custodian_pool[random_index]

    @staticmethod
    def _find_all_req_of_custodian_in_req_list(custodian_account, req_list):
        result = []
        for req in req_list:
            if req.get_custodian(custodian_account) is not None:
                result.append(req)
        return result

    def calculate_liquidation_of_custodian_with_current_rate(self, custodian, token_id, porting_amount=0,
                                                             porting_collateral=0):
        """
        ONLY use for calculating liquidation of a porting request.
        The liquidation cause by rate changing right after porting request is accepted (collateral is locked)
        but before user request for ported token (ptoken is released to user).
        Use with portal state after rate changed
        @param porting_collateral:
        @param porting_amount:
        @param custodian:a CustodianInfo, Account object or incognito addr of custodian
        @param token_id:
        @return:
        """
        prv_rate = self.get_portal_rate(PRV_ID)
        token_rate = self.get_portal_rate(token_id)
        return self.__cal_liquidation_and_return(custodian, token_id, token_rate, prv_rate, porting_amount,
                                                 porting_collateral)

    def estimate_liquidation_of_custodian_with_new_rate(self, custodian, token_id, new_token_rate, new_prv_rate):
        """
        Only use for estimating liquidate collateral and return collateral of custodian BEFORE RATE CHANGES.
        Use with portal state before rate changed
        @param custodian:
        @param token_id:
        @param new_prv_rate:
        @param new_token_rate:
        @return:
        """
        return self.__cal_liquidation_and_return(custodian, token_id, new_token_rate, new_prv_rate, 0, 0)

    def __cal_liquidation_and_return(self, custodian, token_id, new_token_rate, new_prv_rate,
                                     porting_amount, porting_collateral):
        """
        Never call this method directly, use the two method above instead
        @param custodian:
        @param token_id:
        @param new_prv_rate:
        @param new_token_rate:
        @param porting_amount:
        @param porting_collateral:
        @return:
        """
        custodian = self.get_custodian_info_in_pool(custodian)
        my_holding_token = custodian.get_holding_token_amount(token_id)
        waiting_redeem_holding_tok = \
            self.sum_holding_token_waiting_redeem_req(token_id, custodian.get_incognito_addr())

        X = self._lock_collateral_minus_waiting_porting_of_custodian(custodian, token_id) + porting_collateral
        Y = my_holding_token + waiting_redeem_holding_tok + porting_amount
        Z = int((Y * 1.05 * new_token_rate) / new_prv_rate)
        if X > Z:
            F = X - Z  # collateral return to custodian
            liquidate_amount = Z
        else:
            F = 0
            liquidate_amount = X
        return liquidate_amount, F

    def will_custodian_be_liquidated_with_new_rate(self, custodian, token_id, new_tok_rate, new_prv_rate):
        """

        @param custodian: CustodianInfo object
        @param new_tok_rate:
        @param new_prv_rate:
            when collateral <= liquidation_percent (120% by default) of token price in prv, collateral will be liquidize
        @param token_id: token to check, bnb or btc
        @return:
        """
        porting_waiting = self.get_porting_waiting_req()
        waiting_porting_collateral = 0
        waiting_porting_token = 0
        for req in porting_waiting:
            custodian_of_req = req.get_custodian(custodian)
            if custodian_of_req is not None:
                waiting_porting_collateral += custodian_of_req.get_locked_collateral()
                waiting_porting_token += custodian_of_req.get_amount()

        prv_collateral_current = custodian.get_locked_collateral(token_id) + waiting_porting_collateral
        holding_token = custodian.get_holding_token_amount(token_id) + waiting_porting_token

        if holding_token is None or holding_token == 0:
            return False
        holding_tok_in_prv_new_rate = PortalMath.cal_portal_exchange_tok_to_prv(holding_token, new_tok_rate,
                                                                                new_prv_rate)
        new_collateral = int(holding_tok_in_prv_new_rate * ChainConfig.Portal.COLLATERAL_LIQUIDATE_PERCENT)
        if prv_collateral_current <= new_collateral:
            return True
        return False

    def _lock_collateral_minus_waiting_porting_of_custodian(self, custodian, token_id):
        sum_waiting_porting_collateral = self.sum_collateral_porting_waiting(token_id, custodian)
        return custodian.get_locked_collateral(token_id) - sum_waiting_porting_collateral

    def estimate_collateral(self, amount, token_id):
        rate_prv = self.get_portal_rate(PRV_ID)
        rate_tok = self.get_portal_rate(token_id)
        return PortalMath.cal_lock_collateral(amount, rate_tok, rate_prv)

    def estimate_custodian_collateral_unlock(self, custodian, holding_amount_to_unlock, token):
        """
        Estimate mount of prv collateral will be unlock, use with portal state after redeem matched only
        @param custodian: incognito address, Account, or CustodianInfo obj
        @param holding_amount_to_unlock: int, amount of ptoken to unlock
        @param token: mount of prv collateral will be unlock
        @return:
        """
        custodian_holding = self.get_custodian_info_in_pool(custodian).get_holding_token_amount(token)
        custodian_lock_collateral = self.get_custodian_info_in_pool(custodian).get_locked_collateral(token)
        matching_holding = sum(
            [req.get_custodian(custodian).get_amount() for req in self.get_porting_waiting_req(token)])
        if holding_amount_to_unlock == custodian_holding:
            unlock_prv = custodian_lock_collateral
        else:
            unlock_prv = int(
                (holding_amount_to_unlock / custodian_holding) * (custodian_lock_collateral - matching_holding))
        logger.info(f'Estimated: custodian {l6(custodian.get_incognito_addr())}, '
             f'holding {custodian_holding}, '
             f'matched hold {matching_holding}, '
             f'unlock {holding_amount_to_unlock} '
             f'token {l6(token)}, '
             f'locked collateral: {custodian_lock_collateral}, '
             f'to unlock: {unlock_prv} ')
        return unlock_prv

    def estimate_exchange_prv_to_token(self, amount_prv, token_id):
        rate_prv = self.get_portal_rate(PRV_ID)
        rate_tok = self.get_portal_rate(token_id)
        return PortalMath.cal_portal_exchange_prv_to_tok(amount_prv, rate_prv, rate_tok)

    def estimate_exchange_token_to_prv(self, amount_token, token_id):
        rate_prv = self.get_portal_rate(PRV_ID)
        rate_tok = self.get_portal_rate(token_id)
        return PortalMath.cal_portal_exchange_tok_to_prv(amount_token, rate_tok, rate_prv)

    def verify_unlock_collateral_custodian_redeem_expire(self, psi_redeem_expire, redeem, runaway_custodian_list=None):
        """
        Custodian who return public token can request for unlocking collateral
        custodian(s) who not return public token to user (run away):
       - 105% of there's locked collateral of this request will be sent directly to user
       - 45% left will be unlock automatically
        @param runaway_custodian_list: list of custodians who not sending public token back to user
        @param psi_redeem_expire: PortalStateInfo after the redeem is expired
        @param redeem: redeem id or RedeemReqInfo object
        @return: amount prv that will return to user
        """
        if type(redeem) is str:
            redeem_info = RedeemReqInfo().get_redeem_status_by_redeem_id(redeem)
        elif type(redeem) is RedeemReqInfo:
            redeem_info = redeem
        else:
            raise TypeError(
                f'Expected String or {RedeemReqInfo.__module__}.{RedeemReqInfo.__name__}, got {type(redeem)} instead')

        if runaway_custodian_list is None:
            runaway_custodian_list = redeem_info.get_redeem_matching_custodians()
        prv_return_total = 0
        token_id = redeem_info.get_token_id()
        psi_redeem_expire: PortalStateInfo
        for custodian in runaway_custodian_list:
            prv_return_to_user, prv_unlock = \
                self.estimate_prv_custodian_return_to_user_when_redeem_expire(custodian, redeem_info, psi_redeem_expire)

            lock_collateral_b4 = self.get_custodian_info_in_pool(custodian).get_locked_collateral(token_id)
            total_collateral_b4 = self.get_custodian_info_in_pool(custodian).get_total_collateral()
            free_collateral_b4 = self.get_custodian_info_in_pool(custodian).get_free_collateral()

            lock_collateral_af = psi_redeem_expire.get_custodian_info_in_pool(custodian).get_locked_collateral(token_id)
            total_collateral_af = psi_redeem_expire.get_custodian_info_in_pool(custodian).get_total_collateral()
            free_collateral_af = psi_redeem_expire.get_custodian_info_in_pool(custodian).get_free_collateral()
            logger.info(f"""Custodian {l6(custodian.get_incognito_addr())}:
                    locked b4/af    {lock_collateral_b4}-{lock_collateral_af} 
                    total b4/af     {total_collateral_b4}-{total_collateral_af} 
                    free b4/af      {free_collateral_b4}-{free_collateral_af}
                    return to user  {prv_return_to_user}
                    unlock          {prv_unlock}""")
            assert lock_collateral_b4 - (prv_return_to_user + prv_unlock) == lock_collateral_af
            assert total_collateral_b4 - prv_return_to_user == total_collateral_af
            assert free_collateral_b4 + prv_unlock == free_collateral_af
            prv_return_total += int(prv_return_to_user)

        return prv_return_total

    def estimate_prv_custodian_return_to_user_when_redeem_expire(self, custodian, redeem, psi_when_expire):
        """

        @param psi_when_expire: PortalStateInfo when the redeem req is expired
        @param custodian: PortalStateInfo.CustodianInfo
        @param redeem: redeem id (str) or RedeemReqInfo
        @return: amount prv return to user , amount collateral to unlock
        """
        if type(redeem) is str:
            redeem_info = RedeemReqInfo().get_redeem_status_by_redeem_id(redeem)
        elif type(redeem) is RedeemReqInfo:
            redeem_info = redeem
        else:
            raise TypeError(
                f'Expected String or {RedeemReqInfo.__module__}.{RedeemReqInfo.__name__}, got {type(redeem)} instead')
        psi_when_expire: PortalStateInfo
        custodian: PortalStateInfo.CustodianInfo
        cus_addr_s = l6(KeyExtractor.incognito_addr(custodian))
        token_id = redeem_info.get_token_id()
        amount_token_redeem = redeem_info.get_custodian(custodian).get_amount()

        custodian_holding = self.get_custodian_info_in_pool(custodian).get_holding_token_amount(token_id)
        custodian_locked_total = self.get_custodian_info_in_pool(custodian).get_locked_collateral(token_id)

        collateral_of_holding_redeem = int(amount_token_redeem * custodian_locked_total / custodian_holding)
        estimate_return = psi_when_expire.estimate_exchange_token_to_prv(int(amount_token_redeem * 1.05), token_id)
        return_prv = min(collateral_of_holding_redeem, estimate_return)
        unlock = max(0, collateral_of_holding_redeem - return_prv)

        logger.info(f"Estimate: custodian {cus_addr_s}, "
             f"collateral of redeem: {collateral_of_holding_redeem}, "
             f"return prv to user: {return_prv}, "
             f"unlock: {unlock}")
        return return_prv, unlock


class UnlockCollateralReqInfo(_PortalInfoBase):
    def get_unlock_collateral_req_stat(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_portal_req_unlock_collateral_status(tx_id).get_result()
        if self.is_none() and retry:
            WAIT(40)
            self.data = SUT().portal().get_portal_req_unlock_collateral_status(tx_id).get_result()
        return self

    def get_unlock_amount(self):
        return int(self.data['UnlockAmount'])


class DepositTxInfo(_PortalInfoBase):
    _amount = 'DepositedAmount'

    def get_deposit_info(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_portal_custodian_deposit_status(tx_id).get_result()
        if self.is_none() and retry:
            WAIT(40)
            self.data = SUT().portal().get_portal_custodian_deposit_status(tx_id).get_result()
        return self

    def get_deposited_amount(self):
        return self.data[DepositTxInfo._amount]


class CustodianWithdrawTxInfo(_PortalInfoBase):
    _info = 'CustodianWithdraw'
    _payment_addr = 'PaymentAddress'
    _remain_free_collateral = 'RemainCustodianFreeCollateral'

    def get_custodian_withdraw_info_by_tx(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        response = SUT().portal().get_custodian_withdraw_by_tx_id(tx_id)
        if response.get_error_msg() is not None and retry:
            WAIT(40)
            response = SUT().portal().get_custodian_withdraw_by_tx_id(tx_id)
        self.data = response.get_result()[CustodianWithdrawTxInfo._info]
        return self

    def get_payment_addr(self):
        return self.data[CustodianWithdrawTxInfo._payment_addr]

    def get_remain_free_collateral(self):
        return self.data[CustodianWithdrawTxInfo._remain_free_collateral]


class RewardWithdrawTxInfo(_PortalInfoBase):
    _CustodianAddressStr = 'CustodianAddressStr'
    _RewardAmount = 'RewardAmount'
    _TxReqID = 'TxReqID'

    def get_reward_info_by_tx_id(self, tx_id, retry=True):
        from Objects.IncognitoTestCase import SUT
        self.data = SUT().portal().get_request_withdraw_portal_reward_status(tx_id).expect_no_error().get_result()
        if self.is_none() and retry:
            WAIT(40)
            self.data = SUT().portal().get_request_withdraw_portal_reward_status(tx_id).expect_no_error().get_result()
        return self

    def get_custodian_addr_str(self):
        return self.data[RewardWithdrawTxInfo._CustodianAddressStr]

    def get_reward_amount(self):
        return self.data[RewardWithdrawTxInfo._RewardAmount]

    def get_tx_req_id(self):
        return self.data[RewardWithdrawTxInfo._TxReqID]
