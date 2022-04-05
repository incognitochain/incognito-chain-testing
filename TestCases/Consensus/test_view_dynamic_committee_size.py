"""
Must run test with TestData has full info of all nodes in chain (BEACONS, COMMITTEES, STAKER). Ex: Account_testnet.py
"""
import copy
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, ERROR, WARNING
from Helpers.TestHelper import l3
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from TestCases.Staking_Dynamic_Committee_Size import get_staker_by_tx_id

if ChainConfig.ACTIVE_SHARD != 8:
    fix_node = 12
else:
    fix_node = 8
max_shard_comm_size = 48
cross_stake = False
tracking_reward = True
swapPercent = 8
shard_range = range(ChainConfig.ACTIVE_SHARD)


def test_view_dynamic():
    INFO()
    bs = SUT().get_beacon_best_state_info()
    epoch = bs.get_epoch()
    beacon_height = bs.get_beacon_height()
    candidate_waiting_next_random = []
    candidate_waiting_current_random = []
    pending_validator = {}
    syncing_validator = {}
    shard_committees = {}
    shard_missing_signature_penalty = {}
    reward_dict = {}
    shard_height = bs.get_best_shard_height()
    count_vote_by_subset = {}
    expect_by_shard = {}
    fix_node_off = {}
    b = 0
    s = [0] * ChainConfig.ACTIVE_SHARD
    count_blocks_subset_per_epoch = {}
    for shard_id in shard_range:
        count_blocks_subset_per_epoch[str(shard_id)] = {}
        count_vote_by_subset[str(shard_id)] = [0, 0]
    fist_beacon = (epoch - 1) * ChainConfig.BLOCK_PER_EPOCH + 1
    beacon_block = SUT().get_latest_beacon_block(fist_beacon)
    while not beacon_block.get_shard_states():
        fist_beacon += 1
        if fist_beacon == beacon_height:
            break
        beacon_block = SUT().get_latest_beacon_block(fist_beacon)
    for i in shard_range:
        if not beacon_block:
            break
        try:
            first_height = beacon_block.get_shard_states(i).get_smallest_block_height()
        except AttributeError:
            continue
        for height in range(first_height, shard_height[str(i)]):
            subset = SUT().get_shard_block_by_height(i, height, 2).get_subset_id()
            count_vote_by_subset[str(i)][subset] += 1
    while True:
        # SAVE INFO OLD BLOCK: to compare with next block, verify flow swap, dynamic committee size.
        b4_epoch = copy.deepcopy(epoch)
        b4_beacon_height = copy.deepcopy(beacon_height)
        b4_candidate_waiting_next_random = copy.deepcopy(candidate_waiting_next_random)
        b4_candidate_waiting_current_random = copy.deepcopy(candidate_waiting_current_random)
        b4_pending_validator = copy.deepcopy(pending_validator)
        b4_syncing_validator = copy.deepcopy(syncing_validator)
        b4_shard_committees = copy.deepcopy(shard_committees)
        b4_shard_missing_signature_penalty = copy.deepcopy(shard_missing_signature_penalty)
        b4_reward_dict = copy.deepcopy(reward_dict)
        b4_shard_height = copy.deepcopy(shard_height)
        #############################################################################

        # REQUEST INFO NEW BLOCK
        with ThreadPoolExecutor() as executor:
            thread_info = executor.submit(SUT().get_block_chain_info)
            thread_beacon_bs = executor.submit(SUT().get_beacon_best_state_info)
            thread_beacon_bsd = executor.submit(SUT().get_beacon_best_state_detail_info)
            thread_shard = []
            for shard in shard_range:
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
        syncing_validator = beacon_bsd.get_syncing_validators()
        beacon_committees = beacon_bsd.get_beacon_committee()
        shard_committees = beacon_bsd.get_shard_committees()
        missing_signature_penalty = beacon_bsd.get_missing_signature_penalty()
        staking_tx = beacon_bsd.get_staking_tx()
        shard_height = beacon_bs.get_best_shard_height()
        count_vote_by_shard = beacon_bs.get_number_of_shard_block()

        for i in shard_range:
            shard_bsd = thread_shard[i].result()
            height = shard_bsd.get_shard_height()
            proposer_idx = shard_bsd.get_shard_proposer_inx()
            count_blocks_subset_per_epoch[str(i)][str(height)] = proposer_idx % 2
        if b4_epoch != epoch:
            first_height = {}
            for i in shard_range:
                count_vote_by_subset[str(i)] = [0, 0]
            if current_height_in_epoch != 1:
                fist_beacon = b4_epoch * ChainConfig.BLOCK_PER_EPOCH + 1
                beacon_block = SUT().get_latest_beacon_block(fist_beacon)
                for i in shard_range:
                    try:
                        first_height[str(i)] = beacon_block.get_shard_states(i).get_smallest_block_height()
                    except AttributeError:
                        first_height[str(i)] = shard_height[str(i)]
            else:
                for i in shard_range:
                    first_height[str(i)] = shard_height[str(i)]
        else:
            first_height = b4_shard_height
        for i in shard_range:
            for height in range(first_height[str(i)], shard_height[str(i)]):
                try:
                    subset = count_blocks_subset_per_epoch[str(i)].pop(str(height))
                    count_vote_by_subset[str(i)][subset] += 1
                except KeyError:
                    ERROR(f'Count_blocks_subset_per_epoch: {count_blocks_subset_per_epoch}')
                    subset = SUT().get_shard_block_by_height(i, height, 2).get_subset_id()
                    count_vote_by_subset[str(i)][subset] += 1
        expect_total = int(sum(count_vote_by_shard.values()) / (ChainConfig.ACTIVE_SHARD * 2))
        for i in shard_range:
            expect_by_shard[str(i)] = [expect_total, expect_total]
            shard_missing_signature_penalty[str(i)] = []
            fix_node_off[str(i)] = []
        for shard_id, values in count_vote_by_subset.items():
            for i in range(2):
                expect_by_shard[shard_id][i] = max(expect_total, values[i])

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

        from Objects.IncognitoTestCase import COMMITTEE_ACCOUNTS, STAKER_ACCOUNTS, BEACON_ACCOUNTS

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

        def get_string_info_of_committee(committees_list, base_string=None, subset=None):
            """
            Return string info: private_ of staker, public_k validator, pay_k receiver, reward, auto_staking of each
            validator in committees list.
            @param committees_list: list [BeaconBestStateDetailInfo.Committee]
            @param base_string:
            @param subset
            @return: string
            """
            if base_string is None:
                base_string = ''
            count_signature = None
            count_slash = False
            j = 0
            try:
                for shard_id, shard_committee in shard_committees.items():
                    if committees_list[0] in shard_committee:
                        count_signature = shard_id
                        if committees_list[0] in shard_committee[fix_node:]:
                            j += int(fix_node / 2)
                            count_slash = True
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
                    vote = total_signature - miss_signature
                    if vote <= int(expect_by_shard[count_signature][subset] / 2) and expect_by_shard[count_signature][
                        subset] != 0:
                        try:
                            assert missing_signature_penalty.get(pub_k) is not None
                            if count_slash:
                                shard_missing_signature_penalty[count_signature].append(committee)
                            else:
                                fix_node_off[count_signature].append(committee)

                        except AssertionError:
                            if cross_stake:
                                validator = STAKER_ACCOUNTS.find_account_by_key(pub_k)
                            else:
                                validator = stakers[pub_k]
                            if validator is None:
                                INFO(pub_k)
                            committee_pub_k = validator.committee_public_k
                            total_signature, miss_signature = beacon_bs.get_missing_signature(committee_pub_k)
                            vote = total_signature - miss_signature
                            assert vote >= int(expect_by_shard[count_signature][subset] / 2), INFO(
                                f'{committee_pub_k}: miss_signature: {miss_signature}, total_signature: {total_signature}, subset {expect_by_shard[count_signature][subset]}')

                    else:
                        try:
                            assert missing_signature_penalty.get(pub_k) is None
                        except AssertionError:
                            if cross_stake:
                                validator = STAKER_ACCOUNTS.find_account_by_key(pub_k)
                            else:
                                validator = stakers[pub_k]
                            committee_pub_k = validator.committee_public_k
                            total_signature, miss_signature = beacon_bs.get_missing_signature(committee_pub_k)
                            vote = total_signature - miss_signature
                            assert vote <= int(expect_by_shard[count_signature][subset] / 2) and \
                                   expect_by_shard[count_signature][subset] != 0, INFO(
                                f'{committee_pub_k}: miss_signature: {miss_signature}, total_signature: {total_signature}, subset {expect_by_shard[count_signature][subset]}')
                            if count_slash:
                                shard_missing_signature_penalty[count_signature].append(committee)
                            else:
                                fix_node_off[count_signature].append(committee)
                    base_string += f'- missing signature: {miss_signature}/{total_signature}: {vote}'
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
        string_syncing_validator = "\t--SyncingValidator:\n"
        if syncing_validator is not None:
            for shard, committees in syncing_validator.items():
                string_syncing_validator += f'\t--Shard: {shard}\n'
                string_syncing_validator += get_string_info_of_committee(committees)

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
            string_shard_committees += f'\t-----Shard-{shard} height: {shard_height[shard]}: {count_vote_by_subset.get(shard)}\n'
            string_shard_committees += f'\t\tEVEN: _ {int(expect_by_shard[shard][0] / 2)}\n'
            string_shard_committees += get_string_info_of_committee(committees[:fix_node:2], subset=0)
            string_shard_committees += get_string_info_of_committee(committees[fix_node::2], subset=0)
            string_shard_committees += f'\t\tODD: _ {int(expect_by_shard[shard][1] / 2)}\n'
            string_shard_committees += get_string_info_of_committee(committees[1:fix_node:2], subset=1)
            string_shard_committees += get_string_info_of_committee(committees[1 + fix_node::2], subset=1)

        # Get info of validators have missed signature, exist in penalty list.
        string_missing_signature_penalty = '\tMissing_Signature_Penalty\n'
        for shard, committees in shard_missing_signature_penalty.items():
            for j in range(len(committees)):
                pub_k = committees[j].get_inc_public_key()
                is_auto_stk = beacon_bsd.get_auto_staking_committees(pub_k)
                total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
                if stakers[pub_k] is None:
                    string_missing_signature_penalty += f'\tNone__{l3(pub_k)}__{l3(reward_receiver[pub_k])}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'
                else:
                    try:
                        index = STAKER_ACCOUNTS.account_list.index(stakers[pub_k])
                    except:
                        index = 0
                    string_missing_signature_penalty += f'\tstk{index}: {l3(stakers[pub_k].private_key)}__{l3(pub_k)}__{l3(reward_receiver[pub_k])}, auto_stk: {is_auto_stk} - missing signature: {miss_signature}/{total_signature}\n'

        string_fix_node_off = '\tFix_node off\n'
        for shard, committees in fix_node_off.items():
            for j in range(len(committees)):
                pub_k = committees[j].get_inc_public_key()
                total_signature, miss_signature = beacon_bsd.get_missing_signature(pub_k)
                idx_node = beacon_bsd.get_shard_committees(shard).index(committees[j])
                # idx_node = beacon_bsd.get_result('ShardCommittee')[shard].index(committees[j].dict_data)
                string_fix_node_off += f'\tShard_{shard}_{idx_node}: missing signature: {miss_signature}/{total_signature}\n'

        INFO(f"""
                {string_candidate_waiting_next_random}
                {string_wait_4current_random}
                {string_syncing_validator}
                {string_pending_validator}
                {string_beacon_committee}
                {string_shard_committees}
                {string_missing_signature_penalty}
                {string_fix_node_off}
                        ================================================================
                """)

        for i in shard_range:
            if pending_validator.get(str(i)) is None:
                pending_validator[str(i)] = []

        if b4_shard_committees == {}:
            continue

        INFO('Verify dynamic committee size')

        num_of_assigned_candidates = 0
        num_of_swap_out = {}
        num_of_swap_in = {}
        num_of_slash = {}
        num_of_swap_out_node_normal = {}

        # Calculate the number of candidates for assignment and number of swap in - out
        for shard, committees in b4_shard_committees.items():
            num_of_swap_out[shard] = int(1 / swapPercent * len(b4_shard_committees[shard]))
            num_of_assigned_candidates += max(num_of_swap_out[shard], 1)
            num_of_slash[shard] = min(int(1 / 3 * len(b4_shard_committees[shard])),
                                      len(b4_shard_missing_signature_penalty[shard]))
            if len(b4_shard_committees[shard]) == max_shard_comm_size:
                num_of_swap_out_node_normal[shard] = min(max((num_of_swap_out[shard] - num_of_slash[shard]), 0),
                                                         len(b4_pending_validator[shard]))
            else:
                num_of_swap_out_node_normal[shard] = 0
            n = len(b4_shard_committees[shard]) - num_of_slash[shard] - num_of_swap_out_node_normal[shard]
            num_of_swap_in[shard] = min(max(int(1 / swapPercent * n), 1), (max_shard_comm_size - n))
            if len(b4_shard_committees[shard]) == max_shard_comm_size and num_of_slash[shard] == 0:
                num_of_swap_in[shard] = num_of_swap_out[shard]
        pending_validator_list = []
        for committees in pending_validator.values():
            pending_validator_list += committees
        if current_height_in_epoch == random_time:
            num_of_assigned_candidates = min(len(b4_candidate_waiting_next_random), num_of_assigned_candidates)
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
            syncing_validator_size = sum(len(committees) for committees in syncing_validator.values())
            b4_syncing_validator_size = sum(len(committees) for committees in b4_syncing_validator.values())
            for shard, committees in syncing_validator.items():
                for committee in committees:
                    if committee not in b4_syncing_validator.get(shard, []):
                        assert committee in b4_candidate_waiting_current_random, ERROR(committee)
            assert len(
                b4_candidate_waiting_current_random) + b4_syncing_validator_size == syncing_validator_size
            assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)
        elif b4_beacon_height % block_per_epoch < random_time < beacon_height % block_per_epoch:
            assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)
        elif b4_epoch != epoch:
            for shard, committees in shard_committees.items():
                swap_in = min(len(b4_pending_validator[shard]), num_of_swap_in[shard])
                for committee in b4_shard_missing_signature_penalty[shard][:num_of_slash[shard]]:
                    b4_shard_committees[shard].remove(committee)
                index_break = fix_node + num_of_swap_out_node_normal[shard]
                try:
                    assert committees == b4_shard_committees[shard][:fix_node] + b4_shard_committees[shard][
                                                                                 index_break:] + \
                           b4_pending_validator[shard][:swap_in]
                except:
                    ERROR('Check node in sync pool')
                assert b4_pending_validator[shard][swap_in:] == pending_validator[shard][
                                                                :len(b4_pending_validator[shard]) - swap_in]
                for committee in b4_shard_committees[shard][fix_node:index_break]:
                    if beacon_bsd.get_auto_staking_committees(committee) is True:
                        assert committee in pending_validator[shard]
                    else:
                        assert beacon_bsd.get_auto_staking_committees(
                            committee) is None, beacon_bsd.get_auto_staking_committees(committee)
                for committee in b4_shard_committees[shard][fix_node:index_break]:
                    if committee.is_auto_staking():
                        assert committee in pending_validator[shard]
        else:
            assert shard_committees == b4_shard_committees, ERROR(*shard_committees) and ERROR(*b4_shard_committees)

        info_supplement = f'\tEpoch: {epoch}--Beacon- height: {beacon_height}\nCount_vote_by_shard: {count_vote_by_shard}\n'
        for shard, committees in shard_committees.items():
            info_supplement += f'\t--Shard-{shard} height: {shard_height[shard]}:\n'
        INFO(f'\n{info_supplement}')
        try:
            assert beacon_height > b4_beacon_height
            b = 0
        except AssertionError:
            b += 1
            if b > 1:
                WARNING(f'Beacon stop create block at height {beacon_height}: Round {b}')
        if b4_shard_height != {}:
            for shard_id, height in shard_height.items():
                try:
                    assert height > b4_shard_height[shard_id]
                    s[int(shard_id)] = 0
                except AssertionError:
                    s[int(shard_id)] += 1
                    if s[int(shard_id)] > 1:
                        WARNING(f'Shard {shard_id} stop create block at height {height}: Round {s[int(shard_id)]}')
        WAIT(ChainConfig.BLOCK_TIME)
