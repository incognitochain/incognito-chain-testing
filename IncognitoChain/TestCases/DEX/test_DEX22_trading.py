import concurrent
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO, DEBUG, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.DEX import token_id_1, acc_list_1_shard, acc_list_n_shard, token_owner, token_id_2, \
    calculate_trade_order, verify_trading_prv_token, verify_sum_fee_prv_token, verify_contributor_reward_prv_token

# trade_amount = random.randrange(9900000, 10000000)
trade_amounts = [123456] * 10
SUMMARY = '\n'


def setup_function():
    INFO_HEADLINE("SETUP TEST DEX TRADING")
    top = max(trade_amounts)
    COIN_MASTER.top_him_up_prv_to_amount_if(top, 2 * top, acc_list_1_shard + acc_list_n_shard)
    token_owner.top_him_up_token_to_amount_if(token_id_1, top, 2 * top,
                                              acc_list_1_shard + acc_list_n_shard)
    INFO_HEADLINE("DONE SETUP DEX TRADING")


@pytest.mark.parametrize('test_mode,token_sell,token_buy', (
    ["1 shard", token_id_1, PRV_ID],
    ["1 shard", PRV_ID, token_id_1],
    ["n shard", token_id_1, PRV_ID],
    ["n shard", PRV_ID, token_id_1],
    ["1 shard", token_id_2, token_id_1],
    ["n shard", token_id_2, token_id_1],
    ["1 shard", token_id_1, token_id_2],
    ["n shard", token_id_1, token_id_2],
))
def test_bulk_swap_with_prv(test_mode, token_sell, token_buy):
    if test_mode == '1 shard':
        traders = acc_list_1_shard
    else:
        traders = acc_list_n_shard

    global SUMMARY
    print(f"""
       Test bulk swap {test_mode}:
        - token {l6(token_sell)} vs {l6(token_buy)}
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
    trading_fees = [random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    0]
    pde_state_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()

    for i in range(0, len(traders)):
        trader = traders[i]
        amount = trade_amounts[i]
        bal_tok_sell = trader.get_token_balance(token_sell)
        bal_tok_buy = trader.get_token_balance(token_buy)

        if bal_tok_sell <= amount:
            pytest.skip(
                f"This {l6(trader.private_key)} token {l6(token_sell)} bal: {bal_tok_sell} <= {amount},"
                f"NOT ENOUGH FOR TEST")

        balance_tok_sell_before.append(bal_tok_sell)
        balance_tok_buy_before.append(bal_tok_buy)
        private_key_alias.append(l6(trader.private_key))

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell before trade      : {str(balance_tok_sell_before)}")
    INFO(f"{l6(token_buy)} balance token buy before trade         : {str(balance_tok_buy_before)}")
    rate_before = pde_state_b4.get_rate_between_token(token_sell, token_buy)
    INFO(f"Rate {l6(token_sell)} vs {l6(token_buy)} - Before Trade : {str(rate_before)}")

    if token_buy != PRV_ID and token_sell != PRV_ID:
        rate_before_token_buy = pde_state_b4.get_rate_between_token(PRV_ID, token_buy)
        rate_before_token_sell = pde_state_b4.get_rate_between_token(token_sell, PRV_ID)
        INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Before Trade : {str(rate_before_token_buy)}")
        INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Before Trade : {str(rate_before_token_sell)}")

    STEP(1, "Checking pool")
    STEP(2, f"trade {l6(token_sell)} at the same time")
    tx_list = []
    threads = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future = executor.submit(trader.pde_trade_v2, token_sell, trade_amounts[i], token_buy, trading_fees[i])
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

    STEP(4, "Wait for balance to update")
    threads_buy = {}
    threads_sell = {}
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future_buy = executor.submit(trader.wait_for_balance_change, token_buy, balance_tok_buy_before[i], 100)
            future_sell = executor.submit(trader.wait_for_balance_change, token_sell, balance_tok_sell_before[i], -100)
            threads_buy[trader] = future_buy
            threads_sell[trader] = future_sell
    concurrent.futures.wait(threads_buy.values())
    concurrent.futures.wait(threads_sell.values())

    for i in range(0, len(traders)):
        trader = traders[i]
        balance_tok_sell_after.append(threads_sell[trader].result())
        balance_tok_buy_after.append(threads_buy[trader].result())

    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell after trade        : {balance_tok_sell_after}")
    INFO(f"{l6(token_buy)}  balance token buy after trade        : {balance_tok_buy_after}")

    STEP(5, "Double check the algorithm ")
    trade_order = calculate_trade_order(trading_fees, trade_amounts)
    if token_buy == PRV_ID or token_sell == PRV_ID:
        print(f" -- sell: {l6(token_buy)} - buy: {l6(token_sell)} -- ")
        calculated_rate, estimate_bal_sell_after_list, estimate_amount_received_list = \
            verify_trading_prv_token(trade_amounts, trading_fees, trade_order, tx_fee_list, token_sell, token_buy,
                                     pde_state_b4, balance_tok_sell_before)
        estimate_bal_buy_after_list = [v1 + v2 for (v1, v2) in
                                       zip(estimate_amount_received_list, balance_tok_buy_before)]
    else:
        trading_fees_zero = tx_fee_list_zero = [0] * len(tx_fee_list)
        print(f" -- sell: {l6(token_sell)} - buy: {l6(PRV_ID)} -- ")
        calculated_rate1, estimate_bal_sell_after_list, estimate_amount_prv_received_list = \
            verify_trading_prv_token(trade_amounts, trading_fees_zero, trade_order, tx_fee_list_zero, token_sell,
                                     PRV_ID, pde_state_b4, balance_tok_sell_before)

        print(f" -- sell: {l6(PRV_ID)} - buy: {l6(token_buy)} -- ")
        calculated_rate2, estimate_bal_prv_after_list, estimate_amount_received_list = \
            verify_trading_prv_token(estimate_amount_prv_received_list, trading_fees_zero, trade_order,
                                     tx_fee_list_zero, PRV_ID, token_buy, pde_state_b4, balance_tok_sell_before)

        estimate_bal_buy_after_list = [bal + receive for (bal, receive) in
                                       zip(balance_tok_buy_before, estimate_amount_received_list)]

    assert estimate_bal_sell_after_list == balance_tok_sell_after
    assert estimate_bal_buy_after_list == balance_tok_buy_after

    STEP(6, f"Verify rate {l6(token_sell)} vs {l6(token_buy)}")
    pde_state_af = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_after = pde_state_af.get_rate_between_token(token_sell, token_buy)
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - After Trade  : {rate_after}")
    if token_buy == PRV_ID or token_sell == PRV_ID:
        assert calculated_rate == rate_after and INFO("Pair Rate is correct"), "Pair Rate is WRONG after Trade"
    else:
        assert rate_before == rate_after
        rate_prv_tok_sell_af = pde_state_af.get_rate_between_token(token_sell, PRV_ID)
        rate_prv_tok_buy_af = pde_state_af.get_rate_between_token(PRV_ID, token_buy)
        assert calculated_rate1 == rate_prv_tok_sell_af
        assert calculated_rate2 == rate_prv_tok_buy_af

    STEP(7, 'Verify sum fee')
    sum_trading_fee = sum(trading_fees)
    first_half_reward = int(sum_trading_fee / 2)
    second_half_reward = sum_trading_fee - first_half_reward
    if token_buy == PRV_ID or token_sell == PRV_ID:
        verify_sum_fee_prv_token(sum_trading_fee, token_sell, token_buy, pde_state_b4, pde_state_af)
    else:
        # breakpoint()
        verify_sum_fee_prv_token(first_half_reward, token_sell, PRV_ID, pde_state_b4, pde_state_af)
        verify_sum_fee_prv_token(second_half_reward, token_buy, PRV_ID, pde_state_b4, pde_state_af)

    STEP(8, 'Verify each contributor reward ')
    if token_buy == PRV_ID or token_sell == PRV_ID:
        final_reward_result = verify_contributor_reward_prv_token(sum_trading_fee, token_sell, token_buy, pde_state_b4,
                                                                  pde_state_af)
    else:
        reward_result_1 = verify_contributor_reward_prv_token(first_half_reward, token_sell, PRV_ID, pde_state_b4,
                                                              pde_state_af)
        reward_result_2 = verify_contributor_reward_prv_token(second_half_reward, PRV_ID, token_buy, pde_state_b4,
                                                              pde_state_af)
        final_reward_result = reward_result_1 and reward_result_2

    INFO_HEADLINE('Test summary')
    INFO(SUMMARY)

    INFO("--")
    INFO(f"tx fee list   : {str(tx_fee_list)}")
    INFO(f"trading fee list   : {str(trading_fees)}")
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - Before Trade    : {str(rate_before)}")
    INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - After Trade     : {str(rate_after)}")
    if token_buy != PRV_ID and token_sell != PRV_ID:
        INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Before Trade : {str(rate_before_token_buy)}")
        INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - After Trade : {str(calculated_rate2)}")
        INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Before Trade : {str(rate_before_token_sell)}")
        INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - After Trade : {str(calculated_rate1)}")
    else:
        INFO(f"rate {l6(token_sell)} vs {l6(token_buy)} - Calculated Trade: {str(calculated_rate)}")

    assert final_reward_result, 'Wrong reward amount for contributors'
