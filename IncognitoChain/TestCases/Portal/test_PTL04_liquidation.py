import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import PortalHelper, l6, ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import PORTAL_FEEDER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Portal import test_PTL02_create_porting_req as porting_step, portal_user


def setup_function():
    PSI_before_test = SUT().get_latest_portal_state_info()
    # check if there's no holding token, port some
    # for now only check for BNB, need to add check for BTC later if want to test BTC
    if PSI_before_test.help_get_highest_holding_token_custodian(PBNB_ID).get_holding_token_amount(PBNB_ID) == 0:
        INFO('Setup liquidation test')
        porting_step.setup_module()
        porting_step.test_create_porting_req_1_1(PBNB_ID, 100, portal_user, None, 1, 'valid')
        WAIT(60)


@pytest.mark.parametrize("token, percent, waiting_redeem, expected", [
    # BNB
    (PBNB_ID, 1.6, False, 'ok'),
    (PBNB_ID, 1.7, False, 'ok'),
    (PBNB_ID, 1.4, False, 'ok'),
    (PBNB_ID, 1.21, False, 'ok'),
    (PBNB_ID, 1.2, False, 'liquidated'),
    (PBNB_ID, 0.99, False, 'liquidated'),

    # BTC, not yet support testing, just list the cases here. Also need to check setup_function when do the tests
    # (PBTC_ID, 1.6, False, 'ok'),
    # (PBTC_ID, 1.7, False, 'ok'),
    # (PBTC_ID, 1.4, False, 'ok'),
    # (PBTC_ID, 1.21, False, 'ok'),
    # (PBTC_ID, 1.2, False, 'liquidated'),
    # (PBTC_ID, 0.99, False, 'liquidated'),
])
def test_liquidate(token, percent, waiting_redeem, expected):
    STEP(0, 'Get portal status before changing rate')
    PSI_before_test = SUT().get_latest_portal_state_info()
    tok_rate_before_test = PSI_before_test.get_portal_rate(token)
    prv_rate_before_test = PSI_before_test.get_portal_rate(PRV_ID)
    prv_liquidate_rate = PortalHelper.cal_liquidate_rate(percent, tok_rate_before_test, prv_rate_before_test)
    custodians_will_be_liquidate = PSI_before_test.find_custodians_will_be_liquidate_with_new_rate(
        token, tok_rate_before_test, prv_liquidate_rate)

    if expected == 'liquidated':
        assert custodians_will_be_liquidate != [], "custodian list that will be liquidated is empty"
        estimated_liquidation_pool = PSI_before_test.estimate_liquidation_pool_with_new_rate(token,
                                                                                             tok_rate_before_test,
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
    ChainHelper.wait_till_next_beacon_height(2)

    STEP(2, "Check liquidation pool")
    PSI_after_test = SUT().get_latest_portal_state_info()

    INFO(f'Rate before')
    PSI_before_test.print_rate()

    INFO(f'Rate after')
    PSI_after_test.print_rate()

    if expected == 'liquidated':
        INFO("liquidation pool estimated")
        INFO(f"{estimated_liquidation_pool.data}")
        INFO("liquidation pool after")
        INFO(f"{PSI_after_test.get_liquidation_pool()}")
        INFO("liquidation pool before")
        INFO(f"{PSI_before_test.get_liquidation_pool()}")

        INFO(f"wait for collateral to be return to custodian if need")
        WAIT(30)
        for custodian in custodians_will_be_liquidate:
            estimated_liquidated_amount, estimated_return_collateral = PSI_before_test. \
                estimate_liquidation_of_custodian_with_new_rate(custodian, token, tok_rate_before_test,
                                                                prv_liquidate_rate)
            free_collateral_b4_liquidate = custodian.get_free_collateral()
            free_collateral_af_liquidate = PSI_after_test.get_custodian_info_in_pool(
                custodian.get_incognito_addr()).get_free_collateral()
            INFO(f"""Custodian {l6(custodian.get_incognito_addr())} "
                 estimated liquidated amount        : {estimated_liquidated_amount} 
                 estimated return to free collateral: {estimated_return_collateral}
                 free collateral after              : {free_collateral_af_liquidate}""")
            if percent <= 1:
                assert estimated_return_collateral == 0
            else:
                assert estimated_return_collateral > 0
            assert free_collateral_af_liquidate == free_collateral_b4_liquidate + estimated_return_collateral
        INFO(f" Estimated liquidation pool  : {estimated_liquidation_pool}")
        INFO(f" Before test liquidation pool: {PSI_before_test.get_liquidation_pool()}")
        INFO(f" After test liquidation pool : {PSI_after_test.get_liquidation_pool()}")

        assert estimated_liquidation_pool + PSI_before_test.get_liquidation_pool() \
               == PSI_after_test.get_liquidation_pool()
    else:
        assert PSI_before_test.get_liquidation_pool() == PSI_after_test.get_liquidation_pool()
