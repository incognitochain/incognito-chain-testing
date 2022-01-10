import copy
import random
from concurrent.futures import ThreadPoolExecutor
from typing import List

import pytest

from Configs.Constants import PRV_ID
from Configs.TokenIds import pUSDC
from Helpers import Logging
from Objects.AccountObject import AccountGroup, Account, COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS, SUT
from TestCases.DEX3.Suite2 import PATH1


class BulkSwapData:
    def __init__(self):
        self.data = {}
        """ { Acount: [trade amount, trade fee] } """

    def make_new_data(self, traders, trade_min, trade_max):
        fee___min, fee___max = int(trade_min / 10), int(trade_max / 10)
        sell_amounts = [random.randrange(trade_min, trade_max) for i in range(len(traders))]
        trade___fees = [random.randrange(fee___min, fee___max) for i in range(len(traders))]
        for i in range(len(traders)):
            self.data[traders[i]] = [sell_amounts[i], trade___fees[i]]
        return self

    def make_new_data_same_trade_amount(self, traders, trade_amount):
        fee___min, fee___max = int(trade_amount / 15), int(trade_amount / 10)
        trade___fees = [random.randrange(fee___min, fee___max) for i in range(len(traders))]
        for i in range(len(traders)):
            self.data[traders[i]] = [trade_amount, trade___fees[i]]
        return self

    def get_trade_amount(self, acc):
        try:
            return self.data[acc][0]
        except KeyError:
            return 0

    def get_trade_fee(self, acc):
        try:
            return self.data[acc][1]
        except KeyError:
            return 0

    def sort_trade(self):
        self.data = {key: value for key, value in
                     sorted(self.data.items(), key=lambda item: item[1][1] / item[1][0], reverse=True)}
        return self

    def pretty(self):
        pretty = ""
        for acc, amount_n_fee in self.data.items():
            pretty += f"{acc.private_key[-8:]} : sell {amount_n_fee[0]}: fee {amount_n_fee[1]}\n"
        return pretty

    def get_account_group(self):
        return AccountGroup(*[acc for acc in self.data.keys()])

    def get_accounts(self) -> List[Account]:
        return [acc for acc in self.data.keys()]

    def clone(self):
        new_ob = BulkSwapData()
        new_ob.data = copy.deepcopy(self.data)
        return new_ob


@pytest.mark.parametrize("traders, token_sell, token_buy, trade_amount, trade_path", [
    (ACCOUNTS, PRV_ID, pUSDC, int(1e12), PATH1),
])
def test_bulk_swap_same_amount_diff_fee(traders, token_sell, token_buy, trade_amount, trade_path):
    pde_b4 = SUT().pde3_get_state()
    pde_predict = pde_b4.clone()
    traders.pde3_get_nft_ids(pde_b4)
    COIN_MASTER.top_up_if_lower_than(traders, int(1.5 * trade_amount), int(2 * trade_amount), token_sell)
    traders_bal_sel_b4 = traders.get_balance(token_sell)
    traders_bal_buy_b4 = traders.get_balance(token_buy)
    traders_bal_prv_b4 = traders_bal_sel_b4 if token_sell == PRV_ID else traders.get_balance()
    test_data = BulkSwapData().make_new_data_same_trade_amount(traders, trade_amount)
    test_data_sorted = test_data.clone().sort_trade()
    Logging.INFO(f"Trade data:\n"
                 f"{test_data.pretty()}\n"
                 f"Trade order predicted:\n"
                 f"{test_data_sorted.pretty()}")
    Logging.INFO("Making raw trade txs...")
    raw_trade_txs = [acc.pde3_make_raw_trade_tx(token_sell, token_buy, trade_amount, 1, trade_path,
                                                test_data.get_trade_fee(acc))[1] for acc in test_data.get_accounts()]

    Logging.INFO("Sending created txs...")
    with ThreadPoolExecutor() as tpe:
        threads_send_txs = [tpe.submit(SUT().send_proof, raw_tx, token_sell) for raw_tx in raw_trade_txs]

    Logging.INFO("Wait for txs to be confirmed")
    with ThreadPoolExecutor() as tpe:
        thread_wait_txs = [tpe.submit(r.result().get_transaction_by_hash) for r in threads_send_txs]

    Logging.INFO("Checking balance...")
    TXS_IN_SHARD_HEIGHT = {r.result().get_tx_id(): r.result().get_block_height() for r in thread_wait_txs}
    traders_bal_buy_af = {}
    for acc in traders:
        bal = acc.wait_for_balance_change(token_buy, traders_bal_buy_b4[acc])
        traders_bal_buy_af[acc] = bal
    Logging.INFO("Checking trade status...")
    TRADE_STATUS = {tx: SUT().dex_v3().get_trade_status(tx) for tx in TXS_IN_SHARD_HEIGHT.keys()}
    TRADE_STATUS_COUNT = {status: sum(value == status for value in TRADE_STATUS.values()) for status in
                          set(TRADE_STATUS.values())}
    Logging.INFO("Checking pde state...")
    pde_af = SUT().pde3_get_state()
    estimated_receives = {acc: pde_predict.predict_state_after_trade(token_sell, token_buy, trade_amount, trade_path)[0]
                          for acc in test_data_sorted.get_accounts()}
    BAL_REC_COMPARE = ""
    for acc in traders:
        real_receive = traders_bal_buy_af[acc] - traders_bal_buy_b4[acc]
        estimate_receive = estimated_receives[acc]
        BAL_REC_COMPARE += f"    {real_receive} vs {estimated_receives[acc]} ? {real_receive == estimate_receive}\n"
    Logging.INFO(f"Summary: \n    "
                 f"Is pde state b4      = af? {pde_b4 == pde_af}\n    "
                 f"Is pde state predict = af? {pde_predict == pde_af}\n    "
                 f"real receive vs expected receive:\n    "
                 f"{BAL_REC_COMPARE}"
                 )
