import copy
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import PRV_ID, coin, Status
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import STEP, INFO, INFO_HEADLINE
from Helpers.TestHelper import l6, ChainHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from Objects.PdeObjects import PDEStateInfo
from TestCases.DEX import token_owner, token_id_1, token_id_2, token_id_0, acc_list_1_shard, \
    acc_list_n_shard, calculate_trade_order

pde_state_b4 = PDEStateInfo()


def setup_function():
    global pde_state_b4
    STEP(0, "Get pde state b4 test")
    pde_state_b4 = SUT().get_latest_pde_state_info()


@pytest.mark.parametrize('trader,token', [
    (token_owner, PRV_ID),
    (token_owner, token_id_1),
    (token_owner, token_id_2),
])
def test_trade_same_token(trader, token):
    trade_amount = random.randint(coin(1), coin(1000))
    trading_fee = trade_amount // 10
    global pde_state_b4

    STEP(1, f'Trade {l6(token)} for {l6(token)}')
    trade_tx = trader.pde_trade_v2(token, trade_amount, token, trading_fee)

    STEP(2, 'Expect error: TokenIDToSellStr should be different from TokenIDToBuyStr')
    trade_tx.expect_error()
    assert 'TokenIDToSellStr should be different from TokenIDToBuyStr' in trade_tx.get_error_trace().get_message()

    ChainHelper.wait_till_next_epoch()
    STEP(3, 'Compare PDE state before and after test')
    pde_state_after = SUT().get_latest_pde_state_info()
    assert pde_state_b4 == pde_state_after


