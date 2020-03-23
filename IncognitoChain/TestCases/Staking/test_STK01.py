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
import time

import pytest

from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Staking import *


@pytest.mark.parametrize("self_stake", [True, False])
def test_self_stake_n_stake_other(self_stake):
    if self_stake:
        stake = stake_account
        staked = stake_account
    else:
        stake = stake_account
        staked = staked_account

    STEP(1, "Verify environment, 6 node per shard")
    number_committee_shard_0 = SUT.full_node.system_rpc().help_count_committee_in_shard(0, refresh_cache=True)
    number_committee_shard_1 = SUT.full_node.system_rpc().help_count_committee_in_shard(1, refresh_cache=False)
    assert number_committee_shard_0 == 6
    assert number_committee_shard_1 == 6

    STEP(2, 'Get epoch number')
    beacon_height = SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=True)
    epoch_number = None
    while beacon_height >= 20:
        epoch_number = SUT.full_node.system_rpc().help_get_current_epoch(refresh_cache=False)
        WAIT((block_per_epoch - (beacon_height % block_per_epoch)) * 10)
        beacon_height = SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=True)

    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Stake and check balance after stake')
    stake.get_prv_balance()
    if self_stake:
        stake_response = stake.stake_and_reward_me(auto_re_stake=False)
    else:
        stake_response = stake.stake_someone_reward_him(staked, auto_re_stake=False)
    stake_response.subscribe_transaction()
    fee = stake_response.get_transaction_by_hash().get_fee()
    assert stake.get_prv_balance_cache() == stake.get_prv_balance() - fee - coin(1750)
    assert not stake_account.am_i_a_committee()

    STEP(3, f'Wait until epoch {epoch_number} + 1 and Check if the stake become a committee')
    epoch_plus_1 = SUT.full_node.system_rpc().help_wait_till_epoch(epoch_number + 1)
    assert staked.am_i_a_committee() is not False

    STEP(5, "Sending token")
    # token_id da contribute ung voi 10000 prv
    token_receiver.get_token_balance(token_id)
    token_sender.send_token_to(token_receiver, token_id, amount_token_send, token_fee=amount_token_fee) \
        .subscribe_transaction()
    token_receiver.subscribe_cross_output_token()
    assert token_receiver.get_token_balance_cache(token_id) + amount_token_send == token_receiver.get_token_balance(
        token_id)

    STEP(6, "Wait for the stake to be swapped out")
    wait_time_out = 400  # wait 1 epoch = 40 beacon block * 10 sec
    time_wait_start = time.perf_counter()
    epoch_x = None
    while staked.am_i_a_committee() is not False:
        epoch_x = SUT.full_node.system_rpc().help_wait_till_epoch(epoch_plus_1 + 1)
        time_wait_now = time.perf_counter()
        if time_wait_now - time_wait_start > wait_time_out:
            raise TimeoutError('time out while waiting for the stake to be swapped out')
    # print INFO staked is not a committee anymore, epoch: $epoch

    STEP(6.1, "Calculate avg PRV reward per epoch")
    prv_reward = staked.get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_1)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(7.2, "Reward token at epoch_plus_1")
    token_reward = staked.get_reward_amount(token_id)
    INFO(f'Token reward at epoch plus 1 = {token_reward}')

    STEP(7, 'Unstake and verify staking refund')
    stake.get_prv_balance()
    SUT.full_node.system_rpc().help_wait_till_epoch(epoch_x + 2)
    assert stake.get_prv_balance_cache() == stake.get_prv_balance() - coin(1750)

    STEP(8, 'Withdraw reward and verify balance')
    staked.get_token_balance(token_id)
    reward_amount = staked.get_reward_amount(token_id)
    staked.withdraw_reward_to_me(token_id).subscribe_transaction()
    staked.subscribe_cross_output_token()

    assert staked.get_token_balance_cache(token_id) == staked.get_token_balance(token_id) - reward_amount

    # withdraw prv va verify prv amount withdrawn
    # de khoi can clean environment, lan sau chay se thay reward prv = 0
