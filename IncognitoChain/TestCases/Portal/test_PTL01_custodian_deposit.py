import random

import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID, coin, PBTC_ID, Status
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account, PORTAL_FEEDER
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT
from IncognitoChain.Objects.PortalObjects import CustodianWithdrawTxInfo
from IncognitoChain.TestCases.Portal import TEST_SETTING_DEPOSIT_AMOUNT, self_pick_custodian, \
    portal_user, custodian_remote_addr, another_btc_addr, another_bnb_addr

custodian_need_change_remote_addr_back = Account()


def teardown_function():
    custodian = custodian_need_change_remote_addr_back
    if custodian.is_empty():
        return

    INFO("Change remote address back")
    previous_bnb_addr = custodian_remote_addr.get_remote_addr(PBNB_ID, custodian)
    previous_btc_addr = custodian_remote_addr.get_remote_addr(PBTC_ID, custodian)
    custodian_info = custodian.portal_get_my_custodian_info()
    withdraw_tx = custodian.portal_withdraw_my_all_free_collateral()
    if withdraw_tx is not None:
        withdraw_tx.subscribe_transaction()
    WAIT(60)
    if previous_bnb_addr != custodian_info.get_remote_address(PBNB_ID):
        try:
            self_pick_custodian.portal_add_collateral(TEST_SETTING_DEPOSIT_AMOUNT, PBNB_ID,
                                                      previous_bnb_addr).subscribe_transaction()
        except:
            pass

    if previous_btc_addr != custodian_info.get_remote_address(PBTC_ID):
        try:
            self_pick_custodian.portal_add_collateral(TEST_SETTING_DEPOSIT_AMOUNT, PBTC_ID,
                                                      previous_btc_addr).subscribe_transaction()
        except:
            pass


@pytest.mark.parametrize('depositor, token, expected_pass', [
    (ACCOUNTS[3], PRV_ID, False),
    (self_pick_custodian, PBNB_ID, True),
    (ACCOUNTS[3], PBNB_ID, True),
    (self_pick_custodian, PBTC_ID, True),
    (ACCOUNTS[3], PBTC_ID, True),
])
@pytest.mark.dependency()
def test_custodian_deposit(depositor, token, expected_pass):
    STEP(0, "Check if user is already a custodian")
    custodian_info_b4 = depositor.portal_get_my_custodian_info()
    total_collateral_b4 = 0 if custodian_info_b4 is None else custodian_info_b4.get_total_collateral()
    bal_b4 = depositor.get_prv_balance()

    STEP(1, "Make a valid custodian deposit")
    deposit_response = depositor.portal_make_me_custodian(TEST_SETTING_DEPOSIT_AMOUNT, token,
                                                          custodian_remote_addr.get_remote_addr(token, depositor))
    if token == PRV_ID:
        deposit_response.expect_error()
    else:
        deposit_tx = deposit_response.subscribe_transaction()
        tx_fee = deposit_tx.get_fee()
        WAIT(60)  # wait for collateral to be added to portal status

    STEP(2, "Verify custodian PRV balance and portal status")
    custodian_info_af = depositor.portal_get_my_custodian_info()
    if expected_pass:
        INFO('Verify deposit is successful and user becomes custodian')
        deposit_response.expect_no_error()
        assert bal_b4 - TEST_SETTING_DEPOSIT_AMOUNT - tx_fee == depositor.get_prv_balance()
        assert custodian_info_af is not None
        assert custodian_info_af.get_total_collateral() == TEST_SETTING_DEPOSIT_AMOUNT + total_collateral_b4
    else:
        INFO("Verify deposit is failed and user not becomes custodian or collateral must not change")
        deposit_response.expect_error()
        assert 'public token is not supported currently' in deposit_response.get_error_trace().get_message()
        assert bal_b4 == depositor.get_prv_balance()
        if custodian_info_b4 is None:  # if not a custodian before then not after
            assert custodian_info_af is None
        else:  # if was a custodian before then collateral must not change
            assert custodian_info_af.get_total_collateral() == custodian_info_b4.get_total_collateral()


