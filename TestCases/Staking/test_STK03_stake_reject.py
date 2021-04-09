import re

import pytest

from Configs.Constants import coin
from Helpers.Logging import STEP, INFO
from Helpers.TestHelper import ChainHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_x, amount_stake_under_1750, \
    amount_stake_over_1750, account_y, account_t


@pytest.mark.parametrize('amount_prv_stake', [
    amount_stake_under_1750,
    amount_stake_over_1750
])
def test_stake_under_over_1750_prv(amount_prv_stake):
    STEP(0, 'Get balance account before staking')
    balance_before_stake = account_y.get_prv_balance()

    STEP(1, f"Send {amount_prv_stake} PRV to stake")
    stake_response = account_y.stake_and_reward_me(amount_prv_stake, auto_re_stake=False)

    STEP(2, "Verify that the transaction was rejected and PRV was not sent")
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Reject not sansity tx transaction',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake == account_y.get_prv_balance(), "balance no return"


@pytest.mark.parametrize('staker1, staker2, validator', [
    (account_y, account_y, account_y),  # double stake
    (account_y, account_t, account_y),  # self stake then other stake me
    (account_x, account_y, account_t),  # 2 different acc, stake for the same validator
])
def test_stake_same_validator(staker1, staker2, validator):
    # top up use dictionary of receivers, if staker1=staker2 then it will top up one time only,
    # hence using 2 top up as below instead of top_up_if_lower_than([staker1,staker2], coin(1750), coin(1850))
    COIN_MASTER.top_up_if_lower_than(staker1, coin(1750), coin(1850))
    COIN_MASTER.top_up_if_lower_than(staker2, coin(1750), coin(1850))

    STEP(1, 'Wait and stake at the first block of epoch')
    epoch_number, beacon_height = ChainHelper.wait_till_next_epoch(1, block_of_epoch=1)
    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Check if validator is already staked')
    bbsd = SUT().get_beacon_best_state_detail_info()
    staking_state = bbsd.get_auto_staking_committees(validator)
    if staking_state is None:
        STEP(2.1, 'Stake the first time and check balance after staking')
        if staker1 == staker2:
            topup_amount = coin(1750.5) * 2
        else:
            topup_amount = coin(1751)

        COIN_MASTER.top_up_if_lower_than(staker1, topup_amount, topup_amount)

        balance_before_stake_first = staker1.get_prv_balance()
        stake_response = staker1.stake(validator=validator, auto_re_stake=False).subscribe_transaction()
        stake_fee = stake_response.get_fee()
        balance_after_stake_first = staker1.get_prv_balance()
        assert balance_before_stake_first == balance_after_stake_first + stake_fee + coin(1750)

        STEP(2.2, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
        epoch_plus_n = validator.stk_wait_till_i_am_committee()
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        staked_shard = beacon_bsd.is_he_a_committee(validator)
        assert staked_shard is not False
    else:
        assert False, 'Staker already staked, this test must be run again with another account'

    STEP(3, 'Stake the second time')
    balance_before_stake_second = staker2.get_prv_balance()
    stake_response = staker2.stake(validator=validator, auto_re_stake=False)
    print("stake_response = %s" % stake_response)

    STEP(4, 'Verify that the transaction was rejected and PRV was not sent')
    stake_response.expect_error('Double Spend With Current Blockchain')
    assert balance_before_stake_second == staker2.get_prv_balance()

    STEP(5, "Wait for the stake to be swapped out")
    epoch_x = validator.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(6, "Calculate avg PRV reward per epoch")
    prv_reward = staker1.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(7, 'Wait for staking refund and verify staking refund')
    bal_after_stake_refund = staker1.wait_for_balance_change(from_balance=balance_after_stake_first,
                                                             least_change_amount=coin(1750))
    assert balance_before_stake_first - stake_fee == bal_after_stake_refund

    STEP(8, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw = staker1.get_prv_balance()
    prv_reward_amount = staker1.stk_get_reward_amount()
    withdraw_fee = staker1.stk_withdraw_reward_to_me().subscribe_transaction().get_fee()
    prv_bal_after_withdraw = staker1.wait_for_balance_change(from_balance=prv_bal_b4_withdraw, timeout=180)
    INFO(f'Expect reward amount to received: {prv_reward_amount}')
    assert prv_bal_b4_withdraw + prv_reward_amount - withdraw_fee == prv_bal_after_withdraw, \
        f'bal b4={prv_bal_b4_withdraw}, reward amount={prv_reward_amount}, withdraw fee={withdraw_fee} ' \
        f'bal after={prv_bal_after_withdraw}'
