"""
This test cannot run independently as an automation test case
this test is only a support tool to help tester do the manual test faster and easier
REMEMBER: test data file must contains accounts of Beacons, Committee. In case DAO account is changes, must update
    IncognitoChain.Configs.Constants::DAO_PRIVATE_K accordingly
"""
import json

import pytest

from Configs.Constants import ChainConfig, coin
from Helpers.Logging import INFO, INFO_HEADLINE, STEP
from Helpers.TestHelper import ChainHelper, format_dict_side_by_side
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import COMMITTEE_ACCOUNTS, BEACON_ACCOUNTS, SUT, ACCOUNTS
from TestCases.Staking import token_holder_shard_0, token_holder_shard_1, amount_token_send, \
    amount_token_fee


@pytest.mark.parametrize('from_epoch, num_of_epoch_to_test, shard_tx_fee_list,dcz', [
    # if from_epoch == 0: from_epoch = latest_epoch - num_of_epoch_to_test - 1
    (0, 10, [0] * ChainConfig.ACTIVE_SHARD, True),  # true for testing with dcz
    # (0, 10, [0] * ChainConfig.ACTIVE_SHARD, False),  # false for testing with fixed committee size

])
def no_test_verify_reward_instruction(from_epoch, num_of_epoch_to_test, shard_tx_fee_list, dcz):
    """

    @param from_epoch:
    @param num_of_epoch_to_test:
    @param shard_tx_fee_list:
    @param dcz:
    @return:
    """
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
            cal_transaction_reward_from_beacon_block_info(from_epoch, shard_txs_fee_list=shard_tx_fee_list, dcz=dcz)
        instruction_reward = SUT().get_first_beacon_block_of_epoch(
            from_epoch + 1).get_transaction_reward_from_instruction()

        INFO(f"Calculated vs From instruction comparison :\n"
             f"{format_dict_side_by_side(calculated_reward, instruction_reward)} ")
        INFO(f'calculated_reward: {calculated_reward}')
        INFO(f'instruction_reward: {instruction_reward}')
        assert calculated_reward == instruction_reward
        num_of_epoch_to_test -= 1
        from_epoch += 1


