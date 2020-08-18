"""
This test cannot run independently as an automation test case
this test is only a support tool to help tester do the manual test faster and easier
"""
import copy

import pytest

from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Objects.IncognitoTestCase import SUT

beacon_init_reward = 11512801260920
shard_init_reward = [5916960630818, 5372514525094]


@pytest.mark.parametrize('from_epoch, num_of_epoch_to_test, shard_tx_fee_list ', [
    (3114, 3, [0, 0]),
])
def test_verify_reward_instruction(from_epoch, num_of_epoch_to_test, shard_tx_fee_list):
    beacon_rw_accu = beacon_init_reward
    shard_rw_accu = copy.deepcopy(shard_init_reward)
    while num_of_epoch_to_test > 0:
        INFO_HEADLINE(f' verify reward for epoch {from_epoch}')

        current_epoch = SUT.REQUEST_HANDLER.get_latest_beacon_block().get_epoch()
        if current_epoch <= from_epoch:
            SUT.REQUEST_HANDLER.help_wait_till_epoch(from_epoch + 1)

        calculated_reward = SUT.REQUEST_HANDLER. \
            cal_transaction_reward_from_beacon_block_info(from_epoch, shard_txs_fee_list=shard_tx_fee_list)
        instruction_reward = SUT.REQUEST_HANDLER.get_first_beacon_block_of_epoch(
            from_epoch + 1).get_transaction_reward_from_instruction()

        INFO(f"Calculated       : {calculated_reward}")
        INFO(f"From instruction : {instruction_reward}")
        # assert calculated_reward == instruction_reward
        num_of_epoch_to_test -= 1
        from_epoch += 1
        beacon_rw_accu += instruction_reward['beacon']
        try:
            shard_rw_accu[0] += instruction_reward['0']
        except:
            pass

        try:
            shard_rw_accu[1] += instruction_reward['1']
        except:
            pass

    print(f" beacon accu: {beacon_rw_accu}")
    print(f' shard accu: {shard_rw_accu}')


def todo_test_verify_reward_received_by_committee():
    # todo
    pass


def todo_test_verify_reward_received_by_beacon():
    # todo
    pass


def todo_test_verify_reward_received_by_dao():
    # todo
    pass
