"""
1. Precondition: chain committee, min 4, max 6, full committee (4 nodes each shard by default, stake 4 more node with
    auto-staking = true). Epoch = 40 beacon blocks. AccountT of shard-0, Create tokenT,
    contribute 10000PRV vs 10000tokenT, Considering this is the default env config.
2. get current epoch number (n). stake 1 more node (A) auto-staking = false. Verify accountA balance (-1750PRV - tx_fee)
3. at epoch (n+1). verify that node (A) become shard committee. Eg. committee of shard-0. From AccountT, send 10 tokenT
    to another account (B) in shard-1, use 1000000 tokenT as tx_fee. Verify (B) received tokenT.
4. keep watching shard commitee every epoch.
5. Assume at epoch (x), node (A) is swapped out, it was replaced by a node-with-auto-staking-true at step1.
    Note: x could be (n + 2,3,4..), because sometime, node-with-auto-staking-true is assigned to shard-1.
6. calculate average reward per epoch of node (A). reward_PRV / (x - n+1); reward_tokenT / (x - n+1)
7. verify that account balance +1750PRV (stake refund)
8. withdraw reward, verify that account(A) received reward PRV and tokenT
"""

import pytest
from websocket import WebSocketTimeoutException

from IncognitoChain.Configs.Constants import coin, ChainConfig
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Staking import stake_account, token_holder_shard_1, \
    amount_token_send, amount_token_fee, token_holder_shard_0, staked_account, token_id


@pytest.mark.parametrize("the_stake,the_staked,auto_re_stake", [
    (stake_account, stake_account, False),  # self stake
    (stake_account, staked_account, False)  # stake other
])
def test_staking(the_stake, the_staked, auto_re_stake):
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1850), the_stake)
    INFO(f'Run test with token: {token_id}')
    STEP(1, 'Get epoch number')
    blk_chain_info = SUT().get_block_chain_info()
    beacon_height = blk_chain_info.get_beacon_block().get_height()
    epoch_number = blk_chain_info.get_beacon_block().get_epoch()

    while beacon_height % ChainConfig.BLOCK_PER_EPOCH >= (ChainConfig.BLOCK_PER_EPOCH / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % ChainConfig.BLOCK_PER_EPOCH}')
        WAIT((ChainConfig.BLOCK_PER_EPOCH - (beacon_height % ChainConfig.BLOCK_PER_EPOCH)) * 10)
        blk_chain_info = SUT().get_block_chain_info()
        beacon_height = blk_chain_info.get_beacon_block().get_height()
        epoch_number = blk_chain_info.get_beacon_block().get_epoch()

    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Stake and check balance after stake')
    bal_before_stake = the_stake.get_prv_balance()
    stake_response = the_stake.stake_someone_reward_him(the_staked, auto_re_stake=auto_re_stake).expect_no_error()
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    assert the_stake.get_prv_balance_cache() == the_stake.get_prv_balance() + stake_fee + coin(1750)

    STEP(3, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
    epoch_plus_n = the_staked.stk_wait_till_i_am_committee()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(the_staked)
    assert staked_shard is not False

    STEP(4, "Sending token")
    # sending from staked shard, so that the committee will have ptoken reward
    if staked_shard == 0:
        token_sender = token_holder_shard_0
        token_receiver = token_holder_shard_1
    else:
        token_sender = token_holder_shard_1
        token_receiver = token_holder_shard_0

    token_bal_b4_withdraw_reward = token_receiver.get_token_balance(token_id)
    token_sender.send_token_to(token_receiver, token_id, amount_token_send, token_fee=amount_token_fee) \
        .expect_no_error().subscribe_transaction()
    try:
        if token_sender.shard != token_receiver.shard:
            token_receiver.subscribe_cross_output_token()
    except WebSocketTimeoutException:
        pass
    assert token_bal_b4_withdraw_reward + amount_token_send == token_receiver.get_token_balance(token_id)

    if not auto_re_stake:
        STEP(5, "Wait for the stake to be swapped out")
        epoch_x = the_staked.stk_wait_till_i_am_swapped_out_of_committee()
    else:
        STEP(5, 'Wait for next epoch')
        epoch_x = ChainHelper.wait_till_next_epoch()

    STEP(6.1, "Calculate avg PRV reward per epoch")
    prv_reward = the_staked.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(6.2, "Reward token at epoch_plus_n")
    token_reward = the_staked.stk_get_reward_amount(token_id)
    INFO(f'Token reward at epoch {epoch_x} = {token_reward}')

    if not auto_re_stake:
        STEP(7.1, 'Wait for staking refund in case auto-stake = false')
        bal_after_stake_refund = the_stake.wait_for_balance_change()
        STEP(7.2, 'Verify staking refund')
        assert bal_before_stake - stake_fee == bal_after_stake_refund
    else:
        STEP(7, 'Auto staking = True, not verify refund')

    STEP(8.1, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw_reward = the_staked.get_prv_balance()
    prv_reward_amount = the_staked.stk_get_reward_amount()
    the_staked.stk_withdraw_reward_to_me().subscribe_transaction()
    prv_bal_after_withdraw_reward = the_staked.wait_for_balance_change(from_balance=prv_bal_b4_withdraw_reward,
                                                                       timeout=180)
    INFO(f'Expect reward amount to received {prv_reward_amount}')
    assert prv_bal_b4_withdraw_reward == prv_bal_after_withdraw_reward - prv_reward_amount

    STEP(8.2, 'Withdraw token reward and verify balance')
    token_bal_b4_withdraw_reward = the_staked.get_token_balance(token_id)
    token_reward_amount = the_staked.stk_get_reward_amount(token_id)
    the_staked.stk_withdraw_reward_to_me(token_id).subscribe_transaction()
    token_bal_after_withdraw_reward = the_staked.wait_for_balance_change(token_id, timeout=180,
                                                                         from_balance=token_bal_b4_withdraw_reward)
    INFO(f'Expect reward amount to received {token_reward_amount}')
    assert token_bal_b4_withdraw_reward == token_bal_after_withdraw_reward - token_reward_amount