@pytest.mark.parametrize('depositor,token,expected_pass', [
    (ACCOUNTS[3], PBNB_ID, True),
    (ACCOUNTS[3], PBTC_ID, True),
    (ACCOUNTS[3], PRV_ID, False),
])
@pytest.mark.dependency(depends=["test_custodian_deposit"])
def test_add_more_collateral(depositor, token, expected_pass):
    deposit_amount = coin(1)
    STEP(1, "Check existing collateral of user")
    custodian_info_b4 = depositor.portal_get_my_custodian_info()
    bal_b4 = depositor.get_prv_balance()
    if custodian_info_b4.get_total_collateral() == 0:
        pytest.skip(f'{l6(depositor.incognito_addr)} is not an existing custodian,'
                    f' add more collateral test cannot proceed')
    STEP(2, "Add more collateral")
    deposit_tx = depositor.portal_add_collateral(deposit_amount, token)
    if expected_pass:
        deposit_tx.expect_no_error()
        deposit_tx_result = deposit_tx.subscribe_transaction()
    else:
        deposit_tx.expect_error()

    STEP(3, "Wait 40s then verify collateral after deposit")
    WAIT(40)
    custodian_info_af = depositor.portal_get_my_custodian_info()
    if expected_pass:
        assert custodian_info_af.get_total_collateral() == custodian_info_b4.get_total_collateral() + deposit_amount
        assert custodian_info_af.get_free_collateral() == custodian_info_b4.get_free_collateral() + deposit_amount
        assert custodian_info_af.get_locked_collateral(token) == custodian_info_b4.get_locked_collateral(token)
    else:
        assert custodian_info_af.get_total_collateral() == custodian_info_b4.get_total_collateral()
        assert custodian_info_af.get_free_collateral() == custodian_info_b4.get_free_collateral()
        assert custodian_info_af.get_locked_collateral(
            token) == custodian_info_b4.get_locked_collateral(token)

    STEP(4, 'Verify balance')
    balance_after = depositor.get_prv_balance()
    if expected_pass:
        assert bal_b4 == balance_after + deposit_tx_result.get_fee() + deposit_amount
    else:
        assert bal_b4 == balance_after


@pytest.mark.parametrize("custodian,token,total_collateral_precondition,new_addr,expected_pass", [
    (ACCOUNTS[3], PBNB_ID, 0, another_bnb_addr, True),
    (ACCOUNTS[3], PBNB_ID, 100, another_bnb_addr, False),
    (ACCOUNTS[3], PRV_ID, 0, another_bnb_addr, False),
    (ACCOUNTS[3], PBTC_ID, 0, another_btc_addr, True),
    (ACCOUNTS[3], PBTC_ID, 100, another_btc_addr, False),
])
def test_update_remote_address(custodian, token, total_collateral_precondition, new_addr, expected_pass):
    STEP(0, "precondition check")
    custodian_info_b4 = custodian.portal_get_my_custodian_info()
    deposit_amount = 123
    bal_b4 = custodian.get_prv_balance()
    if custodian_info_b4.get_total_collateral() > custodian_info_b4.get_free_collateral():
        pytest.skip(f'{l6(custodian.incognito_addr)} holding '
                    f'{custodian_info_b4.get_holding_token_amount(token)} token {l6(token)}')
    old_remote_address = custodian_info_b4.get_remote_address(token)

    if total_collateral_precondition == 0:
        STEP(1, "Withdraw all collateral")
        withdraw_response = custodian.portal_withdraw_my_all_free_collateral()
        if withdraw_response is not None:
            withdraw_response.subscribe_transaction()
            WAIT(40)

        custodian.get_prv_balance()
        custodian_info_b4 = custodian.portal_get_my_custodian_info()
        bal_b4 = custodian.get_prv_balance()
    else:
        STEP(1, "DO NOT Withdraw collateral")

    STEP(2, "Change remote address")
    deposit_tx = custodian.portal_add_collateral(deposit_amount, token, new_addr)
    if token == PRV_ID:
        deposit_tx.expect_error()
        assert 'public token is not supported' in deposit_tx.get_error_trace().get_message()
        return
    else:
        deposit_tx.expect_no_error()
    WAIT(40)
    deposit_tx_result = deposit_tx.subscribe_transaction()
    custodian_info_af = custodian.portal_get_my_custodian_info()
    if expected_pass:
        assert bal_b4 == custodian.get_prv_balance() + deposit_tx_result.get_fee() + deposit_amount
        assert custodian_info_af.get_remote_address(token) == new_addr
        assert custodian_info_af.get_total_collateral() == custodian_info_b4.get_total_collateral() + deposit_amount
        deposit_tx.expect_no_error()
    else:
        if token == PRV_ID:
            deposit_tx.expect_error()
            assert bal_b4 == custodian.get_prv_balance()
        else:
            deposit_tx.expect_no_error()
            assert bal_b4 == custodian.get_prv_balance() \
                   + deposit_tx_result.get_fee() + deposit_amount
            assert custodian_info_af.get_total_collateral() == custodian_info_b4.get_total_collateral() \
                   + deposit_amount
        assert custodian_info_af.get_remote_address(token) == old_remote_address

    global custodian_need_change_remote_addr_back
    custodian_need_change_remote_addr_back = custodian


