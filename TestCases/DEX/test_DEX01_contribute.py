import pytest

from Configs.Constants import PRV_ID, coin, Status
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import INFO, STEP
from Helpers.TestHelper import l6
from Helpers.Time import get_current_date_time
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from Objects.PdeObjects import PDEContributeInfo
from TestCases.DEX import token_id_1, token_owner, token_id_2


@pytest.mark.parametrize('token1,token2', (
        [PRV_ID, token_id_1],  # contribute prv
        [token_id_1, PRV_ID],  # contribute prv reverse
        [token_id_2, token_id_1],  # contribute token
        [token_id_1, token_id_2],  # contribute token reverse
))
@pytest.mark.dependency(scope='session')
def test_contribute(token1, token2):
    pair_id = f'{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
    tok1_contrib_amount = coin(1234)
    tok2_contrib_amount = coin(2134)
    for tok, amount in zip((token1, token2), (tok1_contrib_amount, tok2_contrib_amount)):
        if tok == PRV_ID:
            COIN_MASTER.top_up_if_lower_than(token_owner, amount, amount + 1000)
    pde_state_b4_test = SUT().get_latest_pde_state_info()
    is_none_zero_pair = pde_state_b4_test.get_contributor_reward_amount(token1, token2) != [0, 0]
    INFO(f"""
            test_DEX01_contribute:
            - contribute a pair of token {l6(token1)} vs {l6(token2)}
            - checking token rate after contribute
            - check share amount after contribute
            - check the amount of refund and the actual amount contribution
            """)
    STEP(0, "Checking env - checking waiting contribution list, pDEX share amount")
    assert pde_state_b4_test.find_waiting_contribution_of_user(token_owner, pair_id, token1) == []
    assert pde_state_b4_test.find_waiting_contribution_of_user(token_owner, pair_id, token2) == []

    bal_tok1_be4_contrib = token_owner.get_token_balance(token1)
    bal_tok2_be4_contrib = token_owner.get_token_balance(token2)
    all_share_amount = pde_state_b4_test.get_pde_shares_amount(None, token1, token2)
    owner_share_amount = pde_state_b4_test.get_pde_shares_amount(token_owner, token2, token1)
    INFO(f'{l6(token1)} balance before contribution: {bal_tok1_be4_contrib}')
    INFO(f'{l6(token2)} balance before contribution: {bal_tok2_be4_contrib}')
    INFO(f'Sum share amount before contribution  : {all_share_amount}')
    INFO(f'Owner share amount before contribution: {owner_share_amount}')
    rate_b4 = pde_state_b4_test.get_rate_between_token(token2, token1)
    INFO(f'Rate {l6(token2)}:{l6(token1)} is {rate_b4}')
    # breakpoint()
    STEP(1, f"Contribute {l6(token1)}")
    if token1 == PRV_ID:
        contribute_token1_result = token_owner.pde_contribute_prv(tok1_contrib_amount, pair_id)
    else:
        contribute_token1_result = token_owner.pde_contribute_token(token1, tok1_contrib_amount, pair_id)
    contribute_token1_fee = contribute_token1_result.subscribe_transaction().get_fee()

    STEP(2, 'Verify contribution')
    assert token_owner.pde_wait_till_my_token_in_waiting_for_contribution(pair_id, token1)

    STEP(3, f'Contribute {l6(token2)}')
    if token2 == PRV_ID:
        contribute_token2_result = token_owner.pde_contribute_prv(tok2_contrib_amount, pair_id)
    else:
        contribute_token2_result = token_owner.pde_contribute_token(token2, tok2_contrib_amount, pair_id)
    contribute_token2_fee = contribute_token2_result.subscribe_transaction().get_fee()
    contrib_fee_sum = contribute_token1_fee + contribute_token2_fee

    STEP(4, f'Verify {l6(token1)} is no longer in waiting contribution list')
    token_owner.pde_wait_till_my_token_out_waiting_for_contribution(pair_id, token1)
    bal_tok1_aft_contrib = token_owner.get_token_balance(token1)
    bal_tok2_aft_contrib = token_owner.get_token_balance(token2)
    INFO(f'{l6(token1)} after contribute (before refund): {bal_tok1_aft_contrib}')
    INFO(f'{l6(token2)} after contribute (before refund): {bal_tok2_aft_contrib}')

    if token1 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_contrib + tok1_contrib_amount + contrib_fee_sum
        assert bal_tok2_be4_contrib == bal_tok2_aft_contrib + tok2_contrib_amount
    elif token2 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_contrib + tok1_contrib_amount
        assert bal_tok2_be4_contrib == bal_tok2_aft_contrib + tok2_contrib_amount + contrib_fee_sum
    else:
        assert bal_tok1_be4_contrib == bal_tok1_aft_contrib + tok1_contrib_amount
        assert bal_tok2_be4_contrib == bal_tok2_aft_contrib + tok2_contrib_amount

    STEP(5, f'Check rate {l6(token1)} vs {l6(token2)}')
    pde_state_af_test = SUT().get_latest_pde_state_info()
    rate_after = pde_state_af_test.get_rate_between_token(token1, token2)
    INFO(f'rate {l6(token1)} vs {l6(token2)} = {rate_after}')
    owner_share_amount_after = pde_state_af_test.get_pde_shares_amount(token_owner, token2, token1)
    all_share_amount_after = pde_state_af_test.get_pde_shares_amount(None, token1, token2)
    INFO(f'Sum share amount after contribution  : {all_share_amount_after}')
    INFO(f'Owner share amount after contribution: {owner_share_amount_after}')
    expect_token1_contribution, expect_token2_contribution, refund_token1, refund_token2 = \
        pde_state_af_test.cal_contribution({token1: tok1_contrib_amount, token2: tok2_contrib_amount})

    INFO(f'Now wait for contribution refund')
    if refund_token1 > 0:
        bal_tok1_aft_refund = token_owner.wait_for_balance_change(token1, bal_tok1_aft_contrib)
    else:
        bal_tok1_aft_refund = bal_tok1_aft_contrib
    if refund_token2 > 0:
        bal_tok2_aft_refund = token_owner.wait_for_balance_change(token2, bal_tok2_aft_contrib)
    else:
        bal_tok2_aft_refund = bal_tok2_aft_contrib

    contribution_status = PDEContributeInfo()
    contribution_status.get_contribute_status(pair_id)
    INFO(f"{l6(token1)} balance after contribution (after refund): {bal_tok1_aft_refund}")
    INFO(f"{l6(token2)} balance after contribution (after refund): {bal_tok2_aft_refund}")
    debug_info = f""" 
        Owner share amount before: {owner_share_amount}
        Owner share amount after : {owner_share_amount_after}
        All share amount before  : {all_share_amount}
        All share amount after   : {all_share_amount_after}
        Rate before: {rate_b4}
        Rate after : {rate_after}
        Contributed:
            contribute {l6(token1)} : {tok1_contrib_amount}
            contribute {l6(token2)} : {tok2_contrib_amount}
        Expect contribution:
            {l6(token1)}            : {expect_token1_contribution}
            {l6(token2)}            : {expect_token2_contribution}"""
    # NOTE: at first time contribute, all will be taken so API will return 0 as api_contrib_tok*
    real_contrib_amount1 = tok1_contrib_amount if is_none_zero_pair else api_contrib_tok1
    real_contrib_amount2 = tok2_contrib_amount if is_none_zero_pair else api_contrib_tok2

    if token1 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + real_contrib_amount1 + contrib_fee_sum
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + real_contrib_amount2
    elif token2 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + real_contrib_amount1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + real_contrib_amount2 + contrib_fee_sum
    else:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + real_contrib_amount1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + real_contrib_amount2

    if is_none_zero_pair:
        api_contrib_tok1 = contribution_status.get_contribute_amount_of_token(token1)
        api_contrib_tok2 = contribution_status.get_contribute_amount_of_token(token2)
        api_return_tok1 = contribution_status.get_return_amount_of_token(token1)
        api_return_tok2 = contribution_status.get_return_amount_of_token(token2)
        debug_info = "NOT FIRST time contribution" + debug_info + f"""
        From API:
            contribute {l6(token1)} : {api_contrib_tok1}
            contribute {l6(token2)} : {api_contrib_tok2}
            return     {l6(token1)} : {api_return_tok1}
            return     {l6(token2)} : {api_return_tok2}"""
        INFO(debug_info)
        assert contribution_status.get_status() == Status.Dex.Contribution.MATCHED_RETURNED
        calculated_owner_share_amount_after = \
            PdeMath.cal_contribution_share(api_contrib_tok2, sum(all_share_amount), rate_b4[0], owner_share_amount)
        assert INFO(f"Contribution shares amount is correct") \
               and abs(calculated_owner_share_amount_after - owner_share_amount_after) <= 1, \
            f'calculated vs real = {calculated_owner_share_amount_after} - {owner_share_amount_after}'
    else:
        debug_info = "FIRST time contribution" + debug_info
        INFO(debug_info)
        assert contribution_status.get_status() == Status.Dex.Contribution.ACCEPTED
