import pytest

from Configs.Constants import coin, PRV_ID
from Helpers.Logging import INFO, STEP, INFO_HEADLINE
from Helpers.TestHelper import l6
from Helpers.Time import get_current_date_time, WAIT
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX import token_owner, token_id_1, token_id_2


def setup_function():
    token_owner.top_up_if_lower_than(ACCOUNTS, coin(500), coin(1000), token_id_1)
    token_owner.top_up_if_lower_than(ACCOUNTS, coin(500), coin(1000), token_id_2)
    token_owner.top_up_if_lower_than(ACCOUNTS, coin(500), coin(1000), )


@pytest.mark.parametrize('contributors, contribute_percent_of_bal_tok2, token1, token2', [
    (ACCOUNTS, 0.01, PRV_ID, token_id_1),
    (ACCOUNTS, 0.1, token_id_1, token_id_2),
])
def test_add_liquidity(contributors, contribute_percent_of_bal_tok2, token1, token2):
    pde_state_b4_test = SUT().get_latest_pde_state_info()
    if pde_state_b4_test.get_rate_between_token(token1, token2) == [0, 0]:
        pytest.skip(' Token pair is not yet existed in pool, cannot add liquidity')
    rate_b4_test = pde_state_b4_test.get_rate_between_token(token1, token2)
    INFO_HEADLINE(f'Test tokens: {l6(token1)}:{l6(token2)}. Rate {rate_b4_test}')
    contributor_balance_b4 = {token1: {}, token2: {}}
    contributor_balance_af = {token1: {}, token2: {}}
    pair_ids = {}
    commit_amount = {token1: {}, token2: {}}

    for account in contributors + [token_owner]:
        contributor_balance_b4[token1][account] = account.get_token_balance(token1)
        contributor_balance_b4[token2][account] = account.get_token_balance(token2)

    INFO(f'Private key | To commit {l6(token1)}/{l6(token2)} | balance {l6(token1)}/{l6(token2)} | '
         f'share amount {l6(token2)}')
    for account in contributors:
        pair_id = f'{l6(account.private_key)}_{l6(token1)}_{l6(token2)}_{get_current_date_time()}'
        pair_ids[account] = pair_id
        bal_tok1 = contributor_balance_b4[token1][account]
        bal_tok2 = contributor_balance_b4[token2][account]
        amount2 = int(bal_tok2 * contribute_percent_of_bal_tok2)
        amount1 = int(amount2 * rate_b4_test[0] / rate_b4_test[1])
        commit_amount[token1][account] = amount1
        commit_amount[token2][account] = amount2
        assert amount1 != 0, f'Calculated commit amount for {l6(token1)} is 0'
        assert amount2 != 0, f'Calculated commit amount for {l6(token2)} is 0'
        pde_share = pde_state_b4_test.get_pde_shares_amount(account, token1, token2)
        INFO("%8s %11s/%s %9s/%s %13s" % (l6(account.private_key), amount1, amount2, bal_tok1, bal_tok2, pde_share))

    STEP(1, f'Contribute {l6(token1)}')
    d_contribute_fee = {}
    d_contribute_tx = {}
    for acc in contributors:
        pair_id = pair_ids[acc]
        contribute_tx = acc.pde_contribute(token1, commit_amount[token1][acc], pair_id)
        contribute_tx.expect_no_error()
        INFO(f"Contribute {l6(token1)} tx_id: {contribute_tx.get_tx_id()} ")
        d_contribute_tx[acc] = contribute_tx

    STEP(2, f'Wait 40s then verify contribution {l6(token1)} is in waiting list')
    WAIT(40)
    pde_state_after_contribute = SUT().get_latest_pde_state_info()
    for acc in contributors:
        pair_id = pair_ids[acc]
        assert pde_state_after_contribute.find_waiting_contribution_of_user(acc, pair_id, token1), \
            f"Expect pair {pair_id} to be in waiting list, but it is not"
        d_contribute_fee[acc] = d_contribute_tx[acc].get_transaction_by_hash().get_fee()

    STEP(3, f'Contribute {l6(token2)}')
    for acc in contributors:
        pair_id = pair_ids[acc]
        if token2 is PRV_ID:
            contribute_tx = acc.pde_contribute_prv(commit_amount[token2][acc], pair_id)
        else:
            contribute_tx = acc.pde_contribute_token(token2, commit_amount[token2][acc], pair_id)

        contribute_tx.expect_no_error()
        d_contribute_tx[acc] = contribute_tx
        INFO(f"Contribute {l6(token1)}, tx_id: {contribute_tx.get_tx_id()}")

    STEP(4, f'Wait 40s then verify {l6(token1)} is no longer in waiting list')
    WAIT(40)
    pde_state_after_test = SUT().get_latest_pde_state_info()
    for acc in contributors:
        pair_id = pair_ids[acc]
        waiting_contribution = pde_state_after_test.find_waiting_contribution_of_user(acc, pair_id, token1)
        assert not waiting_contribution, \
            f'''not expect to found waiting contribution but found anyway
            user {acc.private_key}, 
            pair {pair_id}, token {token1}
            {waiting_contribution[0]}
            '''
        d_contribute_fee[acc] += d_contribute_tx[acc].get_transaction_by_hash().get_fee()

    STEP(5, 'Wait 30s then check balance after contribution')
    WAIT(30)
    for account in contributors + [token_owner]:
        contributor_balance_af[token1][account] = account.get_token_balance(token1)
        contributor_balance_af[token2][account] = account.get_token_balance(token2)

    summary_msg = f'\nUser   | bal {l6(token1)} before/after    | {l6(token1)} commit amount | ' \
                  f'bal {l6(token2)} before/after  | {l6(token2)} commit amount | share amount before/after'
    for account in contributors:
        pde_share_b4 = pde_state_b4_test.get_pde_shares_amount(account, token1, token2)
        pde_share_after = pde_state_after_test.get_pde_shares_amount(account, token1, token2)
        bal_tok1_b4 = contributor_balance_b4[token1][account]
        bal_tok2_b4 = contributor_balance_b4[token2][account]
        bal_tok1_af = contributor_balance_af[token1][account]
        bal_tok2_af = contributor_balance_af[token2][account]
        summary_msg += '\n%s | %13s/%13s | %21s | %13s/%13s | %21s | %13s/%13s' % (
            l6(account.payment_key), bal_tok1_b4, bal_tok1_af, commit_amount[token1][account],
            bal_tok2_b4, bal_tok2_af, commit_amount[token2][account], pde_share_b4, pde_share_after)

        for tok in [token1, token2]:
            tx_fee = d_contribute_fee[account] if tok == PRV_ID else 0
            assert abs(contributor_balance_b4[tok][account] - commit_amount[tok][account] - tx_fee -
                       contributor_balance_af[tok][account]) <= 2, \
                f"wrong balance {tok} after contribute of acc {account}"  # accept error margin =1
    INFO(summary_msg)

    STEP(6, f"Check rate {l6(token2)} vs {l6(token1)}")
    rate_before = pde_state_b4_test.get_rate_between_token(token1, token2)
    rate_after = pde_state_after_test.get_rate_between_token(token1, token2)

    sum_commit_token_1 = sum(commit_amount[token1].values())
    sum_commit_token_2 = sum(commit_amount[token2].values())

    INFO('Rate before test + sum contribute amount - rate after test')
    # each contributor's real vs estimate contribution can be off by 1 nano, so n contributors can be off at most n nano
    INFO(f'{rate_before[0]} + {sum_commit_token_1} - {rate_after[0]} '
         f'= {rate_before[0] + sum_commit_token_1 - rate_after[0]}')
    INFO(f'{rate_before[1]} + {sum_commit_token_2} - {rate_after[1]} '
         f'= {rate_before[1] + sum_commit_token_2 - rate_after[1]}')

    assert abs(rate_before[1] + sum_commit_token_2 - rate_after[1]) <= len(contributors)
    assert abs(rate_before[0] + sum_commit_token_1 - rate_after[0]) <= len(contributors)
