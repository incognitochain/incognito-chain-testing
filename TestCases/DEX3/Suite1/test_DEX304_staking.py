import pytest

from Configs import TokenIds
from Configs.Configs import ChainConfig
from Configs.Constants import PRV_ID, coin
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX3.Suite1 import TOKEN_Y, TOKEN_X, TOKEN_OWNER

COIN_MASTER.pde3_get_my_nft_ids()

last_created_nft = ""


@pytest.mark.parametrize("test, staker, nft, amount, token_id", [
    pytest.param("stake", COIN_MASTER, "new", 4120000000, PRV_ID),  # new user stake
    pytest.param("stake", COIN_MASTER, "reuse", 4120000000, PRV_ID),  # same user stake again
    pytest.param("stake", COIN_MASTER, COIN_MASTER.nft_ids[0], 4120000000, PRV_ID),
    pytest.param("stake", ACCOUNTS[0], ACCOUNTS[0].nft_ids[0], 4120000000, TokenIds.pDEX),
    pytest.param("stake", ACCOUNTS[0], ACCOUNTS[0].nft_ids[0], 4120000000, PRV_ID),

    pytest.param("unstake", COIN_MASTER, "reuse", 0.2, PRV_ID),
    pytest.param("unstake", COIN_MASTER, "reuse", 0.3, PRV_ID),
    pytest.param("unstake", ACCOUNTS[0], ACCOUNTS[0].nft_ids[0], 0.1, PRV_ID),
    pytest.param("unstake", ACCOUNTS[0], ACCOUNTS[0].nft_ids[0], 1.1, PRV_ID,
                 marks=pytest.mark.xfail(reason="unstakingAmount > current staker liquidity")),
])
def test_staking(test, staker: Account, nft, amount, token_id):
    global last_created_nft
    if nft == "new":
        nft = staker.pde3_mint_nft(force=True)
        last_created_nft = nft
    elif nft == "reuse":
        nft = last_created_nft

    COIN_MASTER.top_up_if_lower_than(staker, coin(20), coin(50), token_id)
    Logging.INFO(f"Get pde state before test ")
    pde_b4 = SUT().pde3_get_state()
    pde_predict = pde_b4.clone()
    bal_b4 = staker.get_balance(token_id)
    bal_prv_b4 = staker.get_balance()

    Logging.INFO(f"Do {test} token {token_id}")
    if test == "stake":
        tx = staker.pde3_stake(amount, token_id, nft)
    elif test == "unstake":
        my_liquidity = pde_b4.get_staking_pools(id=token_id).get_stakers(nft).get_liquidity()
        amount = int(amount * my_liquidity)
        tx = staker.pde3_unstake(amount, token_id, nft)
    else:
        raise ValueError(f" Invalid test {test} !!!")
    fee = tx.get_transaction_by_hash().get_fee()
    WAIT(ChainConfig.BLOCK_TIME * 4)
    Logging.INFO(f"calculate pde state after {test}")
    if test == "stake":
        pde_predict.predict_state_after_stake(amount, token_id, nft)
    elif test == "unstake":
        pde_predict.predict_state_after_stake(-amount, token_id, nft)
    pde_af = SUT().pde3_get_state()
    bal_af = staker.get_balance(token_id)

    assert pde_af == pde_predict
    if test == "stake":
        if token_id == PRV_ID:
            assert bal_b4 - amount - fee == bal_af
        else:
            assert bal_prv_b4 - fee == staker.get_balance()
            assert bal_b4 - amount == bal_af
    elif test == "unstake":
        receive_amount = min(amount, my_liquidity)
        if token_id == PRV_ID:
            assert bal_b4 + receive_amount - fee == bal_af
        else:
            assert bal_prv_b4 - fee == staker.get_balance()
            assert bal_b4 + amount == bal_af


def test_staking_fee():
    pde = SUT().pde3_get_state()
    pde_config = pde.get_pde_params()
    pde_config.get_staking_reward_token()
    new_config = pde_config.add_staking_reward_token(TOKEN_Y).get_configs()
    COIN_MASTER.pde3_modify_param(new_config).get_transaction_by_hash()
    WAIT(ChainConfig.BLOCK_TIME * 3)

    pde_predict = SUT().pde3_get_state()
    trade_path = [pde_predict.get_pool_pair(tokens=[TOKEN_X, TOKEN_Y])[0].get_pool_pair_id()]
    trading_fee = coin(10)
    trade_amount = 100000
    trade_tx = TOKEN_OWNER.pde3_trade(TOKEN_Y, TOKEN_X, trade_amount, 1, trade_path, trading_fee, False)
    trade_tx.get_transaction_by_hash()
    WAIT(ChainConfig.BLOCK_TIME * 4)
    pde_af = SUT().pde3_get_state()
    pde_predict.predict_staking_pool_reward(TOKEN_Y, trading_fee)
    assert pde_af == pde_predict
