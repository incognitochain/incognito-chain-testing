"""
1. Precondition: Create tokenT, contribute 10000PRV vs 10000tokenT, Considering this is the default env config.
2. get current epoch number (n). stake 1 more node (A) auto-staking = false. Verify accountA balance (-1750PRV - tx_fee)
3. at epoch (n+1). verify that node (A) become shard committee. Eg. committee of shard-0. From AccountT, send 10 tokenT
    to another account (B) in shard-1, use 1000000 tokenT as tx_fee. Verify (B) received tokenT.
4. keep watching shard committee every epoch.
5. Assume at epoch (x), node (A) is swapped out, it was replaced by a node-with-auto-staking-true at step1.
    Note: x could be (n + 2,3,4..), because sometime, node-with-auto-staking-true is assigned to shard-1.
6. calculate average reward per epoch of node (A). reward_PRV / (x - n+1); reward_tokenT / (x - n+1)
7. verify that account balance +1750PRV (stake refund)
8. withdraw reward, verify that account(A) received reward PRV and tokenT
"""

import pytest

from Configs.Constants import PRV_ID
from Helpers.Logging import ERROR
from Helpers.Logging import STEP
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from TestCases.Staking import *

slashing_v2 = True


@pytest.mark.parametrize("the_stake, validator, reward_receiver, auto_re_stake", [
    (account_y, account_y, account_y, False),  # self stake, self reward
    (account_x, account_x, account_y, False),  # self stake, reward other
    (account_y, account_t, account_y, False),  # stake other, self reward
    (account_x, account_u, account_u, False),  # stake other, reward him
    (account_x, account_a, account_t, False),  # stake other, reward another
    (account_y, account_y, account_y, True),  # self stake, self reward
    (account_x, account_x, account_y, True),  # self stake, reward other
    (account_y, account_t, account_y, True),  # stake other, self reward
    (account_x, account_u, account_u, True),  # stake other, reward him
    (account_x, account_a, account_t, True),  # stake other, reward another
])
def test_staking(the_stake, validator, reward_receiver, auto_re_stake):
    COIN_MASTER.top_up_if_lower_than(the_stake, coin(1750), coin(1850))
    from TestCases.Staking import token_id
    INFO(f'Run test with token: {token_id}')
    STEP(0.1, "Withdraw reward if there's any")
    reward_all_tok = reward_receiver.stk_get_reward_amount('*')
    for tok in [PRV_ID, token_id]:
        reward_receiver.stk_withdraw_reward_to_me(tok).subscribe_transaction()
        WAIT(2 * ChainConfig.BLOCK_TIME)
        assert reward_receiver.stk_get_reward_amount(tok) == 0
    STEP(0.2, "Check if there's coin v1 from last the unstake, then convert")
    for c in the_stake.list_unspent_coin():
        if c.get_version() == 1:
            the_stake.convert_token_to_v2().subscribe_transaction()
            break
    STEP(1, 'Stake and check balance after stake')
    bal_before_stake = the_stake.get_balance()
    bal_before_validator = validator.get_balance()
    bal_before_receiver = reward_receiver.get_balance()
    stake_response = the_stake.stake(validator, reward_receiver, auto_re_stake=auto_re_stake).expect_no_error()
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    assert bal_before_stake == the_stake.get_balance() + stake_fee + coin(1750)
    if the_stake != validator:
        assert bal_before_validator == validator.get_balance()
    if the_stake != reward_receiver:
        assert bal_before_receiver == reward_receiver.get_balance()
    WAIT(40)  # wait beacon confirm trx stake
    beacon_state_after_stake = SUT().get_beacon_best_state_detail_info()
    assert beacon_state_after_stake.get_auto_staking_committees(validator) is auto_re_stake

    STEP(2, f'Wait until the staker be assigned to shard pending')
    validator.stk_wait_till_i_am_in_shard_pending()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_in_shard_pending(validator)
    assert staked_shard is not False

    STEP(3, 'Stop auto staking')
    STEP(3.1, 'Verify stop auto staking success when auto_re_stake = True')
    epoch_plus_n = validator.stk_wait_till_i_am_committee()
    INFO('When validator in shard committee')
    if auto_re_stake:
        result_stop_auto_stake = the_stake.stk_stop_auto_stake_him(validator).subscribe_transaction()
        stop_auto_stake_fee = result_stop_auto_stake.get_fee()
        block_height = result_stop_auto_stake.get_block_height()
        shard_id = the_stake.calculate_shard_id() % ChainConfig.ACTIVE_SHARD
        beacon_height = SUT().get_shard_block_by_height(shard_id, block_height).get_beacon_height()
        INFO(f'Stop_auto_stake at beacon height: {beacon_height}')
        ChainHelper.wait_till_beacon_height(beacon_height + 5)
        auto_re_stake = SUT().get_beacon_best_state_detail_info().get_auto_staking_committees(validator)
        assert auto_re_stake is False
    else:
        stop_auto_stake_fee = 0

    STEP(3.2, 'Verify can not stop auto staking when auto_re_stake = False')
    # INFO('When validator in shard pending')
    tx = the_stake.stk_stop_auto_stake_him(validator)
    try:
        tx.expect_error()
        INFO('Can not stop auto staking when auto_re_stake = False ')
    except:
        ERROR(f'Trx stop auto staking be created, tx_id: {tx.get_tx_id()}')
        tx.subscribe_transaction()
    tx = the_stake.stk_un_stake_tx(validator)
    try:
        tx.expect_error()
        fee = 0
        INFO('Can not unstake when auto_re_stake = False ')
    except:
        WAIT(40)
        ERROR(f'Trx unstake be created, tx_id: {tx.get_tx_id()}')
        res = tx.get_transaction_by_hash(retry=False)
        if res.data:
            fee = res.get_fee()
        else:
            INFO('Transaction is rejected')
            fee = 0

    STEP(4, "Sending token")
    # sending from staked shard, so that the committee will have ptoken reward
    try:
        token_sender = list_acc_x_shard[staked_shard]
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {staked_shard}')

    token_bal_b4_withdraw_reward = token_receiver.get_balance(token_id)
    if ChainConfig.PRIVACY_VERSION == 1:
        token_sender.send_token_to(token_receiver, token_id, amount_token_send, token_fee=amount_token_fee) \
            .expect_no_error().subscribe_transaction()
    else:
        token_sender.send_token_to(token_receiver, token_id, amount_token_send, prv_fee=amount_token_fee) \
            .expect_no_error().subscribe_transaction()
    token_receiver.wait_for_balance_change(token_id, token_bal_b4_withdraw_reward)
    assert token_bal_b4_withdraw_reward + amount_token_send == token_receiver.get_balance(token_id)

    if not auto_re_stake:
        STEP(5, "Wait for the stake to be swapped out")
        epoch_x = validator.stk_wait_till_i_am_out_of_autostaking_list(timeout=ChainConfig.get_epoch_n_block_time(6))
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        assert beacon_bsd.get_auto_staking_committees(validator) is None
    else:
        STEP(5, 'Wait for next epoch')
        epoch_x, _ = ChainHelper.wait_till_next_epoch(1, block_of_epoch=5)

    STEP(6.1, "Calculate avg PRV reward per epoch")
    prv_reward = reward_receiver.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(6.2, "Reward token at epoch_plus_n")
    token_reward = reward_receiver.stk_get_reward_amount(token_id)
    INFO(f'Token reward at epoch {epoch_x} = {token_reward}')

    if not auto_re_stake:
        STEP(7.1, 'Wait for staking refund in case auto-stake = false')
        bal_after_stake_refund = the_stake.wait_for_balance_change()
        STEP(7.2, 'Verify staking refund')
        assert bal_before_stake - stake_fee - stop_auto_stake_fee - fee == bal_after_stake_refund, ERROR(
            f'{bal_before_stake - stake_fee - stop_auto_stake_fee - fee}')
    else:
        STEP(7, 'Auto staking = True, not verify refund')

    STEP(8.1, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw_reward = reward_receiver.get_balance()
    prv_reward_amount = reward_receiver.stk_get_reward_amount()
    if slashing_v2:
        slashing_committees = SUT().get_slashing_committee(epoch_x - 1)
        for committees in slashing_committees.values():
            for committee_key in committees:
                if validator.committee_public_k == committee_key:
                    assert prv_reward_amount == 0
                    return
    assert prv_reward_amount > 0, 'User has no PRV reward while expecting some'
    fee = reward_receiver.stk_withdraw_reward_to_me().subscribe_transaction().get_fee()
    prv_bal_after_withdraw_reward = reward_receiver.wait_for_balance_change(from_balance=prv_bal_b4_withdraw_reward)
    INFO(f'Expect reward amount to received {prv_reward_amount}')
    assert prv_bal_b4_withdraw_reward + prv_reward_amount - fee == prv_bal_after_withdraw_reward

    STEP(8.2, 'Withdraw token reward and verify balance')
    all_reward_b4 = reward_receiver.stk_get_reward_amount('*')
    token_bal_b4_withdraw_reward = reward_receiver.get_balance(token_id)
    prv_bal_b4_withdraw_reward = reward_receiver.get_balance()
    token_reward_amount = reward_receiver.stk_get_reward_amount(token_id)
    if ChainConfig.PRIVACY_VERSION == 1:
        INFO(f'Expect reward amount to received {token_reward_amount}')
        assert token_reward_amount > 0, 'User has no token reward while expecting some'
        reward_receiver.stk_withdraw_reward_to_me(token_id).subscribe_transaction()
        token_bal_after_withdraw_reward = reward_receiver. \
            wait_for_balance_change(token_id, from_balance=token_bal_b4_withdraw_reward)
        assert prv_bal_b4_withdraw_reward == reward_receiver.get_balance()
        assert token_bal_b4_withdraw_reward == token_bal_after_withdraw_reward - token_reward_amount

    elif ChainConfig.PRIVACY_VERSION == 2:
        assert token_reward_amount == 0, 'Privacy v2 should not have any token reward, PRV only'
        assert all_reward_b4 == reward_receiver.stk_get_reward_amount('*')
        reward_receiver.stk_withdraw_reward_to_me(token_id).expect_error()
