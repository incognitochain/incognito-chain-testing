import random

import pytest

from Configs.Constants import Status
from Helpers.Logging import INFO
from Helpers.Time import get_current_date_time
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from Objects.PdexV3Objects import PdeV3State

pde = PdeV3State()
PAIR100, PAIR200, TOKEN_A, TOKEN_B = "", "", "", ""


def setup_module():
    INFO()
    global pde, PAIR100, PAIR200, TOKEN_A, TOKEN_B
    test_date = get_current_date_time()  # format: YYMMDDhhmmss
    TOKEN_A = f"de30{test_date}0000000000000000000000000000000000000000007e570a"
    TOKEN_B = f"de30{test_date}0000000000000000000000000000000000000000007e570b"
    for token, name in zip([TOKEN_A, TOKEN_B], [f"TOKEN_A_{test_date}", f"TOKEN_B_{test_date}"]):
        if COIN_MASTER.get_balance(token) < 1e14:
            COIN_MASTER.issue_centralize_token(COIN_MASTER, token, name, int(1e16)).get_transaction_by_hash()
    for token in [TOKEN_A, TOKEN_B]:
        COIN_MASTER.wait_for_balance_change(token, 0)

    COIN_MASTER.pde3_get_my_nft_ids()
    for i in range(2):
        pair_hash = get_current_date_time()
        for token in [TOKEN_A, TOKEN_B]:
            COIN_MASTER.pde3_add_liquidity(token, int(1e12), 20000, pair_hash).get_transaction_by_hash()

    SUT().wait_till_next_beacon_height(2)

    pde = SUT().pde3_get_state()
    PAIR100, PAIR200 = [pool.get_pool_pair_id() for pool in pde.get_pool_pair(tokens=[TOKEN_A, TOKEN_B])]
    param = pde.get_pde_params()
    param.set_fee_rate_bps(PAIR100, 100)
    param.set_fee_rate_bps(PAIR200, 200)
    param.set_default_fee_rate_bps(150)
    tx_mod = COIN_MASTER.pde3_modify_param(param.get_configs(), tx_fee=10)
    tx_mod.get_transaction_by_hash()
    tx_mod_status = SUT().dex_v3().get_modify_param_status(tx_mod.get_tx_id())
    assert tx_mod_status.is_success()
    SUT().wait_till_next_beacon_height(2)


@pytest.mark.parametrize("trade_amount, trade_fee_rate, path, expected_trade_status", [
    (random.randrange(int(1e9), int(1e10)), 0.01, "[PAIR200]", Status.DexV3.Trade.REJECT),
    (random.randrange(int(1e9), int(1e10)), 0.007, "[PAIR100]", Status.DexV3.Trade.REJECT),

    (random.randrange(int(1e9), int(1e10)), 0.02, "[PAIR200]", Status.DexV3.Trade.SUCCESS),
    (random.randrange(int(1e9), int(1e10)), 0.01, "[PAIR100]", Status.DexV3.Trade.SUCCESS),
])
def test_fee_rate_bps(trade_amount, trade_fee_rate, path, expected_trade_status):
    INFO()
    trader = ACCOUNTS[0]
    path = eval(path)
    COIN_MASTER.top_up_if_lower_than(trader, int(2 * trade_amount), int(3 * trade_amount), TOKEN_A)
    trading_fee = round(trade_fee_rate * trade_amount) + 10
    trade_tx = trader.pde3_trade(TOKEN_A, TOKEN_B, trade_amount, 1, path, trading_fee, False,
                                 10).get_transaction_by_hash()
    SUT().wait_till_next_beacon_height(3)
    trade_status = SUT().dex_v3().get_trade_status(trade_tx.get_tx_id())
    assert trade_status.get_status() == expected_trade_status
