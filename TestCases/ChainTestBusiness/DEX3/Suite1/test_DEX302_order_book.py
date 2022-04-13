import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import Status, PRV_ID
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS, SUT
from TestCases.ChainTestBusiness.DEX3.Suite1 import TOKEN_X, TOKEN_Y, INIT_PAIR_IDS

test_pool = '978ed7a54fea614c7dd65eac6abcc3520b5128a9ee1f6ff19d5d9bb382979357-' \
            'c5c896f9ae266fca6c62b5e9392d56b61dcf5263cd932664de9359f8fd26d679-' \
            '2fea8cdf9cc7aab97e1c15daf7b3a4a01b1c5a63b33c8494184f6a08f9e9a624'


@pytest.mark.dependency()
@pytest.mark.parametrize("user, nft_id, pair_id, token_sell, token_buy, sell_amount, min_acceptable", [
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[1]", TOKEN_X, TOKEN_Y, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[1]", TOKEN_Y, TOKEN_X, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[1]", TOKEN_Y, TOKEN_X, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[1]", TOKEN_X, TOKEN_Y, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[0]", TOKEN_X, PRV_ID, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[0]", PRV_ID, TOKEN_X, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[0]", PRV_ID, TOKEN_X, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),
    pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "INIT_PAIR_IDS[0]", TOKEN_X, PRV_ID, 10000, 10000,
                 marks=pytest.mark.dependency(depends=['add_liquidity'], scope='session')
                 ),

    # pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], test_pool, TOKEN_X, TOKEN_Y, 10000, 10000),
    # pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], test_pool, TOKEN_Y, TOKEN_X, 10000, 10000),
    # pytest.param(ACCOUNTS[2], ACCOUNTS[2].nft_ids[0], "non-exist pool", TOKEN_X, TOKEN_Y, 10000, 10000),
])
def test_add_order(user: Account, nft_id, pair_id, token_sell, token_buy, sell_amount, min_acceptable):
    if "INIT_PAIR_IDS" in pair_id:
        print(INIT_PAIR_IDS)
        pair_id = eval(pair_id)

    pde_b4 = SUT().pde3_get_state()
    pde_param = pde_b4.get_pde_params()
    sum_my_order = sum([count for count in [len(orders) for pp, orders in pde_b4.get_order(nft_id=nft_id).items()]])
    pool_b4 = pde_b4.get_pool_pair(id=pair_id)
    bal_sell_b4 = user.get_balance(token_sell)
    bal_prv_b4 = user.get_balance()

    Logging.STEP(1, "Add order")
    add_tx = user.pde3_add_order(token_sell, token_buy, pair_id, sell_amount, min_acceptable, nft_id)
    tx_fee = add_tx.get_transaction_by_hash().get_fee()

    Logging.STEP(2, "Check order status")
    WAIT(ChainConfig.BLOCK_TIME * 3)
    stat = SUT().dex_v3().get_add_order_status(add_tx.get_tx_id())
    if sum_my_order == pde_param.get_max_order_per_nft():
        Logging.INFO(f"Order limit is reached, refund")
        assert stat.get_status() == Status.DexV3.AddOrder.REFUND
        fee = tx_fee if token_sell == PRV_ID else 0
        assert bal_sell_b4 - fee == user.wait_for_balance_change(token_sell, user.get_balance(token_sell))
        return
    if pool_b4:  # pool exist
        Logging.INFO("Pool exist, order should be accepted")
        assert stat.get_status() == Status.DexV3.AddOrder.SUCCESS
        order_id = stat.get_order_id()
        pde = SUT().pde3_get_state()
        pool = pde.get_pool_pair(id=pair_id)
        order = pool.get_order_books(id=order_id)
        Logging.STEP(3, "Verify order")
        if token_sell == PRV_ID:
            assert bal_sell_b4 - sell_amount - tx_fee == user.get_balance(token_sell)
        else:
            assert bal_sell_b4 - sell_amount == user.get_balance(token_sell)
            assert bal_prv_b4 - tx_fee == user.get_balance()

        assert order.get_balance_token_sell() == sell_amount
        assert order.get_rate_token_buy() == min_acceptable
        assert order.is_un_touched()
        assert order.is_valid()
    else:  # pool not exist
        Logging.INFO("Pool not exist, refund")
        assert stat.get_status() == Status.DexV3.AddOrder.REFUND
        assert bal_sell_b4 == user.wait_for_balance_change(token_sell, user.get_balance(token_sell))


@pytest.mark.parametrize("user, nft_id, amount_percent", [
    pytest.param(ACCOUNTS[2], "my nft", 0.1,
                 marks=pytest.mark.dependency(depends=['test_add_order'])
                 ),
    pytest.param(ACCOUNTS[2], "my nft", 1.1,
                 marks=pytest.mark.dependency(depends=['test_add_order'])
                 ),
    pytest.param(ACCOUNTS[2], "my nft", 1,
                 marks=pytest.mark.dependency(depends=['test_add_order'])
                 ),
])
def test_withdraw_un_traded_order(user: Account, nft_id, amount_percent, ):
    pde_b4 = SUT().pde3_get_state()
    if nft_id == "my nft":
        nft_to_find = user.nft_ids
    else:
        nft_to_find = [nft_id]
    my_orders = {}
    for nft in nft_to_find:
        my_orders = pde_b4.get_order(nft=nft)
        if my_orders:
            break
    if not my_orders:
        Logging.WARNING(f"NO order found which belong to NFT {nft_to_find}, skip test")
        pytest.skip(f"NO order found which belong to NFT {nft_to_find}")
    pool, orders = my_orders.popitem()
    amount_withdraw = int(orders[0].get_balance_token_sell() * amount_percent)
    token_sell = pool.get_token_sell_of_order(orders[0])
    bal_sel_b4 = user.get_balance(token_sell)
    token_buy = pool.get_token_buy_of_order(orders[0])
    bal_buy_b4 = user.get_balance(token_buy)
    Logging.INFO(f"""
        {pool}
        {orders[0]}
        token sell/buy: {token_sell} - {token_buy}
    """)
    Logging.STEP(1, "Issue withdraw order request")
    tx_withdraw = user.pde3_withdraw_order(pool, orders[0], user.nft_ids[0], token_sell, amount_withdraw)
    assert tx_withdraw.get_transaction_by_hash().is_confirmed()

    Logging.STEP(2, "Checking withdraw status")
    WAIT(ChainConfig.BLOCK_TIME * 5)
    status_info = SUT().dex_v3().get_withdraw_order_status(tx_withdraw.get_tx_id())
    assert status_info.get_status() == Status.DexV3.WithdrawOrder.SUCCESS
    receive_amount = status_info.get_amount()
    Logging.STEP(3, "Withdraw success. Verify balance")
    bal_sel_af = user.get_balance(token_sell)
    bal_buy_af = user.get_balance(token_buy)
    Logging.INFO(f"""
        bal buy b4|af: {bal_buy_b4}-{bal_buy_af}
        bal sel b4|af: {bal_sel_b4}-{bal_sel_af}
    """)
    assert bal_buy_af == bal_buy_b4
    assert bal_sel_af == bal_sel_b4 + receive_amount
    assert receive_amount == amount_withdraw if amount_percent <= 1 else receive_amount < amount_withdraw


def test_withdraw_half_traded_order():
    pytest.skip("TO BE DONE LATER")  # todo
