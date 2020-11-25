import pytest

from IncognitoChain.Configs.Constants import PRV_ID, Status
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
from IncognitoChain.Objects.PortalObjects import RewardWithdrawTxInfo
from IncognitoChain.TestCases.Portal import fat_custodian, portal_user


@pytest.mark.parametrize("custodian_account", [
    fat_custodian,
    portal_user,
    ACCOUNTS[3],
    ACCOUNTS[4],
    ACCOUNTS[5],
    ACCOUNTS[6],
])
def test_withdraw_portal_reward(custodian_account):
    STEP(1, "Get reward amount, balance of custodian")
    prv_reward_amount = custodian_account.portal_get_my_reward(PRV_ID)
    prv_balance_before = custodian_account.get_prv_balance()
    INFO(f'''
            Reward amount of {l6(custodian_account.incognito_addr)} is {prv_reward_amount}
            Balance is {prv_balance_before}''')

    STEP(2, "check if custodian has any reward")
    if prv_reward_amount <= 0:
        pytest.skip("no reward to withdraw, skip this test")

    STEP(3, 'Withdraw and check withdraw status')
    withdraw_tx = custodian_account.portal_withdraw_reward(PRV_ID).expect_no_error()
    fee = withdraw_tx.subscribe_transaction().get_fee()
    withdraw_tx_info = RewardWithdrawTxInfo()
    withdraw_tx_info.get_reward_info_by_tx_id(withdraw_tx.get_tx_id())
    assert withdraw_tx_info.get_status() == Status.Portal.RewardWithdrawStatus.ACCEPT

    STEP(4, 'Verify balance')
    prv_balance_after = custodian_account.wait_for_balance_change()
    assert prv_balance_after == prv_balance_before + prv_reward_amount - fee

    STEP(5, 'Continue to withdraw, expect fail')
    withdraw_tx = custodian_account.portal_withdraw_reward(PRV_ID).expect_no_error()
    fee = withdraw_tx.subscribe_transaction().get_fee()
    withdraw_tx_info = RewardWithdrawTxInfo()
    withdraw_tx_info.get_reward_info_by_tx_id(withdraw_tx.get_tx_id())
    assert withdraw_tx_info.get_status() == Status.Portal.RewardWithdrawStatus.REJECTED

    STEP(6, 'Verify balance')
    prv_balance_after_2 = custodian_account.get_prv_balance()
    assert prv_balance_after_2 == prv_balance_after - fee