@pytest.mark.parametrize('custodian', [
    ACCOUNTS[3],
])
def test_with_draw_collateral(custodian):
    STEP(0, "Get collateral")
    PSI = SUT.full_node.get_latest_portal_state_info()
    custodian_info = PSI.get_custodian_info_in_pool(custodian)
    my_free_collateral = custodian_info.get_free_collateral()
    my_total_collateral = custodian_info.get_total_collateral()
    INFO(f""" Custodian {l6(custodian.payment_key) :}
            Total collateral : {my_total_collateral}
            Free collateral  : {my_free_collateral}""")

    if my_free_collateral == 0:
        pytest.skip("Not enough free collateral for testing")

    STEP(1, f"Withdraw all free collateral ({my_free_collateral})")
    withdraw_tx = custodian.portal_withdraw_my_collateral(my_free_collateral)
    withdraw_tx.expect_no_error()
    withdraw_tx.subscribe_transaction()
    withdraw_tx_info = CustodianWithdrawTxInfo()
    withdraw_tx_info.get_custodian_withdraw_info_by_tx(withdraw_tx.get_tx_id())
    assert withdraw_tx_info.get_status() == Status.Portal.CustodianWithdrawStatus.ACCEPT
    assert withdraw_tx_info.get_remain_free_collateral() == 0

    STEP(2, "Keep withdrawing when free collateral = 0 already, expect rejected")
    for withdraw_amount in [-10, 0, 10]:
        withdraw_tx = custodian.portal_withdraw_my_collateral(withdraw_amount)

        if withdraw_amount > 0:
            withdraw_tx.expect_no_error()
            withdraw_tx.subscribe_transaction()
            withdraw_tx_info = CustodianWithdrawTxInfo()
            withdraw_tx_info.get_custodian_withdraw_info_by_tx(withdraw_tx.get_tx_id())
            assert withdraw_tx_info.get_status() == Status.Portal.CustodianWithdrawStatus.REJECTED and \
                   INFO(f"Withdraw {withdraw_amount}, Rejected")
            assert withdraw_tx_info.get_remain_free_collateral() == 0
        else:
            INFO(f"Withdraw {withdraw_amount}, error: {withdraw_tx.get_error_trace().get_message()}")
            withdraw_tx.expect_error()


@pytest.mark.parametrize('account,expected_pass', [
    (portal_user, False),
    (PORTAL_FEEDER, True)
])
def test_creating_rate(account, expected_pass):
    test_rate = {
        PBNB_ID: 1000,
        PBTC_ID: 2000,
        PRV_ID: 100
    }
    STEP(0, 'Get portal state before test')
    portal_state_info_before = SUT.REQUEST_HANDLER.get_latest_portal_state_info()

    STEP(1, "Create rate")
    create_rate_tx = account.portal_create_exchange_rate(test_rate)
    if expected_pass:
        create_rate_tx.expect_no_error()
        create_rate_tx.subscribe_transaction()
        INFO("Wait 60s for new rate to apply")
        WAIT(60)
        portal_state_info = SUT.full_node.get_latest_portal_state_info()
        INFO('Checking new rate')
        for token, value in test_rate.items():
            new_rate = portal_state_info.get_portal_rate(token)
            old_rate = portal_state_info_before.get_portal_rate(token)
            INFO(f"token {l6(token)}: new rate = {new_rate}: old rate = {old_rate} ")
            assert int(new_rate) == int(value)

    else:
        create_rate_tx.expect_error()
        INFO(f"error: {create_rate_tx.get_error_trace().get_message()}")
        portal_state_info = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
        assert portal_state_info_before.get_portal_rate() == portal_state_info.get_portal_rate()


@pytest.mark.parametrize('token', [
    PBNB_ID,
    PBTC_ID
])
def test_calculating_porting_fee(token):
    test_amount = random.randrange(1, 1000000000)
    beacon_height = SUT.REQUEST_HANDLER.help_get_beacon_height()

    STEP(0, 'Get portal state before test')
    portal_state_info_before = SUT.REQUEST_HANDLER.get_latest_portal_state_info(beacon_height)
    bnb_rate = portal_state_info_before.get_portal_rate(token)
    prv_rate = portal_state_info_before.get_portal_rate(PRV_ID)

    STEP(1, f"Get portal fee with amount = {test_amount}")
    portal_fee_from_chain = SUT.full_node.portal().get_porting_req_fees(token, test_amount, beacon_height). \
        get_result(token)
    portal_fee_estimate = PortalHelper.cal_portal_portal_fee(test_amount, bnb_rate, prv_rate)

    STEP(2, 'Compare')
    INFO(f'''
        Estimated fee = {portal_fee_estimate}
        Chain fee     = {portal_fee_from_chain}''')
    assert portal_fee_from_chain == portal_fee_estimate
