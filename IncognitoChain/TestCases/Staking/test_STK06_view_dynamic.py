from concurrent.futures.thread import ThreadPoolExecutor

from IncognitoChain.Configs.Constants import ChainConfig
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Staking import get_staking_info_of_validator


def view_dynamic(reward_dict, info):
    beacon_bs = SUT().get_beacon_best_state_info()
    epoch = beacon_bs.get_epoch()
    beacon_height = beacon_bs.get_beacon_height()
    random_number = beacon_bs.get_current_random_number()
    wait_4random = beacon_bs.get_candidate_shard_waiting_next_random()
    wait_4current_random = beacon_bs.get_candidate_shard_waiting_current_random()
    pending_validator = beacon_bs.get_shard_pending_validator()
    beacon_committees = beacon_bs.get_beacon_committee()
    shard_committees = beacon_bs.get_shard_committees()
    shard_height = beacon_bs.get_best_shard_height()
    shard_active = beacon_bs.get_active_shard()
    wait_4random_dict = {}
    wait_4current_random_dict = {}
    pending_validator_dict = {}
    beacon_committees_dict = {}
    shard_committees_dict = {}

    try:
        missing_sig_list = beacon_bs.get_missing_signature()
    except:
        missing_sig_list = []
    try:
        missing_sig_penalty = beacon_bs.get_missing_signature_penalty()
    except:
        missing_sig_penalty = []
    current_height_in_epoch = beacon_height % ChainConfig.BLOCK_PER_EPOCH
    shard_bsd_list = []
    for i in range(shard_active):
        shard_bsd = SUT().get_shard_best_state_detail_info(i)
        shard_bsd_list.append(shard_bsd)

    string_wait_4random = '\t--wait4random:\n'
    for j in range(len(wait_4random)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(wait_4random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_4random[j], shard_bsd_list)
        reward = receiver_reward.stk_get_reward_amount()
        if reward_dict.get(receiver_reward) is None:
            reward_dict[receiver_reward] = reward
        reward_increase = reward - reward_dict[receiver_reward]
        reward_dict[receiver_reward] = reward
        string_wait_4random += f'\tnode{j}: {string} - reward: {reward}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'
        wait_4random_dict[str(j)] = validator

    string_wait_4current_random = '\t--wait4currentRandom:\n'
    for j in range(len(wait_4current_random)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(wait_4random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_4random[j], shard_bsd_list)
        reward = receiver_reward.stk_get_reward_amount()
        if reward_dict.get(receiver_reward) is None:
            reward_dict[receiver_reward] = reward
        reward_increase = reward - reward_dict[receiver_reward]
        reward_dict[receiver_reward] = reward
        string_wait_4current_random += f'\tnode{j}: {string} - reward: {reward}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'
        wait_4current_random_dict[str(j)] = validator

    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committee_pub_keys in pending_validator.items():
        pending_validator_dict[shard] = {}
        for j in range(len(committee_pub_keys)):
            is_auto_stk = beacon_bs.is_this_committee_auto_stake(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bsd_list)
            reward = receiver_reward.stk_get_reward_amount()
            if reward_dict.get(receiver_reward) is None:
                reward_dict[receiver_reward] = reward
            reward_increase = reward - reward_dict[receiver_reward]
            reward_dict[receiver_reward] = reward
            string_pending_validator += f'\tShard: {shard} - acct{j}: {string} - reward: {reward}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'
            pending_validator_dict[shard][str(j)] = validator


    string_beacon_committee = f'\t--Beacon- height: {beacon_height}\n'
    for j in range(len(beacon_committees)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(beacon_committees[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(beacon_committees[j], shard_bsd_list)
        reward = receiver_reward.stk_get_reward_amount()
        if reward_dict.get(receiver_reward) is None:
            reward_dict[receiver_reward] = reward
        reward_increase = reward - reward_dict[receiver_reward]
        reward_dict[receiver_reward] = reward
        string_beacon_committee += f'\tacct{j}: {string} - reward: {reward}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'
        beacon_committees_dict[str(j)] = validator

    string_shard_committees = '\tShard_committee\n'
    for shard, committee_pub_keys in shard_committees.items():
        shard_committees_dict[shard] = {}
        string_shard_committees += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        for j in range(len(committee_pub_keys)):
            is_auto_stk = beacon_bs.is_this_committee_auto_stake(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bsd_list)
            reward = receiver_reward.stk_get_reward_amount()
            if reward_dict.get(receiver_reward) is None:
                reward_dict[receiver_reward] = reward
            reward_increase = reward - reward_dict[receiver_reward]
            reward_dict[receiver_reward] = reward
            string_shard_committees += f'\tacct{j}: {string} - reward: {reward}, rwinc: {reward_increase}, auto_stk: {is_auto_stk}\n'
            shard_committees_dict[shard][str(j)] = validator

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

    info[str(current_height_in_epoch)] = wait_4random_dict, wait_4current_random_dict, pending_validator_dict, beacon_committees_dict, shard_committees_dict
    return reward_dict, info


def test_view_dynamic():
    epoch_current = SUT().get_beacon_best_state_info().get_epoch()
    first_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch_current + 1)
    ChainHelper.wait_till_beacon_height(first_beacon_height-1)
    reward_dict = {}
    info = {}
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        for i in range(ChainConfig.BLOCK_PER_EPOCH):

            view_dynamic(reward_dict, info)
            WAIT(ChainConfig.BLOCK_TIME-5)
            # if info.get(0):

