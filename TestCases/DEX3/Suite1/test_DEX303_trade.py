import json
import random

import deepdiff
import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import Status, PRV_ID, coin
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX3.Suite1 import TOKEN_Y, TOKEN_X, TOKEN_OWNER

amount = random.randrange(coin(5), coin(7))
PRV_fee, token_fee = True, False
SUCCESS, REJECT = Status.DexV3.Trade.SUCCESS, Status.DexV3.Trade.REJECT


@pytest.mark.parametrize("trader, token_sell, token_buy, sell_amount, trade_fee, fee_type, trade_path, expect_status", [
    pytest.param(ACCOUNTS[-1], TOKEN_X, TOKEN_Y, amount, "double", PRV_fee, "[INIT_PAIR_IDS[1]]", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, "double", PRV_fee, "auto", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, "double", token_fee, "[INIT_PAIR_IDS[1]]", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, "min+10", token_fee, "[INIT_PAIR_IDS[1]]", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee TOKEN

    # Cross pool
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, "min+1", PRV_fee, "INIT_PAIR_IDS", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, "min+10", token_fee, "INIT_PAIR_IDS", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, PRV_ID, amount, "min+1", token_fee, "list(reversed(INIT_PAIR_IDS))", SUCCESS,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    # REJECT 1 pool
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, "min+10", PRV_fee, "[INIT_PAIR_IDS[1]]", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee PRV, have no TOKEN_Y - PRV to use for PRV fee
    pytest.param(ACCOUNTS[-1], TOKEN_X, TOKEN_Y, amount, "min", PRV_fee, "[INIT_PAIR_IDS[1]]", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, "min-1", PRV_fee, "auto", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, "min", token_fee, "[INIT_PAIR_IDS[1]]", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, "min", token_fee, "[INIT_PAIR_IDS[1]]", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),

    # REJECT Cross pool
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, "min-1", PRV_fee, "INIT_PAIR_IDS", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, "min-1", token_fee, "INIT_PAIR_IDS", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, PRV_ID, amount, "min", token_fee, "list(reversed(INIT_PAIR_IDS))", REJECT,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
])
def test_trade_success(trader, token_sell, token_buy, sell_amount, trade_fee, fee_type, trade_path, expect_status):
    """
    Trade with prv trading fee and verify amm pool, order book, receive amount.
    Not yet verify fee in pool and use token fee.
    """
    Logging.INFO()
    if "INIT_PAIR_IDS" in trade_path:
        from TestCases.DEX3.Suite1 import INIT_PAIR_IDS
        print(INIT_PAIR_IDS)
        trade_path = eval(trade_path)

    pde_b4 = SUT().pde3_get_state()
    try:
        min_fee = pde_b4.estimate_min_trading_fee(token_sell, sell_amount, fee_type or token_sell == PRV_ID, trade_path)
    except RuntimeError:
        min_fee = int(sell_amount / 10)
    trade_fee = {"double": 2 * min_fee,
                 "min+1": min_fee + 1,
                 "min+10": min_fee + 10,
                 "min-10": min_fee - 10,
                 "min-1": min_fee - 1,
                 "min": min_fee,
                 }[trade_fee]
    trade_path = pde_b4.make_path(token_sell, token_buy) if trade_path == "auto" else trade_path
    lp_value_b4 = SUT().pde3_get_lp_values_of_pools(trade_path, pde_b4, "LPReward")
    if token_sell == PRV_ID:
        COIN_MASTER.top_up_if_lower_than(trader, 1.3 * sell_amount, 1.5 * sell_amount)
    else:
        TOKEN_OWNER.top_up_if_lower_than(trader, 1.6 * sell_amount, 2 * sell_amount, token_sell)

    if not pde_b4.is_valid_path(token_sell, token_buy, trade_path):
        pytest.skip(f"Trade path is invalid")

    bal_sel_b4 = trader.get_balance(token_sell)
    bal_buy_b4 = trader.get_balance(token_buy)
    bal_prv_b4 = trader.get_balance()

    token_fee_used = PRV_ID if fee_type else token_sell
    Logging.STEP(1, "Init trade request")
    trade_req_tx = trader.pde3_trade(token_sell, token_buy, sell_amount, 1, trade_path, trade_fee, fee_type)
    tx_fee = trade_req_tx.get_transaction_by_hash().get_fee()
    WAIT(ChainConfig.BLOCK_TIME * 5)

    Logging.STEP(2, "Check trade request status")
    trade_status = SUT().dex_v3().get_trade_status(trade_req_tx.get_tx_id())
    receive_from_status = trade_status.get_buy_mount()
    bal_sel_af = trader.get_balance(token_sell)
    bal_buy_af = trader.get_balance(token_buy)
    bal_prv_af = trader.get_balance()
    Logging.INFO(f"""
        bal sel b4 - af: {bal_sel_b4} - {bal_sel_af} = {bal_sel_b4 - bal_sel_af}
        bal buy b4 - af: {bal_buy_b4} - {bal_buy_af} = {bal_buy_b4 - bal_buy_af}
        bal prv b4 - af: {bal_prv_b4} - {bal_prv_af} = {bal_prv_b4 - bal_prv_af}
        """)
    assert trade_status.get_status() == expect_status
    pde_af = SUT().pde3_get_state()

    if expect_status == SUCCESS:
        Logging.INFO("EXPECTED ACCEPT ")
        pde_predict = pde_b4.clone()
        receive_est, lp_value_predict = pde_predict.predict_state_after_trade(token_sell, token_buy, sell_amount,
                                                                              trade_path, trade_fee, fee_type,
                                                                              lp_value_b4)
        lp_value_af = SUT().pde3_get_lp_values_of_pools(trade_path, pde_af, "LPReward")
        Logging.INFO(f'Trade success, trader will receive {receive_from_status} of token {token_buy}')
        Logging.STEP(3, "Verify pde state after trade")
        assert pde_af == pde_predict
        dd = deepdiff.DeepDiff(lp_value_af, lp_value_predict, math_epsilon=2)
        if dd:
            Logging.ERROR(f" after {json.dumps(lp_value_af, indent=3)}")
            Logging.ERROR(f" predict {json.dumps(lp_value_predict, indent=3)}")
            raise AssertionError(dd.pretty())

        Logging.STEP(4, "Verify balance after trade")
        assert receive_est == receive_from_status

        Logging.INFO(f"Use PRV trading fee is {fee_type}")
        if token_sell == PRV_ID != token_buy:  # when token to sell is PRV, ignore use_prv fee option
            Logging.INFO(f"Token sell is PRV != token buy, but ignored (always use PRV)")
            assert bal_sel_b4 - sell_amount - tx_fee - trade_fee == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est
        elif fee_type:  # use prv as trading fee
            if token_buy == PRV_ID != token_sell:
                Logging.INFO(f"Token buy is PRV != token sell")
                assert bal_sel_b4 - sell_amount == bal_sel_af
                assert bal_buy_b4 == bal_buy_af - receive_est - tx_fee - trade_fee
            elif token_buy != token_sell != PRV_ID:
                Logging.INFO(f"Token buy != token sell != PRV")
                assert bal_sel_b4 - sell_amount == bal_sel_af
                assert bal_buy_b4 == bal_buy_af - receive_est
                assert bal_prv_b4 - tx_fee - trade_fee == bal_prv_af
        else:  # use token as trading fee
            if token_buy != PRV_ID:
                assert bal_prv_b4 - tx_fee == bal_prv_af
                assert bal_sel_b4 - trade_fee - sell_amount == bal_sel_af
                assert bal_buy_b4 + receive_est == bal_buy_af
            else:
                assert bal_sel_b4 - trade_fee - sell_amount == bal_sel_af
                assert bal_buy_b4 + receive_est - tx_fee == bal_buy_af
    elif expect_status == REJECT:
        Logging.INFO("EXPECTED REJECT ")
        lp_value_af = SUT().pde3_get_lp_values_of_pools(trade_path, pde_af, "LPReward")
        Logging.STEP(3, "Verify pde state after trade")
        assert pde_b4 == pde_af
        dd = deepdiff.DeepDiff(lp_value_b4, lp_value_af)
        if dd:
            raise AssertionError(dd.pretty())

        Logging.STEP(4, "Verify balance after trade")
        if token_sell == PRV_ID:
            assert bal_buy_b4 == bal_buy_af
            assert bal_prv_b4 - tx_fee == bal_prv_af
        elif token_buy == PRV_ID:
            assert bal_prv_b4 - tx_fee == bal_prv_af
            assert bal_sel_b4 == bal_sel_af
        else:
            assert bal_buy_b4 == bal_buy_af
            assert bal_sel_b4 == bal_sel_af
            assert bal_prv_b4 - tx_fee == bal_prv_af
