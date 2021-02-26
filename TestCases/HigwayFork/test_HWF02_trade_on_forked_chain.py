import copy
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import PRV_ID, coin, ChainConfig
from Helpers.Logging import INFO, STEP, INFO_HEADLINE, ERROR
from Helpers.TestHelper import l6
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX import calculate_trade_order, verify_sum_fee_prv_token, verify_contributor_reward_prv_token
from TestCases.HigwayFork import get_block_height, token_id_1, token_id_2, token_owner, \
    calculated_and_create_fork, verify_trading_prv_token

num_of_traders = 5
trade_amounts = [random.randrange(9900000, 10000000)] * num_of_traders
count_tx_success = [0] * num_of_traders
traders = ACCOUNTS[:num_of_traders]  # should run script with Account_Hang_1 to have enough shard
token_sell = token_id_1
token_buy = token_id_2
min_blocks_wait_fork = 6  # Chain will be forked after at least {num_of_block_wait} blocks
time_send_tx = 3  # create & send transaction before and after {time_send_tx} blocks


def setup_module():
    STEP(0.1, 'Setup contribution pool-pair')
    pde = SUT().get_latest_pde_state_info()
    if not pde.is_trading_pair_v2_is_possible(token_id_1, token_id_2):
        pytest.skip(f'pair {l6(token_id_1)}-{l6(token_id_2)} not ready to trade')


def setup_function():
    top = max(trade_amounts)
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(2), traders)
    token_owner.top_him_up_token_to_amount_if(token_id_1, 10 * top, 20 * top, traders)
    token_owner.top_him_up_token_to_amount_if(token_id_2, 10 * top, 20 * top, traders)


