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
PAIR_X_Y = '215c042e09db3ff2fe8902374e33ed5239bff871d88a208ed2cccaabc92e3f98-' \
           'dbf8513f847263ee4027e9aea9695bbd054d4bd77136c14e70e6aebfe88e5ff2-' \
           'e489359a7a5c334577ad966bf86979eb4c2f98591467fd27655676b101c24c8d'

PAIR_P_X = '0000000000000000000000000000000000000000000000000000000000000004-' \
           'dbf8513f847263ee4027e9aea9695bbd054d4bd77136c14e70e6aebfe88e5ff2-' \
           '066d3e52eecb4001637f95ce07ca3f3c8d39b66deda40721215456f5ed1722f9'

TOKEN_A = '32cf06ea1fdf9c0454db2e462aa6aff10eff50a3cae2cb2f46ef070e1a436b1c'
TOKEN_B = 'b6da743b3d24d6040e45a8672cdb002d103922c242f9c136dd1786644eb54e95'
TOKEN_C = 'f734d103392886384f68b6ef97ddf7cbe780e465f782c45f4f44de879db0e02f'
TOKEN_D = 'bec7aada587f392bc2ab81d9c530e3991f35206238bdfda4edcff3834379b848'
PAIR_P_A = '0000000000000000000000000000000000000000000000000000000000000004-' \
           '32cf06ea1fdf9c0454db2e462aa6aff10eff50a3cae2cb2f46ef070e1a436b1c-' \
           'cfddac5469ad170ffdcc857765fdcfb6dba49e3239c62450bd83171b33c320a0'
PAIR_A_C = '32cf06ea1fdf9c0454db2e462aa6aff10eff50a3cae2cb2f46ef070e1a436b1c-' \
           'f734d103392886384f68b6ef97ddf7cbe780e465f782c45f4f44de879db0e02f-' \
           '52a24637df6c3dff4152902d90b0546b35407d41093ecb0f992f2137524ddf25'
PAIR_B_C = 'b6da743b3d24d6040e45a8672cdb002d103922c242f9c136dd1786644eb54e95-' \
           'f734d103392886384f68b6ef97ddf7cbe780e465f782c45f4f44de879db0e02f-' \
           '3c2aa184ce39b597bd7402250afa7cfbb659c034013021e4e382ae9b91331a8f'
PAIR_B_D = 'b6da743b3d24d6040e45a8672cdb002d103922c242f9c136dd1786644eb54e95-' \
           'bec7aada587f392bc2ab81d9c530e3991f35206238bdfda4edcff3834379b848-' \
           'a8eec641b3712549288265151f57a2c66e19ee628222f0526294bd193e1f4bd6'
PATH_P_D = [PAIR_P_A, PAIR_A_C, PAIR_B_C, PAIR_B_D]
PATH_A_D = [PAIR_A_C, PAIR_B_C, PAIR_B_D]


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
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, trading_fee_prv_min, PRV_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee PRV
    pytest.param(ACCOUNTS[-1], TOKEN_Y, TOKEN_X, amount, trading_fee_tok_min, token_fee, "[INIT_PAIR_IDS[1]]",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),  # use min fee TOKEN

    # Cross pool
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, 2 * trading_fee_prv, PRV_fee, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, 2 * trading_fee_tok, token_fee, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),

    # cross-pool, manual input pair
    # pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, trading_fee, PRV_fee, [PAIR_P_X]),
    # pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_X, amount, trading_fee, token_fee, [PAIR_P_X]),
    # pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, trading_fee, PRV_fee,
    #              [PAIR_P_X, PAIR_P_X, PAIR_P_X, PAIR_P_X, PAIR_P_X]),
    # pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_Y, amount, trading_fee, token_fee, [PAIR_P_X, PAIR_X_Y]),
    # pytest.param(ACCOUNTS[-1], PRV_ID, TOKEN_D, 100000000, 100000000 * default_prv_fee_rate, PRV_fee, PATH_P_D),
    # pytest.param(ACCOUNTS[-1], TOKEN_A, TOKEN_D, 100000000, int(100000000 * default_tok_fee_rate), PRV_fee, PATH_A_D),
])
def test_trade_same_pool_prv_fee(trader, token_sell, token_buy, sell_amount, trade_fee, fee_type, trade_path):
    """
    Trade with prv trading fee and verify amm pool, order book, receive amount.
    Not yet verify fee in pool and use token fee.
    """
    if "INIT_PAIR_IDS" in trade_path:
        from TestCases.DEX3 import INIT_PAIR_IDS
        print(INIT_PAIR_IDS)
        trade_path = eval(trade_path)
    pde_b4 = SUT().pde3_get_state()
    if trade_path == "auto":
        pairs = pde_b4.get_pool_pair(tokens=[token_buy, token_sell])
        if not pairs:
            pytest.skip("There's no pool to trade")
        trade_path = [pde_b4.get_pool_pair(tokens=[token_buy, token_sell])[0].get_pool_pair_id()]
    if token_sell == PRV_ID:
        COIN_MASTER.top_up_if_lower_than(trader, 1.3 * sell_amount, 1.5 * sell_amount)
    else:
        TOKEN_OWNER.top_up_if_lower_than(trader, 1.6 * sell_amount, 2 * sell_amount, token_sell)
    bal_sel_b4 = trader.get_balance(token_sell)
    bal_buy_b4 = trader.get_balance(token_buy)
    bal_prv_b4 = trader.get_balance()
    pde_predict = pde_b4.clone()
    receive_est = pde_predict.pre_dict_state_after_trade(token_sell, token_buy, sell_amount, trade_path)
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
