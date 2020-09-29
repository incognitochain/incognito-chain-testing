import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import SUT, ACCOUNTS
from IncognitoChain.TestCases.DEX import token_owner, token_id_1, token_id_2


@pytest.mark.parametrize('withdrawer, token1, token2, percent_of_share_amount_to_withdraw', [
    # todo: fix 3 first test, always fail at step 3
    (token_owner, PRV_ID, token_id_1, 1.1),
    (token_owner, token_id_1, token_id_2, 0.01),
    (ACCOUNTS[3], PRV_ID, token_id_1, 1.1),
    (ACCOUNTS[3], token_id_1, token_id_2, 0.01),
])
def test_withdraw_liquidity_v2(withdrawer, token1, token2, percent_of_share_amount_to_withdraw):
    pde_state_b4_test = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_b4 = pde_state_b4_test.get_rate_between_token(token1, token2)
    my_pde_share_b4 = pde_state_b4_test.get_pde_shares_amount(withdrawer, token1, token2)
    withdraw_share = int(my_pde_share_b4 * percent_of_share_amount_to_withdraw)
    withdraw_share_received = min(withdraw_share, my_pde_share_b4)
    sum_share_of_pair = pde_state_b4_test.sum_share_pool_of_pair(None, token1, token2)

    if my_pde_share_b4 is None:
        pytest.skip(f'User {withdrawer.payment_key} has no share')
    withdraw_amounts = {
        token1: int(withdraw_share_received * rate_b4[0] / sum_share_of_pair),
        token2: int(withdraw_share_received * rate_b4[1] / sum_share_of_pair)
    }

    STEP(1, 'Get balance of withdrawer before test')
    bal_b4 = {
        token1: withdrawer.get_token_balance(token1),
        token2: withdrawer.get_token_balance(token2)}

    STEP(2, f'Withdraw {percent_of_share_amount_to_withdraw} of my share')
    withdraw_tx = withdrawer.pde_withdraw_contribution_v2(token1, token2, withdraw_share).subscribe_transaction()

    STEP(3, f'Wait for money to come')
    bal_af = {}
    for token in [token1, token2]:

        bal_af[token] = withdrawer.wait_for_balance_change(token, bal_b4[token], int(withdraw_share / 10))
        if token == PRV_ID:
            assert bal_b4[token] + withdraw_share_received - withdraw_tx.get_fee() == bal_af[token]
        else:
            assert bal_b4[token] + withdraw_share_received == bal_af[token]

    # todo:    STEP(4, 'Pool verification')
    INFO_HEADLINE('Summary')
    pde_state_af_test = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_af = pde_state_af_test.get_rate_between_token(token1, token2)
    my_pde_share_af = pde_state_af_test.get_pde_shares_amount(withdrawer, token1, token2)

    INFO(f"""                                                                                
        Balance {l6(token1)} before - after          : {bal_b4[token1]} - {bal_af[token1]} 
        Balance {l6(token2)} before - after          : {bal_b4[token2]} - {bal_af[token2]} 
        Withdraw share actual                  :{withdraw_share_received}
        Withdraw receive amount {l6(token1)} - {l6(token2)}: {withdraw_amounts[token1]} - {withdraw_amounts[token2]}
        Share {l6(token1)} before - after           : {my_pde_share_b4} - {my_pde_share_af} 
        Pool before - after                   : {rate_b4} -  {rate_af}
        """)
