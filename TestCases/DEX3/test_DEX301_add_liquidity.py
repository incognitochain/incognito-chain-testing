import json

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin, PRV_ID, Status
from Helpers import Logging
from Helpers.Time import get_current_date_time, WAIT
from Objects.AccountObject import Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from Objects.PdexV3Objects import PdeV3State
from TestCases.DEX3 import TOKEN_X, TOKEN_Y, TOKEN_OWNER, INIT_PAIR_IDS


@pytest.mark.dependency(scope='session', name="add_liquidity")
@pytest.mark.parametrize("contributor,nft_id, contribution, amplifier", [
    (TOKEN_OWNER, TOKEN_OWNER.nft_ids[0], {TOKEN_X: coin(1000), TOKEN_Y: coin(2100)}, 20000),
    (TOKEN_OWNER, TOKEN_OWNER.nft_ids[0], {TOKEN_X: coin(1000), PRV_ID: coin(2100)}, 20000),
])
def test_add_liquidity_first_time(contributor, nft_id, contribution, amplifier):
    contributor: Account
    Logging.INFO(f"""test_add_liquidity_no_trade with : {contributor}
        {json.dumps(contribution, indent=3)}""")
    pde_b4 = SUT().pde3_get_state()
    token_x, token_y = contribution.keys()
    try:
        top_up_amount = 2 * contribution[PRV_ID]
        COIN_MASTER.top_up_if_lower_than(contributor, top_up_amount, top_up_amount + coin(1))
    except KeyError:
        pass
    x_add_amount, y_add_amount = contribution[token_x], contribution[token_y]
    init_pair = PdeV3State.PoolPairData.make_up_a_pool([token_x, token_y], nft_id)
    return_amount = init_pair.predict_pool_when_add_liquidity(contribution, contributor.nft_ids[0], amplifier)
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
    pde_state = SUT().pde3_get_state()
    new_pool_pair = pde_state.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair.pair_data() == init_pair.pair_data()
    assert return_amount == {token_x: 0, token_y: 0}
    pp_id = new_pool_pair.get_pool_pair_id()
    INIT_PAIR_IDS.append(pp_id)
    INIT_PAIR_IDS.sort()

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
    pde_state2 = SUT().pde3_get_state()
    new_pool_pair2 = pde_state2.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair2.get_real_amount(token_x) == 2 * x_add_amount
    assert new_pool_pair2.get_real_amount(token_y) == 2 * y_add_amount
    pool_predict = new_pool_pair.clone()
    return_amount = pool_predict. \
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
    pytest.param(
        ACCOUNTS[1], ACCOUNTS[1].nft_ids[0], {TOKEN_X: coin(5000), TOKEN_Y: coin(30000)}, "INIT_PAIR_IDS[0]", 200000,
        marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
    pytest.param(
        ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], {TOKEN_X: coin(5000), TOKEN_Y: coin(30000)}, "INIT_PAIR_IDS[0]", 200000,
        marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
    pytest.param(
        ACCOUNTS[3], ACCOUNTS[3].nft_ids[0], {TOKEN_X: coin(5000), TOKEN_Y: coin(30000)}, "INIT_PAIR_IDS[0]", 200000,
        marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
])
def test_add_liquidity_no_trade_with_return(contributor, nft_id, contribution, pair_id, amplifier):
    if "INIT_PAIR_IDS" in pair_id:
        pair_id = eval(pair_id)
    pde_state_b4 = SUT().pde3_get_state()
    token_x, token_y = contribution.keys()
    if pair_id:
        pool_b4 = pde_state_b4.get_pool_pair(id=pair_id)
    else:
        pool_b4 = PdeV3State.PoolPairData.make_up_a_pool([token_x, token_y], nft_id)
    pair_id = pool_b4.get_pool_pair_id() if not pair_id else pair_id
    predict_pool = pool_b4.clone()
    amount_x = contribution[token_x]
    amount_y = contribution[token_y]
    return_amount = \
        predict_pool.predict_pool_when_add_liquidity({token_x: amount_x, token_y: amount_y}, nft_id, amplifier)
    contrib_id = f"{token_x[-6:]}-{token_y[-6:]}-{get_current_date_time()}"
    TOKEN_OWNER.top_up_if_lower_than(contributor, amount_x, amount_x, token_x)
    TOKEN_OWNER.top_up_if_lower_than(contributor, amount_y, amount_y, token_y)

    Logging.STEP(1, f"Contribute {token_x}")
    contributor.pde3_add_liquidity(token_x, amount_x, amplifier, contrib_id, nft_id, pair_id).get_transaction_by_hash()
    Logging.STEP(2, f"Contribute {token_y}")
    contributor.pde3_add_liquidity(token_y, amount_y, amplifier, contrib_id, nft_id, pair_id).get_transaction_by_hash()
    Logging.STEP(3, f"Verify pool")
    WAIT(3 * ChainConfig.BLOCK_TIME)
    pde_state = SUT().pde3_get_state()
    new_pool_pair = pde_state.get_pool_pair(id=pair_id)
    Logging.INFO(f"Real pool after contribution\n {new_pool_pair}")
    Logging.INFO(f"Predicted pool \n {predict_pool}")
    assert new_pool_pair == predict_pool


