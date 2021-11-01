import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin, PRV_ID, Status
from Helpers import TestHelper
from Helpers.Logging import INFO
from Helpers.TestHelper import make_random_word
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account
from Objects.IncognitoTestCase import SUT, ACCOUNTS

TOKEN_OWNER = ACCOUNTS[0]
TOKEN_ID = '0000000000000000000000000000000000000000000000000000301021202725'
PAIR_ID = '0000000000000000000000000000000000000000000000000000000000000004-' \
          '0000000000000000000000000000000000000000000000000000301021202725-' \
          '6baab7c747fded4ab823e6f8661f5e1b1c4a52e8f3ec7327bd2e677a925219d6.'

go_uint64_max = pow(2, 64) - 1
go_int64_max = pow(2, 63) - 1


@pytest.mark.dependency(name="big_liquidity")
def test_add_liquidity_big_num():
    global TOKEN_ID, PAIR_ID
    amp = 2
    AMP = amp * ChainConfig.Dex3.AMP_DECIMAL
    contrib_amount_prv = coin(1000000)

    bal_tok_b4 = TOKEN_OWNER.sum_my_utxo(TOKEN_ID)
    bal_prv_b4 = TOKEN_OWNER.sum_my_utxo()

    pde_b4 = SUT().pde3_get_state()
    pp_b4 = pde_b4.get_pool_pair(id=PAIR_ID)
    TOKEN_OWNER.pde3_get_my_nft_ids(pde_b4)
    if pp_b4:
        contrib_amount_tok = go_uint64_max - pp_b4.get_real_amount(TOKEN_ID)
        contrib_amount_prv = pp_b4.cal_contribute_amount_other_token(TOKEN_ID, contrib_amount_tok)
    else:
        contrib_amount_tok = go_uint64_max
        PAIR_ID = ""
    COIN_MASTER.top_up_if_lower_than(TOKEN_OWNER, contrib_amount_prv, contrib_amount_prv + 10000)
    if bal_tok_b4 == 0:
        token_name = TestHelper.make_random_word()
        for i in range(10):
            tx_init = COIN_MASTER.issue_centralize_token(TOKEN_OWNER, TOKEN_ID, token_name, go_uint64_max)
            assert tx_init.get_transaction_by_hash().is_confirmed()
            bal_tok_b4 += go_uint64_max

    fee = [0] * 4
    contrib_id1 = f"uint64_max_first_half_{make_random_word()}"
    tok_1st_contrib = int(contrib_amount_tok / 2)
    prv_1st_contrib = int(contrib_amount_prv / 2)
    fee[0] = TOKEN_OWNER.pde3_add_liquidity(TOKEN_ID, tok_1st_contrib, AMP, contrib_id1,
                                            pool_pair_id=PAIR_ID).get_transaction_by_hash().get_fee()
    fee[1] = TOKEN_OWNER.pde3_add_liquidity(PRV_ID, prv_1st_contrib, AMP, contrib_id1,
                                            pool_pair_id=PAIR_ID).get_transaction_by_hash().get_fee()

    if not pp_b4:
        WAIT(ChainConfig.BLOCK_TIME * 5)
        PAIR_ID = SUT().pde3_get_state().get_pool_pair(ntf=TOKEN_OWNER.nft_ids[0], amp=AMP,
                                                       size={TOKEN_ID: tok_1st_contrib,
                                                             PRV_ID: prv_1st_contrib})[0].get_pool_pair_id()

    contrib_id2 = f"uint64_max_second_half_{make_random_word()}"
    fee[2] = TOKEN_OWNER.pde3_add_liquidity(TOKEN_ID, contrib_amount_tok - tok_1st_contrib, AMP, contrib_id2,
                                            pool_pair_id=PAIR_ID).get_transaction_by_hash().get_fee()
    tx_3 = TOKEN_OWNER.pde3_add_liquidity(PRV_ID, contrib_amount_prv - prv_1st_contrib, AMP, contrib_id2,
                                          pool_pair_id=PAIR_ID).get_transaction_by_hash()
    fee[3] = tx_3.get_fee()

    WAIT(ChainConfig.BLOCK_TIME * 5)
    status = SUT().dex_v3().get_contribution_status(tx_3.get_tx_id())
    assert status.get_status() == Status.DexV3.AddLiquidity.MATCH_N_REFUND
    tok_2nd_accepted = status.get_token_contribute_amount(TOKEN_ID)
    prv_2nd_accepted = status.get_token_contribute_amount(PRV_ID)
    all_tok_contrib = tok_1st_contrib + tok_2nd_accepted
    all_prv_contrib = prv_1st_contrib + prv_2nd_accepted
    pde = SUT().pde3_get_state()
    pp = pde.get_pool_pair(id=PAIR_ID)
    INFO(f"""{pp.get_pool_pair_id()}
        1st + 2nd contrib tok         : {tok_1st_contrib} + {tok_2nd_accepted} = {all_tok_contrib}
        1st + 2nd contrib PRV         : {prv_1st_contrib} + {prv_2nd_accepted} = {all_prv_contrib}

        real amount tok in pool: {pp.get_real_amount(TOKEN_ID)}
                    contributed: {all_tok_contrib}
        virt amount tok in pool: {pp.get_virtual_amount(TOKEN_ID)}
                       expected: {int(all_tok_contrib * amp)}
        
        real amount PRV in pool: {pp.get_real_amount(PRV_ID)}
                    contributed: {all_prv_contrib}
        virt amount PRV in pool: {pp.get_virtual_amount(PRV_ID)}
                       expected: {int(all_prv_contrib * amp)}
        
        bal PRV real after: {TOKEN_OWNER.sum_my_utxo()}
                  expected: {bal_prv_b4 - sum(fee) - all_prv_contrib}
        bal tok real after: {TOKEN_OWNER.sum_my_utxo(TOKEN_ID)}
                  expected: {bal_tok_b4 - all_tok_contrib}
    """)