@pytest.mark.parametrize('trader, token_sell, token_buy', [
    (token_owner, PRV_ID, token_id_0),
    (token_owner, token_id_0, PRV_ID),
    (token_owner, token_id_0, token_id_2),
    (token_owner, token_id_0, token_id_1),
])
def test_trade_non_exist_pair(trader, token_sell, token_buy):
    """
    @param trader:
    @param token_sell: if this token is not existed, RPC will return Invalid Token Error
    @param token_buy: if this token is not existed, RPC returns no error but will refund token_sell
    @return:
    """
    trade_amount = random.randint(1000, 20000000)
    trading_fee = max(1, trade_amount // 100)

    STEP(0, 'Check balance before trade and token pair is not existed in pool')
    pde = SUT().get_latest_pde_state_info()
    if pde.is_trading_pair_v2_is_possible(token_sell, token_buy):
        pytest.skip(f"trade possible due to prv-token pair is exist")
    bal_tok_sell_b4 = trader.get_token_balance(token_sell)
    bal_tok_buy_b4 = trader.get_token_balance(token_buy)

    STEP(1, f'Trade {l6(token_sell)} for {l6(token_buy)}')
    trade_tx = trader.pde_trade_v2(token_sell, trade_amount, token_buy, trading_fee)
    if trade_tx.get_error_trace() is not None and 'Invalid Token ID' in trade_tx.get_error_trace().get_message():
        trade_tx.expect_error('Invalid Token ID')
        return

    STEP(2, 'Wait for tx to be confirmed')
    trade_tx = trade_tx.subscribe_transaction()

    STEP(3, "Wait for balance to update")
    bal_tok_sell_af = trader.wait_for_balance_change(token_sell, bal_tok_sell_b4, -trade_amount / 2)
    bal_tok_buy_af = trader.wait_for_balance_change(token_buy, bal_tok_buy_b4, trade_amount / 2)

    STEP(4.1, f"Verify selling token balance change = trade amount =  {-trade_amount}")
    if token_sell == PRV_ID:
        assert bal_tok_sell_af == bal_tok_sell_b4 - trade_amount - trading_fee - trade_tx.get_fee()
    else:
        assert bal_tok_sell_af == bal_tok_sell_b4 - trade_amount

    STEP(4.2, f"Verify buy token balance does not change")
    if token_buy == PRV_ID:
        assert bal_tok_buy_b4 - trade_tx.get_fee() == bal_tok_buy_af
    else:
        assert bal_tok_buy_b4 == bal_tok_buy_af

    STEP(5, 'Wait for selling token amount to be returned both trade amount and trading fee')
    bal_tok_sell_returned = trader.wait_for_balance_change(token_sell, bal_tok_sell_af, trade_amount)
    if token_sell == PRV_ID:
        assert bal_tok_sell_returned == bal_tok_sell_b4 - trade_tx.get_fee(), \
            f'Token is not returned while it must be: before - after = {bal_tok_sell_b4 - bal_tok_sell_returned} \n' \
            f'Trade amount = {trade_amount}. Trade fee = {trading_fee}. Tx fee = {trade_tx.get_fee()} \n' \
            f'Trade tx = {trade_tx.get_tx_id()}'
    else:
        assert bal_tok_sell_returned == bal_tok_sell_b4

    STEP(6, "Verify PDEstate will not change")
    pde_state_af = SUT().get_latest_pde_state_info()
    assert pde_state_b4 == pde_state_af


@pytest.mark.parametrize('test_mode,token_sell,token_buy', (
        ["1 shard", token_id_1, PRV_ID],
        ["1 shard", PRV_ID, token_id_1],
        ["n shard", token_id_1, PRV_ID],
        ["n shard", PRV_ID, token_id_1],
        # tests below are hard to predict the min-acceptable value since they're cross pool trading
        # just list them here to acknowledge their existence
        # don't enable them since the test script cannot handle those cases just yet
        # ["1 shard", token_id_2, token_id_1],
        # ["n shard", token_id_2, token_id_1],
        # ["1 shard", token_id_1, token_id_2],
        # ["n shard", token_id_1, token_id_2],
))
def test_trading_with_min_acceptable_not_meet_expectation(test_mode, token_sell, token_buy):
    num_of_trade_tx = 10
    trade_amounts = [2234900] * num_of_trade_tx
    top = max(trade_amounts)
    COIN_MASTER.top_up_if_lower_than(acc_list_1_shard + acc_list_n_shard, 1.5 * top, 2 * top)
    token_owner.top_up_if_lower_than(acc_list_1_shard + acc_list_n_shard, 1.5 * top, 2 * top, token_id_1)
    token_owner.top_up_if_lower_than(acc_list_1_shard + acc_list_n_shard, 1.5 * top, 2 * top, token_id_2)
    trading_fees = [random.randrange(190000, 200000) for x in range(num_of_trade_tx - 1)] + [0]
    trade_order = calculate_trade_order(trading_fees, trade_amounts)

    if test_mode == '1 shard':
        traders = acc_list_1_shard
    else:
        traders = acc_list_n_shard

    global SUMMARY, pde_state_b4
    assert pde_state_b4.is_trading_pair_v2_is_possible(token_sell, token_buy)
    print(f"""
       Test bulk swap {test_mode}:
        - token {l6(token_sell)} vs {l6(token_buy)}
        - {num_of_trade_tx} address make trading at same time
        - difference trading fee
        - highest trading fee get better price
       """)

    STEP(1.1, 'Estimate rate and receive amount of each trade. '
              'Calculate min acceptable mount for half of the trades to be rejected')
    rate_b4 = pde_state_b4.get_rate_between_token(token_sell, token_buy)
    calculated_rate_latest = copy.deepcopy(rate_b4)
    estimated_rate_each_trade = [[]] * len(trade_order)
    estimated_receive_amount_each_trade = [0] * len(trade_order)
    for order in range(0, len(trade_order)):
        order_index = trade_order.index(order)
        trade_amount = trade_amounts[order_index]

        current_rate = copy.deepcopy(calculated_rate_latest)
        received_amount_token_buy = PdeMath.cal_trade_receive(trade_amount, current_rate[0], current_rate[1])
        estimated_rate_each_trade[order_index] = current_rate
        estimated_receive_amount_each_trade[order_index] = received_amount_token_buy
        calculated_rate_latest[0] += trade_amount
        calculated_rate_latest[1] -= received_amount_token_buy

    # take the middle trading turn receive amount as min acceptable amount
    mid_order = (len(trade_order) // 2) - 1
    mid_order_index = trade_order.index(mid_order)
    min_acceptable = estimated_receive_amount_each_trade[mid_order_index]

    STEP(1.2, "Checking balance")
    bal_tok_sell_b4 = []
    bal_tok_buy_b4 = []
    bal_tok_sell_af_tx = []
    bal_tok_buy_af_tx = []
    bal_tok_sell_af_ret = []
    bal_tok_buy_af_ret = []
    private_key_alias = []

    for i in range(0, len(traders)):
        trader = traders[i]
        amount = trade_amounts[i]
        bal_tok_sell = trader.get_token_balance(token_sell)
        bal_tok_buy = trader.get_token_balance(token_buy)

        if bal_tok_sell <= amount:
            pytest.skip(
                f"This {l6(trader.private_key)} token {l6(token_sell)} bal: {bal_tok_sell} <= {amount},"
                f"NOT ENOUGH FOR TEST")

        bal_tok_sell_b4.append(bal_tok_sell)
        bal_tok_buy_b4.append(bal_tok_buy)
        private_key_alias.append(l6(trader.private_key))

    INFO(f"Private key alias                : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell before trade      : {str(bal_tok_sell_b4)}")
    INFO(f"{l6(token_buy)} balance token buy before trade         : {str(bal_tok_buy_b4)}")
    INFO(f"Rate {l6(token_sell)} vs {l6(token_buy)} - Before Trade : {str(rate_b4)}")

    if token_buy != PRV_ID and token_sell != PRV_ID:
        rate_before_token_buy = pde_state_b4.get_rate_between_token(PRV_ID, token_buy)
        rate_before_token_sell = pde_state_b4.get_rate_between_token(token_sell, PRV_ID)
        INFO(f"Rate {l6(PRV_ID)} vs {l6(token_buy)} - Before Trade : {str(rate_before_token_buy)}")
        INFO(f"Rate {l6(token_sell)} vs {l6(PRV_ID)} - Before Trade : {str(rate_before_token_sell)}")
    STEP(2, f"trade {l6(token_sell)} at the same time: amount: {trade_amounts[0]}. Min acceptable: {min_acceptable}")
    trade_tx_list = []
    trade_threads = []
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future = executor.submit(trader.pde_trade_v2, token_sell, trade_amounts[i], token_buy, trading_fees[i],
                                     min_acceptable)
            trade_threads.append(future)

    INFO(f"Transaction id list")
    for thread in trade_threads:
        tx = thread.result()
        trade_tx_list.append(tx)
        INFO(f'    {tx.get_tx_id()}')

    STEP(3, "Wait for Tx to be confirmed")
    tx_fee_list = []
    for tx in trade_tx_list:
        print(f'          checking tx id: {l6(tx.get_tx_id())}')
        tx_detail = tx.get_transaction_by_hash(interval=10)
        assert tx_detail.is_confirmed(), f"The {tx.get_tx_id()} is NOT yet confirmed"
        tx_fee_list.append(tx_detail.get_fee())

    STEP(4.1, "Wait for balance of traders to update after tx accepted")
    threads_buy = {}
    threads_sell = {}
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future_buy = executor.submit(trader.wait_for_balance_change, token_buy, bal_tok_buy_b4[i], 100)
            future_sell = executor.submit(trader.wait_for_balance_change, token_sell, bal_tok_sell_b4[i], -100)
            threads_buy[trader] = future_buy
            threads_sell[trader] = future_sell

    STEP(4.2, "Balance summary after trade tx accept")

    for i in range(len(traders)):
        trader = traders[i]
        bal_tok_sell_af_tx.append(threads_sell[trader].result())
        bal_tok_buy_af_tx.append(threads_buy[trader].result())
    if token_buy == PRV_ID:
        actual_buy_token_received = [bal2 - bal1 + trading_fee + tx_fee for bal2, bal1, trading_fee, tx_fee in
                                     zip(bal_tok_buy_af_tx, bal_tok_buy_b4, trading_fees, tx_fee_list)]
    else:
        actual_buy_token_received = [bal2 - bal1 for bal2, bal1 in zip(bal_tok_buy_af_tx, bal_tok_buy_b4)]
    ##
    STEP(4.3, "Wait for balance of traders to update after trade returned")
    threads_buy = {}
    threads_sell = {}
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(traders)):
            trader = traders[i]
            future_buy = executor.submit(trader.wait_for_balance_change, token_buy, bal_tok_buy_b4[i], 100)
            future_sell = executor.submit(trader.wait_for_balance_change, token_sell, bal_tok_sell_b4[i], -100)
            threads_buy[trader] = future_buy
            threads_sell[trader] = future_sell

    STEP(4.4, "Balance summary after trade returned")
    for i in range(0, len(traders)):
        trader = traders[i]
        bal_tok_sell_af_ret.append(threads_sell[trader].result())
        bal_tok_buy_af_ret.append(threads_buy[trader].result())

    # todo: verify algorithm later, for now there's seem a bug here that does not match with trading priority
    real_trade_pass_count = 0
    for tx in trade_tx_list:
        trade_status = tx.get_trade_tx_status()
        if trade_status == Status.Dex.Trading.ACCEPTED:
            INFO(f'trade tx ACCEPTED: {tx.get_tx_id()}, status {trade_status}')
            real_trade_pass_count += 1
        else:
            INFO(f'trade tx RETURNED: {tx.get_tx_id()}, status {trade_status}')

    estimated_trade_pass_count = 0
    for amount in estimated_receive_amount_each_trade:
        if amount >= min_acceptable:
            estimated_trade_pass_count += 1
    compare_min_acceptable_with_actual_received_result = [x >= min_acceptable for x in actual_buy_token_received]

    INFO_HEADLINE('Summary !')
    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f'Min acceptable = {min_acceptable}')
    INFO(f'Trading order  : {trade_order}')
    INFO(f'Trading fee    : {trading_fees}')
    INFO(f'Transaction fee: {tx_fee_list}')
    INFO(f"Private key alias                 : {str(private_key_alias)}")
    INFO(f"{l6(token_sell)} balance token sell before trade       : {str(bal_tok_sell_b4)}")
    INFO(f"{l6(token_buy)} balance token buy  before trade       : {str(bal_tok_buy_b4)}")
    INFO(f"{l6(token_sell)} balance token sell after  tx accepted : {bal_tok_sell_af_tx}")
    INFO(f"{l6(token_buy)} balance token buy  after  tx accepted : {bal_tok_buy_af_tx}")
    INFO(f"{l6(token_sell)} balance token sell after  trade return: {bal_tok_sell_af_ret}")
    INFO(f"{l6(token_buy)} balance token buy  after  trade return: {bal_tok_buy_af_ret}")
    INFO(f"{l6(token_buy)}  actual received : {actual_buy_token_received}")
    INFO(f'Estimated trade receive    : {estimated_receive_amount_each_trade}')
    INFO(f"Compare to min acceptable: {compare_min_acceptable_with_actual_received_result}")
    INFO(f'Num of trade success estimated/reality: {estimated_trade_pass_count}/{real_trade_pass_count}')

    assert real_trade_pass_count == estimated_trade_pass_count
