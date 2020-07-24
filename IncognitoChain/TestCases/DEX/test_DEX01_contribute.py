import pytest

from IncognitoChain.Configs.Constants import PRV_ID, coin
from IncognitoChain.Helpers.Logging import INFO, STEP
from IncognitoChain.Helpers.TestHelper import calculate_contribution, l6
from IncognitoChain.Helpers.Time import get_current_date_time
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.DEX import token_id_1, token_owner, token_id_2


@pytest.mark.parametrize('token1,token2', (
    # all 4 cases pass on test net
    # last 2 always fail on jenkins testbed,
    # the very last case offend fail by missing 1 nano prv calculation of bal after contribute
    # the other fail because contribute amount from api is always 0
    [PRV_ID, token_id_1],  # contribute prv
    [token_id_1, PRV_ID],  # contribute prv reverse
    [token_id_2, token_id_1],  # contribute token
    [token_id_1, token_id_2],  # contribute token reverse
))
def test_contribute(token1, token2):
    pair_id = f'{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
    tok1_contrib_amount = coin(1234)
    tok2_contrib_amount = coin(2134)

    INFO(f"""
            test_DEX01_contribute:
            - contribute a pair of token {l6(token1)} vs {l6(token2)}
            - checking token rate after contribute
            - check share amount after contribute
            - check the amount of refund and the actual amount contribution
            """)
    STEP(0, "Checking env - checking waiting contribution list, pDEX share amount")
    assert not token_owner.is_my_token_waiting_for_contribution(pair_id, token1)
    assert not token_owner.is_my_token_waiting_for_contribution(pair_id, token2)

    bal_tok1_be4_contrib = token_owner.get_token_balance(token1)
    bal_tok2_be4_contrib = token_owner.get_token_balance(token2)
    all_share_amount = SUT.full_node.help_get_pde_share_list(token2, token1)
    owner_share_amount = token_owner.get_my_current_pde_share(token2, token1)
    INFO(f'{l6(token1)} balance before contribution: {bal_tok1_be4_contrib}')
    INFO(f'{l6(token2)} balance before contribution: {bal_tok2_be4_contrib}')
    INFO(f'Sum share amount before contribution  : {all_share_amount}')
    INFO(f'Owner share amount before contribution: {owner_share_amount}')
    rate = SUT.full_node.get_latest_rate_between(token2, token1)
    INFO(f'Rate {l6(token2)}:{l6(token1)} is {rate}')
    # breakpoint()
    STEP(1, f"Contribute {l6(token1)}")
    if token1 == PRV_ID:
        contribute_token1_result = token_owner.pde_contribute_prv(tok1_contrib_amount, pair_id)
    else:
        contribute_token1_result = token_owner.pde_contribute_token(token1, tok1_contrib_amount, pair_id)
    contribute_token1_fee = contribute_token1_result.subscribe_transaction().get_fee()

    STEP(2, 'Verify contribution')
    assert token_owner.wait_till_my_token_in_waiting_for_contribution(pair_id, token1)

    STEP(3, f'Contribute {l6(token2)}')
    if token2 == PRV_ID:
        contribute_token2_result = token_owner.pde_contribute_prv(tok2_contrib_amount, pair_id)
    else:
        contribute_token2_result = token_owner.pde_contribute_token(token2, tok2_contrib_amount, pair_id)
    contribute_token2_fee = contribute_token2_result.subscribe_transaction().get_fee()
    contrib_fee_sum = contribute_token1_fee + contribute_token2_fee

    STEP(4, f'Verify {l6(token1)} is no longer in waiting contribution list')
    token_owner.wait_till_my_token_out_waiting_for_contribution(token1)
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
    rate_after = SUT.full_node.get_latest_rate_between(token1, token2)
    INFO(f'rate {l6(token1)} vs {l6(token2)} = {rate_after}')
    owner_share_amount_after = token_owner.get_my_current_pde_share(token2, token1)
    all_share_amount_after = SUT.full_node.help_get_pde_share_list(token2, token1)
    INFO(f'Sum share amount after contribution  : {all_share_amount_after}')
    INFO(f'Owner share amount after contribution: {owner_share_amount_after}')
    expect_token1_contribution, expect_token2_contribution, refund_token1, refund_token2 = \
        calculate_contribution(tok1_contrib_amount, tok2_contrib_amount, rate_after)

    INFO(f'Now wait for contribution refund')
    if refund_token1 > 0:
        bal_tok1_aft_refund = token_owner.wait_for_balance_change(token1, bal_tok1_aft_contrib)
    else:
        bal_tok1_aft_refund = bal_tok1_aft_contrib
    if refund_token2 > 0:
        bal_tok2_aft_refund = token_owner.wait_for_balance_change(token2, bal_tok2_aft_contrib)
    else:
        bal_tok2_aft_refund = bal_tok2_aft_contrib

    contribution_status = SUT.full_node.dex().get_contribution_status(pair_id)
    api_contrib_tok1 = contribution_status.get_contributed_2_amount()
    api_contrib_tok2 = contribution_status.get_contributed_1_amount()
    api_return_tok1 = contribution_status.get_returned_2_amount()
    api_return_tok2 = contribution_status.get_returned_1_amount()

    INFO(f"""
        Owner share amount before: {owner_share_amount}
        Owner share amount after : {owner_share_amount_after}
        All share amount before  : {all_share_amount}
        All share amount after   : {all_share_amount_after}
        Rate before: {rate}
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

    if rate is not None:
        calculated_owner_share_amount_after = round((api_contrib_tok2 * sum(all_share_amount)) / rate[0]) + \
                                              owner_share_amount
        assert calculated_owner_share_amount_after == owner_share_amount_after and INFO(
            "Contribution shares amount is correct")

    if token1 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1 + contrib_fee_sum
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2
    elif token2 == PRV_ID:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2 + contrib_fee_sum
    else:
        assert bal_tok1_be4_contrib == bal_tok1_aft_refund + api_contrib_tok1
        assert bal_tok2_be4_contrib == bal_tok2_aft_refund + api_contrib_tok2
