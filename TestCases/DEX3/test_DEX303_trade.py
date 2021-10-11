import random

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import Status, PRV_ID, coin
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX3 import TOKEN_Y, TOKEN_OWNER, TOKEN_X

pde = SUT().get_pde3_state()
param = pde.get_params()
default_fee_rate = param.get_default_fee_rate_bps() * (100 - param.get_prv_discount_percent()) / 10000
amount = random.randrange(coin(10), coin(15))
PAIR_X_Y = '4a380dd28b431f320f062f9ea7cd6942a700feb4c98553987f7a6b9ea48774d8-' \
           '634d4c6591c79f029b261c3663af77efc5ee60fcc4b6a0d7823a114180ea2e1f-' \
           'd19ed28ae13d6ec46004a0bfe654518331e667ea7865c986a7dae7388dcfae9d'
PAIR_P_X = '0000000000000000000000000000000000000000000000000000000000000004-' \
           '634d4c6591c79f029b261c3663af77efc5ee60fcc4b6a0d7823a114180ea2e1f-' \
           '87560a911d728e06d537d21a09c7f2e32982f527f677ced61d6d397658706e48'


@pytest.mark.parametrize("trader, token_sell, token_buy, sell_amount,trading_fee, prv_fee, trade_path", [
    pytest.param(ACCOUNTS[-1], TOKEN_X, TOKEN_Y, amount, round(amount * default_fee_rate), True, "INIT_PAIR_IDS[0]",
                 marks=pytest.mark.dependency(
                     depends=['Testcases/DEX3/test_DEX301_ad_liquidity.py::test_add_liquidity_first_time'],
                     scope='session')),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, round(amount * default_fee_rate), True, "auto",
                 marks=pytest.mark.dependency(
                     depends=['Testcases/DEX3/test_DEX301_ad_liquidity.py::test_add_liquidity_first_time'],
                     scope='session')),
    # cross-pool, manual input pair
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, round(amount * default_fee_rate), True, [PAIR_P_X, PAIR_X_Y]),
])
def test_trade_same_pool_prv_fee(trader, token_sell, token_buy, sell_amount, trading_fee, prv_fee, trade_path):
    """
    Trade with prv trading fee and verify amm pool, order book, receive amount.
    Not yet verify fee in pool and use token fee.
    """
    if "INIT_PAIR_IDS" in trade_path:
        from TestCases.DEX3 import INIT_PAIR_IDS
        print(INIT_PAIR_IDS)
        trade_path = eval(f"[{trade_path}]")
    pde_b4 = SUT().get_pde3_state()
    if trade_path == "auto":
        pairs = pde_b4.get_pool_pair(tokens=[token_buy, token_sell])
        if not pairs:
            pytest.skip("There's no pool to trade")
        trade_path = [pde_b4.get_pool_pair(tokens=[token_buy, token_sell])[0].get_pool_pair_id()]
    if token_sell == PRV_ID:
        COIN_MASTER.top_up_if_lower_than(trader, 1.3 * sell_amount, 1.5 * sell_amount)
    else:
        TOKEN_OWNER.top_up_if_lower_than(trader, 1.3 * sell_amount, 1.5 * sell_amount, token_sell)

    bal_sel_b4 = trader.get_balance(token_sell)
    bal_buy_b4 = trader.get_balance(token_buy)
    bal_prv_b4 = trader.get_balance()
    pde_predict = pde_b4.clone()
    receive_est = pde_predict.pre_dict_state_after_trade(token_sell, token_buy, sell_amount, trade_path)
    Logging.STEP(1, "Init trade request")
    trade_req_tx = trader.pde3_trade(token_sell, token_buy, sell_amount, 1, trade_path, trading_fee, prv_fee)
    tx_fee = trade_req_tx.get_transaction_by_hash().get_fee()
    WAIT(ChainConfig.BLOCK_TIME * 5)

    Logging.STEP(2, "Check trade request status")
    trade_status = SUT().dex_v3().get_trade_status(trade_req_tx.get_tx_id())
    receive_from_status = trade_status.get_buy_mount()
    assert trade_status.get_status() == Status.DexV3.Trade.SUCCESS
    Logging.INFO(f'Trade success, trader will receive {receive_from_status} of token {token_buy}')

    Logging.STEP(3, "Verify pde state after trade")
    pde_af = SUT().get_pde3_state()
    breakpoint()
    assert pde_af == pde_predict

    Logging.STEP(4, "Verify balance after trade")
    bal_sel_af = trader.get_balance(token_sell)
    bal_buy_af = trader.get_balance(token_buy)
    bal_prv_af = trader.get_balance()
    assert receive_est == receive_from_status
    if prv_fee:
        if token_sell == PRV_ID != token_buy:
            Logging.INFO("Token sell is PRV # token buy")
            assert bal_sel_b4 - sell_amount - tx_fee - trading_fee == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est
        elif token_buy == PRV_ID != token_sell:
            Logging.INFO("Token buy is PRV # token sell")
            assert bal_sel_b4 - sell_amount == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est - tx_fee - trading_fee
        elif token_buy != token_sell != PRV_ID:
            Logging.INFO("Token buy is not token sell is not PRV")
            assert bal_sel_b4 - sell_amount == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est
            assert bal_prv_b4 - tx_fee - trading_fee == bal_prv_af
    else:
        pass
        # todo: implement later
