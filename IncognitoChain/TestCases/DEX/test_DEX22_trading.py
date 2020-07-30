import concurrent
import copy
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO, DEBUG, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import calculate_actual_trade_received, l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.DEX import token_id_1, acc_list_1_shard, acc_list_n_shard, token_owner, token_id_2

trade_amount = random.randrange(9900000, 10000000)


def setup_function():
    INFO_HEADLINE("SETUP TEST DEX TRADING")
    COIN_MASTER.top_him_up_prv_to_amount_if(trade_amount, 2 * trade_amount, acc_list_1_shard + acc_list_n_shard)
    token_owner.top_him_up_token_to_amount_if(token_id_1, trade_amount, 2 * trade_amount,
                                              acc_list_1_shard + acc_list_n_shard)
    INFO_HEADLINE("DONE SETUP DEX TRADING")


@pytest.mark.parametrize('test_mode,token_sell,token_buy', (
    ["1 shard", token_id_1, PRV_ID],
    ["1 shard", PRV_ID, token_id_1],
    ["n shard", token_id_1, PRV_ID],
    ["n shard", PRV_ID, token_id_1],
))
def test_bulk_swap_with_prv(test_mode, token_sell, token_buy):
    if test_mode == '1 shard':
        traders = acc_list_1_shard
    else:
        traders = acc_list_n_shard
    print(f"""
       Test bulk swap {test_mode}:
        - token {l6(token_sell)} vd {l6(token_buy)}
        - 10 address make trading at same time
        - difference trading fee
        - highest trading fee get better price
       """)

    STEP(0, "Checking balance")
    balance_tok_sell_before = []
    balance_tok_buy_before = []
    balance_tok_sell_after = []
    balance_tok_buy_after = []
    private_key_alias = []
    # trading_fees = [7700000, 2200000, 1100000, 6600000, 9900000, 200000, 3300000, 5500000, 8800000, 4400000]
    trading_fees = [random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    random.randrange(1000000, 2000000),
                    0]
    pde_state_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()

    for trader in traders:
        bal_tok_sell = trader.get_token_balance(token_sell)
        bal_tok_buy = trader.get_token_balance(token_buy)

        if bal_tok_sell <= trade_amount:
            pytest.skip(
                f"This {l6(trader.private_key)} token {l6(token_sell)} bal: {bal_tok_sell} <= {trade_amount},"
                f"NOT ENOUGH FOR TEST")

        balance_tok_sell_before.append(bal_tok_sell)
        balance_tok_buy_before.append(bal_tok_buy)
        private_key_alias.append(l6(trader.private_key))

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance before trade      : {str(balance_tok_sell_before)}")
    INFO(f"{l6(token_buy)} balance before trade         : {str(balance_tok_buy_before)}")
    rate_before = pde_state_b4.get_rate_between_token(token_sell, token_buy)
    INFO(f"Rate {l6(token_sell)} vs {l6(token_buy)} - Before Trade : {str(rate_before)}")

    STEP(1, "Checking pool")
    STEP(2, f"trade {l6(token_sell)} at the same time")
    tx_list = []
    threads = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future = executor.submit(trader.pde_trade_v2, token_sell, trade_amount, token_buy, trading_fees[i])
            threads.append(future)
    concurrent.futures.wait(threads)
    INFO(f"Transaction id list")
    for thread in threads:
        tx = thread.result()
        tx_list.append(tx)
        INFO(f'    {tx.get_tx_id()}')

    STEP(3, "Wait for Tx to be confirmed")
    tx_fee_list = []
    for tx in tx_list:
        tx_is_confirmed = False
        print(f'          checking tx id: {l6(tx.get_tx_id())}')
        for i in range(0, 10):  # check 10 times each Tx
            tx_confirm = tx.get_transaction_by_hash()
            if tx_confirm.get_block_hash() != "":
                tx_is_confirmed = True
                tx_fee_list.append(tx_confirm.get_fee())
                DEBUG("the " + tx.get_tx_id() + " is confirmed")
                break
            else:
                print(f"shard id: {tx_confirm.get_shard_id()}")
                WAIT(10)
        assert tx_is_confirmed, f"The {tx.get_tx_id()} is NOT yet confirmed"

    STEP(4, "CHECK BALANCE AFTER")
    threads_buy = {}
    threads_sell = {}
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future_buy = executor.submit(trader.wait_for_balance_change, token_buy, balance_tok_buy_before[i], 100)
            future_sell = executor.submit(trader.wait_for_balance_change, token_sell, balance_tok_buy_before[i], 100)
            threads_buy[trader] = future_buy
            threads_sell[trader] = future_sell
    concurrent.futures.wait(threads_buy.values())
    concurrent.futures.wait(threads_sell.values())

    for i in range(0, len(traders)):
        trader = traders[i]
        balance_tok_sell_after.append(threads_sell[trader].result())
        balance_tok_buy_after.append(threads_buy[trader].result())

    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance after trade        : {balance_tok_sell_after}")
    INFO(f"{l6(token_buy)}  balance after trade        : {balance_tok_buy_after}")

    STEP(5, f"Check rate {l6(token_sell)}  vs {l6(token_buy)}")
    pde_state_af = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_after = pde_state_af.get_rate_between_token(token_sell, token_buy)
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - After Trade  : {rate_after}")

    STEP(6, "Double check the algorithm ")
    SUMMARY = '\n'

    result_token = []
    result_prv = []
    calculated_rate = copy.deepcopy(rate_before)
    trade_priority = []

    for i in range(0, len(trading_fees)):
        trade_priority.append(trade_amount / trading_fees[i])
    print("Trade Priority: " + str(trade_priority))

    sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k])
    print("Sort order: " + str(sort_order))

    for order in sort_order:
        trader = traders[order]
        tx_fee = tx_fee_list[order]
        trading_fee = trading_fees[order]
        bal_tok_buy_b4 = balance_tok_buy_before[order]
        bal_tok_sell_b4 = balance_tok_sell_before[order]

        bal_tok_buy_after = balance_tok_buy_after[order]
        bal_tok_sell_after = balance_tok_sell_after[order]

        print(str(order) + "--")
        received_amount_token_buy = calculate_actual_trade_received(trade_amount, calculated_rate[0],
                                                                    calculated_rate[1])
        calculated_rate[0] += trade_amount
        calculated_rate[1] -= received_amount_token_buy

        # check balance
        estimate_bal_sell_after = bal_tok_sell_b4 - trade_amount
        estimate_bal_buy_after = bal_tok_buy_b4 + received_amount_token_buy
        if token_sell == PRV_ID:
            estimate_bal_sell_after -= (trading_fee + tx_fee)
        if token_buy == PRV_ID:
            estimate_bal_buy_after -= (trading_fee + tx_fee)

        assert estimate_bal_buy_after == bal_tok_buy_after and INFO(f'{l6(trader.payment_key)} '
                                                                    f'balance {l6(token_buy)} is correct')
        assert estimate_bal_sell_after == bal_tok_sell_after and INFO(f'{l6(trader.payment_key)} '
                                                                      f'balance {l6(token_sell)} is correct')

    STEP(7, 'Verify sum fee')
    sum_trading_fee = sum(trading_fees)
    sum_fee_pool_b4 = pde_state_b4.sum_contributor_reward_of_pair(None, token_sell, token_buy)
    sum_fee_pool_af = pde_state_af.sum_contributor_reward_of_pair(None, token_sell, token_buy)
    assert sum_fee_pool_af - sum_fee_pool_b4 == sum_trading_fee and INFO('Sum fee is correct')

    STEP(8, 'Verify each contributor reward ')
    contributors_of_pair = pde_state_b4.get_contributor_of_pair(token_sell, token_buy)
    sum_share_of_pair = pde_state_b4.sum_share_pool_of_pair(None, token_sell, token_buy)
    sum_split_reward = 0
    final_fee_result = True
    for contributor in contributors_of_pair:
        share_of_contributor = pde_state_b4.get_pde_shares_amount(contributor, token_sell, token_buy)
        pde_reward_b4 = pde_state_b4.get_contributor_reward(contributor, token_sell, token_buy)
        pde_reward_af = pde_state_af.get_contributor_reward(contributor, token_sell, token_buy)
        calculated_reward = int(sum_trading_fee * share_of_contributor / sum_share_of_pair)
        sum_split_reward += calculated_reward
        if contributor == contributors_of_pair[-1]:  # last contributor get all remaining fee as reward
            calculated_reward = sum_trading_fee - sum_split_reward
        INFO(f'''Verify PDE reward for contributor {l6(contributor)} with: 
                    reward before               : {pde_reward_b4}
                    reward after                : {pde_reward_af}
                    estimated additional reward : {calculated_reward}
                    share amount                : {share_of_contributor}
                    sum share of pair           : {sum_share_of_pair}
                    sum trading fee             : {sum_trading_fee}''')
        if pde_reward_b4 + calculated_reward == pde_reward_af:
            SUMMARY += f'\tPde reward of {l6(contributor)} is correct: ' \
                       f'estimated/actual received {calculated_reward}/{pde_reward_af - pde_reward_b4}\n'
            final_fee_result = final_fee_result and True
        else:
            SUMMARY += (f'\tPde reward of {l6(contributor)} not correct: '
                        f'estimated/actual received {calculated_reward}/{pde_reward_af - pde_reward_b4} \n')
            final_fee_result = final_fee_result and False

    INFO_HEADLINE('Test summary')
    INFO(SUMMARY)
    # sort result before print
    result_token.sort()
    result_prv.sort()
    INFO("--")
    INFO(f"tx fee list   : {str(tx_fee_list)}")
    INFO(f"trading fee list   : {str(trading_fees)}")
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - Before Trade    : {str(rate_before)}")
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - After Trade     : {str(rate_after)}")
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - Calculated Trade: {str(calculated_rate)}")
    assert calculated_rate == rate_after and INFO("Pair Rate is correct"), "Pair Rate is WRONG after Trade"
    assert final_fee_result, 'Wrong reward amount for contributors'


@pytest.mark.parametrize('token_sell, token_buy', [
    (token_id_1, token_id_2),

])
def test_trading_tokens(token_sell, token_buy):
    # todo
    pytest.skip('Not yet implement')
