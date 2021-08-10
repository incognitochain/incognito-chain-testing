import pytest

from Configs.Constants import PRV_ID
from Helpers.Logging import STEP, INFO, INFO_HEADLINE
from Helpers.TestHelper import l6
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX import token_owner, token_id_1, token_id_2, acc_list_1_shard


@pytest.mark.parametrize('withdrawer, token1, token2, percent_of_share_to_withdraw', [
    # todo: fix 3 first test, always fail at step 3
    pytest.param(ACCOUNTS[1], PRV_ID, token_id_1, 0.1),
    pytest.param(ACCOUNTS[1], token_id_1, token_id_2, 0.01),
    pytest.param(ACCOUNTS[3], PRV_ID, token_id_1, 1.1),
    pytest.param(ACCOUNTS[4], token_id_1, PRV_ID, 1.1),
    pytest.param(ACCOUNTS[4], PRV_ID, token_id_1, 0.5,
                 marks=pytest.mark.xfail(reason="Withdraw above already, nothing left")),
    pytest.param(ACCOUNTS[3], PRV_ID, token_id_1, 1.1,
                 marks=pytest.mark.xfail(reason="Withdraw above already, nothing left")),
    pytest.param(acc_list_1_shard[3], PRV_ID, token_id_1, 1.1,
                 marks=pytest.mark.xfail(reason="User has no share")),
])
def test_withdraw_liquidity_v2(withdrawer, token1, token2, percent_of_share_to_withdraw):
    pde_state_b4_test = SUT().get_latest_pde_state_info()
    rate_b4 = pde_state_b4_test.get_rate_between_token(token1, token2)
    my_pde_share_b4 = pde_state_b4_test.get_pde_shares_amount(withdrawer, token1, token2)
    wdraw_share_x_percent = int(my_pde_share_b4 * percent_of_share_to_withdraw)
    wdraw_share_available = min(wdraw_share_x_percent, my_pde_share_b4)
    # assert my_pde_share_b4 != 0, f'User {withdrawer.payment_key} has no share'
    wdraw_recv_amount_est = pde_state_b4_test.cal_share_withdrawal(withdrawer, wdraw_share_x_percent, token1, token2)
    STEP(1, 'Get balance of withdrawer before test')
    bal_b4 = {
        token1: withdrawer.get_balance(token1),
        token2: withdrawer.get_balance(token2)}

    STEP(2, f'Withdraw {percent_of_share_to_withdraw} of my share')
    withdraw_tx = withdrawer.pde_withdraw_contribution_v2(token1, token2, wdraw_share_x_percent).subscribe_transaction()

    STEP(3, f'Wait for money to come')
    bal_af = {}
    for token in [token1, token2]:
        bal_af[token] = withdrawer.wait_for_balance_change(token, bal_b4[token], int(wdraw_recv_amount_est[token] / 10))

    INFO_HEADLINE('Summary')
    pde_state_af_test = SUT().get_latest_pde_state_info()
    rate_af = pde_state_af_test.get_rate_between_token(token1, token2)
    my_pde_share_af = pde_state_af_test.get_pde_shares_amount(withdrawer, token1, token2)
    INFO(f"""                                                                                
        Balance {l6(token1)} before - after           : {bal_b4[token1]} - {bal_af[token1]} 
        Balance {l6(token2)} before - after           : {bal_b4[token2]} - {bal_af[token2]} 
        Withdraw share actual                   : {wdraw_share_available}
        Withdraw receive amount {l6(token1)} - {l6(token2)} : {wdraw_recv_amount_est[token1]} - {wdraw_recv_amount_est[token2]}
        Share {l6(token1)} before - after             : {my_pde_share_b4} - {my_pde_share_af} 
        Withdraw tx fee                         : {withdraw_tx.get_fee()}
        Pool before - after                     : {rate_b4} -  {rate_af}
        """)

    for token in [token1, token2]:
        INFO(f'Checking balance of token {l6(token)}')
        if token == PRV_ID:
            bal_af_est = bal_b4[token] + wdraw_recv_amount_est[token] - withdraw_tx.get_fee()
        else:
            bal_af_est = bal_b4[token] + wdraw_recv_amount_est[token]
        missing = bal_af_est - bal_af[token]
        INFO(f"bal after estimate-real: {bal_af_est} - {bal_af[token]} = {missing}")
        # assert bal_af_est == bal_af[token], f'missing {missing}'

    # todo:    STEP(4, 'Pool verification')
    assert wdraw_share_available == my_pde_share_b4 - my_pde_share_af
    assert wdraw_recv_amount_est[token1] == rate_b4[0] - rate_af[0]
    assert wdraw_recv_amount_est[token2] == rate_b4[1] - rate_af[1]
