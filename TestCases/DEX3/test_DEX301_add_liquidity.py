import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers import Logging
from Helpers.Time import get_current_date_time, WAIT
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import SUT
from TestCases.DEX3 import token_X, token_Y, token_owner


@pytest.mark.dependency()
@pytest.mark.parametrize("contributor, token_x, token_y, amplifier", [
    (token_owner, token_X, token_Y, 20000),
])
def test_add_liquidity_first_time(contributor, token_x, token_y, amplifier):
    contributor: Account
    Logging.INFO(f"""test_add_liquidity_no_trade with : {contributor}
        token X: {token_x}
        token Y: {token_y}""")
    x_add_mount = coin(1000)
    y_add_mount = coin(2100)
    pde_b4 = SUT().get_pde3_state()
    contribute_id = f"{contributor.private_key[-6:]}-{get_current_date_time()}"
    bal_x_b4 = contributor.get_balance(token_x)
    bal_y_b4 = contributor.get_balance(token_y)

    Logging.STEP(1, f"Add token X, amount {x_add_mount}")
    tx0 = contributor.pde3_add_liquidity(token_x, x_add_mount, amplifier, contribute_id)
    tx0.get_transaction_by_hash()
    Logging.STEP(2, f"Add token Y, amount {y_add_mount}")
    tx1 = contributor.pde3_add_liquidity(token_y, y_add_mount, amplifier, contribute_id)
    tx1.get_transaction_by_hash()
    Logging.STEP(3, f"Verify pool")
    WAIT(3 * ChainConfig.BLOCK_TIME)
    pde_state = SUT().get_pde3_state()
    new_pool_pair = pde_state.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair.get_real_amount(token_x) == x_add_mount
    assert new_pool_pair.get_real_amount(token_y) == y_add_mount
    pp_id = new_pool_pair.get_pool_pair_id()

    bal_x_af = contributor.get_balance(token_x)
    bal_y_af = contributor.get_balance(token_y)
    assert bal_x_b4 - x_add_mount == bal_x_af
    assert bal_y_b4 - y_add_mount == bal_y_af
    pool_x0 = x_add_mount
    pool_y0 = y_add_mount

    contribute_id = f"{contributor.private_key[-6:]}-{get_current_date_time()}"
    tx0 = contributor.pde3_add_liquidity(token_x, x_add_mount, amplifier, contribute_id,
                                         pool_pair_id=pp_id).get_transaction_by_hash()
    tx1 = contributor.pde3_add_liquidity(token_y, y_add_mount, amplifier, contribute_id,
                                         pool_pair_id=pp_id).get_transaction_by_hash()
    WAIT(120)
    pde_state2 = SUT().get_pde3_state()
    new_pool_pair2 = pde_state2.get_pool_pair(tokens=[token_x, token_y])[0]
    assert new_pool_pair2.get_real_amount(token_x) == 2 * x_add_mount
    assert new_pool_pair2.get_real_amount(token_y) == 2 * y_add_mount
    pool_predict, return_amount = new_pool_pair. \
        predict_pool_when_add_liquidity({token_x: x_add_mount, token_y: y_add_mount}, contributor.nft_ids[0])
    bal_x_af2 = contributor.get_balance(token_x)
    bal_y_af2 = contributor.get_balance(token_y)
    assert bal_x_af - x_add_mount == bal_x_af2
    assert bal_y_af - y_add_mount == bal_y_af2
    print(new_pool_pair2)
    print(pool_predict)
    assert new_pool_pair2 == pool_predict

    @pytest.mark.dependency(depends=["test_add_liquidity_first_time"])
    @pytest.mark.parametrize("contributor,nft_id, token_x, token_y, pair_id, amplifier", [
        (token_owner, token_owner.nft_ids[0], token_X, token_Y, "", 200),
    ])
    def test_add_liquidity_no_trade_with_return(contributor, nft_id, token_x, token_y, pair_id, amplifier):
        # todo: continue here, not yet complete
        pde_state_b4 = SUT().get_pde3_state()
        pool_b4_add = pde_state_b4.get_pool_pair(tokens=[token_x, token_y])
        pool_b4 = pde_state_b4.get_pool_pair(tokens=[token_x, token_y], nft=nft_id)[0]
        share_b4 = pool_b4.get_share(by_nft_id=nft_id)
        pair_id = pool_b4.get_pool_pair_id() if not pair_id else pair_id
        amount_x = coin(5000)
        amount_y = coin(30000)
        contrib_id = f"{token_x[-6:]}-{token_y[-6:]}-{get_current_date_time()}"
        Logging.STEP(1, f"Contribute {token_x}")
        contributor.pde3_add_liquidity(token_x, amount_x, amplifier, nft_id, contrib_id, pair_id)
        Logging.STEP(2, f"Contribute {token_y}")
        contributor.pde3_add_liquidity(token_y, amount_y, amplifier, nft_id, contrib_id, pair_id)
        Logging.STEP(3, f"Verify pool")

    def test_withdraw_liquidity():
        pass
