from IncognitoChain.Configs.Constants import pbnb_id, prv_token_id
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.TestCases.Portal import deposit_amount, custodian, custodian_remote_address

current_total_collateral = 0


def setup_function():
    INFO("Check if user is already a custodian")
    my_custodian_info = custodian.get_my_portal_custodian_status()
    if my_custodian_info is not None:
        global current_total_collateral
        current_total_collateral = my_custodian_info.get_total_collateral()
    else:
        assert my_custodian_info is None


def teardown_function():
    INFO(f"Withdraw collateral, only leave {deposit_amount}")
    custodian_status = custodian.get_my_portal_custodian_status()
    if custodian_status.get_total_collateral() > deposit_amount:
        custodian.withdraw_my_portal_collateral(current_total_collateral - deposit_amount).subscribe_transaction()


def test_custodian_deposit_success():
    STEP(0, "Get balance before deposit")
    custodian.get_prv_balance()

    STEP(1, "Make a valid custodian deposit")
    deposit_tx = custodian.make_me_custodian(deposit_amount, pbnb_id, custodian_remote_address).subscribe_transaction()
    tx_fee = deposit_tx.get_fee()

    STEP(2, "Verify deposit is successful and user becomes custodian")
    assert custodian.get_prv_balance_cache() - deposit_amount - tx_fee == custodian.get_prv_balance()
    WAIT(10)  # wait for collateral to be added to portal status
    custodian_info = custodian.get_my_portal_custodian_status()
    assert custodian_info is not None
    global current_total_collateral
    assert custodian_info.get_total_collateral() == deposit_amount + current_total_collateral
    current_total_collateral += deposit_amount


def test_custodian_deposit_un_success():
    STEP(0, "Get balance before deposit")
    custodian.get_prv_balance()
    custodian_info_before = custodian.get_my_portal_custodian_status()

    STEP(1, "Make an invalid custodian deposit")
    deposit_tx = custodian.make_me_custodian(deposit_amount, prv_token_id, custodian_remote_address)
    assert deposit_tx.get_error_msg() is not None

    STEP(2, "verify balance")
    assert custodian.get_prv_balance_cache() == custodian.get_prv_balance()
    custodian_info_after = custodian.get_my_portal_custodian_status()
    if custodian_info_before is None:
        assert custodian_info_after is None
    else:
        assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral()
