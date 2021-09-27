import json

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin, PRV_ID
from Helpers import Logging
from Helpers.Time import get_current_date_time, WAIT
from Objects.AccountObject import Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from Objects.PdexV3Objects import PdeV3State
from TestCases.DEX3 import TOKEN_X, TOKEN_Y, TOKEN_OWNER

INIT_PAIR_IDS = []


@pytest.mark.dependency()
@pytest.mark.parametrize("contributor,nft_id, contribution, amplifier", [
    (TOKEN_OWNER, TOKEN_OWNER.nft_ids[0], {TOKEN_X: coin(1000), TOKEN_Y: coin(2100)}, 20000),
    (TOKEN_OWNER, TOKEN_OWNER.nft_ids[0], {TOKEN_X: coin(1000), PRV_ID: coin(2100)}, 20000),
])
def test_add_liquidity_first_time(contributor, nft_id, contribution, amplifier):
    contributor: Account
    Logging.INFO(f"""test_add_liquidity_no_trade with : {contributor}
        {json.dumps(contribution, indent=3)}""")
    pde_b4 = SUT().get_pde3_state()
    token_x, token_y = contribution.keys()
    try:
        top_up_amount = 2 * contribution[PRV_ID]
        COIN_MASTER.top_up_if_lower_than(contributor, top_up_amount, top_up_amount + coin(1))
    except KeyError:
        pass
    x_add_amount, y_add_amount = contribution[token_x], contribution[token_y]
    empty_pair = PdeV3State.PoolPairData.make_empty_pool([token_x, token_y], nft_id)
    predict_pool, return_amount = empty_pair.predict_pool_when_add_liquidity(contribution, contributor.nft_ids[0],
                                                                             amplifier)
    contribute_id = f"{contributor.private_key[-6:]}-{get_current_date_time()}"
    bal_x_b4 = contributor.get_balance(token_x)
    bal_y_b4 = contributor.get_balance(token_y)

    Logging.STEP(1, f"Add token X, amount {x_add_amount}")
    tx0 = contributor.pde3_add_liquidity(token_x, x_add_amount, amplifier, contribute_id,
                                         nft_id).get_transaction_by_hash()
    Logging.STEP(2, f"Add token Y, amount {y_add_amount}")
    tx1 = contributor.pde3_add_liquidity(token_y, y_add_amount, amplifier, contribute_id,
                                         nft_id).get_transaction_by_hash()
    fee_if_prv_x = tx0.get_fee() + tx1.get_fee() if token_x == PRV_ID else 0
    fee_if_prv_y = tx0.get_fee() + tx1.get_fee() if token_y == PRV_ID else 0
    Logging.STEP(3, f"Verify pool")
    WAIT(3 * ChainConfig.BLOCK_TIME)
    pde_state = SUT().get_pde3_state()
    new_pool_pair = pde_state.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair.pair_data() == predict_pool.pair_data()
    assert return_amount == {token_x: 0, token_y: 0}
    pp_id = new_pool_pair.get_pool_pair_id()
    global INIT_PAIR_IDS
    INIT_PAIR_IDS.append(pp_id)

    bal_x_af = contributor.get_balance(token_x)
    bal_y_af = contributor.get_balance(token_y)
    assert bal_x_b4 - x_add_amount - fee_if_prv_x == bal_x_af
    assert bal_y_b4 - y_add_amount - fee_if_prv_y == bal_y_af

    Logging.STEP(4, "Contribute one more time to the same pool with same amount")
    contribute_id = f"{contributor.private_key[-6:]}-{get_current_date_time()}"
    tx0 = contributor.pde3_add_liquidity(token_x, x_add_amount, amplifier, contribute_id,
                                         pool_pair_id=pp_id).get_transaction_by_hash()
    tx1 = contributor.pde3_add_liquidity(token_y, y_add_amount, amplifier, contribute_id,
                                         pool_pair_id=pp_id).get_transaction_by_hash()
    fee_if_prv_x = tx0.get_fee() + tx1.get_fee() if token_x == PRV_ID else 0
    fee_if_prv_y = tx0.get_fee() + tx1.get_fee() if token_y == PRV_ID else 0
    WAIT(120)
    pde_state2 = SUT().get_pde3_state()
    new_pool_pair2 = pde_state2.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair2.get_real_amount(token_x) == 2 * x_add_amount
    assert new_pool_pair2.get_real_amount(token_y) == 2 * y_add_amount
    pool_predict, return_amount = new_pool_pair. \
        predict_pool_when_add_liquidity({token_x: x_add_amount, token_y: y_add_amount}, contributor.nft_ids[0])
    bal_x_af2 = contributor.get_balance(token_x)
    bal_y_af2 = contributor.get_balance(token_y)
    assert bal_x_af - x_add_amount - fee_if_prv_x == bal_x_af2
    assert bal_y_af - y_add_amount - fee_if_prv_y == bal_y_af2
    print(new_pool_pair2)
    print(pool_predict)
    assert new_pool_pair2 == pool_predict
    assert return_amount == {token_x: 0, token_y: 0}


