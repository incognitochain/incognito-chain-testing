import random

import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID, coin, PortalCustodianWithdrawStatus, PBTC_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import _CustodianInfo, CustodianWithdrawTxInfo, PortalStateInfo
from IncognitoChain.TestCases.Portal import TEST_SETTING_DEPOSIT_AMOUNT, self_pick_custodian, \
    custodian_remote_address, just_another_remote_addr, portal_user

current_total_collateral = 0
custodian_info_before = _CustodianInfo()
custodian_info_after = _CustodianInfo()


def setup_function():
    INFO("Check if user is already a custodian")
    my_custodian_info = self_pick_custodian.portal_get_my_custodian_info()
    if my_custodian_info is not None:
        global current_total_collateral
        current_total_collateral = my_custodian_info.get_total_collateral()
    else:
        assert my_custodian_info is None

    INFO("Get user prv balance before deposit")
    self_pick_custodian.get_prv_balance()

    INFO("get custodian info before test")
    global custodian_info_before
    custodian_info_before = self_pick_custodian.portal_get_my_custodian_info()


def teardown_function():
    try:
        if custodian_info_before.data is None: return
        if custodian_info_after.data is None: return
    except AttributeError:
        return

    if custodian_info_before.get_remote_address(PBNB_ID) != custodian_info_after.get_remote_address(PBNB_ID):
        INFO("# change back remote address")
        try:
            self_pick_custodian.portal_withdraw_my_all_free_collateral().subscribe_transaction()
            WAIT(60)
            self_pick_custodian.portal_add_collateral(custodian_info_before.get_total_collateral(), PBNB_ID,
                                                      custodian_remote_address).subscribe_transaction()
        except:
            pass


@pytest.mark.parametrize('token,expected_pass', [
    (PRV_ID, False),
    # (PBTC_ID, True),
    (PBNB_ID, True),

])
@pytest.mark.dependency()
def test_custodian_deposit(token, expected_pass):
    STEP(1, "Make a valid custodian deposit")
    deposit_tx = self_pick_custodian.portal_make_me_custodian(TEST_SETTING_DEPOSIT_AMOUNT, token,
                                                              custodian_remote_address).subscribe_transaction()
    tx_fee = deposit_tx.get_fee()

    STEP(2, "Verify custodian PRV balance and portal status")
    WAIT(60)  # wait for collateral to be added to portal status
    global custodian_info_after
    custodian_info_after = self_pick_custodian.portal_get_my_custodian_info()
    if expected_pass:
        INFO('Verify deposit is successful and user becomes custodian')
        assert self_pick_custodian.get_prv_balance_cache() - TEST_SETTING_DEPOSIT_AMOUNT - tx_fee \
               == self_pick_custodian.get_prv_balance()
        assert custodian_info_after is not None
        global current_total_collateral
        assert custodian_info_after.get_total_collateral() == TEST_SETTING_DEPOSIT_AMOUNT + current_total_collateral
        current_total_collateral += TEST_SETTING_DEPOSIT_AMOUNT
    else:
        INFO("Verify deposit is failed and user not becomes custodian")
        assert self_pick_custodian.get_prv_balance_cache() == self_pick_custodian.get_prv_balance()
        if custodian_info_before is None:
            assert custodian_info_after is None
        else:
            assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral()


@pytest.mark.parametrize('token,expected_pass', [
    (PBNB_ID, True),
    # (PBTC_ID, True),
    (PRV_ID, False),
])
@pytest.mark.dependency(depends=["test_custodian_deposit"])
def test_add_more_collateral(token, expected_pass):
    deposit_amount = coin(1)
    global custodian_info_after
    STEP(1, "Check existing collateral of user")
    if custodian_info_before.get_total_collateral() == 0:
        pytest.skip(f'{l6(self_pick_custodian.incognito_addr)} is not an existing custodian,'
                    f' add more collateral test cannot proceed')
    STEP(2, "Add more collateral")
    deposit_tx = self_pick_custodian.portal_add_collateral(deposit_amount, token, custodian_remote_address)
    if expected_pass:
        deposit_tx.expect_no_error()
        deposit_tx_result = deposit_tx.subscribe_transaction()
    else:
        deposit_tx.expect_error()

    STEP(3, "Wait 40s then verify collateral after deposit")
    WAIT(40)
    custodian_info_after = self_pick_custodian.portal_get_my_custodian_info()
    if expected_pass:
        assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral() + deposit_amount
        assert custodian_info_after.get_free_collateral() == custodian_info_before.get_free_collateral() + deposit_amount
        assert custodian_info_after.get_locked_collateral(token) == custodian_info_before.get_locked_collateral(token)
    else:
        assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral()
        assert custodian_info_after.get_free_collateral() == custodian_info_before.get_free_collateral()
        assert custodian_info_after.get_locked_collateral(token) == custodian_info_before.get_locked_collateral(token)

    STEP(4, 'Verify balance')
    balance_before = self_pick_custodian.get_prv_balance_cache()
    balance_after = self_pick_custodian.get_prv_balance()
    if expected_pass:
        assert balance_before == balance_after + deposit_tx_result.get_fee() + deposit_amount
    else:
        assert balance_before == balance_after


