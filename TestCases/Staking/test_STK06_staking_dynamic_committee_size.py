import copy
import concurrent

from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import ChainConfig
from Helpers.Logging import INFO
from Helpers.TestHelper import l3
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT, BEACON_ACCOUNTS, COMMITTEE_ACCOUNTS
from TestCases.Staking import get_staker_by_tx_id


def view_dynamic(reward_dict):
    reward_b4_dict = copy.deepcopy(reward_dict)
    with ThreadPoolExecutor() as executor:
        thread_beacon_bsd = executor.submit(SUT.beacons.get_node().get_beacon_best_state_detail_info)
        thread_info = executor.submit(SUT.beacons.get_node().get_block_chain_info)
        thread_beacon_bs = executor.submit(SUT.beacons.get_node().get_beacon_best_state_info)
    beacon_bsd = thread_beacon_bsd.result()
    beacon_bs = thread_beacon_bs.result()
    block_chain_info = thread_info.result()
    epoch = beacon_bs.get_epoch()
    beacon_height = beacon_bs.get_beacon_height()
    random_number = beacon_bs.get_current_random_number()
    shard_height = beacon_bs.get_best_shard_height()
    reward_receiver = beacon_bs.get_reward_receiver()
    thread_pool = []
    executor1 = ThreadPoolExecutor()
    for pub_k, pay_k in reward_receiver.items():
        thread = executor1.submit(SUT().transaction().get_reward_amount, pay_k)
        reward_dict[pub_k] = thread
        thread_pool.append(thread)

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
    wait_4current_random = beacon_bsd.get_candidate_shard_waiting_current_random()
    pending_validator = beacon_bsd.get_shard_pending_validator()
    beacon_committees = beacon_bsd.get_beacon_committee()
    shard_committees = beacon_bsd.get_shard_committees()
    remaining_block_epoch = block_chain_info.get_beacon_block().get_remaining_block_epoch()
    current_height_in_epoch = ChainConfig.BLOCK_PER_EPOCH - remaining_block_epoch

    concurrent.futures.wait(thread_pool)
    for pub_k, thread in reward_dict.items():
        reward_dict[pub_k] = thread.result().get_result("PRV")

    for pub_k, thread in stakers.items():
        stakers[pub_k] = thread.result()

    string_wait_4random = '\t--wait4random:\n'
    for j in range(len(wait_4random)):
        pub_k = wait_4random[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_b4_dict[pub_k] - reward_dict[pub_k]
        string_wait_4random += f'\tnode{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase} - auto_stk: {is_auto_stk}\n'

    string_wait_4current_random = '\t--wait4currentRandom:\n'
    for j in range(len(wait_4current_random)):
        pub_k = wait_4current_random[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_b4_dict[pub_k] - reward_dict[pub_k]
        string_wait_4current_random += f'\tnode{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'

    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committees in pending_validator.items():
        for j in range(len(committees)):
            pub_k = committees[j].get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            if reward_b4_dict.get(pub_k) is None:
                reward_b4_dict[pub_k] = reward_dict[pub_k]
            reward_increase = reward_b4_dict[pub_k] - reward_dict[pub_k]
            string_pending_validator += f'\tShard: {shard} - acct{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'

    string_beacon_committee = f'\t--Beacon- height: {beacon_height}\n'
    for j in range(len(beacon_committees)):
        pub_k = beacon_committees[j].get_inc_public_key()
        is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
        total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
        if reward_b4_dict.get(pub_k) is None:
            reward_b4_dict[pub_k] = reward_dict[pub_k]
        reward_increase = reward_b4_dict[pub_k] - reward_dict[pub_k]
        string_beacon_committee += f'\tacct{j}: {l3(BEACON_ACCOUNTS.find_account_by_key(pub_k).private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'

    string_shard_committees = '\tShard_committee\n'
    for shard, committees in shard_committees.items():
        string_shard_committees += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        for j in range(len(committees)):
            pub_k = committees[j].get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
            if reward_b4_dict.get(pub_k) is None:
                reward_b4_dict[pub_k] = reward_dict[pub_k]
            reward_increase = reward_b4_dict[pub_k] - reward_dict[pub_k]
            if j in range(4):
                string_shard_committees += f'\tacct{j}_FIX node: {l3(COMMITTEE_ACCOUNTS.find_account_by_key(pub_k).private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'
            else:
                string_shard_committees += f'\tacct{j}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])} - reward: {reward_dict[pub_k]}, rwinc: {reward_increase}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'

    INFO(f"""
                ================================================================
        private_key_staker - public_key_validator - payment_add_receive_reward
        ---- epoch: {epoch} - beacon_height: {beacon_height} - at: {current_height_in_epoch}/{ChainConfig.BLOCK_PER_EPOCH} - rand: -{random_number} ----
        {string_wait_4random}
        {string_wait_4current_random}
        {string_pending_validator}
        {string_beacon_committee}
        {string_shard_committees}
                ================================================================
    """)
    return reward_dict


def test_view_dynamic():
    reward_dict = {}
    for i in range(1000):
        view_dynamic(reward_dict)
        WAIT(ChainConfig.BLOCK_TIME)
