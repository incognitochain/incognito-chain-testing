import copy
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import PRV_ID, coin
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import STEP, INFO, INFO_HEADLINE
from Helpers.TestHelper import l6
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.DEX import token_id_1, acc_list_1_shard, acc_list_n_shard, token_owner, token_id_2

trade_amount = random.randrange(9900000, 10000000)


def setup_function():
    INFO_HEADLINE("SETUP TEST DEX 02")
    COIN_MASTER.top_up_if_lower_than(acc_list_1_shard + acc_list_n_shard, trade_amount, 2 * trade_amount)
    token_owner.top_up_if_lower_than(acc_list_1_shard + acc_list_n_shard, trade_amount, 2 * trade_amount, token_id_1)
    INFO_HEADLINE("DONE SETUP DEX 02")


@pytest.mark.parametrize('test_mode,token_sell,token_buy', (
        ["1 shard", token_id_1, PRV_ID],
        ["n shard", token_id_1, PRV_ID],
        ["1 shard", token_id_1, token_id_2],
        ["n shard", token_id_1, token_id_2],
        ["1 shard", PRV_ID, token_id_2],
        ["n shard", PRV_ID, token_id_2],
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
    pde_state_b4 = SUT().get_latest_pde_state_info()

    if not pde_state_b4.is_pair_existed(token_buy, token_sell):
        token_owner.pde_contribute_pair({token_sell: coin(15000), token_buy: coin(21000)})
        WAIT(40)  # wait for pde state to be updated
        pde_state_b4 = SUT().get_latest_pde_state_info()
    else:
        INFO('Pair is already existed')

    STEP(1, "Checking balance")
    bal_tok_sel_before = []
    bal_tok_buy_before = []
    bal_tok_sel_after = []
    bal_tok_buy_after = []
    private_key_alias = []
    trading_fee = [77, 22, 11, 66, 99, 2, 33, 55, 88, 44]

    for trader in traders:
        bal_tok_1 = trader.get_token_balance(token_sell)
        bal_tok_2 = trader.get_token_balance(token_buy)

        if bal_tok_1 <= trade_amount:
            pytest.skip(
                f"This {l6(trader.private_key)} token {l6(token_sell)} bal: {bal_tok_1} <= {trade_amount},"
                f"NOT ENOUGH FOR TEST")

        bal_tok_sel_before.append(bal_tok_1)
        bal_tok_buy_before.append(bal_tok_2)
        private_key_alias.append(l6(trader.private_key))

    rate_before = pde_state_b4.get_rate_between_token(token_sell, token_buy)

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{token_sell[-6:]} balance before trade      : {str(bal_tok_sel_before)}")
    INFO(f"{token_buy[-6:]} balance before trade         : {str(bal_tok_buy_before)}")
    INFO(f"Rate {token_sell[-6:]} vs {token_buy[-6:]} - Before Trade : {str(rate_before)}")

    STEP(2, f"trade {token_sell[-6:]} at the same time")
    tx_list = []
    threads = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future = executor.submit(trader.pde_trade, token_sell, trade_amount, token_buy, 1, trading_fee[i])
            threads.append(future)
    INFO(f"Transaction id list")
    for thread in threads:
        tx = thread.result()
        tx_list.append(tx)
        INFO(f'    {tx.get_tx_id()}')

    STEP(3, "Wait for Tx to be confirmed")
    tx_fee_list = []
    for tx in tx_list:
        print(f'          checking tx id: {l6(tx.get_tx_id())}')
        tx_detail = tx.get_transaction_by_hash()
        assert tx_detail.get_block_height() != 0, f"The {tx.get_tx_id()} is NOT yet confirmed"
        tx_fee_list.append(tx_detail.get_fee())

    STEP(4, "CHECK BALANCE AFTER")
    for i in range(0, len(traders)):
        trader = traders[i]
        balance_tok_2 = trader.wait_for_balance_change(token_buy, bal_tok_buy_before[i], 100)
        if balance_tok_2 is not False:
            bal_tok_buy_after.append(balance_tok_2)
            balance_tok1 = trader.wait_for_balance_change(token_sell, bal_tok_sel_before[i], -100)
            bal_tok_sel_after.append(balance_tok1)
        else:
            assert False, "Wait time expired, {token2[-6:]} did NOT increase"
    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{token_sell[-6:]} balance after trade        : {bal_tok_sel_after}")
    INFO(f"{token_buy[-6:]}    balance after trade        : {bal_tok_buy_after}")

    STEP(5, f"Check rate {token_sell[-6:]}  vs {token_buy[-6:]}")
    pde_state_af = SUT().get_latest_pde_state_info()
    rate_after = pde_state_af.get_rate_between_token(token_sell, token_buy)
    INFO(f"rate {token_sell[-6:]} vs {token_buy[-6:]} - After Trade  : {rate_after}")

    STEP(6, "Double check the algorithm ")
    result_sell = []
    sell_false = []
    result_buy = []
    buy_false = []
    calculated_rate = copy.deepcopy(rate_before)
    trade_priority = []

    for i in range(0, len(trading_fee)):
        trade_priority.append(trade_amount / trading_fee[i])
    print("Trade Priority: " + str(trade_priority))

    sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k])
    print("Sort order: " + str(sort_order))

    for order in sort_order:
        print(str(order) + "--")
        received_amount_estimated = received_amount_estimated_without_tx_fee = \
            PdeMath.cal_trade_receive(trade_amount, calculated_rate[0], calculated_rate[1])
        if token_buy == PRV_ID:
            received_amount_estimated = received_amount_estimated_without_tx_fee - tx_fee_list[order]

        received_amount_actual = bal_tok_buy_after[order] - bal_tok_buy_before[order]

        if received_amount_estimated == received_amount_actual:
            result_buy.append(str(order) + "Received_True")
        else:
            result_buy.append(str(order) + "Received_False")
        INFO(f'Received calculate/actual: {received_amount_estimated} - {received_amount_actual}')

        bal_after_sel_estimate = bal_tok_sel_before[order] - trading_fee[order] - trade_amount
        if token_sell == PRV_ID:
            bal_after_sel_estimate = bal_tok_sel_before[order] - trading_fee[order] - trade_amount - tx_fee_list[order]

        INFO(f" estimate vs real: {bal_after_sel_estimate}-{bal_tok_sel_after[order]}")
        if bal_after_sel_estimate == bal_tok_sel_after[order]:  # todo double check this
            result_sell.append(str(order) + "Trade_True")
        else:
            result_sell.append(str(order) + "Trade_False")
            sell_false.append(order)

        print("  Actual Trade amount: %d " % (
                bal_tok_sel_before[order] - bal_tok_sel_after[order] - trading_fee[order]))

        calculated_rate[0] = calculated_rate[0] + trade_amount + trading_fee[order]
        calculated_rate[1] = calculated_rate[1] - received_amount_estimated_without_tx_fee

    # sort result before print
    result_sell.sort()
    result_buy.sort()
    INFO("--")
    INFO(f"tx fee list   : {str(tx_fee_list)}")
    INFO(f"result {l6(token_sell)} : {str(result_sell)}")
    INFO(f"result {token_buy[-6:]} : {str(result_buy)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - Before Trade    : {str(rate_before)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - After Trade     : {str(rate_after)}")
    INFO(f"rate {l6(token_sell)} vs {token_buy[-6:]} - Calculated Trade: {str(calculated_rate)}")
    assert calculated_rate == rate_after and INFO("Pair Rate is correct"), "Pair Rate is WRONG after Trade"
    assert buy_false == [], f'Received_False at {buy_false}'
    assert sell_false == [], f'Trade_False at {sell_false}'
