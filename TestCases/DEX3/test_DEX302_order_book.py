import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import Status
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS, SUT
from TestCases.DEX3 import TOKEN_X

test_pool = "15a5d111eb5c03f259fafe140cdefbda9d7400cd2b3ab592b0476d979ef1f950-" \
            "3afb065181239a8c731c9d3e0f8933fb87830276050b55d1a17a55ac274884f8-" \
            "f09c48beb92f33df46bd214a9508f7d75c0422c05144b3e23f22dc488132fd3c"


@pytest.mark.parametrize("user, nft_id,, pair_id, token_sell, sell_amount, min_acceptable", [
    # (ACCOUNTS[2], ACCOUNTS[2].nft_ids[0],INIT_PAIR_IDS[0], TOKEN_X, 10000, 10000),
    # (ACCOUNTS[2], ACCOUNTS[2].nft_ids[0],INIT_PAIR_IDS[0], TOKEN_X, 10000, 10000),
    # (ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], test_pool, TOKEN_X, 10000, 10000),
    (ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "non-exist pool", TOKEN_X, 10000, 10000),
])
def test_add_order(user: Account, nft_id, pair_id, token_sell, sell_amount, min_acceptable):
    pde_b4 = SUT().get_pde3_state()
    pool_b4 = pde_b4.get_pool_pair(id=pair_id)

    bal_sell_b4 = user.get_balance(token_sell)

    Logging.STEP(1, "Add order")
    add_tx = user.pde3_add_order(nft_id, token_sell, pair_id, sell_amount, min_acceptable)
    tx_fee = add_tx.get_transaction_by_hash()
    bal_sell_af = user.get_balance(token_sell)
    assert bal_sell_b4 - sell_amount == bal_sell_af

    Logging.STEP(2, "Check order status")
    WAIT(ChainConfig.BLOCK_TIME * 3)
    stat = SUT().dex_v3().get_add_order_status(add_tx.get_tx_id())
    if pool_b4:  # pool exist
        Logging.INFO("Pool exist, order's accepted")
        assert stat.get_status() == Status.DexV3.Order.ACCEPT
        order_id = stat.get_order_id()
        bal_sell_af = user.get_balance(token_sell)
        pde = SUT().get_pde3_state()
        pool = pde.get_pool_pair(id=pair_id)
        order = pool.get_order_books(id=order_id)
        Logging.STEP(3, "Verify order")
        assert bal_sell_b4 - sell_amount == bal_sell_af
        assert order.get_balance_token_sell() == sell_amount
        assert order.get_rate_token_buy() == min_acceptable
        assert order.is_un_touched()
        assert order.is_valid()

        Logging.STEP(4, "Withdraw order")
        # todo
    else:  # pool not exist
        Logging.INFO("Pool not exist, refund")
        assert stat.get_status() == Status.DexV3.Order.REFUND
        assert bal_sell_b4 == user.wait_for_balance_change(token_sell, bal_sell_af)