@pytest.mark.parametrize("contributor,nft_id, with_draw_percent, pair_id", [
    pytest.param(ACCOUNTS[3], ACCOUNTS[3].nft_ids[0], 0.1, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
    pytest.param(ACCOUNTS[2], ACCOUNTS[3].nft_ids[0], 1, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
    pytest.param(ACCOUNTS[1], ACCOUNTS[3].nft_ids[0], 1.1, "INIT_PAIR_IDS",
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')),
])
def test_withdraw_liquidity(contributor: Account, nft_id, with_draw_percent, pair_id):
    pair_id = INIT_PAIR_IDS[0] if pair_id == "INIT_PAIR_IDS" else pair_id
    pde_b4 = SUT().pde3_get_state()
    pool_b4 = pde_b4.get_pool_pair(id=pair_id)
    token_x, token_y = pool_b4.get_token_id()
    bal_x_b4 = contributor.get_balance(token_x)
    bal_y_b4 = contributor.get_balance(token_y)
    my_current_share = pde_b4.get_pool_pair(id=pair_id).get_share(nft_id).amount
    withdraw_amount = int(with_draw_percent * my_current_share)

    Logging.STEP(1, "Withdraw liquidity")
    tx = contributor.pde3_withdraw_liquidity(pair_id, withdraw_amount, nft_id)
    if with_draw_percent > 1:
        tx.expect_error("error shareAmount > current share amount")
        Logging.INFO("shareAmount > current share amount, tx is rejected, end test")
        return
    fee = tx.get_transaction_by_hash().get_fee()

    Logging.STEP(2, "Checking status")
    WAIT(3 * ChainConfig.BLOCK_TIME)
    status = SUT().dex_v3().get_withdraw_liquidity_status(tx.get_tx_id())

    Logging.STEP(3, "Wait for balance update")
    bal_x_af = contributor.wait_for_balance_change(token_x, from_balance=bal_x_b4)
    bal_y_af = contributor.wait_for_balance_change(token_y, from_balance=bal_y_b4)

    Logging.STEP(3, "Check pool")
    pool_predict = pool_b4.clone()
    return_amounts = pool_predict.predict_pool_after_withdraw_share(withdraw_amount, nft_id)
    pool_af = SUT().pde3_get_state().get_pool_pair(id=pair_id)
    assert status.get_status() == Status.DexV3.ShareWithdraw.SUCCESS
    assert return_amounts[token_x] == bal_x_af - bal_x_b4
    assert return_amounts[token_y] == bal_y_af - bal_y_b4
    assert pool_af == pool_predict
    if with_draw_percent == 1:
        assert pool_af.get_share(nft_id).amount == 0
