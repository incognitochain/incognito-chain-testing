import re

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import STEP, INFO, ERROR
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_x, amount_stake_under_1750, \
    amount_stake_over_1750, account_y, account_t
staking_flowv3 = False


@pytest.mark.parametrize('amount_prv_stake', [
    amount_stake_under_1750,
    amount_stake_over_1750
])
def test_stake_under_over_1750_prv(amount_prv_stake):
    COIN_MASTER.top_up_if_lower_than(account_y, amount_prv_stake, amount_prv_stake + 100)
    STEP(0, 'Get balance account before staking')
    balance_before_stake = account_y.get_balance()

    STEP(1, f"Send {amount_prv_stake} PRV to stake")
    stake_response = account_y.stake_and_reward_me(amount_prv_stake, auto_re_stake=False)

    STEP(2, "Verify that the transaction was rejected and PRV was not sent")
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'error invalid Stake Shard Amount',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake == account_y.get_balance(), "balance no return"


@pytest.mark.parametrize('staker1, staker2, validator', [
    (account_y, account_y, account_y),  # double stake
    (account_y, account_t, account_y),  # self stake then other stake me
    (account_x, account_y, account_t),  # 2 different acc, stake for the same validator
])
def test_stake_same_validator(staker1, staker2, validator):
    STEP(0, 'Check if validator is already staked')
    bbsd = SUT().get_beacon_best_state_detail_info()
    staking_state = bbsd.get_auto_staking_committees(validator)
    if staking_state is not None:
        pytest.skip(
            f'Validator_key: {validator.validator_key} already staked, this test must be run again with another account')

    STEP(1, 'Balance before test')
    COIN_MASTER.top_up_if_lower_than(staker1, coin(1750), coin(1850))
    COIN_MASTER.top_up_if_lower_than(staker2, coin(1750), coin(1850))
    balance_before_stake_first = staker1.get_balance()

    STEP(2, 'Stake the first time and check balance after staking')
    stake_response = staker1.stake(validator=validator, auto_re_stake=False).subscribe_transaction()
    stake_fee = stake_response.get_fee()
    WAIT(20)
    balance_after_stake_first = staker1.get_balance()
    assert balance_before_stake_first == balance_after_stake_first + stake_fee + coin(1750)

    STEP(3, 'Stake the second time: Verify that the transaction was rejected and PRV was not sent')
    balance_before_stake_second = staker2.get_balance()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.is_he_in_waiting_next_random(validator) is True:
        STEP(3.1, 'Check stake 2nd when acc in waiting for next random')
        tx = staker2.stake(validator)
        try:
            tx.expect_error()
            INFO('Cannot stake the second time')
            assert balance_before_stake_second == staker2.get_balance()
        except:
            WAIT(40)
            ERROR(f'Trx stake be created, tx_id: {tx.get_tx_id()}')
            res = tx.expect_no_error().get_transaction_by_hash(time_out=0)
            if res.get_block_height():
                fee = res.get_fee()
            else:
                INFO('Transaction is rejected')
                fee = 0
            ERROR(f'Trx stake the second time be created, tx_id: {tx.get_tx_id()}')
            INFO('And wait refund amount')
            WAIT(40)
            bal = staker2.get_balance()
            assert balance_before_stake_second == bal + fee
            balance_before_stake_second = bal

    STEP(3.2, 'Check stake 2nd when acc in shard pending')
    if staking_flowv3:
        validator.stk_wait_till_i_am_in_sync_pool()
        staker2.stake(validator).expect_error()
        assert balance_before_stake_second == staker2.get_balance()

    shard_pending, x = validator.stk_wait_till_i_am_in_shard_pending(sfv3=staking_flowv3)
    assert shard_pending is not False
    staker2.stake(validator).expect_error()
    assert balance_before_stake_second == staker2.get_balance()

    STEP(3.3, 'Check stake 2nd when acc in shard committee')
    epoch_plus_n = validator.stk_wait_till_i_am_committee()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(validator)
    assert staked_shard == shard_pending
    staker2.stake(validator=validator, auto_re_stake=False).expect_error('This pubkey may staked already')
    assert balance_before_stake_second == staker2.get_balance()

    STEP(4, "Wait for the stake to be swapped out")
    balance_before_swap_out = staker1.get_balance()
    epoch_x = validator.stk_wait_till_i_am_out_of_autostaking_list()

    STEP(5, "Calculate avg PRV reward per epoch")
    prv_reward = staker1.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(6, 'Wait for staking refund and verify staking refund')
    bal_after_stake_refund = staker1.wait_for_balance_change(from_balance=balance_before_swap_out,
                                                             least_change_amount=coin(1750))
    assert bal_after_stake_refund == balance_before_swap_out + ChainConfig.STK_AMOUNT

    STEP(7, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw = staker1.get_balance()
    prv_reward_amount = staker1.stk_get_reward_amount()
    withdraw_fee = staker1.stk_withdraw_reward_to_me().subscribe_transaction().get_fee()
    prv_bal_after_withdraw = staker1.wait_for_balance_change(from_balance=prv_bal_b4_withdraw)
    INFO(f'Expect reward amount to received: {prv_reward_amount}')
    assert prv_bal_b4_withdraw + prv_reward_amount - withdraw_fee == prv_bal_after_withdraw, \
        f'bal b4={prv_bal_b4_withdraw}, reward amount={prv_reward_amount}, withdraw fee={withdraw_fee} ' \
        f'bal after={prv_bal_after_withdraw}'
