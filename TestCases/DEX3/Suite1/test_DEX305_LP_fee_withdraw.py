import pytest

from Configs.Constants import Status, PRV_ID
from Helpers import Logging
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.DEX3.Suite1 import TOKEN_OWNER


@pytest.mark.parametrize("pool_id, lp_provider, nft, receiver", [
    # ("INIT_PAIR_IDS[0]", TOKEN_OWNER, '7a349994463d60961c8649428aadbbb3405b873e9eb718a9042a464097a49d31', TOKEN_OWNER),
    ("INIT_PAIR_IDS[0]", TOKEN_OWNER, TOKEN_OWNER.nft_ids[0], TOKEN_OWNER),
    ("INIT_PAIR_IDS[1]", ACCOUNTS[1], ACCOUNTS[1].nft_ids[0], ACCOUNTS[1])
])
def test_withdraw_lp_fee(pool_id, lp_provider: Account, nft, receiver: Account):
    Logging.INFO()
    if "INIT_PAIR_IDS" in pool_id:
        from TestCases.DEX3.Suite1 import INIT_PAIR_IDS
        pool_id = eval(pool_id)
        print(INIT_PAIR_IDS)
        print(pool_id)

    all_my_reward_b4 = SUT().pde3_get_lp_value(pool_id, nft, extract_value='PoolReward')
    bal_b4 = {token_id: lp_provider.get_balance(token_id) for token_id in all_my_reward_b4.keys()}
    tx = lp_provider.pde3_withdraw_lp_fee(receiver, pool_id, nft)
    fee_tx = tx.get_transaction_by_hash().get_fee()
    SUT().wait_till_next_beacon_height(2)
    withdraw_status = SUT().dex_v3().get_withdrawal_lp_fee_status(tx.get_tx_id())
    receive_amount = withdraw_status.get_amounts()
    all_my_reward_af = SUT().pde3_get_lp_value(pool_id, nft, extract_value='PoolReward')
    bal_af = {token_id: lp_provider.wait_for_balance_change(token_id, from_balance=bal_b4[token_id]) for token_id in
              all_my_reward_b4.keys()}
    assert withdraw_status.get_status() == Status.DexV3.WithdrawLPFee.SUCCESS
    assert all_my_reward_af == {}
    assert receive_amount == all_my_reward_b4
    for token, amount in receive_amount.items():
        if token == PRV_ID:
            assert bal_af[token] - bal_b4[token] == amount - fee_tx
        else:
            assert bal_af[token] - bal_b4[token] == amount
