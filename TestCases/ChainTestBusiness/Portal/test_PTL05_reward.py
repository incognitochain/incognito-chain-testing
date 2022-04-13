import pytest

from Configs.Constants import PRV_ID, Status
from Helpers.Logging import STEP, INFO
from Helpers.TestHelper import l6
from Objects.IncognitoTestCase import ACCOUNTS
from Objects.PortalObjects import RewardWithdrawTxInfo
from TestCases.ChainTestBusiness.Portal import portal_user, find_fat_custodian


@pytest.mark.parametrize("custodian_account", [
    'fat custodian',
    portal_user,
    ACCOUNTS[3],
    ACCOUNTS[4],
    ACCOUNTS[5],
    ACCOUNTS[6],
])
def test_withdraw_portal_reward(custodian_account):
    if type(custodian_account) is str and custodian_account == 'fat custodian':
        custodian_account = find_fat_custodian()
    STEP(1, "Get reward amount, balance of custodian")
    prv_reward_amount = custodian_account.portal_get_my_reward(PRV_ID)
    prv_balance_before = custodian_account.get_balance()
    INFO(f'''
            Reward amount of {l6(custodian_account.incognito_addr)} is {prv_reward_amount}
            Balance is {prv_balance_before}''')

    STEP(2, "check if custodian has any reward")
    assert prv_reward_amount > 0, f'Custodian has no reward, fail the test'

    STEP(3, 'Withdraw and check withdraw status')
    withdraw_tx = custodian_account.portal_withdraw_reward(PRV_ID).expect_no_error().subscribe_transaction()
    fee = withdraw_tx.get_fee()
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
    prv_balance_after_2 = custodian_account.get_balance()
    assert prv_balance_after_2 == prv_balance_after - fee
