"""
This test cannot run independently as an automation test case
this test is only a support tool to help tester do the manual test faster and easier
REMEMBER: test data file must contains accounts of Beacons, Committee. In case DAO account is changes, must update
    IncognitoChain.Configs.Constants::DAO_PRIVATE_K accordingly
"""
import json

import pytest
from deepdiff import DeepDiff

from Configs.Configs import ChainConfig
from Helpers import TestHelper
from Helpers.Logging import INFO, INFO_HEADLINE, STEP
from Helpers.TestHelper import ChainHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import COMMITTEE_ACCOUNTS, BEACON_ACCOUNTS, SUT


@pytest.mark.parametrize('from_epoch, num_of_epoch_to_test, shard_tx_fee_list,DCZ', [
    # if from_epoch == 0: from_epoch = latest_epoch - num_of_epoch_to_test - 1
    (0, 10, [0] * ChainConfig.ACTIVE_SHARD, True),  # true for testing with DCZ
    (0, 10, [0] * ChainConfig.ACTIVE_SHARD, False),  # false for testing with fixed committee size

])
def test_verify_reward_instruction(from_epoch, num_of_epoch_to_test, shard_tx_fee_list, DCZ):
    current_epoch = SUT().help_get_current_epoch()
    if from_epoch == 0:
        from_epoch = max(1, current_epoch - num_of_epoch_to_test - 1)
    num_of_epoch_to_test = min(current_epoch - from_epoch, num_of_epoch_to_test)

    INFO(f'Verify reward instruction for {num_of_epoch_to_test} epoch, from epoch number {from_epoch}')

    while num_of_epoch_to_test > 0:
        INFO_HEADLINE(f' verify reward for epoch {from_epoch}')
        current_epoch = SUT().get_block_chain_info().get_beacon_block().get_epoch()
        if current_epoch <= from_epoch:  # if epoch is not yet to come, wait til it comes
            ChainHelper.wait_till_next_epoch(from_epoch + 1)

        calculated_reward = SUT(). \
            cal_transaction_reward_from_beacon_block_info(from_epoch, shard_txs_fee_list=shard_tx_fee_list, dcz=DCZ)
        instruction_reward = SUT().get_first_beacon_block_of_epoch(
            from_epoch + 1).get_transaction_reward_from_instruction()

        INFO(f"Calculated vs From instruction comparison")
        dd = DeepDiff(calculated_reward, instruction_reward)
        if dd:
            INFO(dd.pretty())
            assert False, dd.pretty()
        num_of_epoch_to_test -= 1
        from_epoch += 1


def test_verify_reward_received():
    # WARNING: for now, this test does not cover the case which committees are swapped in and out in the next epoch
    # NOTE: when run this test, tester observes that the rewards always come late 1 epoch,
    # so this test will take instruction reward of this epoch to compare with real received reward of the future epoch
    # BEST USE WITH account_sample
    STEP(0, ' prepare')
    BBD_b4 = SUT().get_beacon_best_state_detail_info()

    STEP(1, "Get current epoch")
    current_bb = SUT().get_latest_beacon_block()
    current_epoch = current_bb.get_epoch()
    INFO(f'Current epoch = {current_epoch}')

    STEP(2, "Wait till next epoch")
    next_epoch = ChainHelper.wait_till_next_epoch(current_epoch + 1)

    STEP(3.1, "Get Beacons earned reward before test")
    sum_beacons_earned_reward_b4 = 0
    for acc in BEACON_ACCOUNTS:
        sum_beacons_earned_reward_b4 += acc.stk_get_reward_amount()

    STEP(3.2, "Get Committees earned reward before test")
    committees_earned_reward_b4 = [0] * SUT().get_block_chain_info().get_num_of_shard()
    for acc in COMMITTEE_ACCOUNTS:
        shard = BBD_b4.is_he_a_committee(acc)
        committees_earned_reward_b4[shard] += acc.stk_get_reward_amount()

    STEP(3.3, "Get DAO earned reward before test")
    DAO_earned_reward_b4 = COIN_MASTER.stk_get_reward_amount()

    STEP(4.1, 'Get reward instruction from beacon')
    instruction_beacon_height = TestHelper.ChainHelper.cal_first_height_of_epoch(next_epoch)
    instruction_BB = SUT().get_latest_beacon_block(instruction_beacon_height)
    BB_reward_instruction = instruction_BB.get_transaction_reward_from_instruction()

    STEP(4.2, 'Wait for 1 more epoch')
    ChainHelper.wait_till_next_epoch(current_epoch + 2)
    STEP(5.1, "Get Beacons earned reward after 1 epoch")
    sum_beacons_earned_reward_af = 0
    for acc in BEACON_ACCOUNTS:
        sum_beacons_earned_reward_af += acc.stk_get_reward_amount()

    STEP(5.2, "Get Committees earned reward after 1 epoch")
    committees_earned_reward_af = [0] * len(committees_earned_reward_b4)
    for acc in COMMITTEE_ACCOUNTS:
        shard = BBD_b4.is_he_a_committee(acc)
        if shard is not False:
            committees_earned_reward_af[shard] += acc.stk_get_reward_amount()

    STEP(5.3, "Get DAO earned reward after 1 epoch")
    DAO_earned_reward_af = COIN_MASTER.stk_get_reward_amount()

    STEP(6, 'Compare actual earned reward in 1 epoch to instruction reward')
    real_dao_received = DAO_earned_reward_af - DAO_earned_reward_b4
    real_beacon_received = sum_beacons_earned_reward_af - sum_beacons_earned_reward_b4
    INFO(f"""
        DAO reward after - before              : {DAO_earned_reward_af} - {DAO_earned_reward_b4} = {real_dao_received}
        Sum beacons reward after - before      : {sum_beacons_earned_reward_af} - {sum_beacons_earned_reward_b4} = {real_beacon_received}
        Sum shards reward after  [shard 0 , 1] : {committees_earned_reward_af}
        Sum shards reward before [shard 0 , 1] : {committees_earned_reward_b4}
        From instruction                       : {json.dumps(BB_reward_instruction)} """)

    # breakpoint()
    assert BB_reward_instruction['DAO'] == real_dao_received
    assert BB_reward_instruction['beacon'] == real_beacon_received
    for shard_id in range(0, len(committees_earned_reward_af)):
        assert BB_reward_instruction[str(shard_id)] == committees_earned_reward_af[shard_id] - \
               committees_earned_reward_b4[shard_id]
