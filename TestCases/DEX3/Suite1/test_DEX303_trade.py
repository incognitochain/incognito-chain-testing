import random

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import Status, PRV_ID, coin
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX3.Suite1 import TOKEN_Y, TOKEN_X, TOKEN_OWNER

pde = SUT().pde3_get_state()
param = pde.get_pde_params()
amount = random.randrange(coin(5), coin(7))
default_tok_fee_rate = param.get_default_fee_rate_bps(to_float=True)
default_prv_fee_rate = param.get_default_fee_rate_bps(to_float=True) \
                       * (1 - param.get_prv_discount_percent(to_float=True))
trading_fee_prv_min = int(amount * default_prv_fee_rate)
trading_fee_tok_min = int(amount * default_tok_fee_rate)
trading_fee_prv = 2 * trading_fee_prv_min
trading_fee_tok = 2 * trading_fee_tok_min
PRV_fee = True
token_fee = False


# TOKEN_OWNER = Account(
#     '112t8rnX3VTd3MTWMpfbYP8HGY4ToAaLjrmUYzfjJBrAcb8iPLkNqvVDXWrLNiFV5yb2NBpR3FDZj3VW8GcLUwRdQ61hPMWP3YrREZAZ1UbH')


@pytest.mark.parametrize("trader, token_sell, token_buy, sell_amount, trade_fee, fee_type, trade_path", [
    pytest.param(ACCOUNTS[-1], TOKEN_X, TOKEN_Y, amount, trading_fee_prv, PRV_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, trading_fee_prv, PRV_fee, "auto",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, trading_fee_tok, token_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, trading_fee_prv_min + 10, PRV_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee PRV
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, trading_fee_tok_min + 10, token_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee TOKEN

    # Cross pool
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, 2 * trading_fee_prv, PRV_fee, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, 2 * trading_fee_tok, token_fee, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
])
def test_trade_success(trader, token_sell, token_buy, sell_amount, trade_fee, fee_type, trade_path):
    """
    Trade with prv trading fee and verify amm pool, order book, receive amount.
    Not yet verify fee in pool and use token fee.
    """
    if "INIT_PAIR_IDS" in trade_path:
        from TestCases.DEX3.Suite1 import INIT_PAIR_IDS
        print(INIT_PAIR_IDS)
        trade_path = eval(trade_path)
    pde_b4 = SUT().pde3_get_state()
    if trade_path == "auto":
        pairs = pde_b4.get_pool_pair(tokens=[token_buy, token_sell])
        trade_path = [pde_b4.get_pool_pair(tokens=[token_buy, token_sell])[0].get_pool_pair_id()]
    if token_sell == PRV_ID:
        COIN_MASTER.top_up_if_lower_than(trader, 1.3 * sell_amount, 1.5 * sell_amount)
    else:
        TOKEN_OWNER.top_up_if_lower_than(trader, 1.6 * sell_amount, 2 * sell_amount, token_sell)

    if not pde_b4.is_valid_path(token_sell, token_buy, trade_path):
        pytest.skip(f"Trade path is invalid")

    bal_sel_b4 = trader.get_balance(token_sell)
    bal_buy_b4 = trader.get_balance(token_buy)
    bal_prv_b4 = trader.get_balance()
    pde_predict = pde_b4.clone()
    receive_est = pde_predict.predict_state_after_trade(token_sell, token_buy, sell_amount, trade_path, trade_fee,
                                                        fee_type)
    token_fee_used = PRV_ID if fee_type else token_sell
    Logging.STEP(1, "Init trade request")
    trade_req_tx = trader.pde3_trade(token_sell, token_buy, sell_amount, 1, trade_path, trade_fee, fee_type)
    tx_fee = trade_req_tx.get_transaction_by_hash().get_fee()
    WAIT(ChainConfig.BLOCK_TIME * 5)

    Logging.STEP(2, "Check trade request status")
    trade_status = SUT().dex_v3().get_trade_status(trade_req_tx.get_tx_id())
    receive_from_status = trade_status.get_buy_mount()
    assert trade_status.get_status() == Status.DexV3.Trade.SUCCESS
    Logging.INFO(f'Trade success, trader will receive {receive_from_status} of token {token_buy}')

    Logging.STEP(3, "Verify pde state after trade")
    pde_af = SUT().pde3_get_state()
    assert pde_af == pde_predict

    Logging.STEP(4, "Verify balance after trade")
    bal_sel_af = trader.get_balance(token_sell)
    bal_buy_af = trader.get_balance(token_buy)
    bal_prv_af = trader.get_balance()
    assert receive_est == receive_from_status

    if token_sell == PRV_ID != token_buy:  # when token to sell is PRV, ignore use_prv fee option
        Logging.INFO(f"Token sell is PRV != token buy, use PRV trading fee is {fee_type}, but ignored (always use PRV)")
        assert bal_sel_b4 - sell_amount - tx_fee - trade_fee == bal_sel_af
        assert bal_buy_b4 == bal_buy_af - receive_est
    elif fee_type:  # use prv as trading fee
        if token_buy == PRV_ID != token_sell:
            Logging.INFO(f"Token buy is PRV != token sell, use PRV trading fee is {fee_type}")
            assert bal_sel_b4 - sell_amount == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est - tx_fee - trade_fee
        elif token_buy != token_sell != PRV_ID:
            Logging.INFO(f"Token buy != token sell != PRV, use PRV trading fee is {fee_type}")
            assert bal_sel_b4 - sell_amount == bal_sel_af
            assert bal_buy_b4 == bal_buy_af - receive_est
            assert bal_prv_b4 - tx_fee - trade_fee == bal_prv_af
    else:  # use token as trading fee
        Logging.INFO(f"Use PRV trading fee is {fee_type}")
        assert bal_prv_b4 - tx_fee == bal_prv_af
        assert bal_sel_b4 - trade_fee - sell_amount == bal_sel_af
        assert bal_buy_b4 + receive_est == bal_buy_af


def trade_fail_and_return():
    pass  # todo
