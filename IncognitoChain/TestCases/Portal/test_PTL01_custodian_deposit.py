from IncognitoChain.Configs.Constants import pbnb_id, prv_token_id
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.TestCases.Portal import TEST_SETTING_DEPOSIT_AMOUNT, self_pick_custodian, custodian_remote_address

current_total_collateral = 0


def setup_function():
    INFO("Check if user is already a custodian")
    my_custodian_info = self_pick_custodian.get_my_portal_custodian_status()
    if my_custodian_info is not None:
        global current_total_collateral
        current_total_collateral = my_custodian_info.get_total_collateral()
    else:
        assert my_custodian_info is None


def test_custodian_deposit_success():
    STEP(0, "Get balance before deposit")
    self_pick_custodian.get_prv_balance()

    STEP(1, "Make a valid custodian deposit")
    deposit_tx = self_pick_custodian.make_me_custodian(TEST_SETTING_DEPOSIT_AMOUNT, pbnb_id,
                                                       custodian_remote_address).subscribe_transaction()
    tx_fee = deposit_tx.get_fee()

    STEP(2, "Verify deposit is successful and user becomes custodian")
    assert self_pick_custodian.get_prv_balance_cache() - TEST_SETTING_DEPOSIT_AMOUNT - tx_fee == self_pick_custodian.get_prv_balance()
    WAIT(10)  # wait for collateral to be added to portal status
    custodian_info = self_pick_custodian.get_my_portal_custodian_status()
    assert custodian_info is not None
    global current_total_collateral
    assert custodian_info.get_total_collateral() == TEST_SETTING_DEPOSIT_AMOUNT + current_total_collateral
    current_total_collateral += TEST_SETTING_DEPOSIT_AMOUNT


def test_custodian_deposit_un_success():
    STEP(0, "Get balance before deposit")
    self_pick_custodian.get_prv_balance()
    custodian_info_before = self_pick_custodian.get_my_portal_custodian_status()

    STEP(1, "Make an invalid custodian deposit")
    deposit_tx = self_pick_custodian.make_me_custodian(TEST_SETTING_DEPOSIT_AMOUNT, prv_token_id, custodian_remote_address)
    assert deposit_tx.get_error_msg() is not None

    STEP(2, "verify balance")
    assert self_pick_custodian.get_prv_balance_cache() == self_pick_custodian.get_prv_balance()
    custodian_info_after = self_pick_custodian.get_my_portal_custodian_status()
    if custodian_info_before is None:
        assert custodian_info_after is None
    else:
        assert custodian_info_after.get_total_collateral() == custodian_info_before.get_total_collateral()
