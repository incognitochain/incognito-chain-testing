import pytest

from Helpers import Logging
from Helpers.Time import get_current_date_time
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
    x_add_mount = 1000000000000
    y_add_mount = 2100000000000
    contribute_id = f"{contributor.private_key[-6:]}-{get_current_date_time()}"
    Logging.STEP(0, "Create new nft id")
    contributor.pde3_mint_nft()
    Logging.STEP(1, f"Add token X, amount {x_add_mount}")
    tx0 = contributor.pde3_add_liquidity(token_x, x_add_mount, amplifier, contributor.nft_ids[0], contribute_id)
    tx0.get_transaction_by_hash()
    Logging.STEP(2, f"Add token Y, amount {y_add_mount}")
    tx1 = contributor.pde3_add_liquidity(token_y, y_add_mount, amplifier, contributor.nft_ids[0], contribute_id)
    tx1.get_transaction_by_hash()
    Logging.STEP(3, f"Verify pool")
    pde_state = SUT().get_pde3_state()
    new_pool_pair = pde_state.get_pool_pair(tokens=[token_x, token_y])
    assert new_pool_pair[0].get_real_amount(token_x) == x_add_mount
    assert new_pool_pair[0].get_real_amount(token_y) == y_add_mount
    pool_x0 = x_add_mount
    pool_y0 = y_add_mount


@pytest.mark.dependency(depends=["test_add_liquidity_first_time"])
@pytest.mark.parametrize("contributor, token_x, token_y, amplifier", [
    (token_owner, token_X, token_Y, 200),
])
def test_add_liquidity_no_trade_with_return(contributor, token_x, token_y, amplifier):
    pass
