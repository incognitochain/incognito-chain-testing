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

from IncognitoChain.Configs.Constants import ONE_COIN
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Staking import *
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6

amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = 100000 * ONE_COIN
token_contribute_amount = 10000 * ONE_COIN
prv_contribute_amount = 10000 * ONE_COIN


def setup_function():
    trx008.account_init = account_t
    trx008.setup_module()
    trx008.test_init_ptoken(prv_contribute_amount, token_contribute_amount, token_init_amount)
    INFO(trx008.custom_token_id)


def teardown_function():
    trx008.teardown_module()


def test_staking_01():
    breakpoint()
    token_id = trx008.custom_token_id
    STEP(1, "Stake 4 more with auto-stake")
    for acc in auto_stake_acc:
        acc.stake_and_reward_me()

    STEP(2, 'Get epoch number')
    epoch_number = SUT.full_node.system_rpc().help_get_current_epoch()
    block_height = SUT.full_node.system_rpc().help_get_beacon_height_in_best_state_detail(refresh_cache=False)
    INFO(f'epoch: {epoch_number}, block height: {block_height}')

    STEP(3, 'Stake and check balance after stake')
    stake.get_prv_balance()
    stake_response = stake.stake_and_reward_me(auto_re_stake=False)
    stake_response.subscribe_transaction()
    fee = stake_response.get_transaction_by_hash().get_fee()
    assert stake.get_prv_balance_cache() == stake.get_prv_balance() - fee
    assert not stake.am_i_a_committee()

    STEP(4, f'Wait until epoch {epoch_number} + 1 and Check if the stake become a committee')
    epoch_plus_1 = SUT.full_node.system_rpc().help_wait_till_epoch(epoch_number + 1)
    assert stake.am_i_a_committee() is not False

    STEP(5, "Sending token")
    account_b.get_token_balance(token_id)
    account_t.send_token_to(account_b, token_id, amount_token_send, token_fee=amount_token_fee).subscribe_transaction()
    account_b.subscribe_cross_output_token()
    assert account_b.get_token_balance_cache(token_id) + amount_token_send == account_b.get_token_balance(token_id)

    STEP(6, "Wait for the stake to be swapped out")
    wait_time_out = 300
    time_wait_start = time.perf_counter()
    while stake.am_i_a_committee() is not False:
        epoch_x = SUT.full_node.system_rpc().help_wait_till_epoch(epoch_plus_1 + 1)
        time_wait_now = time.perf_counter()
        if time_wait_now - time_wait_start > wait_time_out:
            raise TimeoutError('time out while waiting for the stake to be swapped out')

    STEP(7.1, "Calculate avg PRV reward per epoch")
    prv_reward = stake.get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_1)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(7.2, "Calculate avg token reward per epoch")
    token_reward = stake.get_reward_amount(token_id)
    avg_token_reward = token_reward / (epoch_x - epoch_plus_1)
    INFO(f'AVG token reward = {avg_token_reward}')

    STEP(8, 'Unstake and verify staking refund')
    stake.get_prv_balance()
    stake.un_stake_me()

    STEP(9, 'Withdraw reward and verify balance')