@pytest.mark.parametrize('dcz', [
    True,  # true for testing with dcz
    False,
])
def test_verify_reward_received(dcz):
    # WARNING: for now, this test does not cover the case which committees are swapped in and out in the next epoch
    # NOTE: when run this test, tester observes that the rewards always come late 1 epoch,
    # so this test will take instruction reward of this epoch to compare with real received reward of the future epoch
    # BEST USE WITH account_sample
    from TestCases.Staking import token_id
    STEP(1, ' prepare')
    bbd_b4 = SUT().get_beacon_best_state_detail_info()
    current_epoch = bbd_b4.get_epoch()
    INFO(f'Current epoch = {current_epoch}')

    STEP(2, "Wait till next epoch")
    epoch_reward = ChainHelper.wait_till_next_epoch(current_epoch + 1, 10)

    INFO('Create transaction send PRV')
    fee_shard_0_tx1 = COIN_MASTER.send_prv_to(ACCOUNTS[3], coin(5), coin(1)).subscribe_transaction().get_fee()
    fee_shard_0_tx2 = COIN_MASTER.send_prv_to(ACCOUNTS[6], coin(5), 100).subscribe_transaction().get_fee()
    fee_shard_1_tx1 = ACCOUNTS.get_accounts_in_shard(1)[0].send_prv_to(ACCOUNTS[5], coin(1),
                                                                       1000).subscribe_transaction().get_fee()
    fee_shard_1_tx2 = ACCOUNTS.get_accounts_in_shard(1)[0].send_prv_to(ACCOUNTS[5], coin(1),
                                                                       100).subscribe_transaction().get_fee()
    fee_shard_0_tx3 = 0
    fee_shard_1_tx3 = 0
    sum_fee_shard_0_tok = 0
    sum_fee_shard_1_tok = 0

    INFO('Create transaction send ptoken')
    if ChainConfig.PRIVACY_VERSION == 1:
        fee_shard_0_tok_tx1 = token_holder_shard_0.send_token_to(token_holder_shard_1, token_id, amount_token_send,
                                                                 token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        fee_shard_0_tok_tx2 = token_holder_shard_0.send_token_to(token_holder_shard_1, token_id, amount_token_send,
                                                                 token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        sum_fee_shard_0_tok = fee_shard_0_tok_tx1 + fee_shard_0_tok_tx2
        fee_shard_1_tok_tx1 = token_holder_shard_1.send_token_to(token_holder_shard_0, token_id, amount_token_send,
                                                                 token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        fee_shard_1_tok_tx2 = token_holder_shard_1.send_token_to(token_holder_shard_0, token_id, amount_token_send,
                                                                 token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        sum_fee_shard_1_tok = fee_shard_1_tok_tx1 + fee_shard_1_tok_tx2
    else:
        fee_shard_0_tx3 = token_holder_shard_0.send_token_to(token_holder_shard_1, token_id, amount_token_send,
                                                             prv_fee=amount_token_fee) \
            .subscribe_transaction().get_privacy_custom_token_fee()
        fee_shard_1_tx3 = token_holder_shard_1.send_token_to(token_holder_shard_0, token_id, amount_token_send,
                                                             prv_fee=amount_token_fee) \
            .subscribe_transaction().get_privacy_custom_token_fee()

    sum_fee_prv_shard_0 = fee_shard_0_tx1 + fee_shard_0_tx2 + fee_shard_0_tx3
    sum_fee_prv_shard_1 = fee_shard_1_tx1 + fee_shard_1_tx2 + fee_shard_1_tx3
    shard_tx_fee_prv_list = [sum_fee_prv_shard_0, sum_fee_prv_shard_1]
    shard_tx_fee_tok_list = [sum_fee_shard_0_tok, sum_fee_shard_1_tok]

    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward)
    ChainHelper.wait_till_beacon_height(block_height_random)

    STEP(3.1, "Get Beacons earned reward before test")

    sum_beacons_earned_reward_b4_prv = 0
    sum_beacons_earned_reward_b4_ptoken = 0
    for acc in BEACON_ACCOUNTS:
        sum_beacons_earned_reward_b4_prv += acc.stk_get_reward_amount()
        sum_beacons_earned_reward_b4_ptoken += acc.stk_get_reward_amount(token_id)

    STEP(3.2, "Get Committees earned reward before test")
    committees_earned_reward_b4_prv = [0] * SUT().get_block_chain_info().get_num_of_shard()
    committees_earned_reward_b4_ptoken = [0] * SUT().get_block_chain_info().get_num_of_shard()
    for acc in COMMITTEE_ACCOUNTS:
        shard = bbd_b4.is_he_a_committee(acc)
        committees_earned_reward_b4_prv[shard] += acc.stk_get_reward_amount()
        committees_earned_reward_b4_ptoken[shard] += acc.stk_get_reward_amount(token_id)

    STEP(3.3, "Get DAO earned reward before test")
    dao_earned_reward_b4_prv = COIN_MASTER.stk_get_reward_amount()
    dao_earned_reward_b4_ptoken = COIN_MASTER.stk_get_reward_amount(token_id)

    ChainHelper.wait_till_next_epoch(epoch_reward + 1, 10)

    STEP(4.1, 'Get reward instruction from beacon')
    instruction_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch_reward + 1)
    instruction_bb = SUT().get_latest_beacon_block(instruction_beacon_height)
    bb_reward_instruction_prv = instruction_bb.get_transaction_reward_from_instruction()
    bb_reward_instruction_ptoken = instruction_bb.get_transaction_reward_from_instruction(token_id)
    calculated_reward_prv = SUT(). \
        cal_transaction_reward_from_beacon_block_info(epoch_reward, shard_txs_fee_list=shard_tx_fee_prv_list, dcz=dcz)
    calculated_reward_tok = SUT(). \
        cal_transaction_reward_from_beacon_block_info(epoch_reward, token=token_id,
                                                      shard_txs_fee_list=shard_tx_fee_tok_list, dcz=dcz)

    STEP(4.2, 'Wait receive reward')
    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward + 1)
    ChainHelper.wait_till_beacon_height(block_height_random)

    STEP(5.1, "Get Beacons earned reward after 1 epoch")
    sum_beacons_earned_reward_af_prv = 0
    sum_beacons_earned_reward_af_ptoken = 0
    for acc in BEACON_ACCOUNTS:
        sum_beacons_earned_reward_af_prv += acc.stk_get_reward_amount()
        sum_beacons_earned_reward_af_ptoken += acc.stk_get_reward_amount(token_id)

    STEP(5.2, "Get Committees earned reward after 1 epoch")
    committees_earned_reward_af_prv = [0] * len(committees_earned_reward_b4_prv)
    committees_earned_reward_af_ptoken = [0] * len(committees_earned_reward_b4_ptoken)
    for acc in COMMITTEE_ACCOUNTS:
        shard = bbd_b4.is_he_a_committee(acc)
        if shard is not False:
            committees_earned_reward_af_prv[shard] += acc.stk_get_reward_amount()
            committees_earned_reward_af_ptoken[shard] += acc.stk_get_reward_amount(token_id)

    real_shard_0_received_prv = committees_earned_reward_af_prv[0] - committees_earned_reward_b4_prv[0]
    real_shard_1_received_prv = committees_earned_reward_af_prv[1] - committees_earned_reward_b4_prv[1]
    real_shard_0_received_ptoken = committees_earned_reward_af_ptoken[0] - committees_earned_reward_b4_ptoken[0]
    real_shard_1_received_ptoken = committees_earned_reward_af_ptoken[1] - committees_earned_reward_b4_ptoken[1]

    STEP(5.3, "Get DAO earned reward after 1 epoch")
    dao_earned_reward_af_prv = COIN_MASTER.stk_get_reward_amount()
    dao_earned_reward_af_ptoken = COIN_MASTER.stk_get_reward_amount(token_id)

    STEP(6, 'Compare actual earned reward in 1 epoch to instruction reward')
    real_dao_received_prv = dao_earned_reward_af_prv - dao_earned_reward_b4_prv
    real_dao_received_ptoken = dao_earned_reward_af_ptoken - dao_earned_reward_b4_ptoken
    real_beacon_received_prv = sum_beacons_earned_reward_af_prv - sum_beacons_earned_reward_b4_prv
    real_beacon_received_ptoken = sum_beacons_earned_reward_af_ptoken - sum_beacons_earned_reward_b4_ptoken

    INFO(f"""
                 *** REWARD PRV ***
        DAO reward after - before                 : {dao_earned_reward_af_prv} - {dao_earned_reward_b4_prv} = {real_dao_received_prv}
        Sum beacons reward after - before         : {sum_beacons_earned_reward_af_prv} - {sum_beacons_earned_reward_b4_prv} = {real_beacon_received_prv}
        Sum shards reward [shard 0] after - before: {committees_earned_reward_af_prv[0]} - {committees_earned_reward_b4_prv[0]} = {real_shard_0_received_prv}
        Sum shards reward [shard 1] after - before: {committees_earned_reward_af_prv[1]} - {committees_earned_reward_b4_prv[1]} = {real_shard_1_received_prv}
        From instruction                          : {json.dumps(bb_reward_instruction_prv)} 
        Calculated reward PRV                     : {calculated_reward_prv}
        
                 *** REWARD pTOKEN ***
        DAO reward after - before                 : {dao_earned_reward_af_ptoken} - {dao_earned_reward_b4_ptoken} = {real_dao_received_ptoken}
        Sum beacons reward after - before         : {sum_beacons_earned_reward_af_ptoken} - {sum_beacons_earned_reward_b4_ptoken} = {real_beacon_received_ptoken}
        Sum shards reward [shard 0] after - before: {committees_earned_reward_af_ptoken[0]} - {committees_earned_reward_b4_ptoken[0]} = {real_shard_0_received_ptoken}
        Sum shards reward [shard 1] after - before: {committees_earned_reward_af_ptoken[1]} - {committees_earned_reward_b4_ptoken[1]} = {real_shard_1_received_ptoken}
        From instruction                          : {json.dumps(bb_reward_instruction_ptoken)} 
        Calculated reward                         : {calculated_reward_tok}
        """)

    # breakpoint()
    INFO('Compare reward PRV')
    assert bb_reward_instruction_prv['DAO'] == real_dao_received_prv == calculated_reward_prv['DAO']
    assert bb_reward_instruction_prv['beacon'] == real_beacon_received_prv == calculated_reward_prv['beacon']
    for shard_id in range(0, len(committees_earned_reward_af_prv)):
        assert bb_reward_instruction_prv[str(shard_id)] == committees_earned_reward_af_prv[shard_id] - \
               committees_earned_reward_b4_prv[shard_id] == calculated_reward_prv[str(shard_id)]
    INFO('Compare reward pToken')
    assert bb_reward_instruction_ptoken['DAO'] == real_dao_received_ptoken == calculated_reward_tok['DAO']
    assert bb_reward_instruction_ptoken['beacon'] == real_beacon_received_ptoken == calculated_reward_tok['beacon']
    for shard_id in range(0, len(committees_earned_reward_af_prv)):
        assert bb_reward_instruction_ptoken[str(shard_id)] == committees_earned_reward_af_ptoken[shard_id] - \
               committees_earned_reward_b4_ptoken[shard_id] == calculated_reward_tok[str(shard_id)]
