import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import PortalHelper, l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import PortalStateInfo
from IncognitoChain.TestCases.Portal import test_PTL02_create_porting_req as porting_step, portal_user, \
    find_custodian_account_by_incognito_addr

portal_state_before_test = None


def setup_module():
    INFO('Setup liquidation test')
    porting_step.test_create_porting_req_1_1(100, None, 'valid')
    global portal_state_before_test
    portal_state_before_test = SUT.full_node.get_latest_portal_state()


@pytest.mark.parametrize("percent,waiting_redeem,expected", [
    # (1.6, False, 'ok'),
    # (1.7, False, 'ok'),
    # (1.4, False, 'ok'),
    # (1.21, False, 'ok'),
    # (1.2, False, 'liquidated'),
    (0.99, False, 'liquidated'),
])
def test_liquidate(percent, waiting_redeem, expected):
    STEP(0, 'Get portal status before changing rate')
    global portal_state_before_test
    portal_info_before = PortalStateInfo(portal_state_before_test.get_result())
    tok_rate_before_test = portal_info_before.get_portal_rate(PBNB_ID)
    prv_rate_before_test = portal_info_before.get_portal_rate(PRV_ID)

    prv_liquidate_rate = PortalHelper.cal_liquidate_rate(percent, PBNB_ID, tok_rate_before_test, prv_rate_before_test)
    custodians_will_be_liquidate = portal_info_before.find_custodians_will_be_liquidate_with_new_rate(
        PBNB_ID, tok_rate_before_test, prv_liquidate_rate)

    if expected == 'liquidated':
        assert (not custodians_will_be_liquidate) is False, "custodian list that will be liquidate is empty"
        estimated_liquidation_pool = portal_info_before.estimate_liquidation_pool(PBNB_ID, tok_rate_before_test,
                                                                                  prv_liquidate_rate)

    if waiting_redeem:  # todo: cover liquidation case which has waiting redeem in portal state
        low_custodian_info = portal_info_before.find_lowest_free_collateral_custodian()
        low_custodian_account = find_custodian_account_by_incognito_addr(low_custodian_info.get_incognito_addr())
        redeem_amount = low_custodian_info.get_free_collateral() + 10
        STEP(0.1, 'Create redeem req')
        redeem_req_tx = portal_user.portal_req_redeem_my_token(portal_state_before_test, PBNB_ID, redeem_amount)
        redeem_req_tx.expect_no_error()
        redeem_req_tx.subscribe_transaction()

    STEP(1, f'Rate change, which make locked collateral amount percentage reduce to {percent}')

    rate_feed_tx = PORTAL_FEEDER.portal_create_exchange_rate({PRV_ID: str(prv_liquidate_rate)})
    rate_feed_tx.subscribe_transaction()
    assert rate_feed_tx.get_error_msg() is None, "Fail to create rate"
    SUT.full_node.help_wait_till_next_epoch()

    STEP(2, "Check liquidation pool")
    portal_state_after_rate_change = SUT.full_node.get_latest_portal_state()
    portal_info_after = PortalStateInfo(portal_state_after_rate_change.get_result())

    INFO(f'Rate before')
    portal_info_before.print_rate()

    INFO(f'Rate after')
    portal_info_after.print_rate()

    if expected == 'liquidated':
        INFO("liquidation pool estimated")
        INFO(f"{estimated_liquidation_pool.data}")
        INFO("liquidation pool after")
        INFO(f"{portal_info_after.get_liquidation_pool().data}")
        INFO("liquidation pool before")
        INFO(f"{portal_info_before.get_liquidation_pool().data}")

        INFO(f"wait for collateral to be return to custodian if need")
        WAIT(30)

        for custodian in custodians_will_be_liquidate:
            liquidated_amount, return_collateral = custodian.estimate_liquidation(
                PBNB_ID, tok_rate_before_test, prv_liquidate_rate, portal_info_before)
            current_free_collateral = custodian.get_free_collateral()
            new_free_collateral = portal_info_after.get_custodian_info_in_pool(
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
        assert estimated_liquidation_pool + portal_info_before. \
            get_liquidation_pool() == portal_info_after.get_liquidation_pool()
    else:
        assert portal_info_before.get_liquidation_pool() == portal_info_after.get_liquidation_pool()
