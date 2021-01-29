import re

import pytest

from Configs import Constants
from Configs.Constants import coin
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_x, amount_stake_under_1750, \
    amount_stake_over_1750, account_y, account_t


def setup_function():
    if account_y.get_prv_balance() < coin(1750):
        COIN_MASTER.send_prv_to(account_y, coin(1850) - account_y.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()
        if account_y.shard != COIN_MASTER.shard:
            account_y.subscribe_cross_output_coin()


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
    assert balance_before_stake == account_y.get_prv_balance()


@pytest.mark.parametrize('staker1, validator1, staker2, validator2', [
    (account_y, account_y, account_y, account_y),  # double stake
    (account_y, account_y, account_t, account_y),  # self stake then other stake me
    (account_x, account_t, account_y, account_t),  # 2 different acc, stake for the same validator
])
def test_stake_same_validator(staker1, validator1, staker2, validator2):
    STEP(1, 'Get epoch number')
    beacon_state = SUT().get_beacon_best_state_info()
    beacon_height = beacon_state.get_beacon_height()
    epoch_number = beacon_state.get_epoch()
    while beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH >= (Constants.ChainConfig.BLOCK_PER_EPOCH / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH}')
        WAIT((Constants.ChainConfig.BLOCK_PER_EPOCH - (beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH)) * 10)
        beacon_state = SUT().get_beacon_best_state_info()
        beacon_height = beacon_state.get_beacon_height()
        epoch_number = beacon_state.get_epoch()
    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Check if validator is already staked')
    bbsd = SUT().get_beacon_best_state_detail_info()
    staking_state = bbsd.get_auto_staking_committees(validator1)
    if staking_state is None:
        STEP(2.1, 'Stake the first time and check balance after staking')
        COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1751), staker1)
        balance_before_stake_first = validator1.get_prv_balance()
        stake_response = validator1.stake_and_reward_me(auto_re_stake=False).subscribe_transaction()
        stake_fee = stake_response.get_fee()
        assert balance_before_stake_first == validator1.get_prv_balance() + stake_fee + coin(1750)

        STEP(2.2, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
        epoch_plus_n = validator1.stk_wait_till_i_am_committee()
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        staked_shard = beacon_bsd.is_he_a_committee(validator1)
        assert staked_shard is not False
    else:
        INFO('Staker already staked, proceed to next step')

    STEP(3, 'Stake the second time')
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1751), staker2)
    balance_before_stake_second = staker2.get_prv_balance()
    stake_response = staker2.stake(validator=validator2, auto_re_stake=False)
    print("stake_response = %s" % stake_response)

    STEP(4, 'Verify that the transaction was rejected and PRV was not sent')
    stake_response.expect_error('Double Spend With Current Blockchain')
    assert balance_before_stake_second == staker2.get_prv_balance()

    STEP(5, "Wait for the stake to be swapped out")
    epoch_x = validator2.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(6, "Calculate avg PRV reward per epoch")
    prv_reward = validator1.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(7, 'Wait for staking refund and verify staking refund')
    bal_after_stake_refund = validator1.wait_for_balance_change(from_balance=balance_before_stake_second)
    assert balance_before_stake_first - stake_fee == bal_after_stake_refund

    STEP(8, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw = validator1.get_prv_balance()
    prv_reward_amount = validator1.stk_get_reward_amount()
    withdraw_fee = validator1.stk_withdraw_reward_to_me().subscribe_transaction().get_fee()
    prv_bal_after_withdraw = validator1.wait_for_balance_change(from_balance=prv_bal_b4_withdraw,
                                                                timeout=180)
    INFO(f'Expect reward amount to received: {prv_reward_amount}')
    assert prv_bal_b4_withdraw + prv_reward_amount - withdraw_fee == prv_bal_after_withdraw, \
        f'bal b4={prv_bal_b4_withdraw}, reward amount={prv_reward_amount}, withdraw fee={withdraw_fee} ' \
        f'bal after={prv_bal_after_withdraw}'
