import copy
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, ERROR
from Helpers.TestHelper import l3
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT, BEACON_ACCOUNTS, COMMITTEE_ACCOUNTS, STAKER_ACCOUNTS
from TestCases.Staking_Dynamic_Committee_Size import get_staker_by_tx_id

fix_node = ChainConfig.FIX_BLOCK_VALIDATOR
max_shard_comm_size = ChainConfig.SHARD_COMMITTEE_SIZE
staking_flowv2_height = 1
enable_slashing_staking_flowV2 = 1
slashingV2 = True
cross_stake = False
tracking_reward = False


def view_dynamic(epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator,
                 shard_committees, beacon_height, shard_missing_signature_penalty):
    """
    Display dynamic committee size follow each beacon height, verify swap in-out according to staking flow v2
    @param epoch:
    @param reward_dict: dict of {public_key: reward}
    @param candidate_waiting_next_random: a list candidate shard waiting next random: list of BeaconBestStateDetailInfo.Committee
    @param candidate_waiting_current_random: a list candidate shard waiting current random: list of BeaconBestStateDetailInfo.Committee
    @param pending_validator: a dict candidate shard pending: Dict of {shard_num: list of BeaconBestStateDetailInfo.Committee}
    @param shard_committees: a dict shard committees: dict of {shard_num: list of BeaconBestStateDetailInfo.Committee}
    @param beacon_height: beacon height: integer
    @param shard_missing_signature_penalty:
    @return:
    """
    # SAVE INFO OLD BLOCK: to compare with next block, verify flow swap, dynamic committee size.
    b4_epoch = copy.deepcopy(epoch)
    b4_beacon_height = copy.deepcopy(beacon_height)
    b4_candidate_waiting_next_random = copy.deepcopy(candidate_waiting_next_random)
    b4_candidate_waiting_current_random = copy.deepcopy(candidate_waiting_current_random)
    b4_pending_validator = copy.deepcopy(pending_validator)
    b4_shard_committees = copy.deepcopy(shard_committees)
    b4_shard_missing_signature_penalty = copy.deepcopy(shard_missing_signature_penalty)
    b4_reward_dict = copy.deepcopy(reward_dict)
    #############################################################################

    # REQUEST INFO NEW BLOCK
    with ThreadPoolExecutor() as executor:
        thread_info = executor.submit(SUT().get_block_chain_info)
        thread_beacon_bs = executor.submit(SUT().get_beacon_best_state_info)
        thread_beacon_bsd = executor.submit(SUT().get_beacon_best_state_detail_info)
        thread_shard = []
        for shard in range(ChainConfig.ACTIVE_SHARD):
            thread = executor.submit(SUT().get_shard_best_state_detail_info, shard)
            thread_shard.append(thread)
    block_chain_info = thread_info.result()
    remaining_block_epoch = block_chain_info.get_beacon_block().get_remaining_block_epoch()
    block_per_epoch = block_chain_info.get_block_per_epoch_number()
    random_time = block_per_epoch / 2
    current_height_in_epoch = block_per_epoch - remaining_block_epoch  # number of blocks created in the current epoch
    beacon_bs = thread_beacon_bs.result()
    reward_receiver = beacon_bs.get_reward_receiver()
    beacon_bsd = thread_beacon_bsd.result()
    epoch = beacon_bsd.get_epoch()
    beacon_height = beacon_bsd.get_beacon_height()
    current_height_in_epoch = beacon_height % block_per_epoch  # comment if have TestnetEpochV2BreakPoint
    random_number = beacon_bsd.get_current_random_number()
    candidate_waiting_next_random = beacon_bsd.get_candidate_shard_waiting_next_random()
    candidate_waiting_current_random = beacon_bsd.get_candidate_shard_waiting_current_random()
    pending_validator = beacon_bsd.get_shard_pending_validator()
    beacon_committees = beacon_bsd.get_beacon_committee()
    shard_committees = beacon_bsd.get_shard_committees()
    missing_signature_penalty = beacon_bsd.get_missing_signature_penalty()
    staking_tx = beacon_bsd.get_staking_tx()
    shard_height = {}
    for i in range(len(thread_shard)):
        shard_bsd = thread_shard[i].result()
        shard_height[str(i)] = shard_bsd.get_shard_height()

    if slashingV2:
        count_vote_by_shard = beacon_bs.get_number_of_shard_block()
        expect_total = int(sum(count_vote_by_shard.values()) / ChainConfig.ACTIVE_SHARD)
    else:
        expect_total = 0
        count_vote_by_shard = {}

    INFO(f"""
                ================================================================
        private_key_staker - public_key_validator - payment_add_receive_reward
        ---- epoch: {epoch} - beacon_height: {beacon_height} - at: {current_height_in_epoch}/{block_per_epoch} - rand: {random_number} ----
        """)

    # Get reward received and staker with public_key
    def get_reward_received():
        with ThreadPoolExecutor() as executor:
            for pub_k, pay_k in reward_receiver.items():
                thread = executor.submit(SUT().transaction().get_reward_amount, pay_k)
                reward_dict[pub_k] = thread
        for pub_k, thread in reward_dict.items():
            try:
                reward_dict[pub_k] = thread.result().get_result("PRV")
            except AttributeError:
                pass
        return reward_dict

    def get_stakers():
        stakers = {}
        with ThreadPoolExecutor() as executor:
            for pub_k, tx_id in staking_tx.items():
                staker = (BEACON_ACCOUNTS + COMMITTEE_ACCOUNTS).find_account_by_key(pub_k)
                if staker:
                    # beacons & shard committees have not stake transaction
                    stakers[pub_k] = staker
                    continue
                if cross_stake:
                    thread = executor.submit(get_staker_by_tx_id, tx_id)
                    stakers[pub_k] = thread
                else:
                    staker = STAKER_ACCOUNTS.find_account_by_key(pub_k)
                    stakers[pub_k] = staker
        for pub_k, thread in stakers.items():
            try:
                stakers[pub_k] = thread.result()
            except AttributeError:
                pass
        return stakers

    with ThreadPoolExecutor() as executor_m:
        if tracking_reward:
            thread_reward_dict = executor_m.submit(get_reward_received)
        thread_stakers = executor_m.submit(get_stakers)

    if tracking_reward:
        reward_dict = thread_reward_dict.result()
    stakers = thread_stakers.result()

    def get_string_info_of_committee(committees_list, base_string=None):
        """
        Return string info: private_ of staker, public_k validator, pay_k receiver, reward, auto_staking of each
        validator in committees list.
        @param committees_list: list [BeaconBestStateDetailInfo.Committee]
        @param base_string:
        @return: string
        """
        if base_string is None:
            base_string = ''
        global missing_signature_penalty_list
        missing_signature_penalty_list = []
        count_signature = None
        j = 0
        try:
            for shard_id, shard_committee in shard_committees.items():
                if committees_list[0] in shard_committee:
                    count_signature = shard_id
                    if committees_list[0] in shard_committee[fix_node:]:
                        j += fix_node
                    break
        except IndexError:
            pass
        for committee in committees_list:
            pub_k = committee.get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            try:
                reward_increase = reward_dict.get(pub_k) - b4_reward_dict.get(pub_k)
            except:
                reward_increase = None
            if stakers[pub_k] is None:
                str = ""
                if tracking_reward:
                    base_string += f'\t{j}_{str}\t: None__{l3(pub_k)}__{l3(reward_receiver.get(pub_k))} - reward: {reward_dict.get(pub_k)}, rwinc: {reward_increase} - auto_stk: {is_auto_stk}'
                else:
                    base_string += f'\t{j}_{str}\t: None__{l3(pub_k)}__{l3(reward_receiver.get(pub_k))} - auto_stk: {is_auto_stk}'
            else:
                try:
                    index = STAKER_ACCOUNTS.account_list.index(stakers[pub_k])
                    str = f'stk{index}'
                except ValueError:
                    str = ""
                if tracking_reward:
                    base_string += f'\t{j}_{str}\t: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver.get(pub_k))} - reward: {reward_dict.get(pub_k)}, rwinc: {reward_increase} - auto_stk: {is_auto_stk}'
                else:
                    base_string += f'\t{j}_{str}\t: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver.get(pub_k))} - auto_stk: {is_auto_stk}'
            if count_signature is not None:
                total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
                if slashingV2:
                    if total_signature < count_vote_by_shard[count_signature]:
                        miss_signature += count_vote_by_shard[count_signature] - total_signature
                    total_signature = count_vote_by_shard[count_signature]
                if total_signature is not None:
                    if total_signature < expect_total:
                        miss_signature += expect_total - total_signature
                        total_signature = expect_total
                    if miss_signature >= total_signature / 2 and total_signature != 0:
                    # if miss_signature >= total_signature / 2:
                        assert missing_signature_penalty.get(pub_k) is not None, INFO(f'{pub_k}: miss_signature: {miss_signature}, total_signature: {total_signature}, expect_total: {expect_total}')
                        missing_signature_penalty_list.append(committee)
                    else:
                        assert missing_signature_penalty.get(pub_k) is None, INFO(f'{pub_k}: miss_signature: {miss_signature}, total_signature: {total_signature}, expect_total: {expect_total}')
                    base_string += f'- missing signature: {miss_signature}/{total_signature}'
            base_string += '\n'
            j += 1
        return base_string

    # ./ Info of candidates in waiting next random:
    string = '\t--wait4random:\n'
    string_candidate_waiting_next_random = get_string_info_of_committee(candidate_waiting_next_random, string)

    # ./ Info of candidates waiting current random:
    string = '\t--wait4currentRandom:\n'
    string_wait_4current_random = get_string_info_of_committee(candidate_waiting_current_random, string)

    # ./ Info of validators in shard pending list:
    string_pending_validator = "\t--PendingValidator:\n"
    for shard, committees in pending_validator.items():
        string_pending_validator += f'\t--Shard: {shard}\n'
        string_pending_validator += get_string_info_of_committee(committees)

    # ./ Info of committees in beacon committee:
    string = f'\t--Beacon- height: {beacon_height}\n'
    string_beacon_committee = get_string_info_of_committee(beacon_committees, string)

    # ./ Info of committees in shard committee:
    string_shard_committees = '\t--Shard_committee\n'
    for shard, committees in shard_committees.items():
        string_shard_committees += f'\t-----Shard-{shard} height: {shard_height[shard]}: {count_vote_by_shard.get(str(shard))}\n'
        string_shard_committees += '\t--FIX node\n'
        string_shard_committees += get_string_info_of_committee(committees[:fix_node])
        string_shard_committees += '\t--Normal node\n'
        string_shard_committees += get_string_info_of_committee(committees[fix_node:])
        shard_missing_signature_penalty[shard] = missing_signature_penalty_list

    # Get info of validators have missed signature, exist in penalty list.
    string_missing_signature_penalty = '\tMissing_Signature_Penalty\n'
    for shard, committees in shard_missing_signature_penalty.items():
        for j in range(len(committees)):
            pub_k = committees[j].get_inc_public_key()
            is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
            total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
            if stakers[pub_k] is None:
                # INFO(pub_k)
                string_missing_signature_penalty += f'\tNone__{l3(pub_k)}__{l3(reward_receiver[pub_k])}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'
            else:
                try:
                    index = STAKER_ACCOUNTS.account_list.index(stakers[pub_k])
                except:
                    index = 0
                string_missing_signature_penalty += f'\tstk{index}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'

    INFO(f"""
        {string_candidate_waiting_next_random}
        {string_wait_4current_random}
        {string_pending_validator}
        {string_beacon_committee}
        {string_shard_committees}
        {string_missing_signature_penalty}
                ================================================================
        """)

    if beacon_height <= staking_flowv2_height:
        # this test script not support verify staking flowV1, only can view
        return epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator, shard_committees, beacon_height, shard_missing_signature_penalty, shard_height

    if beacon_height <= enable_slashing_staking_flowV2:
        # shard_missing_signature_penalty not empty but disable slashing, so set it is empty to verify.
        for shard, committees in shard_committees.items():
            b4_shard_missing_signature_penalty[shard] = []

    for i in range(ChainConfig.ACTIVE_SHARD):
        if pending_validator.get(str(i)) is not None:
            continue
        pending_validator[str(i)] = []

    if b4_shard_committees == {}:
        return epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator, shard_committees, beacon_height, shard_missing_signature_penalty, shard_height

    INFO('Verify dynamic committee size')

    num_of_assigned_candidates = 0
    num_of_swap_out = {}
    num_of_swap_in = {}

    # Calculate the number of candidates for assignment and number of swap in - out
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
        if len(b4_candidate_waiting_next_random) < num_of_assigned_candidates:
            num_of_assigned_candidates = len(b4_candidate_waiting_next_random)
        if not b4_candidate_waiting_current_random:
            assert candidate_waiting_current_random == b4_candidate_waiting_next_random[
                                                       :num_of_assigned_candidates], ERROR(
                *candidate_waiting_current_random) and ERROR(
                *b4_candidate_waiting_next_random[:num_of_assigned_candidates])
        else:
            assert candidate_waiting_current_random == b4_candidate_waiting_current_random, ERROR(
                *candidate_waiting_current_random) and ERROR(*b4_candidate_waiting_current_random)
        for committee in b4_candidate_waiting_next_random[num_of_assigned_candidates:]:
            assert committee in candidate_waiting_next_random, ERROR(committee)
    else:
        assert candidate_waiting_current_random == [], ERROR(*candidate_waiting_current_random)

    if b4_candidate_waiting_current_random:
        for shard, committees in pending_validator.items():
            for committee in committees:
                if committee not in b4_pending_validator[shard]:
                    assert committee in b4_candidate_waiting_current_random, ERROR(committee)
        assert len(
            b4_candidate_waiting_current_random) + b4_pending_validator_size == pending_validator_size, f'{len(b4_candidate_waiting_current_random) + b4_pending_validator_size} == {pending_validator_size}'
        assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)
    elif b4_beacon_height % block_per_epoch < random_time < beacon_height % block_per_epoch:
        assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)
    elif b4_epoch != epoch:
        for shard, committees in shard_committees.items():
            if len(b4_pending_validator[shard]) > num_of_swap_in[shard]:
                swap_in = num_of_swap_in[shard]
            else:
                swap_in = len(b4_pending_validator[shard])

            if len(b4_shard_missing_signature_penalty[shard]) >= num_of_swap_out[shard]:
                for committee in b4_shard_missing_signature_penalty[shard][:num_of_swap_out[shard]]:
                    b4_shard_committees[shard].remove(committee)
                swap_out = 0
            else:
                swap_out = num_of_swap_out[shard] - len(b4_shard_missing_signature_penalty[shard])
                for committee in b4_shard_missing_signature_penalty[shard]:
                    b4_shard_committees[shard].remove(committee)
            index_break = fix_node + swap_out
            assert committees == b4_shard_committees[shard][:fix_node] + b4_shard_committees[shard][index_break:] + \
                   b4_pending_validator[shard][:swap_in], ERROR(*committees) and ERROR(*(
                    b4_shard_committees[shard][:fix_node] + b4_shard_committees[shard][index_break:] +
                    b4_pending_validator[shard][:swap_in]))
            assert b4_pending_validator[shard][swap_in:] == pending_validator[shard][
                                                            :len(b4_pending_validator[shard]) - swap_in], ERROR(
                *b4_pending_validator[shard][swap_in:]) and ERROR(
                *(pending_validator[shard][:len(b4_pending_validator[shard]) - swap_in]))
            for committee in b4_shard_committees[shard][fix_node:index_break]:
                if beacon_bsd.get_auto_staking_committees(committee) is True:
                    assert committee in pending_validator_list, ERROR(committee)
                else:
                    assert beacon_bsd.get_auto_staking_committees(
                        committee) is None, beacon_bsd.get_auto_staking_committees(committee)
    else:
        assert b4_pending_validator == pending_validator, ERROR(*b4_pending_validator) and ERROR(*pending_validator)
        assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)

    return epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator, shard_committees, beacon_height, shard_missing_signature_penalty, shard_height


