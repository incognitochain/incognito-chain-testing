import json
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import coin
from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, STEP
from Helpers.TestHelper import ChainHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import list_acc_x_shard, amount_token_send, \
    amount_token_fee

token_holder_shard_0 = list_acc_x_shard[0]
token_holder_shard_1 = list_acc_x_shard[1]
shard_trx_prv_fee_list = [0] * ChainConfig.ACTIVE_SHARD
shard_trx_ptoken_fee_list = [0] * ChainConfig.ACTIVE_SHARD
slashing_v2 = True


@pytest.mark.parametrize('dcz', [
    # True,  # true for testing with dcz
    False,
])
def test_verify_reward_received(dcz):
    from TestCases.Staking import token_id
    STEP(1, 'Prepare - Wait till first height of epoch')
    epoch_reward, height = ChainHelper.wait_till_next_epoch()

    INFO('Create transaction send PRV')
    shard_trx_prv_fee_list[0] += COIN_MASTER.send_prv_to(token_holder_shard_0, coin(5),
                                                         coin(1)).subscribe_transaction().get_fee()
    shard_trx_prv_fee_list[0] += COIN_MASTER.send_prv_to(token_holder_shard_1, coin(5),
                                                         100).subscribe_transaction().get_fee()
    shard_trx_prv_fee_list[1] += token_holder_shard_1.send_prv_to(token_holder_shard_0, coin(1),
                                                                  1000).subscribe_transaction().get_fee()
    shard_trx_prv_fee_list[1] += token_holder_shard_1.send_prv_to(COIN_MASTER, coin(1),
                                                                  100).subscribe_transaction().get_fee()

    INFO('Create transaction send ptoken')
    if ChainConfig.PRIVACY_VERSION == 1:
        shard_trx_ptoken_fee_list[0] += token_holder_shard_0.send_token_to(token_holder_shard_1, token_id,
                                                                           amount_token_send,
                                                                           token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        shard_trx_ptoken_fee_list[0] += token_holder_shard_0.send_token_to(token_holder_shard_1, token_id,
                                                                           amount_token_send,
                                                                           token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        shard_trx_ptoken_fee_list[1] += token_holder_shard_1.send_token_to(token_holder_shard_0, token_id,
                                                                           amount_token_send,
                                                                           token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
        shard_trx_ptoken_fee_list[1] += token_holder_shard_1.send_token_to(token_holder_shard_0, token_id,
                                                                           amount_token_send,
                                                                           token_fee=amount_token_fee).subscribe_transaction().get_privacy_custom_token_fee()
    else:
        shard_trx_prv_fee_list[0] += token_holder_shard_0.send_token_to(token_holder_shard_1, token_id,
                                                                        amount_token_send,
                                                                        prv_fee=amount_token_fee).subscribe_transaction().get_fee()
        shard_trx_prv_fee_list[1] += token_holder_shard_1.send_token_to(token_holder_shard_0, token_id,
                                                                        amount_token_send,
                                                                        prv_fee=amount_token_fee).subscribe_transaction().get_fee()

    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward)
    ChainHelper.wait_till_beacon_height(block_height_random)
    with ThreadPoolExecutor() as executor:
        thread_bbd = executor.submit(SUT().get_beacon_best_state_detail_info)
        thread_bb = executor.submit(SUT().get_beacon_best_state_info)
    bbd_epoch_reward = thread_bbd.result()
    beacon_bs = thread_bb.result()
    reward_all_receivers = beacon_bs.get_reward_receiver()
    reward_receivers = {}
    for shard, committees in bbd_epoch_reward.get_shard_committees().items():
        for committee in committees:
            pub_k = committee.get_inc_public_key()
            reward_receivers[pub_k] = reward_all_receivers[pub_k]
    for committee in bbd_epoch_reward.get_beacon_committee():
        pub_k = committee.get_inc_public_key()
        reward_receivers[pub_k] = reward_all_receivers[pub_k]

    STEP(2, "Get reward before test")
    thread_reward_dict = {}
    with ThreadPoolExecutor() as executor:
        for pub_k, pay_k in reward_receivers.items():
            thread = executor.submit(SUT().transaction().get_reward_amount, pay_k)
            thread_reward_dict[pub_k] = thread
    reward_b4_PRV = {}
    reward_b4_ptoken = {}
    real_earned_reward_b4_prv = {}
    real_earned_reward_b4_ptoken = {}
    for pub_k, thread in thread_reward_dict.items():
        reward = thread.result()
        reward_b4_PRV[pub_k] = reward.get_result("PRV")
        reward_b4_ptoken[pub_k] = 0 if reward.get_result(token_id) is None else reward.get_result(token_id)

    INFO("Get Committees earned reward")
    for shard, committees in bbd_epoch_reward.get_shard_committees().items():
        real_earned_reward_b4_prv[shard] = 0
        real_earned_reward_b4_ptoken[shard] = 0
        for committee in committees:
            real_earned_reward_b4_prv[shard] += reward_b4_PRV[committee.get_inc_public_key()]
            real_earned_reward_b4_ptoken[shard] += reward_b4_ptoken[committee.get_inc_public_key()]

    INFO('Get Beacons earned reward')
    real_earned_reward_b4_prv["beacon"] = 0
    real_earned_reward_b4_ptoken["beacon"] = 0
    for committee in bbd_epoch_reward.get_beacon_committee():
        real_earned_reward_b4_prv["beacon"] += reward_b4_PRV[committee.get_inc_public_key()]
        real_earned_reward_b4_ptoken["beacon"] += reward_b4_ptoken[committee.get_inc_public_key()]

    INFO("Get DAO earned reward")
    real_earned_reward_b4_prv['DAO'] = COIN_MASTER.stk_get_reward_amount()
    real_earned_reward_b4_ptoken['DAO'] = 0 if COIN_MASTER.stk_get_reward_amount(
        token_id) is None else COIN_MASTER.stk_get_reward_amount(token_id)

    STEP(3, 'Wait till next epoch, after reward epoch. Wait receive reward')
    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward + 1)
    ChainHelper.wait_till_beacon_height(block_height_random)

    STEP(4, 'Get reward instruction from beacon')
    instruction_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch_reward + 1)
    instruction_bb = SUT().get_latest_beacon_block(instruction_beacon_height)
    bb_reward_instruction_prv = instruction_bb.get_transaction_reward_from_instruction()
    bb_reward_instruction_ptoken = instruction_bb.get_transaction_reward_from_instruction(token_id)
    calculated_reward_prv = SUT(). \
        cal_transaction_reward_from_beacon_block_info(epoch_reward, shard_txs_fee_list=shard_trx_prv_fee_list, dcz=dcz)
    calculated_reward_tok = SUT(). \
        cal_transaction_reward_from_beacon_block_info(epoch_reward, token=token_id,
                                                      shard_txs_fee_list=shard_trx_ptoken_fee_list, dcz=dcz)

    STEP(5, "Get reward after 1 epoch")
    thread_reward_dict = {}
    with ThreadPoolExecutor() as executor:
        for pub_k, pay_k in reward_receivers.items():
            thread = executor.submit(SUT().transaction().get_reward_amount, pay_k)
            thread_reward_dict[pub_k] = thread
    reward_af_PRV = {}
    reward_af_ptoken = {}
    real_earned_reward_af_prv = {}
    real_earned_reward_af_ptoken = {}
    for pub_k, thread in thread_reward_dict.items():
        reward = thread.result()
        reward_af_PRV[pub_k] = reward.get_result("PRV")
        reward_af_ptoken[pub_k] = 0 if reward.get_result(token_id) is None else reward.get_result(token_id)

    if slashing_v2:
        INFO('Get slashing committees')
        slashing_committees = SUT().get_slashing_committee_detail(epoch_reward)
        for shard_id, committees in slashing_committees.items():
            for committee in committees:
                pub_k = committee.get_inc_public_key()
                assert reward_b4_PRV[pub_k] == reward_af_PRV[pub_k]
                assert reward_b4_ptoken[pub_k] == reward_af_ptoken[pub_k]

    INFO("Get Committees earned reward")
    for shard, committees in bbd_epoch_reward.get_shard_committees().items():
        real_earned_reward_af_prv[shard] = 0
        real_earned_reward_af_ptoken[shard] = 0
        for committee in committees:
            real_earned_reward_af_prv[shard] += reward_af_PRV[committee.get_inc_public_key()]
            real_earned_reward_af_ptoken[shard] += reward_af_ptoken[committee.get_inc_public_key()]

    INFO('Get Beacons earned reward')
    real_earned_reward_af_prv["beacon"] = 0
    real_earned_reward_af_ptoken["beacon"] = 0
    for committee in bbd_epoch_reward.get_beacon_committee():
        real_earned_reward_af_prv["beacon"] += reward_af_PRV[committee.get_inc_public_key()]
        real_earned_reward_af_ptoken["beacon"] += reward_af_ptoken[committee.get_inc_public_key()]

    INFO("Get DAO earned reward")
    real_earned_reward_af_prv['DAO'] = COIN_MASTER.stk_get_reward_amount()
    real_earned_reward_af_ptoken['DAO'] = 0 if COIN_MASTER.stk_get_reward_amount(
        token_id) is None else COIN_MASTER.stk_get_reward_amount(token_id)

    STEP(6, 'Compare actual earned reward in 1 epoch to instruction reward')
    real_earned_reward_prv = {}
    real_earned_reward_ptoken = {}
    for key in real_earned_reward_af_prv.keys():
        real_earned_reward_prv[key] = real_earned_reward_af_prv[key] - real_earned_reward_b4_prv[key]
        real_earned_reward_ptoken[key] = real_earned_reward_af_ptoken[key] - real_earned_reward_b4_ptoken[key]

    INFO(f"""
                 *** REWARD PRV ***
        Real earned reward                    : {real_earned_reward_prv}
        From instruction                      : {json.dumps(bb_reward_instruction_prv)}
        Calculated reward                     : {calculated_reward_prv}

                 *** REWARD pTOKEN ***
        Real earned reward                    : {real_earned_reward_ptoken}
        From instruction                      : {json.dumps(bb_reward_instruction_ptoken)}
        Calculated reward                     : {calculated_reward_tok}
        """)

    # breakpoint()
    for key in real_earned_reward_prv.keys():
        INFO('Compare reward PRV')
        assert real_earned_reward_prv[key] == bb_reward_instruction_prv[key] == calculated_reward_prv[key]
        INFO('Compare reward pToken')
        if ChainConfig.PRIVACY_VERSION == 1:
            assert real_earned_reward_ptoken[key] == bb_reward_instruction_ptoken[key] == calculated_reward_tok[key]
        else:
            assert real_earned_reward_ptoken[key] == calculated_reward_tok[key] == 0
            assert bb_reward_instruction_ptoken[key]
