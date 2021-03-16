from concurrent.futures.thread import ThreadPoolExecutor
from Configs.Constants import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import get_staking_info_of_validator


def view_dynamic():
    shard_active = ChainConfig.ACTIVE_SHARD
    shard_bs_list = []
    shard_committees = {}
    shard_height = {}
    with ThreadPoolExecutor() as executor:
        thread_beacon_bs = executor.submit(SUT.beacons.get_node().get_beacon_best_state_info)
        thread_info = executor.submit(SUT.beacons.get_node().get_block_chain_info)
        for i in range(shard_active):
            thread_shard_bs = executor.submit(SUT.shards[i].get_node().get_shard_best_state_info, i)
            shard_bs_list.append(thread_shard_bs)
    beacon_bs = thread_beacon_bs.result()
    block_chain_info = thread_info.result()
    for i in range(shard_active):
        shard_bs = shard_bs_list[i].result()
        shard_bs_list[i] = shard_bs
        shard_committees[str(i)] = shard_bs.get_shard_committee()
        shard_height[str(i)] = shard_bs.get_shard_height()
    epoch = beacon_bs.get_epoch()
    beacon_height = beacon_bs.get_beacon_height()
    random_number = beacon_bs.get_current_random_number()
    wait_4random = beacon_bs.get_candidate_shard_waiting_next_random()
    wait_current_random = beacon_bs.get_candidate_shard_waiting_current_random()
    beacon_committees = beacon_bs.get_beacon_committee()
    pending_validator = beacon_bs.get_shard_pending_validator()
    remaining_block_poch = block_chain_info.get_beacon_block().get_remaining_block_epoch()
    current_height_in_epoch = ChainConfig.BLOCK_PER_EPOCH - remaining_block_poch

    try:
        missing_sig_list = beacon_bs.get_missing_signature()
    except:
        missing_sig_list = []
    try:
        missing_sig_penalty = beacon_bs.get_missing_signature_penalty()
    except:
        missing_sig_penalty = []

    string_wait_4random = '\t--wait4random:\n'
    for j in range(len(wait_4random)):
        is_auto_stk = beacon_bs.get_auto_staking_committees(wait_4random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_4random[j], shard_bs_list)
        string_wait_4random += f'\tnode{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_wait_4current_random = '\t--waitcurrentRandom:\n'
    for j in range(len(wait_current_random)):
        is_auto_stk = beacon_bs.get_auto_staking_committees(wait_current_random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_current_random[j],
                                                                                   shard_bs_list)
        string_wait_4current_random += f'\tnode{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committee_pub_keys in pending_validator.items():
        for j in range(len(committee_pub_keys)):
            is_auto_stk = beacon_bs.get_auto_staking_committees(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bs_list)
            string_pending_validator += f'\tShard: {shard} - acct{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_beacon_committee = f'\t--Beacon- height: {beacon_height}\n'
    for j in range(len(beacon_committees)):
        is_auto_stk = beacon_bs.get_auto_staking_committees(beacon_committees[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(beacon_committees[j], shard_bs_list)
        string_beacon_committee += f'\tacct{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_shard_committees = '\tShard_committee\n'
    for shard, committee_pub_keys in shard_committees.items():
        string_shard_committees += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        for j in range(len(committee_pub_keys)):
            is_auto_stk = beacon_bs.get_auto_staking_committees(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bs_list)
            string_shard_committees += f'\tacct{j}: {string} - auto_stk: {is_auto_stk}\n'

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


def view_height():
    chain_info = SUT.beacons.get_node().get_block_chain_info()
    epoch = chain_info.get_beacon_block().get_epoch()
    beacon_height = chain_info.get_beacon_block().get_height()
    shard_0_height = chain_info.get_shard_block(0).get_height()
    shard_1_height = chain_info.get_shard_block(1).get_height()
    current_height_in_epoch = beacon_height % ChainConfig.BLOCK_PER_EPOCH
    remaining_block_poch = chain_info.get_beacon_block().get_remaining_block_epoch()
    INFO()
    INFO(f"""
            ---- epoch: {epoch} - beacon_height: {beacon_height} - shard_0_height: {shard_0_height} - shard_1_height: {shard_1_height} - at: {current_height_in_epoch}/{ChainConfig.BLOCK_PER_EPOCH} - RemainingBlockEpoch: {remaining_block_poch} ----

    """)
    INFO()


def test_view_dynamic():
    for i in range(1000):
        view_dynamic()
        WAIT(ChainConfig.BLOCK_TIME)


def test_view_height():
    for i in range(1000):
        view_height()
        WAIT(ChainConfig.BLOCK_TIME)


def test_view_detail():
    for i in range(1000):
        string_beacon = 'Beacon: '
        string_beacon += str(SUT.beacons.get_node().get_all_view_detail(-1).num_of_hash_follow_height())
        string_shard_0 = 'Shard 0: '
        string_shard_0 += str(SUT.shards[0].get_node().get_all_view_detail(0).num_of_hash_follow_height())
        string_shard_1 = 'Shard 1: '
        string_shard_1 += str(SUT.shards[1].get_node().get_all_view_detail(1).num_of_hash_follow_height())
        INFO()
        INFO(string_beacon)
        INFO(string_shard_0)
        INFO(string_shard_1)
        INFO()
        WAIT(ChainConfig.BLOCK_TIME)
