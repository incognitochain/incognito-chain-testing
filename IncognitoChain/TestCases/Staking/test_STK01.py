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

from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.Staking import stake_account, block_per_epoch, token_holder_shard_1, \
    amount_token_send, amount_token_fee, token_holder_shard_0, staked_account


def setup_function():
    if stake_account.get_prv_balance() < coin(1750):
        COIN_MASTER.send_prv_to(stake_account, coin(1850) - stake_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()
        if stake_account.shard != COIN_MASTER.shard:
            stake_account.subscribe_cross_output_coin()


@pytest.mark.parametrize("the_stake,the_staked", [
    (stake_account, stake_account),  # self stake
    (stake_account, staked_account)  # stake other
])
def test_self_stake_n_stake_other_with_auto_stake_false(the_stake, the_staked):
    from IncognitoChain.TestCases.Staking import token_id
    INFO(f'Run test with token: {token_id}')
    STEP(1, 'Get epoch number')
    beacon_height = SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=True)
    epoch_number = SUT.full_node.system_rpc().help_get_current_epoch(refresh_cache=False)
    while beacon_height % block_per_epoch >= (block_per_epoch / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % block_per_epoch}')
        WAIT((block_per_epoch - (beacon_height % block_per_epoch)) * 10)
        epoch_number = SUT.full_node.system_rpc().help_get_current_epoch(refresh_cache=False)
        beacon_height = SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=True)

    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Stake and check balance after stake')
    bal_before_stake = the_stake.get_prv_balance()
    stake_response = the_stake.stake_someone_reward_him(the_staked, auto_re_stake=False)
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    assert the_stake.get_prv_balance_cache() == the_stake.get_prv_balance() + stake_fee + coin(1750)

    STEP(3, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
    # epoch_plus_1 = SUT.full_node.system_rpc().help_wait_till_epoch(epoch_number + 3, block_per_epoch * 10,
    #                                                                block_per_epoch * 20)
    epoch_plus_n = the_staked.wait_till_i_am_committee()
    staked_shard = the_staked.am_i_a_committee(refresh_cache=False)
    assert staked_shard is not False

    STEP(4, "Sending token")
    if staked_shard == 0:
        token_sender = token_holder_shard_0
        token_receiver = token_holder_shard_1
    else:
        token_sender = token_holder_shard_1
        token_receiver = token_holder_shard_0

    token_bal_before = token_receiver.get_token_balance(token_id)
    token_sender.send_token_to(token_receiver, token_id, amount_token_send, token_fee=amount_token_fee) \
        .subscribe_transaction()
    try:
        if token_sender.shard != token_receiver.shard:
            token_receiver.subscribe_cross_output_token()
    except WebSocketTimeoutException:
        pass
    assert token_bal_before + amount_token_send == token_receiver.get_token_balance(token_id)

    STEP(5, "Wait for the stake to be swapped out")
    epoch_x = the_staked.wait_till_i_am_swapped_out_of_committee()

    STEP(6.1, "Calculate avg PRV reward per epoch")
    prv_reward = the_staked.get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(6.2, "Reward token at epoch_plus_n")
    token_reward = the_staked.get_reward_amount(token_id)
    INFO(f'Token reward at epoch {epoch_x} = {token_reward}')

    STEP(7, 'Verify staking refund')
    assert bal_before_stake - stake_fee == the_stake.get_prv_balance()

    STEP(8.1, 'Withdraw PRV reward and verify balance')
    the_staked.get_prv_balance()
    prv_reward_amount = the_staked.get_reward_amount()
    the_staked.withdraw_reward_to_me().subscribe_transaction()
    try:
        the_staked.subscribe_cross_output_coin()
    except WebSocketTimeoutException:
        pass

    assert the_staked.get_prv_balance_cache() == the_staked.get_prv_balance() - prv_reward_amount

    STEP(8.2, 'Withdraw token reward and verify balance')
    token_bal_before = the_staked.get_token_balance(token_id)
    token_reward_amount = the_staked.get_reward_amount(token_id)
    the_staked.withdraw_reward_to_me(token_id)
    try:
        the_staked.subscribe_cross_output_token()
    except WebSocketTimeoutException:
        pass

    assert token_bal_before == the_staked.get_token_balance(token_id) - token_reward_amount
