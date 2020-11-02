import re

import pytest

from IncognitoChain.Configs import Constants
from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Staking import stake_account, amount_stake_under_1750, \
    amount_stake_over_1750


def setup_function():
    if stake_account.get_prv_balance() < coin(1750):
        COIN_MASTER.send_prv_to(stake_account, coin(1850) - stake_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()
        if stake_account.shard != COIN_MASTER.shard:
            stake_account.subscribe_cross_output_coin()


@pytest.mark.parametrize('amount_prv_stake', [
    amount_stake_under_1750,
    amount_stake_over_1750
])
def test_stake_under_over_1750_prv(amount_prv_stake):
    STEP(0, 'Get balance account before staking')
    balance_before_stake = stake_account.get_prv_balance()

    STEP(1, f"Send {amount_prv_stake} PRV to stake")
    stake_response = stake_account.stake_and_reward_me(amount_prv_stake, auto_re_stake=False)

    STEP(2, "Verify that the transaction was rejected and PRV was not sent")
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Reject not sansity tx transaction',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake == stake_account.get_prv_balance()


def test_stake_double():
    if stake_account.get_prv_balance() < coin(3600):
        COIN_MASTER.send_prv_to(stake_account, coin(3700) - stake_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()

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

    STEP(2, 'Stake the first time and check balance after staking')
    balance_before_stake_first = stake_account.get_prv_balance()
    stake_response = stake_account.stake_and_reward_me(auto_re_stake=False)
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    assert balance_before_stake_first == stake_account.get_prv_balance() + stake_fee + coin(1750)

    STEP(3, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
    epoch_plus_n = stake_account.stk_wait_till_i_am_committee()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(stake_account)
    assert staked_shard is not False

    STEP(4, 'Stake the second time')
    balance_before_stake_second = stake_account.get_prv_balance()
    stake_response = stake_account.stake_and_reward_me(auto_re_stake=False)
    print("stake_response = %s" % stake_response)

    STEP(5, 'Verify that the transaction was rejected and PRV was not sent')
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Double Spend With Current Blockchain',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake_second == stake_account.get_prv_balance()

    STEP(6, "Wait for the stake to be swapped out")
    epoch_x = stake_account.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(7, "Calculate avg PRV reward per epoch")
    prv_reward = stake_account.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(8, 'Wait for staking refund and verify staking refund')
    bal_after_stake_refund = stake_account.wait_for_balance_change()
    assert balance_before_stake_first - stake_fee == bal_after_stake_refund

    STEP(9, 'Withdraw PRV reward and verify balance')
    prv_bal_withdraw_reward = stake_account.get_prv_balance()
    prv_reward_amount = stake_account.stk_get_reward_amount()
    stake_account.stk_withdraw_reward_to_me().subscribe_transaction()
    prv_bal_after_withdraw_reward = stake_account.wait_for_balance_change(from_balance=prv_bal_withdraw_reward,
                                                                          timeout=180)
    INFO(f'Expect reward amount to received: {prv_reward_amount}')
    assert prv_bal_withdraw_reward == prv_bal_after_withdraw_reward - prv_reward_amount
