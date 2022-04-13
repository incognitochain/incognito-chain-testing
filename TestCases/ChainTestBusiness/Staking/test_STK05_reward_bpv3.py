import json
import random
from concurrent.futures.thread import ThreadPoolExecutor


from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, STEP
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.ChainTestBusiness.Staking import amount_token_send, amount_token_fee, token_owner

trx_list = []
fee_reward_by_shard = []
for shard_id in range(ChainConfig.ACTIVE_SHARD):
    fee_reward_by_shard.append({"0": 0, "1": 0})


def test_verify_reward_received():
    INFO()
    from TestCases.ChainTestBusiness.Staking import token_id
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, amount_token_send, amount_token_send + amount_token_fee * 5)
    token_owner.top_up_if_lower_than(ACCOUNTS, 10e9, 11e9, token_id)

    STEP(1, 'Prepare - Wait till first height of epoch')
    epoch_reward, height = SUT().wait_till_next_epoch()

    INFO('Create and send transaction')
    indx_receiver = random.randrange(0, len(ACCOUNTS))
    for acc in ACCOUNTS:
        trx = acc.send_prv_to(ACCOUNTS[indx_receiver], amount_token_send, amount_token_fee).expect_no_error()
        trx_list.append(trx)
    WAIT(4 * ChainConfig.BLOCK_TIME)
    for acc in ACCOUNTS:
        trx = acc.send_token_to(ACCOUNTS[indx_receiver], token_id, amount_token_send,
                                amount_token_fee).expect_no_error()
        trx_list.append(trx)
    WAIT(4 * ChainConfig.BLOCK_TIME)
    for trx in trx_list:
        trx = trx.get_transaction_by_hash()
        fee = trx.get_fee()
        shard = trx.get_shard_id()
        subset_id = SUT().get_shard_block_by_height(shard, trx.get_block_height(), level=2).get_subset_id()
        fee_reward_by_shard[shard][str(subset_id)] += fee

    INFO(f'Fee_reward_by_shard: {fee_reward_by_shard}')

    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward)
    SUT().wait_till_beacon_height(block_height_random)
    with ThreadPoolExecutor() as executor:
        thread_bbd = executor.submit(SUT().get_beacon_best_state_detail_info)
        thread_bb = executor.submit(SUT().get_beacon_best_state_info)
    beacon_bsd_epoch_reward = thread_bbd.result()
    beacon_bs = thread_bb.result()
    reward_receivers = beacon_bs.get_reward_receiver()

    STEP(2, "Get reward before test")
    thread_reward_dict = {}
    with ThreadPoolExecutor() as executor:
        for pub_k, pay_k in reward_receivers.items():
            thread = executor.submit(SUT().transaction().get_reward_amount, pay_k)
            thread_reward_dict[pub_k] = thread
    reward_b4_PRV = {}
    real_earned_reward_b4_prv = {}
    for pub_k, thread in thread_reward_dict.items():
        reward = thread.result()
        reward_b4_PRV[pub_k] = reward.get_result("PRV")

    INFO("Get Committees earned reward")
    for shard, committees in beacon_bsd_epoch_reward.get_shard_committees().items():
        real_earned_reward_b4_prv[shard] = {"0": 0, "1": 0}
        for i in range(len(committees)):
            real_earned_reward_b4_prv[shard][str(i % 2)] += reward_b4_PRV[committees[i].get_inc_public_key()]

    INFO('Get Beacons earned reward')
    real_earned_reward_b4_prv["beacon"] = 0
    for committee in beacon_bsd_epoch_reward.get_beacon_committee():
        real_earned_reward_b4_prv["beacon"] += reward_b4_PRV[committee.get_inc_public_key()]

    INFO("Get DAO earned reward")
    real_earned_reward_b4_prv['DAO'] = COIN_MASTER.stk_get_reward_amount()

    STEP(3, 'Wait till next epoch, after reward epoch. Wait receive reward')
    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch_reward + 1)
    SUT().wait_till_beacon_height(block_height_random)

    STEP(4, 'Get reward instruction from beacon')
    instruction_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch_reward + 1)
    instruction_bb = SUT().get_latest_beacon_block(instruction_beacon_height)
    bb_reward_instruction_prv = instruction_bb.get_transaction_reward_from_instruction(bpv3=True)
    calculated_reward_prv = SUT(). \
        cal_transaction_reward_v3_from_beacon_block_info(epoch=epoch_reward, shard_txs_fee_list=fee_reward_by_shard)
    dao_ctr_percent = SUT().pde3_get_state(key_filter="Params").get_pde_params().get_dao_contributing_percent()
    calculated_reward_prv['DAO'] = (100-dao_ctr_percent)/100 * calculated_reward_prv['DAO']
    STEP(5, "Get reward after 1 epoch")
    thread_reward_dict = {}
    with ThreadPoolExecutor() as executor:
        for pub_k, pay_k in reward_receivers.items():
            thread = executor.submit(SUT().transaction().get_reward_amount, pay_k)
            thread_reward_dict[pub_k] = thread
    reward_af_PRV = {}
    real_earned_reward_af_prv = {}
    for pub_k, thread in thread_reward_dict.items():
        reward = thread.result()
        reward_af_PRV[pub_k] = reward.get_result("PRV")

    INFO('Get slashing committees')
    slashing_committees = SUT().get_slashing_committee_detail(epoch_reward)
    if slashing_committees:
        for committees in slashing_committees.values():
            for committee in committees:
                pub_k = committee.get_inc_public_key()
                assert reward_b4_PRV[pub_k] == reward_af_PRV[pub_k]

    INFO("Get Committees earned reward")

    for shard, committees in beacon_bsd_epoch_reward.get_shard_committees().items():
        real_earned_reward_af_prv[shard] = {"0": 0, "1": 0}
        for i in range(len(committees)):
            real_earned_reward_af_prv[shard][str(i % 2)] += reward_af_PRV[committees[i].get_inc_public_key()]

    INFO('Get Beacons earned reward')
    real_earned_reward_af_prv["beacon"] = 0
    for committee in beacon_bsd_epoch_reward.get_beacon_committee():
        real_earned_reward_af_prv["beacon"] += reward_af_PRV[committee.get_inc_public_key()]

    INFO("Get DAO earned reward")
    real_earned_reward_af_prv['DAO'] = COIN_MASTER.stk_get_reward_amount()

    STEP(6, 'Compare actual earned reward in 1 epoch to instruction reward')
    real_earned_reward_prv = {}
    for key in real_earned_reward_af_prv.keys():
        if isinstance(real_earned_reward_af_prv[key], dict):
            real_earned_reward_prv[key] = {}
            for k in real_earned_reward_af_prv[key].keys():
                real_earned_reward_prv[key][k] = real_earned_reward_af_prv[key][k] - real_earned_reward_b4_prv[key][k]
        else:
            real_earned_reward_prv[key] = real_earned_reward_af_prv[key] - real_earned_reward_b4_prv[key]

    INFO(f"""
                 *** REWARD PRV ***
        Real earned reward                    : {real_earned_reward_prv}
        From instruction                      : {json.dumps(bb_reward_instruction_prv)}
        Calculated reward                     : {calculated_reward_prv}
        """)

    difference_earned_instr = {}
    difference_instr_cal = {}
    for key in real_earned_reward_prv.keys():
        if type(real_earned_reward_prv[key]) is not int:
            difference_earned_instr[key] = []
            difference_instr_cal[key] = []
            for subset_id in real_earned_reward_prv[key].keys():
                n = abs(real_earned_reward_prv[key][subset_id] - bb_reward_instruction_prv[key][subset_id])
                m = abs(bb_reward_instruction_prv[key][subset_id] - calculated_reward_prv[key][subset_id])
                difference_earned_instr[key].append(n)
                difference_instr_cal[key].append(m)
                assert n < 10000
                assert m < 10000
        else:
            n = abs(real_earned_reward_prv[key] - bb_reward_instruction_prv[key])
            m = abs(bb_reward_instruction_prv[key] - calculated_reward_prv[key])
            difference_earned_instr[key] = n
            difference_instr_cal[key] = m
            assert n < 10000
            assert m < 10000
    INFO(f'Difference_earned_instr: {difference_earned_instr}')
    INFO(f'Difference_instr_cal: {difference_instr_cal}')
