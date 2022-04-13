import pytest

from Configs.Constants import PRV_ID
from Helpers.Logging import STEP, INFO, INFO_HEADLINE, WARNING
from Helpers.TestHelper import l6
from Objects.IncognitoTestCase import SUT
from TestCases.ChainTestBusiness.DEX import token_owner, token_id_1, token_id_2, acc_list_1_shard


@pytest.mark.parametrize('withdrawer, token1, token2, percent_of_reward_amount_to_withdraw', [
    pytest.param(token_owner, PRV_ID, token_id_1, 1.1),
    pytest.param(token_owner, token_id_1, token_id_2, 0.01,
                 marks=pytest.mark.xfail(reason="there's no token-token reward")),
    pytest.param(acc_list_1_shard[2], PRV_ID, token_id_1, 1.1,
                 marks=pytest.mark.xfail(reason="there's no reward")),
    pytest.param(acc_list_1_shard[2], token_id_1, token_id_2, 0.01,
                 marks=pytest.mark.xfail(reason="there's no token-token reward")),
])
def test_withdraw_liquidity_v2(withdrawer, token1, token2, percent_of_reward_amount_to_withdraw):
    pde_state_b4_test = SUT().get_latest_pde_state_info()
    rate_b4 = pde_state_b4_test.get_rate_between_token(token1, token2)

    my_pde_reward_b4 = pde_state_b4_test.get_contributor_reward_amount(withdrawer, token1, token2)
    withdraw_reward_amount = int(my_pde_reward_b4 * percent_of_reward_amount_to_withdraw)
    received_amount = 0 if percent_of_reward_amount_to_withdraw > 1 else withdraw_reward_amount

    if my_pde_reward_b4 != 0:
        # because there are test cases which test withdrawing reward when there's no reward. do don't assert here.
        # assert here will make this test ends here in such cases, and we can never now if user can still
        # withdraw something out of out PDEX even when they have no PDEX reward
        # Hence the WARNING instead of assert
        WARNING(f'User {withdrawer.payment_key} has no pde reward')

    STEP(1, 'Get balance of withdrawer before test')
    prv_bal_b4 = withdrawer.get_balance()
    bal_b4 = {
        token1: withdrawer.get_balance(token1),
        token2: withdrawer.get_balance(token2)}

    STEP(2, f'Withdraw {percent_of_reward_amount_to_withdraw} of my reward')
    withdraw_tx = withdrawer.pde_withdraw_reward_v2(token1, token2, withdraw_reward_amount) \
        .expect_no_error().subscribe_transaction()

    STEP(3, f'Wait for money to come')
    prv_bal_af = withdrawer.wait_for_balance_change(PRV_ID, prv_bal_b4, int(withdraw_reward_amount / 10))
    assert prv_bal_b4 + received_amount - withdraw_tx.get_fee() == prv_bal_af

    bal_af = {
        token1: withdrawer.get_balance(token1),
        token2: withdrawer.get_balance(token2)}

    INFO_HEADLINE('Summary')
    pde_state_af_test = SUT().get_latest_pde_state_info()
    rate_af = pde_state_af_test.get_rate_between_token(token1, token2)
    my_pde_reward_af = pde_state_af_test.get_contributor_reward_amount(withdrawer, token1, token2)
    assert rate_b4 == rate_af  # make sure rate not change
    assert my_pde_reward_af == my_pde_reward_b4 - received_amount

    INFO(f"""                                                                                
        Balance {l6(token1)} before - after          : {bal_b4[token1]} - {bal_af[token1]} 
        Balance {l6(token2)} before - after          : {bal_b4[token2]} - {bal_af[token2]} 
        Balance prv before - after =           : {prv_bal_b4} - {prv_bal_af}
        Withdraw reward actual                 : {withdraw_reward_amount}
        """)
