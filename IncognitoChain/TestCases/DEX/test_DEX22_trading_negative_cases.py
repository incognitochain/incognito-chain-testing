import random

import pytest

from IncognitoChain.Configs.Constants import PRV_ID, coin
from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.DEX import token_owner, token_id_1, token_id_2, token_id_0


@pytest.mark.parametrize('trader,token', [
    (token_owner, PRV_ID),
    (token_owner, token_id_1),
    (token_owner, token_id_2),
])
def test_trade_same_token(trader, token):
    trade_amount = random.randint(coin(1), coin(1000))
    trading_fee = trade_amount // 10

    STEP(1, f'Trade {l6(token)} for {l6(token)}')
    trade_tx = trader.pde_trade_v2(token, trade_amount, token, trading_fee)

    STEP(2, 'Expect error: TokenIDToSellStr should be different from TokenIDToBuyStr')
    trade_tx.expect_error()
    assert 'TokenIDToSellStr should be different from TokenIDToBuyStr' in trade_tx.get_error_trace().get_message()


@pytest.mark.parametrize('trader, token_sell, token_buy', [
    (token_owner, PRV_ID, token_id_0),
    # (token_owner, token_id_0, PRV_ID),
    # (token_owner, token_id_0, token_id_2),
    # (token_owner, token_id_0, token_id_1),
])
def test_trade_non_exist_pair(trader, token_sell, token_buy):
    trade_amount = random.randint(1000, 20000000)
    trading_fee = max(1, trade_amount // 100)
    pde_state_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()

    STEP(0, 'Check balance before trade')
    bal_tok_sell_b4 = trader.get_token_balance(token_sell)
    bal_tok_buy_b4 = trader.get_token_balance(token_buy)

    STEP(1, f'Trade {l6(token_sell)} for {l6(token_buy)}')
    trade_tx = trader.pde_trade_v2(token_sell, trade_amount, token_buy, trading_fee)

    STEP(2, 'Wait for tx to be confirmed')
    trade_tx = trade_tx.subscribe_transaction_obj()

    STEP(3, "Wait for balance to update")
    bal_tok_sell_af = trader.wait_for_balance_change(token_sell, bal_tok_sell_b4, -trade_amount / 2)
    bal_tok_buy_af = trader.wait_for_balance_change(token_buy, bal_tok_buy_b4, trade_amount / 2)

    STEP(4.1, f"Verify selling token balance change = trade amount =  {-(trade_amount)}")
    if token_sell == PRV_ID:
        assert bal_tok_sell_af == bal_tok_sell_b4 - trade_amount - trading_fee - trade_tx.get_fee()
    else:
        assert bal_tok_sell_af == bal_tok_sell_b4 - trade_amount - trading_fee

    STEP(4.2, f"Verify buy token balance does not change")
    if token_buy == PRV_ID:
        assert bal_tok_buy_b4 == bal_tok_buy_af - trade_tx.get_fee()
    else:
        assert bal_tok_buy_b4 == bal_tok_buy_af

    STEP(5, 'Wait for selling token amount to be returned both trade amount and trading fee')
    bal_tok_sell_returned = trader.wait_for_balance_change(token_sell, bal_tok_sell_af, trade_amount)
    if token_sell == PRV_ID:
        assert bal_tok_sell_returned == bal_tok_sell_b4 - trade_tx.get_fee()
    else:
        assert bal_tok_sell_returned == bal_tok_sell_b4

    STEP(6, "Verify PDEstate will not change")
    pde_state_af = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_b4 == pde_state_af
