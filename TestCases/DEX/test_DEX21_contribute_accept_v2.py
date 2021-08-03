import pytest

from Configs.Constants import PRV_ID, coin
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import INFO, STEP
from Helpers.TestHelper import l6, ChainHelper
from Helpers.Time import get_current_date_time
from Objects import PdeObjects
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from Objects.PdeObjects import PDEContributeInfo
from TestCases.DEX import token_id_1, token_owner


@pytest.mark.parametrize('contributor,token1,token2', (
        [ACCOUNTS[1], PRV_ID, token_id_1],
        [ACCOUNTS[1], token_id_1, PRV_ID],
))
def test_contribute_prv(contributor, token1, token2):
    pair_id = f'{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
    tok1_contrib_amount = coin(1234)
    tok2_contrib_amount = coin(2134)
    for tok, amount in zip((token1, token2), (tok1_contrib_amount, tok2_contrib_amount)):
        token_owner.top_up_if_lower_than(contributor, amount + 1000, int(amount * 1.5), tok)

    pde_state_b4 = SUT().get_latest_pde_state_info()
    INFO(f"""
            test_DEX01_contribute:
            - contribute a pair of token {l6(token1)} vs {l6(token2)}
            - checking token rate after contribute
            - check share amount after contribute
            - check the amount of refund and the actual amount contribution
            """)
    STEP(0, "Checking env - checking waiting contribution list, pDEX share amount")
    assert pde_state_b4.find_waiting_contribution_of_user(contributor, pair_id, token1) == []
    assert pde_state_b4.find_waiting_contribution_of_user(contributor, pair_id, token2) == []

    bal_tok1_be4_contrib = contributor.get_balance(token1)
    bal_tok2_be4_contrib = contributor.get_balance(token2)
    all_share_amount_b4 = pde_state_b4.get_pde_shares_amount(None, token1, token2)
    owner_share_amount_b4 = pde_state_b4.get_pde_shares_amount(contributor, token1, token2)
    rate_b4 = pde_state_b4.get_rate_between_token(token1, token2)
    INFO(f'{l6(token1)} balance before contribution: {bal_tok1_be4_contrib}')
    INFO(f'{l6(token2)} balance before contribution: {bal_tok2_be4_contrib}')
    INFO(f'Sum share amount before contribution  : {all_share_amount_b4}')
    INFO(f'Owner share amount before contribution: {owner_share_amount_b4}')
    INFO(f'Rate before contribution: {l6(token1)}:{l6(token2)} is {rate_b4}')
    # breakpoint()
    STEP(1, f"Contribute {l6(token1)}")
    contribute_token1_result = contributor.pde_contribute_v2(token1, tok1_contrib_amount, pair_id).expect_no_error()
    contribute_token1_fee = contribute_token1_result.subscribe_transaction().get_fee()

    STEP(2, 'Verify contribution')
    assert PdeObjects.wait_for_user_contribution_in_waiting(contributor, pair_id, token1) is not None

    STEP(3, f'Contribute {l6(token2)}')
    contribute_token2_result = contributor.pde_contribute_v2(token2, tok2_contrib_amount, pair_id)
    contribute_token2_fee = contribute_token2_result.subscribe_transaction().get_fee()
    contrib_fee_sum = contribute_token1_fee + contribute_token2_fee

    STEP(4, f'Verify {l6(token1)} is no longer in waiting contribution list')
    PdeObjects.wait_for_user_contribution_in_waiting(contributor, pair_id, token1)
    bal_tok1_aft_contrib = contributor.get_balance(token1)
    bal_tok2_aft_contrib = contributor.get_balance(token2)
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

    STEP(5, f'Verify contribution pair {l6(token1)} vs {l6(token2)}')
    ChainHelper.wait_till_next_beacon_height(2)
    pde_state_af = SUT().get_latest_pde_state_info()
    rate_after = pde_state_af.get_rate_between_token(token1, token2)
    owner_share_amount_after = pde_state_af.get_pde_shares_amount(contributor, token1, token2)
    all_share_amount_after = pde_state_af.get_pde_shares_amount(None, token1, token2)
    expect_token1_contribution, expect_token2_contribution, refund_token1, refund_token2 = \
        pde_state_af.cal_contribution({token1: tok1_contrib_amount, token2: tok2_contrib_amount})

    INFO(f'Now wait for contribution refund')
    if refund_token1 > 0:
        bal_tok1_aft_refund = contributor.wait_for_balance_change(token1, bal_tok1_aft_contrib)
    else:
        bal_tok1_aft_refund = bal_tok1_aft_contrib
    if refund_token2 > 0:
        bal_tok2_aft_refund = contributor.wait_for_balance_change(token2, bal_tok2_aft_contrib)
    else:
        bal_tok2_aft_refund = bal_tok2_aft_contrib

    contribution_status = PDEContributeInfo()
    contribution_status.get_contribute_status(pair_id)
    api_contrib_tok1 = contribution_status.get_contribute_amount_of_token(token1)
    api_contrib_tok2 = contribution_status.get_contribute_amount_of_token(token2)
    api_return_tok1 = contribution_status.get_return_amount_of_token(token1)
    api_return_tok2 = contribution_status.get_return_amount_of_token(token2)

    # contribution_status = SUT().dex().get_contribution_status(pair_id)
    # api_contrib_tok1 = contribution_status.get_contributed_2_amount()
    # api_contrib_tok2 = contribution_status.get_contributed_1_amount()
    # api_return_tok1 = contribution_status.get_returned_2_amount()
    # api_return_tok2 = contribution_status.get_returned_1_amount()

    INFO(f"""
        Owner share amount before: {owner_share_amount_b4}
        Owner share amount after : {owner_share_amount_after}
        All share amount before  : {all_share_amount_b4}
        All share amount after   : {all_share_amount_after}
        Rate before: {rate_b4}
        Rate after : {rate_after}
        Contributed:
            contribute {l6(token1)} : {tok1_contrib_amount}
            contribute {l6(token2)} : {tok2_contrib_amount}
        Expect contribution:
            {l6(token1)}            : {expect_token1_contribution}
            {l6(token2)}            : {expect_token2_contribution}
        From API:
            contribute {l6(token1)} : {api_contrib_tok1}
            contribute {l6(token2)} : {api_contrib_tok2}
            return     {l6(token1)} : {api_return_tok1}
            return     {l6(token2)} : {api_return_tok2}""")

    INFO(f"{l6(token1)} balance after contribution (after refund): {bal_tok1_aft_refund}")
    INFO(f"{l6(token2)} balance after contribution (after refund): {bal_tok2_aft_refund}")

    if rate_b4 != 0:
        calculated_owner_share_amount_after = \
            PdeMath.cal_contribution_share(api_contrib_tok1, sum(all_share_amount_b4), rate_b4[0],
                                           owner_share_amount_b4)
        assert abs(calculated_owner_share_amount_after - owner_share_amount_after) <= 1 and INFO(
            f"Calculated vs Actual share : {calculated_owner_share_amount_after}-{owner_share_amount_after}"), \
            'actual share amount vs estimated share amount is off by more than 1 nano'

    if token1 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1 + contrib_fee_sum
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2
    elif token2 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2 + contrib_fee_sum
    else:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2

    INFO('Check amount contribute by api vs expect')
    assert api_contrib_tok1 - expect_token1_contribution <= 1
    assert api_contrib_tok2 - expect_token2_contribution <= 1

    INFO('Check rate')
    assert rate_after[0] == rate_b4[0] + api_contrib_tok1
    assert rate_after[1] == rate_b4[1] + api_contrib_tok2
