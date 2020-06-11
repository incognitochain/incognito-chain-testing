import copy
import random

import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO, DEBUG
from IncognitoChain.Helpers.TestHelper import calculate_actual_trade_received, l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.DEX import token_id_1, acc_list_1_shard, acc_list_n_shard, token_owner, token_id_2

trade_amount = random.randrange(5000, 10000)


def setup_module():
    for acc in acc_list_1_shard + acc_list_n_shard:
        if acc.get_prv_balance() <= trade_amount:
            COIN_MASTER.send_prv_to(acc, trade_amount * 2 - acc.get_prv_balance_cache()).subscribe_transaction()
            if COIN_MASTER.shard != acc.shard:
                try:
                    acc.subscribe_cross_output_coin()
                except:
                    pass
        if acc.get_token_balance(token_id_1) <= trade_amount:
            token_owner.send_token_to(acc, token_id_1, trade_amount * 2 - acc.get_token_balance_cache(token_id_1),
                                      prv_fee=-1, prv_privacy=0).subscribe_transaction()
            if token_owner.shard != acc.shard:
                try:
                    acc.subscribe_cross_output_token()
                except:
                    pass
        # if acc.get_token_balance(token_id_2) <= trade_amount:
        #     contributor.send_token_to(acc, token_id_2, trade_amount * 2 - acc.get_token_balance_cache(token_id_2),
        #                               prv_fee=-1, prv_privacy=0).subscribe_transaction()
        #     if contributor.shard != acc.shard:
        #         try:
        #             acc.subscribe_cross_output_token()
        #         except:
        #             pass


@pytest.mark.parametrize('test_mode,token1,token2', (
    ["1 shard", token_id_1, PRV_ID],
    ["n shard", token_id_1, PRV_ID],
    ["1 shard", token_id_1, token_id_2],
    ["n shard", token_id_1, token_id_2]
))
def test_bulk_swap(test_mode, token1, token2):
    if test_mode == '1 shard':
        traders = acc_list_1_shard
    else:
        traders = acc_list_n_shard
    print(f"""
       Test bulk swap {test_mode}:
        - token {l6(token1)} vd {l6(token2)}
        - 10 address make trading at same time
        - difference trading fee
        - highest trading fee get better price
       """)

    STEP(0, "Checking balance")
    balance_tok1_before = []
    balance_tok2_before = []
    balance_tok1_after = []
    balance_tok2_after = []
    private_key_alias = []
    trading_fee = [7, 2, 1, 6, 9, 2, 3, 5, 8, 4]

    trade_amount_token1 = trade_amount

    for trader in traders:
        trader.get_token_balance(token1)
        trader.get_token_balance(token2)

        assert trader.get_token_balance_cache(token1) > trade_amount_token1, \
            f"This {trader.private_key[-6:]} balance {token1[-6:]} less than trading amount"

        balance_tok1_before.append(trader.get_token_balance_cache(token1))
        balance_tok2_before.append(trader.get_token_balance_cache(token2))
        private_key_alias.append(trader.private_key[-6:])

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{token1[-6:]} balance before trade      : {str(balance_tok1_before)}")
    INFO(f"{token2[-6:]} balance before trade         : {str(balance_tok2_before)}")
    rate_before = SUT.full_node.get_latest_rate_between(token1, token2)
    INFO(f"Rate {token1[-6:]} vs {token2[-6:]} - Before Trade : {str(rate_before)}")

    STEP(2, f"trade {token1[-6:]} at the same time")
    tx_list = []
    for i in range(0, len(traders)):
        trader = traders[i]
        trade_tx = trader.trade_token(token1, trade_amount, token2, 1, trading_fee[i])
        tx_list.append(trade_tx)

    INFO(f"Transaction id list")
    for tx in tx_list:
        INFO(f'    {tx.get_tx_id()}')

    STEP(3, "Wait for Tx to be confirmed")
    tx_fee_list = []
    for tx in tx_list:
        tx_is_confirmed = False
        print(f'          checking tx id: {tx.get_tx_id()[-6:]}')
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
        balance_prv = trader.wait_for_balance_change(token2, balance_tok2_before[i])
        if balance_prv is not False:
            balance_tok2_after.append(balance_prv)
            balance_token = trader.wait_for_balance_change(token1, balance_tok1_before[i])
            balance_tok1_after.append(balance_token)
        else:
            assert False, "Wait time expired, {token2[-6:]} did NOT increase"
    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{token1[-6:]} balance after trade        : {balance_tok1_after}")
    INFO(f"{token2[-6:]}    balance after trade        : {balance_tok2_after}")

    STEP(5, f"Check rate {token1[-6:]}  vs {token2[-6:]}")
    rate_after = SUT.full_node.get_latest_rate_between(token1, token2)
    INFO(f"rate {token1[-6:]} vs {token2[-6:]} - After Trade  : {rate_after}")

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
    INFO(f"result {l6(token1)} : {str(result_token)}")
    INFO(f"result {token2[-6:]} : {str(result_prv)}")
    INFO(f"rate {l6(token1)} vs {token2[-6:]} - Before Trade   : {str(rate_before)}")
    INFO(f"rate {l6(token1)} vs {token2[-6:]} - After Trade    : {str(rate_after)}")
    INFO(f"rate {l6(token1)} vs {token2[-6:]} - Calulated Trade: {str(calculated_rate)}")
    assert calculated_rate == rate_after and INFO("Pair Rate is correct"), "Pair Rate is WRONG after Trade"