@pytest.mark.parametrize("contributor,nft_id, contribution, pair_id, amplifier", [
    pytest.param(ACCOUNTS[1], ACCOUNTS[1].nft_ids[0], {TOKEN_X: coin(5000), TOKEN_Y: coin(30000)}, "INIT_PAIR_IDS",
                 200, marks=pytest.mark.dependency(name="test_add_liquidity_first_time")),

])
def test_add_liquidity_no_trade_with_return(contributor, nft_id, contribution, pair_id, amplifier):
    pair_id = INIT_PAIR_IDS[0] if pair_id == "INIT_PAIR_IDS" else pair_id
    pde_state_b4 = SUT().get_pde3_state()
    token_x, token_y = contribution.keys()
    if pair_id:
        pool_b4 = pde_state_b4.get_pool_pair(id=pair_id)
    else:
        pool_b4 = PdeV3State.PoolPairData.make_empty_pool([token_x, token_y], nft_id)
    pair_id = pool_b4.get_pool_pair_id() if not pair_id else pair_id
    amount_x = contribution[token_x]
    amount_y = contribution[token_y]
    predict_pool, return_amount = \
        pool_b4.predict_pool_when_add_liquidity({token_x: amount_x, token_y: amount_y}, nft_id, amplifier)
    contrib_id = f"{token_x[-6:]}-{token_y[-6:]}-{get_current_date_time()}"
    TOKEN_OWNER.top_up_if_lower_than(contributor, amount_x, amount_x, token_x)
    TOKEN_OWNER.top_up_if_lower_than(contributor, amount_y, amount_y, token_y)

    Logging.STEP(1, f"Contribute {token_x}")
    contributor.pde3_add_liquidity(token_x, amount_x, amplifier, contrib_id, nft_id, pair_id).get_transaction_by_hash()
    Logging.STEP(2, f"Contribute {token_y}")
    contributor.pde3_add_liquidity(token_y, amount_y, amplifier, contrib_id, nft_id, pair_id).get_transaction_by_hash()
    Logging.STEP(3, f"Verify pool")
    WAIT(3 * ChainConfig.BLOCK_TIME)
    pde_state = SUT().get_pde3_state()
    new_pool_pair = pde_state.get_pool_pair(id=pair_id)
    Logging.INFO("Real pool after contribution\n", new_pool_pair)
    Logging.INFO("Predicted pool \n", predict_pool)
    assert new_pool_pair == predict_pool


@pytest.mark.dependency(depends=["test_add_liquidity_first_time"])
@pytest.mark.parametrize("contributor,nft_id, with_draw_percent, pair_id", [
    (ACCOUNTS[1], TOKEN_OWNER.nft_ids[0], 0.1, "INIT_PAIR_IDS"),
])
def test_withdraw_liquidity(contributor, nft_id, with_draw_percent, pair_id):
    # TODO: not yet done
    pair_id = INIT_PAIR_IDS[0] if pair_id == "INIT_PAIR_IDS" else pair_id
    pde_b4 = SUT().get_pde3_state()
    my_current_share = pde_b4.get_pool_pair(id=pair_id).get_share(nft_id).amount
    with_draw_amount = int(with_draw_percent * my_current_share)
    # contributor.pde3_withdraw_liquidity()