@pytest.mark.parametrize('cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch', [
    (0, 2, None, None, True),
    (0, 2, None, None, False),
    (255, 2, None, None, True),
    (255, 2, None, None, False),
    (1, 2, 255, 2, True),
    (1, 2, 255, 2, False),
    (1, 2, 0, 2, True),
    (1, 2, 0, 2, False),
])
def test_trade_on_forked_chain(cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch):
    pde_state_b4 = SUT().get_latest_pde_state_info()
    rate_toks_prv_before = pde_state_b4.get_rate_between_token(token_sell, PRV_ID)
    rate_prv_tokb_before = pde_state_b4.get_rate_between_token(PRV_ID, token_buy)

    STEP(0, "Checking balance")
    balance_tok_sell_before = []
    balance_prv_sell_before = []
    balance_tok_buy_before = []
    balance_tok_sell_after = []
    balance_prv_sell_after = []
    balance_tok_buy_after = []
    private_key_alias = []
    trading_fees = [random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    random.randrange(190000, 200000),
                    ]

    threads_buy = []
    threads_sell = []
    threads_prv_sell = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, num_of_traders):
            trader = traders[i]
            future_buy = executor.submit(trader.get_token_balance, token_buy)
            future_sell = executor.submit(trader.get_token_balance, token_sell)
            future_prv_sell = executor.submit(trader.get_prv_balance)
            threads_buy.append(future_buy)
            threads_sell.append(future_sell)
            threads_prv_sell.append(future_prv_sell)

    for i in range(0, num_of_traders):
        amount = trade_amounts[i]
        bal_tok_sell = threads_sell[i].result()
        if bal_tok_sell <= amount:
            pytest.skip(
                f"This {l6(traders[i].private_key)} token {l6(token_sell)} bal: {bal_tok_sell} <= {amount},"
                f"NOT ENOUGH FOR TEST")
        balance_tok_sell_before.append(bal_tok_sell)
        balance_prv_sell_before.append(threads_prv_sell[i].result())
        balance_tok_buy_before.append(threads_buy[i].result())
        private_key_alias.append(l6(traders[i].private_key))

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell before trade      : {str(balance_tok_sell_before)}")
    INFO(f"{l6(token_buy)} balance token buy before trade         : {str(balance_tok_buy_before)}")
    INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Before Trade : {str(rate_toks_prv_before)}")
    INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Before Trade : {str(rate_prv_tokb_before)}")

    STEP(1, f'Create fork on chain_id {cID1} & chain_id {cID2}')
    with ThreadPoolExecutor() as executor:
        if cID1 is not None:
            thread = executor.submit(calculated_and_create_fork, cID1, at_transfer_next_epoch=at_transfer_next_epoch,
                                     min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch1)
        if cID2 is not None:
            executor.submit(calculated_and_create_fork, cID2, at_transfer_next_epoch=at_transfer_next_epoch,
                            min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch2)
    height_b4, block_fork_list, real_blocks_wait = thread.result()

    WAIT((real_blocks_wait - time_send_tx) * ChainConfig.BLOCK_TIME)

    STEP(2, f"Trade {l6(token_sell)}")
    list_threads = []
    height_current = copy.deepcopy(height_b4)
    thread_pool_view = []
    round_height = {}
    for height in range(height_current, block_fork_list[-1] + time_send_tx + 20):
        round_height[height] = 0
    while height_current < block_fork_list[-1] + time_send_tx + 5:
        threads = []
        with ThreadPoolExecutor() as executor:
            thread_height = executor.submit(get_block_height, cID1)
            for cID in [cID1, cID2]:
                if cID == 255:
                    REQ_HANDLER = SUT.beacons.get_node()
                    thread_view_detail = executor.submit(REQ_HANDLER.get_all_view_detail, -1)
                    thread_pool_view.append(thread_view_detail)
                elif cID is not None:
                    REQ_HANDLER = SUT.shards[cID].get_node()
                    thread_view_detail = executor.submit(REQ_HANDLER.get_all_view_detail, cID)
                    thread_pool_view.append(thread_view_detail)
            for i in range(0, num_of_traders):
                trader = traders[i]
                future = executor.submit(trader.pde_trade_v2, token_sell, trade_amounts[i], token_buy, trading_fees[i])
                threads.append(future)
        list_threads.append(threads)
        height_current = thread_height.result()
        INFO(f'Block_height: {height_current}')
        round_height[height_current] += 1
        assert round_height[height_current] <= num_of_branch1 * 2 + 2, ERROR(f'Chain is stopped at {height_current}')
        if height_current in block_fork_list:
            WAIT(40)
        else:
            WAIT(ChainConfig.BLOCK_TIME * 2)

    STEP(3, 'Wait for Tx to be confirmed and balance to update')
    WAIT(15 * ChainConfig.BLOCK_TIME)  # wait 10 blocks to balance update
    INFO('Get all view detail')
    for thread in thread_pool_view:
        result = thread.result()
        INFO(result.num_of_hash_follow_height())
    threads_buy = []
    threads_sell = []
    threads_sell_prv = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, num_of_traders):
            trader = traders[i]
            future_buy = executor.submit(trader.get_token_balance, token_buy)
            future_sell = executor.submit(trader.get_token_balance, token_sell)
            future_sell_prv = executor.submit(trader.get_prv_balance)
            threads_buy.append(future_buy)
            threads_sell.append(future_sell)
            threads_sell_prv.append(future_sell_prv)

    for i in range(0, num_of_traders):
        balance_tok_sell_after.append(threads_sell[i].result())
        balance_prv_sell_after.append(threads_sell_prv[i].result())
        balance_tok_buy_after.append(threads_buy[i].result())

    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell after trade       : {balance_tok_sell_after}")
    INFO(f"{l6(token_buy)}  balance token buy after trade        : {balance_tok_buy_after}")

    STEP(4, "Double check the algorithm ")
    trade_order = calculate_trade_order(trading_fees, trade_amounts)
    sum_estimate_amount_received_list = [0] * num_of_traders
    sum_estimate_amount_sold_after_list = [0] * num_of_traders
    sum_trading_fee_list = [0] * num_of_traders
    tx_fee_list = [0] * num_of_traders
    calculated_rate_toks_prv = copy.deepcopy(rate_toks_prv_before)
    calculated_rate_prv_tokb = copy.deepcopy(rate_prv_tokb_before)
    for threads in list_threads:
        real_trade_amounts = copy.deepcopy(trade_amounts)
        real_trading_fees = copy.deepcopy(trading_fees)
        for i in range(0, len(threads)):
            result = threads[i].result()
            if result.get_error_msg() is None:
                INFO(f'Get transaction tx_id = {result.get_tx_id()}')
                tx_detail = result.get_transaction_by_hash()
                if not tx_detail.is_none():
                    height = tx_detail.get_block_height()
                    shard = tx_detail.get_shard_id()
                    INFO(f'Shard {shard}-height {height}')
                    if height:
                        tx_fee = tx_detail.get_fee()
                        tx_fee_list[i] += tx_fee
                        count_tx_success[i] += 1
                    else:
                        real_trade_amounts[i] = 0
                        real_trading_fees[i] = 0
                else:
                    msg_error = SUT().transaction().get_tx_by_hash(result.get_tx_id()).get_error_msg()
                    ERROR(msg_error)
                    real_trade_amounts[i] = 0
                    real_trading_fees[i] = 0
            else:
                ERROR(result.get_error_msg())
                real_trade_amounts[i] = 0
                real_trading_fees[i] = 0
        INFO(f" -- sell: {l6(token_sell)} - buy: {l6(PRV_ID)} -- ")
        calculated_rate_toks_prv, estimate_amount_prv_received_list = \
            verify_trading_prv_token(real_trade_amounts, trade_order, calculated_rate_toks_prv)

        INFO(f" -- sell: {l6(PRV_ID)} - buy: {l6(token_buy)} -- ")
        calculated_rate_prv_tokb, estimate_amount_received_list = \
            verify_trading_prv_token(estimate_amount_prv_received_list, trade_order, calculated_rate_prv_tokb)
        for i in range(0, num_of_traders):
            sum_estimate_amount_received_list[i] += estimate_amount_received_list[i]
            sum_estimate_amount_sold_after_list[i] += real_trade_amounts[i]
            sum_trading_fee_list[i] += real_trading_fees[i]

    estimate_bal_buy_after_list = [bal + receive for (bal, receive) in
                                   zip(balance_tok_buy_before, sum_estimate_amount_received_list)]
    estimate_bal_sell_after_list = [bal - sell for (bal, sell) in
                                    zip(balance_tok_sell_before, sum_estimate_amount_sold_after_list)]
    estimate_bal_prv_sell_after_list = [bal - fee - trading_fee for (bal, fee, trading_fee) in
                                        zip(balance_prv_sell_before, tx_fee_list, sum_trading_fee_list)]

    pde_state_af = SUT().get_latest_pde_state_info()
    rate_toks_prv_after = pde_state_af.get_rate_between_token(token_sell, PRV_ID)
    rate_prv_tokb_after = pde_state_af.get_rate_between_token(PRV_ID, token_buy)

    INFO("---")
    INFO(f'Count tx success: {count_tx_success}')
    INFO(f"tx fee list   : {str(tx_fee_list)}")
    INFO(f"trading fee list   : {str(sum_trading_fee_list)}")
    INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Before Trade : {str(rate_prv_tokb_before)}")
    INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - After Trade : {str(rate_prv_tokb_after)}")
    INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Calculated Trade : {str(calculated_rate_prv_tokb)}")
    INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Before Trade : {str(rate_toks_prv_before)}")
    INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - After Trade : {str(rate_toks_prv_after)}")
    INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Calculated Trade : {str(calculated_rate_toks_prv)}")
    INFO(f"""::: estimated after vs real after of token buy
            {estimate_bal_buy_after_list}
            {balance_tok_buy_after}""")
    INFO(f"""::: estimated after vs real after of token sell
                {estimate_bal_sell_after_list}
                {balance_tok_sell_after}""")
    INFO(f"""::: estimated after vs real after of PRV
                {estimate_bal_prv_sell_after_list}
                {balance_prv_sell_after}""")

    STEP(5, 'Verify sum fee')
    sum_trading_fee = sum(sum_trading_fee_list)
    first_half_reward = int(sum_trading_fee / 2)
    sum_fee_pool_b4 = pde_state_b4.sum_contributor_reward_of_pair(None, token_sell, PRV_ID)
    sum_fee_pool_af = pde_state_af.sum_contributor_reward_of_pair(None, token_sell, PRV_ID)
    INFO(f'Verify contributor reward of {l6(token_sell)}-{l6(PRV_ID)}, '
         f'Expected sum reward = {first_half_reward}, actual sum reward = {sum_fee_pool_af - sum_fee_pool_b4}')
    different_trading_fee = abs(first_half_reward - (sum_fee_pool_af - sum_fee_pool_b4))
    second_half_reward = sum_trading_fee - first_half_reward
    sum_fee_pool_b4 = pde_state_b4.sum_contributor_reward_of_pair(None, token_buy, PRV_ID)
    sum_fee_pool_af = pde_state_af.sum_contributor_reward_of_pair(None, token_buy, PRV_ID)
    INFO(f'Verify contributor reward of {l6(token_buy)}-{l6(PRV_ID)}, '
         f'Expected sum reward = {second_half_reward}, actual sum reward = {sum_fee_pool_af - sum_fee_pool_b4}')
    different_trading_fee += abs(second_half_reward - (sum_fee_pool_af - sum_fee_pool_b4))

    STEP(6, 'Verify each contributor reward ')
    reward_result_1, SUMMARY1 = verify_contributor_reward_prv_token((sum_fee_pool_af - sum_fee_pool_b4), token_sell,
                                                                    PRV_ID, pde_state_b4, pde_state_af)
    reward_result_2, SUMMARY2 = verify_contributor_reward_prv_token((sum_fee_pool_af - sum_fee_pool_b4), PRV_ID,
                                                                    token_buy, pde_state_b4, pde_state_af)
    SUMMARY = SUMMARY1 + '\n' + SUMMARY2
    final_reward_result = reward_result_1 and reward_result_2

    INFO_HEADLINE('Test summary')
    INFO(SUMMARY)

    assert final_reward_result, 'Wrong reward amount for contributors'

    STEP(7, f"Verify rate {l6(token_sell)} vs {l6(token_buy)}")
    for i in range(len(calculated_rate_toks_prv)):
        assert abs(calculated_rate_toks_prv[i] - rate_toks_prv_after[i]) <= sum(count_tx_success * 2), ERROR(
            'WRONG: rate token sell vs prv')
        assert abs(calculated_rate_prv_tokb[i] - rate_prv_tokb_after[i]) <= sum(count_tx_success * 2), ERROR(
            'WRONG: rate prv vs token buy')

    STEP(8, 'Verify balance')
    sum(abs(estimate_bal_sell_after_list[i] - balance_tok_sell_after[i]) for i in range(num_of_traders))
    different_PRV = sum(
        abs(estimate_bal_prv_sell_after_list[i] - balance_prv_sell_after[i]) for i in range(num_of_traders))
    sum(abs(estimate_bal_buy_after_list[i] - balance_tok_buy_after[i]) for i in range(num_of_traders))

    assert abs(different_trading_fee - different_PRV) <= sum(count_tx_success)
