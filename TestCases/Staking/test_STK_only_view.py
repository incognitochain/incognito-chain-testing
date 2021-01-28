from Configs.Constants import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import get_staking_info_of_validator


def view_dynamic():
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

    try:
        missing_sig_list = beacon_bs.get_missing_signature()
    except:
        missing_sig_list = []
    try:
        missing_sig_penalty = beacon_bs.get_missing_signature_penalty()
    except:
        missing_sig_penalty = []
    current_height_in_epoch = (beacon_height - 5000) % ChainConfig.BLOCK_PER_EPOCH
    shard_bsd_list = []
    for i in range(shard_active):
        shard_bsd = SUT().get_shard_best_state_detail_info(i)
        shard_bsd_list.append(shard_bsd)

    string_wait_4random = '\t--wait4random:\n'
    for j in range(len(wait_4random)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(wait_4random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_4random[j], shard_bsd_list)
        string_wait_4random += f'\tnode{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_wait_4current_random = '\t--wait4currentRandom:\n'
    for j in range(len(wait_4current_random)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(wait_4current_random[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(wait_4current_random[j],
                                                                                   shard_bsd_list)
        string_wait_4current_random += f'\tnode{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committee_pub_keys in pending_validator.items():
        for j in range(len(committee_pub_keys)):
            is_auto_stk = beacon_bs.is_this_committee_auto_stake(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bsd_list)
            string_pending_validator += f'\tShard: {shard} - acct{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_beacon_committee = f'\t--Beacon- height: {beacon_height}\n'
    for j in range(len(beacon_committees)):
        is_auto_stk = beacon_bs.is_this_committee_auto_stake(beacon_committees[j])
        staker, validator, receiver_reward, string = get_staking_info_of_validator(beacon_committees[j], shard_bsd_list)
        string_beacon_committee += f'\tacct{j}: {string} - auto_stk: {is_auto_stk}\n'

    string_shard_committees = '\tShard_committee\n'
    for shard, committee_pub_keys in shard_committees.items():
        string_shard_committees += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        for j in range(4, len(committee_pub_keys)):
            is_auto_stk = beacon_bs.is_this_committee_auto_stake(committee_pub_keys[j])
            staker, validator, receiver_reward, string = get_staking_info_of_validator(committee_pub_keys[j],
                                                                                       shard_bsd_list)
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


def test_view_dynamic():
    for i in range(100):
        view_dynamic()
        WAIT(ChainConfig.BLOCK_TIME * (ChainConfig.BLOCK_PER_EPOCH / 2))