@pytest.mark.parametrize("token,total_collateral_precondition,expected_pass", [
    (PBNB_ID, 0, True),
    (PBNB_ID, 100, False),
    (PRV_ID, 0, False),
])
def test_update_remote_address(token, total_collateral_precondition, expected_pass):
    global custodian_info_after, custodian_info_before
    STEP(0, "precondition check")
    deposit_amount = 123
    if custodian_info_before.get_total_collateral() > custodian_info_before.get_free_collateral():
        pytest.skip(f'{l6(self_pick_custodian.incognito_addr)} holding '
                    f'{custodian_info_before.get_holding_token_amount(token)} token {l6(token)}')
    old_remote_address = custodian_info_before.get_remote_address(PBNB_ID)

    if total_collateral_precondition == 0:
        STEP(1, "Withdraw all collateral")
        self_pick_custodian.portal_withdraw_my_all_free_collateral().subscribe_transaction()
        WAIT(40)
        self_pick_custodian.get_prv_balance()
        custodian_info_before = self_pick_custodian.portal_get_my_custodian_info()
    else:
        STEP(1, "DO NOT Withdraw collateral")

    STEP(2, "Change remote address")
    deposit_tx = self_pick_custodian.portal_add_collateral(deposit_amount, token, just_another_remote_addr)
    WAIT(40)
    deposit_tx_result = deposit_tx.subscribe_transaction()
    custodian_info_after = self_pick_custodian.portal_get_my_custodian_info()
    if expected_pass:
        assert self_pick_custodian.get_prv_balance_cache() == self_pick_custodian.get_prv_balance() \
               + deposit_tx_result.get_fee() + deposit_amount
        assert custodian_info_after.get_remote_address(PBNB_ID) == just_another_remote_addr
        assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral() \
               + deposit_amount
        deposit_tx.expect_no_error()
    else:
        if token == PRV_ID:
            deposit_tx.expect_error()
            assert self_pick_custodian.get_prv_balance_cache() == self_pick_custodian.get_prv_balance()
        else:
            deposit_tx.expect_no_error()
            assert self_pick_custodian.get_prv_balance_cache() == self_pick_custodian.get_prv_balance() \
                   + deposit_tx_result.get_fee() + deposit_amount
            assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral() \
                   + deposit_amount
        assert custodian_info_after.get_remote_address(PBNB_ID) == old_remote_address


@pytest.mark.parametrize('custodian', [
    ACCOUNTS[3],
    # self_pick_custodian,
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
    assert withdraw_tx_info.get_status() == PortalCustodianWithdrawStatus.ACCEPT
    assert withdraw_tx_info.get_remain_free_collateral() == 0

    STEP(2, "Keep withdrawing when free collateral = 0 already, expect rejected")
    for withdraw_amount in [-10, 0, 10]:
        withdraw_tx = custodian.portal_withdraw_my_collateral(withdraw_amount)

        if withdraw_amount > 0:
            withdraw_tx.expect_no_error()
            withdraw_tx.subscribe_transaction()
            withdraw_tx_info = CustodianWithdrawTxInfo()
            withdraw_tx_info.get_custodian_withdraw_info_by_tx(withdraw_tx.get_tx_id())
            assert withdraw_tx_info.get_status() == PortalCustodianWithdrawStatus.REJECTED and \
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
    portal_state_before = SUT.full_node.get_latest_portal_state()
    portal_state_info_before = PortalStateInfo(portal_state_before.get_result())

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
        portal_state = SUT.full_node.get_latest_portal_state()
        portal_state_info = PortalStateInfo(portal_state.get_result())
        assert portal_state_info_before.get_portal_rate() == portal_state_info.get_portal_rate()


@pytest.mark.parametrize('token', [
    PBNB_ID,
    PBTC_ID
])
def test_calculating_porting_fee(token):
    test_amount = random.randrange(1, 1000000000)
    beacon_height = SUT.full_node.help_get_beacon_height()

    STEP(0, 'Get portal state before test')
    portal_state_before = SUT.full_node.get_latest_portal_state(beacon_height)
    portal_state_info_before = PortalStateInfo(portal_state_before.get_result())
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
