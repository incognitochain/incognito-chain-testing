import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin, PRV_ID, Status
from Helpers import TestHelper
from Helpers.Logging import INFO
from Helpers.TestHelper import make_random_word
from Helpers.Time import WAIT, get_current_date_time
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.DEX3 import TOKEN_OWNER

TOKEN_ID = '0000000000000000000000000000000000000000000000000000271021072311'
PAIR_ID = "0000000000000000000000000000000000000000000000000000000000000004-" \
          "0000000000000000000000000000000000000000000000000000271021072311-" \
          "d32fb3459cc8625db29f1d040832b2016584752b4b0ac00fd20dd30bd33b40b4"
go_uint64_max = 18446744073709551615
go_int64_max = 9223372036854775808


@pytest.mark.dependency(name="big_liquidity")
def test_add_liquidity_big_num():
    global TOKEN_ID, PAIR_ID
    AMP = 2

    contrib_amount_prv = coin(1000000)
    COIN_MASTER.top_up_if_lower_than(TOKEN_OWNER, contrib_amount_prv, contrib_amount_prv + 10000)
    b1 = TOKEN_OWNER.sum_my_utxo(TOKEN_ID)
    if b1 == 0:
        TOKEN_ID = "0000000000000000000000000000000000000000000000000000" + get_current_date_time()
        token_name = TestHelper.make_random_word()
        for i in range(10):
            mint_amount = go_uint64_max  # - 10000
            tx_init = COIN_MASTER.issue_centralize_token(TOKEN_OWNER, TOKEN_ID, token_name, mint_amount)
            b2 = TOKEN_OWNER.wait_for_balance_change(TOKEN_ID, b1)
            print(f" !!!! b1 = {b1}, b2 = {b2}")
            b1 = b2
            assert tx_init.get_transaction_by_hash().is_confirmed()
    for i in range(3):
        contrib_id = f"int64_max_{make_random_word()}"
        TOKEN_OWNER.pde3_add_liquidity(TOKEN_ID, go_int64_max, AMP * ChainConfig.Dex3.AMP_DECIMAL,
                                       contrib_id, pool_pair_id=PAIR_ID).get_transaction_by_hash()
        TOKEN_OWNER.pde3_add_liquidity(PRV_ID, int(contrib_amount_prv / 4), AMP * ChainConfig.Dex3.AMP_DECIMAL,
                                       contrib_id, pool_pair_id=PAIR_ID).get_transaction_by_hash()
        if not PAIR_ID:
            WAIT(ChainConfig.BLOCK_TIME * 5)
            PAIR_ID = SUT().pde3_get_state().get_pool_pair(tokens=[TOKEN_ID, PRV_ID])[0].get_pool_pair_id()

    WAIT(ChainConfig.BLOCK_TIME * 5)
    pde = SUT().pde3_get_state()
    pp = pde.get_pool_pair(tokens=[PRV_ID, TOKEN_ID])[0]
    pp.print_pool()
    assert pp.get_real_amount(TOKEN_ID) == go_int64_max * 4
    assert pp.get_real_amount(PRV_ID) == contrib_amount_prv
    assert pp.get_virtual_amount(TOKEN_ID) == go_int64_max * AMP
    assert pp.get_virtual_amount(PRV_ID) == contrib_amount_prv * AMP


@pytest.mark.dependency(depends=['big_liquidity'])
def test_trade_big_num():
    pde_b4 = SUT().pde3_get_state()
    sell_prv_amount = coin(10)
    receive = pde_b4.pre_dict_state_after_trade(PRV_ID, TOKEN_ID, sell_prv_amount, PAIR_ID)
    trading_fee = pde_b4.cal_min_trading_fee(sell_prv_amount, PRV_ID, PAIR_ID) + 1000
    COIN_MASTER.top_up_if_lower_than(TOKEN_OWNER, sell_prv_amount, 1.5 * sell_prv_amount)

    bal_tok_b4 = TOKEN_OWNER.get_balance(TOKEN_ID)
    tx = TOKEN_OWNER.pde3_trade(PRV_ID, TOKEN_ID, sell_prv_amount, 1, PAIR_ID, trading_fee)
    assert tx.get_transaction_by_hash().is_confirmed()
    WAIT(ChainConfig.BLOCK_TIME * 5)
    status = SUT().dex_v3().get_trade_status(tx.get_tx_id()).get_status()
    bal_tok_after = TOKEN_OWNER.wait_for_balance_change(TOKEN_ID, bal_tok_b4)
    pde_af = SUT().pde3_get_state()
    INFO(f"""
        Trade status success?        {status == Status.DexV3.Trade.SUCCESS}
        Real received vs expected:   {bal_tok_after - bal_tok_b4} - {receive} = {bal_tok_after - bal_tok_b4 - receive}
        Real PDE state == predicted? {pde_af == pde_b4}
    """)
    # assert status == Status.DexV3.Trade.SUCCESS
    # assert bal_tok_after - bal_tok_b4 == receive
    # assert pde_af == pde_b4


@pytest.mark.dependency(depends=['big_liquidity', 'test_trade_big_num'])
def test_withdraw_liquidity():
    pde_b4 = SUT().pde3_get_state()
    pp_predict = pde_b4.get_pool_pair(id=PAIR_ID).clone()
    receives = pp_predict.predict_pool_after_withdraw_share()
    bal_tok_b4 = TOKEN_OWNER.get_balance(TOKEN_ID)
    TOKEN_OWNER.pde3_withdraw_liquidity(PAIR_ID).get_transaction_by_hash()
    bal_tok_af = TOKEN_OWNER.wait_for_balance_change(TOKEN_ID, bal_tok_b4)
    pde_af = SUT().pde3_get_state()
    pde_af.get_pool_pair(id=PAIR_ID).print_pool()
    assert bal_tok_af - bal_tok_b4 == receives[TOKEN_ID]
    assert pp_predict == pde_af.get_pool_pair(id=PAIR_ID)