def test_view_dynamic():
    reward_dict = {}
    candidate_waiting_next_random = []
    candidate_waiting_current_random = []
    pending_validator = {}
    shard_committees = {}
    beacon_height_b4 = 0
    shard_missing_signature_penalty = {}
    epoch = 0
    shard_height_b4 = {}
    b = 0
    s = [0]*ChainConfig.ACTIVE_SHARD
    while True:
        epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator, shard_committees, beacon_height, shard_missing_signature_penalty, shard_height = view_dynamic(
            epoch, reward_dict, candidate_waiting_next_random, candidate_waiting_current_random, pending_validator,
            shard_committees, beacon_height_b4, shard_missing_signature_penalty)
        print(f'\tEpoch: {epoch}--Beacon- height: {beacon_height}\n')
        for shard, committees in shard_committees.items():
            print(f'\t--Shard-{shard} height: {shard_height[shard]}:\n')
        try:
            assert beacon_height > beacon_height_b4
            b = 0
        except:
            b += 1
            if b > 1:
                INFO(f'Beacon stop create block at height {beacon_height}: ')
        if shard_height_b4 != {}:
            for shard_id, height in shard_height.items():
                try:
                    assert height > shard_height_b4[shard_id]
                    s[int(shard_id)] = 0
                except:
                    s[int(shard_id)] += 1
                    if s[int(shard_id)] > 1:
                        INFO(f'Shard {shard_id} stop create block at height {height}: ')
        beacon_height_b4 = beacon_height
        shard_height_b4 = shard_height
        if ChainConfig.ACTIVE_SHARD != 8:
            WAIT(ChainConfig.BLOCK_TIME)
        else:
            WAIT(5)
