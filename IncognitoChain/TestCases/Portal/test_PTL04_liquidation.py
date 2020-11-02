import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID, PBTC_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import PortalHelper, l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import PORTAL_FEEDER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.Objects.PortalObjects import PortalStateInfo
from IncognitoChain.TestCases.Portal import test_PTL02_create_porting_req as porting_step, portal_user

PSI_before_test = PortalStateInfo()
need_holding_token = False


def setup_function():
    if need_holding_token:
        INFO('Setup liquidation test')
        porting_step.setup_module()
        porting_step.test_create_porting_req_1_1(PBNB_ID, 100, portal_user, None, 1, 'valid')
        global PSI_before_test
        PSI_before_test = SUT().get_latest_portal_state_info()


@pytest.mark.parametrize("token, percent, waiting_redeem, expected", [
    # BNB
    (PBNB_ID, 1.6, False, 'ok'),
    (PBNB_ID, 1.7, False, 'ok'),
    (PBNB_ID, 1.4, False, 'ok'),
    (PBNB_ID, 1.21, False, 'ok'),
    (PBNB_ID, 1.2, False, 'liquidated'),
    (PBNB_ID, 0.99, False, 'liquidated'),

    # BTC
    (PBTC_ID, 1.6, False, 'ok'),
    (PBTC_ID, 1.7, False, 'ok'),
    (PBTC_ID, 1.4, False, 'ok'),
    (PBTC_ID, 1.21, False, 'ok'),
    (PBTC_ID, 1.2, False, 'liquidated'),
    (PBTC_ID, 0.99, False, 'liquidated'),
])
def test_liquidate(token, percent, waiting_redeem, expected):
    STEP(0, 'Get portal status before changing rate')
    tok_rate_before_test = PSI_before_test.get_portal_rate(token)
    prv_rate_before_test = PSI_before_test.get_portal_rate(PRV_ID)

    prv_liquidate_rate = PortalHelper.cal_liquidate_rate(percent, tok_rate_before_test, prv_rate_before_test)
    custodians_will_be_liquidate = PSI_before_test.find_custodians_will_be_liquidate_with_new_rate(
        token, tok_rate_before_test, prv_liquidate_rate)

    if expected == 'liquidated':
        assert (not custodians_will_be_liquidate) is False, "custodian list that will be liquidated is empty"
        estimated_liquidation_pool = PSI_before_test.estimate_liquidation_pool(token, tok_rate_before_test,
                                                                               prv_liquidate_rate)

    if waiting_redeem:
        low_custodian_info = PSI_before_test.find_lowest_free_collateral_custodian()
        redeem_amount = low_custodian_info.get_free_collateral() + 10
        STEP(0.1, 'Create redeem req')
        redeem_req_tx = portal_user.portal_req_redeem_my_token(PSI_before_test, token, redeem_amount)
        redeem_req_tx.expect_no_error()
        redeem_req_tx.subscribe_transaction()

    STEP(1, f'Rate change, which make locked collateral amount percentage reduce to {percent}')

    rate_feed_tx = PORTAL_FEEDER.portal_create_exchange_rate({PRV_ID: str(prv_liquidate_rate)})
    rate_feed_tx.subscribe_transaction()
    assert rate_feed_tx.get_error_msg() is None, "Fail to create rate"
    SUT().help_wait_till_next_epoch()

    STEP(2, "Check liquidation pool")
    PSI_after_test = SUT().get_latest_portal_state_info()

    INFO(f'Rate before')
    PSI_before_test.print_rate()

    INFO(f'Rate after')
    PSI_after_test.print_rate()

    if expected == 'liquidated':
        global need_holding_token
        need_holding_token = True
        INFO("liquidation pool estimated")
        INFO(f"{estimated_liquidation_pool.data}")
        INFO("liquidation pool after")
        INFO(f"{PSI_after_test.get_liquidation_pool().data}")
        INFO("liquidation pool before")
        INFO(f"{PSI_before_test.get_liquidation_pool().data}")

        INFO(f"wait for collateral to be return to custodian if need")
        WAIT(30)

        for custodian in custodians_will_be_liquidate:
            liquidated_amount, return_collateral = PSI_before_test.estimate_liquidation_of_custodian(
                custodian, token, tok_rate_before_test, prv_liquidate_rate)
            current_free_collateral = custodian.get_free_collateral()
            new_free_collateral = PSI_after_test.get_custodian_info_in_pool(
                custodian.get_incognito_addr()).get_free_collateral()
            INFO(f"Custodian {l6(custodian.get_incognito_addr())} "
                 f"liquidated: {liquidated_amount} "
                 f"return to free collateral: {return_collateral} "
                 f"free collateral after: {new_free_collateral}")
            if percent <= 1:
                assert return_collateral == 0
            else:
                assert return_collateral > 0
            assert new_free_collateral == current_free_collateral + return_collateral
        assert estimated_liquidation_pool + PSI_before_test.get_liquidation_pool() \
               == PSI_after_test.get_liquidation_pool()
    else:
        assert PSI_before_test.get_liquidation_pool() == PSI_after_test.get_liquidation_pool()
