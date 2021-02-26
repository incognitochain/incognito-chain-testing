import pytest

from Configs.Constants import PRV_ID
from Helpers.Logging import STEP, INFO, INFO_HEADLINE, ERROR
from Helpers.TestHelper import l6
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX import token_id_1, token_id_2, token_owner


@pytest.mark.parametrize('withdrawer, token1, token2, percent_of_share_amount_to_withdraw', [
    (token_owner, PRV_ID, token_id_1, 0.71),
    (token_owner, token_id_1, token_id_2, 0.21),
    (ACCOUNTS[3], PRV_ID, token_id_1, 0.3),
    (ACCOUNTS[3], token_id_1, token_id_2, 0.81),
])
def test_withdraw_liquidity(withdrawer, token1, token2, percent_of_share_amount_to_withdraw):
    pde_state_b4_test = SUT().get_latest_pde_state_info()
    rate_b4 = pde_state_b4_test.get_rate_between_token(token1, token2)
    STEP(1, 'Get balance of withdrawer before test')
    bal_b4 = {
        token1: withdrawer.get_token_balance(token1),
        token2: withdrawer.get_token_balance(token2)}
    my_pde_share_b4 = pde_state_b4_test.get_pde_shares_amount(withdrawer, token1, token2)
    assert my_pde_share_b4 is not None, ERROR(f"share of {l6(withdrawer.private_key)} is NULL")

    withdraw_share = int(my_pde_share_b4 * percent_of_share_amount_to_withdraw)
    withdraw_share_actual = min(withdraw_share, my_pde_share_b4)
    sum_share_of_pair = pde_state_b4_test.sum_share_pool_of_pair(None, token1, token2)
    withdraw_amounts = {
        token1: int(withdraw_share_actual * rate_b4[0] / sum_share_of_pair),
        token2: int(withdraw_share_actual * rate_b4[1] / sum_share_of_pair)
    }

    STEP(2, f'Withdraw {percent_of_share_amount_to_withdraw} of my share')
    withdraw_tx = withdrawer.pde_withdraw_contribution(token1, token2, withdraw_share).subscribe_transaction()

    STEP(3, f'Wait for money to come')
    bal_af = {}
    for token in [token1, token2]:

        bal_af[token] = withdrawer.wait_for_balance_change(token, bal_b4[token], int(withdraw_amounts[token] / 10))
        if token == PRV_ID:
            assert bal_b4[token] + withdraw_amounts[token] - withdraw_tx.get_fee() == bal_af[token]
        else:
            assert bal_b4[token] + withdraw_amounts[token] == bal_af[token]

    # todo:    STEP(4, 'Pool verification')
    INFO_HEADLINE('Summary')
    pde_state_af_test = SUT().get_latest_pde_state_info()
    rate_af = pde_state_af_test.get_rate_between_token(token1, token2)
    my_pde_share_af = pde_state_af_test.get_pde_shares_amount(withdrawer, token1, token2)

    INFO(f"""                                                                                
        Blance {l6(token1)} before - after          : {bal_b4[token1]} - {bal_af[token1]} 
        Blance {l6(token2)} before - after          : {bal_b4[token2]} - {bal_af[token2]} 
        Withdraw share actual                  :{withdraw_share_actual}
        Withdraw receive amount {l6(token1)} - {l6(token2)}: {withdraw_amounts[token1]} - {withdraw_amounts[token2]}
        Share {l6(token1)} before - after           : {my_pde_share_b4} - {my_pde_share_af} 
        Pool before - after                   : {rate_b4} -  {rate_af}
        """)
