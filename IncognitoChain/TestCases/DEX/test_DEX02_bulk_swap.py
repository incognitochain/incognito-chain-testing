import concurrent
import copy
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import PRV_ID, coin
from IncognitoChain.Helpers.Logging import STEP, INFO, DEBUG, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import calculate_actual_trade_received, l6
from IncognitoChain.Helpers.Time import WAIT, get_current_date_time
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.DEX import token_id_1, acc_list_1_shard, acc_list_n_shard, token_owner, token_id_2

trade_amount = random.randrange(9900000, 10000000)


def setup_function():
    INFO_HEADLINE("SETUP TEST DEX 02")
    COIN_MASTER.top_him_up_prv_to_amount_if(trade_amount, 2 * trade_amount, acc_list_1_shard + acc_list_n_shard)
    token_owner.top_him_up_token_to_amount_if(token_id_1, trade_amount, 2 * trade_amount,
                                              acc_list_1_shard + acc_list_n_shard)
    INFO_HEADLINE("DONE SETUP DEX 02")


@pytest.mark.parametrize('test_mode,token_sell,token_buy', (
        ["1 shard", token_id_1, PRV_ID],
        ["n shard", token_id_1, PRV_ID],
        ["1 shard", token_id_1, token_id_2],
        ["n shard", token_id_1, token_id_2]
))
def test_bulk_swap(test_mode, token_sell, token_buy):
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
    STEP(0, 'Contribute if pair is not yet existed')
    pde_state_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()

    if not pde_state_b4.is_pair_existed(token_buy, token_sell):
        pair_id = f'pde_{l6(token_sell)}_{l6(token_buy)}_{get_current_date_time()}'
        token_owner.pde_contribute(token_sell, coin(15000), pair_id).expect_no_error().subscribe_transaction()
        token_owner.pde_contribute(token_buy, coin(21000), pair_id).expect_no_error().subscribe_transaction()
        WAIT(40)
    else:
        INFO('Pair is already existed')

    STEP(1, "Checking balance")
    balance_tok1_before = []
    balance_tok2_before = []
    balance_tok1_after = []
    balance_tok2_after = []
    private_key_alias = []
    trading_fee = [77, 22, 11, 66, 99, 2, 33, 55, 88, 44]

    trade_amount_token1 = trade_amount

    for trader in traders:
        bal_tok_1 = trader.get_token_balance(token_sell)
        bal_tok_2 = trader.get_token_balance(token_buy)

        if bal_tok_1 <= trade_amount_token1:
            pytest.skip(
                f"This {l6(trader.private_key)} token {l6(token_sell)} bal: {bal_tok_1} <= {trade_amount_token1},"
                f"NOT ENOUGH FOR TEST")

        balance_tok1_before.append(bal_tok_1)
        balance_tok2_before.append(bal_tok_2)
        private_key_alias.append(l6(trader.private_key))

    rate_before = pde_state_b4.get_rate_between_token(token_sell, token_buy)

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{token_sell[-6:]} balance before trade      : {str(balance_tok1_before)}")
    INFO(f"{token_buy[-6:]} balance before trade         : {str(balance_tok2_before)}")
    INFO(f"Rate {token_sell[-6:]} vs {token_buy[-6:]} - Before Trade : {str(rate_before)}")

    STEP(2, f"trade {token_sell[-6:]} at the same time")
    tx_list = []
    threads = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future = executor.submit(trader.pde_trade, token_sell, trade_amount, token_buy, 1, trading_fee[i])
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
    for i in range(0, len(traders)):
        trader = traders[i]
        balance_tok_2 = trader.wait_for_balance_change(token_buy, balance_tok2_before[i], 100)
        if balance_tok_2 is not False:
            balance_tok2_after.append(balance_tok_2)
            balance_tok1 = trader.wait_for_balance_change(token_sell, balance_tok1_before[i], -100)
            balance_tok1_after.append(balance_tok1)
        else:
            assert False, "Wait time expired, {token2[-6:]} did NOT increase"
    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{token_sell[-6:]} balance after trade        : {balance_tok1_after}")
    INFO(f"{token_buy[-6:]}    balance after trade        : {balance_tok2_after}")

    STEP(5, f"Check rate {token_sell[-6:]}  vs {token_buy[-6:]}")
    pde_state_af = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_after = pde_state_af.get_rate_between_token(token_sell, token_buy)
    INFO(f"rate {token_sell[-6:]} vs {token_buy[-6:]} - After Trade  : {rate_after}")

    STEP(6, "Double check the algorithm ")
    result_token = []
    result_prv = []
    calculated_rate = copy.deepcopy(rate_before)
    trade_priority = []

    for i in range(0, len(trading_fee)):
        trade_priority.append(trade_amount_token1 / trading_fee[i])
    print("Trade Priority: " + str(trade_priority))

    sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k])
    print("Sort order: " + str(sort_order))

    for order in sort_order:
        print(str(order) + "--")
        received_amount_prv = calculate_actual_trade_received(trade_amount_token1, calculated_rate[0],
                                                              calculated_rate[1])
        if received_amount_prv == balance_tok2_after[order] - balance_tok2_before[order] - tx_fee_list[order]:
            result_prv.append(str(order) + "Received_True")
        else:
            result_prv.append(str(order) + "Received_False")
        print("  Actual received: %d" % (balance_tok2_after[order] - balance_tok2_before[order] - tx_fee_list[order]))

        if trade_amount_token1 == balance_tok1_before[order] - balance_tok1_after[order] - trading_fee[order]:
            result_token.append(str(order) + "Trade_True")
        else:
            result_token.append(str(order) + "Trade_False")
        print("  Actual Trade amount: %d " % (
                balance_tok1_before[order] - balance_tok1_after[order] - trading_fee[order]))

        calculated_rate[1] = calculated_rate[1] - received_amount_prv
        calculated_rate[0] = calculated_rate[0] + trade_amount_token1 + trading_fee[order]

    # sort result before print
    result_token.sort()
    result_prv.sort()
    INFO("--")
    INFO(f"tx fee list   : {str(tx_fee_list)}")
    INFO(f"result {l6(token_sell)} : {str(result_token)}")
    INFO(f"result {token_buy[-6:]} : {str(result_prv)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - Before Trade    : {str(rate_before)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - After Trade     : {str(rate_after)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - Calculated Trade: {str(calculated_rate)}")
    assert calculated_rate == rate_after and INFO("Pair Rate is correct"), "Pair Rate is WRONG after Trade"