@pytest.mark.parametrize("trader, tok_sell, tok_buy, sell_amount, description", [
    pytest.param(TOKEN_OWNER, TOKEN_ID, PRV_ID, coin(10), "UINT64 limit reached, trade should fail",
                 marks=pytest.mark.dependency(depends=['big_liquidity'])
                 ),
    pytest.param(TOKEN_OWNER, PRV_ID, TOKEN_ID, coin(10), "not yet reach UNIT64 limit, trade should pass",
                 marks=pytest.mark.dependency(depends=['big_liquidity'])
                 )
])
def test_trade_big_num_single_path(trader: Account, tok_sell, tok_buy, sell_amount, description):
    pde_b4 = SUT().pde3_get_state()
    pde_predict = pde_b4.clone()
    trading_fee = 2 * pde_predict.cal_min_trading_fee(sell_amount, tok_sell, PAIR_ID)
    estimated_receive = pde_predict.pre_dict_state_after_trade(tok_sell, tok_buy, sell_amount, PAIR_ID)
    COIN_MASTER.top_up_if_lower_than(trader, sell_amount, 1.5 * sell_amount)

    bal_buy_b4 = trader.sum_my_utxo(tok_buy)
    tx = trader.pde3_trade(tok_sell, tok_buy, sell_amount, 1, PAIR_ID, trading_fee)
    assert tx.get_transaction_by_hash().is_confirmed()
    WAIT(ChainConfig.BLOCK_TIME * 5)
    status_info = SUT().dex_v3().get_trade_status(tx.get_tx_id())
    found_utxo = False
    for utxo in trader.list_utxo(tok_buy):
        if utxo.get_value() == status_info.get_buy_mount():
            found_utxo = True
    status = status_info.get_status()
    bal_tok_after = TOKEN_OWNER.sum_my_utxo(tok_buy)
    real_received = bal_tok_after - bal_buy_b4
    off = real_received - estimated_receive
    pde_af = SUT().pde3_get_state()
    INFO(f"""
        Trade status success?        {status == Status.DexV3.Trade.SUCCESS} {description}
        Real received vs expected:   {real_received} - {estimated_receive} (= {off})
        Amount receive status:       {status_info.get_buy_mount()}
        Found the same utxo?         {found_utxo}
        Real PDE state af == predicted? {pde_af == pde_predict}
        Real PDE state after == before? {pde_af == pde_b4}
    """)


@pytest.mark.dependency(depends=['big_liquidity', 'test_trade_big_num'])
def test_withdraw_liquidity():
    pde_b4 = SUT().pde3_get_state()
    TOKEN_OWNER.pde3_get_my_nft_ids(pde_b4)
    pp_b4 = pde_b4.get_pool_pair(id=PAIR_ID).clone()
    pp_predict = pp_b4.clone()
    my_share_info = pp_b4.get_share(TOKEN_OWNER.nft_ids[0])
    receives = pp_predict.predict_pool_after_withdraw_share(my_share_info.amount - 10, TOKEN_OWNER.nft_ids[0])
    bal_prv_b4 = TOKEN_OWNER.sum_my_utxo()
    bal_tok_b4 = TOKEN_OWNER.sum_my_utxo(TOKEN_ID)
    TOKEN_OWNER.pde3_withdraw_liquidity(PAIR_ID, my_share_info.amount - 10).get_transaction_by_hash()
    pde_af = SUT().pde3_get_state()
    pde_af.get_pool_pair(id=PAIR_ID).print_pool()
    bal_prv_af = TOKEN_OWNER.wait_for_balance_change(PRV_ID)
    bal_tok_af = TOKEN_OWNER.sum_my_utxo(TOKEN_ID)
    INFO(f"""
        real token received vs estimated:  {bal_tok_af - bal_tok_b4} == {receives[TOKEN_ID]}
        real PRV received vs estimated:    {bal_prv_af - bal_prv_b4} == {receives[PRV_ID]}
        pool predicted == real pool after? {pp_predict == pde_af.get_pool_pair(id=PAIR_ID)}
    """)
