from typing import List

from IncognitoChain.Helpers.Logging import INFO, DEBUG
from IncognitoChain.Helpers.TestHelper import l6


class PortalInfoObj:
    def __init__(self, dict_data=None):
        self.data = dict_data
        self.err = None

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


class CustodianInfo(PortalInfoObj):

    def get_incognito_addr(self):
        try:
            return self.data['IncognitoAddress']  # this only exists in custodian pool
        except KeyError:
            return self.data['IncAddress']  # this only exists porting req

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
            return None

    def get_locked_collateral(self, token_id=None):
        if token_id is None:
            ret = self.data['LockedAmountCollateral']
        else:
            try:
                ret = int(self.data['LockedAmountCollateral'][token_id])
            except (KeyError, TypeError):
                ret = None
        return ret

    def get_remote_address(self):
        return self.data['RemoteAddress']

    def get_reward_amount(self, token_id=None):
        if token_id is None:
            return self.data['RewardAmount']
        return int(self.data['RewardAmount'][token_id])


class PortingReqInfo(PortalInfoObj):
    """
    response of "getportalportingrequestbykey"
             or "getportalportingrequestbyportingid"
             or "getportalreqptokenstatus"
    """

    def get_porting_req_by_tx_id(self, tx_id):
        INFO()
        INFO(f'Get porting req info, tx_id = {tx_id}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        response = SUT.full_node.portal().get_portal_porting_req_by_key(tx_id)
        self.data = response.get_result('PortingRequest')
        return self

    def get_porting_req_by_porting_id(self, porting_id):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data = SUT.full_node.portal().get_portal_porting_req_by_porting_id(porting_id).get_result('PortingRequest')
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

    def get_custodian(self, account):
        custodian_list = self.get_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == account.payment_key:
                return custodian
        return None

    def get_porting_fee(self):
        return int(self.data['PortingFee'])

    def get_beacon_height(self):
        return int(self.data['BeaconHeight'])


class RedeemReqInfo(PortalInfoObj):

    def get_redeem_status_by_redeem_id(self, redeem_id):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data = SUT.full_node.portal().get_portal_redeem_status(redeem_id).get_result()
        return self

    def get_req_matching_redeem_status(self, tx_id):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data = SUT.full_node.portal().get_req_matching_redeem_status(tx_id).get_result()
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

    def get_custodian(self, account):
        custodian_list = self.get_redeem_matching_custodians()
        for custodian in custodian_list:
            if custodian.get_incognito_addr() == account.payment_key:
                return custodian
        return None

    def get_redeem_amount(self):
        return int(self.data['RedeemAmount'])


class PTokenReqInfo(PortalInfoObj):
    def get_ptoken_req_by_tx_id(self, tx_id):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data = SUT.full_node.portal().get_portal_req_ptoken_status(tx_id).get_result()
        return self


class PortalStateInfo(PortalInfoObj):
    def get_custodian_pool(self) -> List[CustodianInfo]:
        custodian_pool = self.data['CustodianPool']
        custodian_list = [CustodianInfo(value) for key, value in custodian_pool.items()]
        return custodian_list

    def get_portal_rate(self, token_id=None):
        if token_id is None:
            return self.data['FinalExchangeRatesState']['Rates']
        else:
            return int(self.data['FinalExchangeRatesState']['Rates'][token_id]['Amount'])

    def get_porting_waiting_req(self) -> List[PortingReqInfo]:
        req_list = []
        req_data = self.data['WaitingPortingRequests']
        for req in req_data.keys():
            req_list.append(PortingReqInfo(req_data[req]))
        return req_list

    def get_redeem_waiting_req(self) -> List[RedeemReqInfo]:
        req_list = []
        req_data = self.data['WaitingRedeemRequests']
        for req in req_data.keys():
            req_list.append(RedeemReqInfo(req_data[req]))
        return req_list

    def get_redeem_matched_req(self) -> List[RedeemReqInfo]:
        req_list = []
        req_data = self.data['MatchedRedeemRequests']
        for req in req_data.keys():
            req_list.append(RedeemReqInfo(req_data[req]))
        return req_list


class UnlockCollateralReqInfo(PortalInfoObj):
    def get_unlock_collateral_req_stat(self, tx_id):
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        self.data = SUT.full_node.portal().get_portal_req_unlock_collateral_status(tx_id).get_result()

    def get_unlock_amount(self):
        return int(self.data['UnlockAmount'])
