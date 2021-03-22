import copy
import concurrent

from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import ChainConfig
from Helpers.Logging import INFO
from Helpers.TestHelper import l3
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT, BEACON_ACCOUNTS, COMMITTEE_ACCOUNTS
from TestCases.Staking_Dynamic_Committee_Size import get_staker_by_tx_id

fix_node = ChainConfig.FIX_BLOCK_VALIDATOR
max_shard_comm_size = ChainConfig.SHARD_COMMITTEE_SIZE


def view_dynamic(reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, beacon_height):
    """
    Display dynamic committee size follow each beacon height, verify swap in-out according to staking flow v2
    @param reward_dict: dict of {public_key: reward}
    @param wait_4random: a list candidate shard waiting next random: list of BeaconBestStateDetailInfo.Committee
    @param wait_current_random: a list candidate shard waiting current random: list of BeaconBestStateDetailInfo.Committee
    @param pending_validator: a dict candidate shard pending: Dict of {shard_num: list of BeaconBestStateDetailInfo.Committee}
    @param shard_committees: a dict shard committees: dict of {shard_num: list of BeaconBestStateDetailInfo.Committee}
    @param beacon_height: number
    @return:
    """
    reward_b4_dict = copy.deepcopy(reward_dict)
    b4_wait_4random = copy.deepcopy(wait_4random)
    b4_wait_current_random = copy.deepcopy(wait_current_random)
    b4_pending_validator = copy.deepcopy(pending_validator)
    b4_shard_committees = copy.deepcopy(shard_committees)
    b4_beacon_height = copy.deepcopy(beacon_height)

    with ThreadPoolExecutor() as executor:
        thread_beacon_bsd = executor.submit(SUT.beacons.get_node().get_beacon_best_state_detail_info)
        thread_info = executor.submit(SUT.beacons.get_node().get_block_chain_info)
        thread_beacon_bs = executor.submit(SUT.beacons.get_node().get_beacon_best_state_info)
    block_chain_info = thread_info.result()
    remaining_block_epoch = block_chain_info.get_beacon_block().get_remaining_block_epoch()
    block_per_epoch = block_chain_info.get_block_per_epoch_number()
    random_time = block_per_epoch / 2
    current_height_in_epoch = block_per_epoch - remaining_block_epoch
    beacon_bs = thread_beacon_bs.result()
    epoch = beacon_bs.get_epoch()
    beacon_height = beacon_bs.get_beacon_height()
    current_height_in_epoch = beacon_height % block_per_epoch  # comment if have TestnetEpochV2BreakPoint
    random_number = beacon_bs.get_current_random_number()
    shard_height = beacon_bs.get_best_shard_height()
    if beacon_height != b4_beacon_height + 1 and b4_beacon_height != 0:
        return reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, b4_beacon_height
    INFO(f"""
                ================================================================
        private_key_staker - public_key_validator - payment_add_receive_reward
        ---- epoch: {epoch} - beacon_height: {beacon_height} - at: {current_height_in_epoch}/{block_per_epoch} - rand: {random_number} ----
        """)

    reward_receiver = beacon_bs.get_reward_receiver()
    thread_pool = []
    executor1 = ThreadPoolExecutor()
    for pub_k, pay_k in reward_receiver.items():
        thread = executor1.submit(SUT().transaction().get_reward_amount, pay_k)
        reward_dict[pub_k] = thread
        thread_pool.append(thread)

    beacon_bsd = thread_beacon_bsd.result()
    staking_tx = beacon_bsd.get_staking_tx()
    executor2 = ThreadPoolExecutor()
    stakers = {}
    for pub_k, tx_id in staking_tx.items():
        if (BEACON_ACCOUNTS + COMMITTEE_ACCOUNTS).find_account_by_key(pub_k):
            # beacons & shard committees have not stake transaction
            continue
        thread = executor2.submit(get_staker_by_tx_id, tx_id)
        stakers[pub_k] = thread
        thread_pool.append(thread)

    wait_4random = beacon_bsd.get_candidate_shard_waiting_next_random()
    wait_current_random = beacon_bsd.get_candidate_shard_waiting_current_random()
    pending_validator = beacon_bsd.get_shard_pending_validator()
    beacon_committees = beacon_bsd.get_beacon_committee()
    shard_committees = beacon_bsd.get_shard_committees()
    missing_signature_penalty = beacon_bsd.get_missing_signature_penalty()

    concurrent.futures.wait(thread_pool)
    for pub_k, thread in reward_dict.items():
        try:
            reward_dict[pub_k] = thread.result().get_result("PRV")
        except AttributeError:
            pass

    for pub_k, thread in stakers.items():
        stakers[pub_k] = thread.result()

    string_wait_4random = '\t--wait4random:\n'
    for j in range(len(wait_4random)):
        pub_k = wait_4random[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_dict[pub_k] - reward_b4_dict[pub_k]
        string_wait_4random += f'\tnode{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase} - auto_stk: {is_auto_stk}\n'

    string_wait_4current_random = '\t--wait4currentRandom:\n'
    for j in range(len(wait_current_random)):
        pub_k = wait_current_random[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_dict[pub_k] - reward_b4_dict[pub_k]
        string_wait_4current_random += f'\tnode{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'

    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committees in pending_validator.items():
        for j in range(len(committees)):
            pub_k = committees[j].get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            if reward_b4_dict.get(pub_k) is None:
                reward_b4_dict[pub_k] = reward_dict[pub_k]
            reward_increase = reward_dict[pub_k] - reward_b4_dict[pub_k]
            string_pending_validator += f'\tShard: {shard} - acct{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'

    string_beacon_committee = f'\t--Beacon- height: {beacon_height}\n'
    for j in range(len(beacon_committees)):
        pub_k = beacon_committees[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_dict[pub_k] - reward_b4_dict[pub_k]
        string_beacon_committee += f'\tacct{j}: {l3(BEACON_ACCOUNTS.find_account_by_key(pub_k).private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'

    string_shard_committees = '\tShard_committee\n'
    for shard, committees in shard_committees.items():
        string_shard_committees += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        for j in range(len(committees)):
            pub_k = committees[j].get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
            if miss_signature > total_signature/2:
                assert missing_signature_penalty.get(pub_k) is not None, print(committees[j])
            if reward_b4_dict.get(pub_k) is None:
                reward_b4_dict[pub_k] = reward_dict[pub_k]
            reward_increase = reward_dict[pub_k] - reward_b4_dict[pub_k]
            if j in range(4):
                string_shard_committees += f'\tacct{j}_FIX node: {l3(COMMITTEE_ACCOUNTS.find_account_by_key(pub_k).private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'
            else:
                string_shard_committees += f'\tacct{j}         : {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'

    string_missing_signature_penalty = '\tMissing_Signature_Penalty\n'
    for key, value in missing_signature_penalty.items():
        min_percent = value["MinPercent"]
        time = value["Time"]
        force_unstake = value["ForceUnstake"]
        string_missing_signature_penalty += f'\t{key}: {min_percent}_{time}_{force_unstake}'

    INFO(f"""
        {string_wait_4random}
        {string_wait_4current_random}
        {string_pending_validator}
        {string_beacon_committee}
        {string_shard_committees}
        {string_missing_signature_penalty}
                ================================================================
        """)

    for i in range(ChainConfig.ACTIVE_SHARD):
        if pending_validator.get(str(i)) is not None:
            continue
        pending_validator[str(i)] = []

    if b4_shard_committees == {}:
        return reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, beacon_height
    INFO('Verify dynamic committee size')

    num_of_assigned_candidates = 0
    num_of_swap_out = {}
    num_of_swap_in = {}

    for shard, committees in b4_shard_committees.items():
        num_of_swap_out[shard] = int(1 / 6 * len(b4_shard_committees[shard]))
        if num_of_swap_out[shard] == 0:
            num_of_assigned_candidates += 1
        else:
            num_of_assigned_candidates += num_of_swap_out[shard]
        num_of_swap_in[shard] = max_shard_comm_size - (len(b4_shard_committees[shard]) - num_of_swap_out[shard])

    pending_validator_size = sum(len(committees) for committees in pending_validator.values())
    b4_pending_validator_size = sum(len(committees) for committees in b4_pending_validator.values())
    pending_validator_list = []
    for committees in pending_validator.values():
        pending_validator_list += committees

    if current_height_in_epoch == random_time:
        if len(b4_wait_4random) < num_of_assigned_candidates:
            num_of_assigned_candidates = len(b4_wait_4random)
        assert wait_current_random == b4_wait_4random[:num_of_assigned_candidates]
        for committee in b4_wait_4random[num_of_assigned_candidates:]:
            assert committee in wait_4random, print(committee)
    else:
        assert wait_current_random == []

    if current_height_in_epoch == random_time + 1:
        for shard, committees in pending_validator.items():
            for committee in committees:
                if committee not in b4_pending_validator[shard]:
                    assert committee in b4_wait_current_random, print(committee)
        assert len(b4_wait_current_random) + b4_pending_validator_size == pending_validator_size, print(
            f'{len(b4_wait_current_random) + b4_pending_validator_size} == {pending_validator_size}')
        assert shard_committees == b4_shard_committees, print(f'{shard_committees} = {b4_shard_committees}')
    elif current_height_in_epoch == 1:
        for shard, committees in shard_committees.items():
            if len(b4_pending_validator[shard]) > num_of_swap_in[shard]:
                swap_in = num_of_swap_in[shard]
            else:
                swap_in = len(b4_pending_validator[shard])

            if len(missing_signature_penalty) >= num_of_swap_out[shard]:
                swap_out = 0
            else:
                swap_out = num_of_swap_out[shard] - len(missing_signature_penalty)
            index_break = fix_node + swap_out
            assert committees == b4_shard_committees[shard][:fix_node] + b4_shard_committees[shard][index_break:] + \
                   b4_pending_validator[shard][:swap_in], print(
                f"{committees}={b4_shard_committees[shard][:fix_node] + b4_shard_committees[shard][index_break:] + b4_pending_validator[shard][:swap_in]}")
            assert b4_pending_validator[shard][swap_in:] == pending_validator[shard][
                                                            :len(b4_pending_validator[shard]) - swap_in], print(
                f'{b4_pending_validator[shard][swap_in:]} = {pending_validator[shard][:len(b4_pending_validator[shard]) - swap_in]}')
            for committee in b4_shard_committees[shard][fix_node:index_break]:
                if beacon_bsd.get_auto_staking_committees(committee) is True:
                    assert committee in pending_validator_list, print(committee)
                else:
                    assert beacon_bsd.get_auto_staking_committees(committee) is None
    else:
        assert b4_pending_validator == pending_validator, print(f'{b4_pending_validator} = {pending_validator}')
        assert shard_committees == b4_shard_committees, print(f'{shard_committees} = {b4_shard_committees}')

    return reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, beacon_height


def test_view_dynamic():
    reward_dict = {}
    wait_4random = []
    wait_current_random = []
    pending_validator = {}
    shard_committees = {}
    beacon_height = 0
    for i in range(1000):
        reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, beacon_height = view_dynamic(
            reward_dict, wait_4random, wait_current_random, pending_validator, shard_committees, beacon_height)
        WAIT(5)
