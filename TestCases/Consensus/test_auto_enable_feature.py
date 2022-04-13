import math
import random
from concurrent.futures import ThreadPoolExecutor

import pytest
import json

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, ERROR
from Helpers.Time import WAIT, get_current_date_time
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS
from TestCases.Staking_Dynamic_Committee_Size import create_param

swapPercent = 8
shard_committee_size = ChainConfig.SHARD_COMMITTEE_SIZE
block_per_epoch = ChainConfig.BLOCK_PER_EPOCH
test_percentage = 90
committee_percentage_require = 95
shard_range = range(ChainConfig.ACTIVE_SHARD)


def get_features_stats(name_feature):  # Use for ValidatorStat null, have not feature waiting trigger,
    INFO()
    raw = SUT.beacons[0].getfeaturestats()
    data = {"ValidatorStat": raw["ValidatorStat"].get(name_feature),
            "CommitteeStat": raw["CommitteeStat"].get(name_feature),
            "ValidatorSize": raw["CommitteeStat"],
            }
    beacon_height_b4 = 0
    time_wait = 10 * ChainConfig.BLOCK_PER_EPOCH
    while time_wait > 0:
        data_b4 = data
        raw = SUT.beacons[0].getfeaturestats()
        data = {"ValidatorStat": raw["ValidatorStat"].get(name_feature),
                "CommitteeStat": raw["CommitteeStat"].get(name_feature),
                "ValidatorSize": raw["CommitteeStat"],
                }
        if data.get("ValidatorStat") and beacon_height_b4 == 0:
            beacon_height_b4 = SUT.beacons[0].get_beacon_best_state_info().get_beacon_height()
            INFO(f'\nBeacon height{beacon_height_b4}: {data}')
        if data != data_b4:
            beacon_height_af = SUT.beacons[0].get_beacon_best_state_info().get_beacon_height()
            INFO(f'\nBeacon height {beacon_height_af}: \n'
                 f'\tData_b4: {data_b4}\n'
                 f'\tData: {data}')
        if not data.get("ValidatorStat") and beacon_height_b4 != 0:
            break
        WAIT(ChainConfig.BLOCK_TIME)
        time_wait -= 1
    INFO(f'\nBeacon height start stats: {beacon_height_b4}\n'
         f'Beacon height finish stats: {beacon_height_af}\n'
         f'Data stats: {data_b4}')
    triggered_feature = SUT().get_beacon_best_state_info().get_triggered_feature()
    assert triggered_feature.get(name_feature) is not None
    INFO(f'{name_feature}: {triggered_feature.get(name_feature)}')


@pytest.mark.parametrize("mode_committee, mode_committee_pending", [
    # ("Full", "Full"),
    # ("More", "More"),
    # ("More", "Less"),
    ("Less", "More"),
    # ("Less", "Less"),
])
def test_auto_enable_new_feature(mode_committee, mode_committee_pending):
    INFO()
    name_feature = f'feature_{get_current_date_time("%d%H%M%S")}'
    # name_feature = f'feature_test_1'
    executor = ThreadPoolExecutor()
    executor.submit(get_features_stats, name_feature)
    bs = SUT().get_beacon_best_state_info()
    i = ChainConfig.BLOCK_PER_EPOCH
    while bs.get_beacon_height() % i != 1:
        WAIT(5)
        bs = SUT().get_beacon_best_state_info()
    committee_shard = bs.get_shard_committees()
    pending_shard = bs.get_shard_pending_validator()
    min_trigger = bs.get_beacon_height() + 2
    param = create_param(name_feature, min_trigger, test_percentage)
    SUT().system_rpc().set_auto_enable_feature_config(param)
    for node in SUT.beacons:
        node.system_rpc().set_auto_enable_feature_config(param)
    nodes_updated = {}
    shard_test = random.randint(0, ChainConfig.ACTIVE_SHARD - 1)
    INFO(f"Shard {shard_test} test mode_committee")
    for i in shard_range:
        nodes_updated[str(i)] = []
        size_committee_shard = len(committee_shard[str(i)])
        if mode_committee == "More":
            num_of_node_need_set_config = math.ceil(size_committee_shard * committee_percentage_require / 100)
        elif mode_committee == "Less":
            if i == shard_test:
                num_of_node_need_set_config = math.ceil(size_committee_shard * committee_percentage_require / 100 - 1)
            else:
                num_of_node_need_set_config = math.ceil(size_committee_shard * committee_percentage_require / 100)
        elif mode_committee == "Full":
            num_of_node_need_set_config = size_committee_shard
        list_idx_node_update = random.sample(range(ChainConfig.FIX_BLOCK_VALIDATOR, size_committee_shard),
                                             num_of_node_need_set_config - ChainConfig.FIX_BLOCK_VALIDATOR)
        list_idx_node_update.sort()
        print(f'list_idx_node_update{list_idx_node_update}')
        for idx in range(ChainConfig.FIX_BLOCK_VALIDATOR):
            SUT.shards[i].get_node(idx).system_rpc().set_auto_enable_feature_config(param)
            nodes_updated[str(i)].append(f'shard_{i}_{idx}')
        for idx in list_idx_node_update:
            key = committee_shard[str(i)][idx]
            acc = STAKER_ACCOUNTS.find_account_by_key(key)
            stk_idx = STAKER_ACCOUNTS.account_list.index(acc)
            SUT.stakers[stk_idx].system_rpc().set_auto_enable_feature_config(param)
            nodes_updated[str(i)].append(f'staker_{stk_idx}')
        calculate_percent_shard_committee = len(nodes_updated[str(i)]) / size_committee_shard * 100
        string = f'\nCOMMITTEE\nSet config for shard_{i}, {len(nodes_updated[str(i)])}/{size_committee_shard} node, account for {int(calculate_percent_shard_committee)}%\n'
        string += f'List nodes updated: {nodes_updated[str(i)]}'
        INFO(string)
    shard_test = random.randint(0, ChainConfig.ACTIVE_SHARD - 1)
    INFO(f"Shard {shard_test} test mode_committee_pending")
    for i in shard_range:
        size_pending_committee = len(pending_shard[str(i)]) + len(committee_shard[str(i)])
        if mode_committee_pending == "More":
            num_of_node_need_set_config = math.ceil(size_pending_committee * test_percentage / 100)
        elif mode_committee_pending == "Less":
            if i == shard_test:
                num_of_node_need_set_config = math.ceil(size_pending_committee * test_percentage / 100 - 1)
            else:
                num_of_node_need_set_config = math.ceil(size_pending_committee * test_percentage / 100)
        elif mode_committee_pending == "Full":
            num_of_node_need_set_config = size_pending_committee
        remain_node_need_set_config = num_of_node_need_set_config - len(nodes_updated[str(i)])
        list_idx_node_pending = random.sample(range(len(pending_shard[str(i)])), remain_node_need_set_config)
        list_idx_node_pending.sort()
        print(f'list_idx_node_pending{list_idx_node_pending}')
        for idx in list_idx_node_pending:
            key = pending_shard[str(i)][idx]
            acc = STAKER_ACCOUNTS.find_account_by_key(key)
            stk_idx = STAKER_ACCOUNTS.account_list.index(acc)
            SUT.stakers[stk_idx].system_rpc().set_auto_enable_feature_config(param)
            nodes_updated[str(i)].append(f'staker_{stk_idx}')
        calculate_percent_pending_committee = len(nodes_updated[str(i)]) / size_pending_committee * 100
        string = f'\nPENDING+COMMITTEE\nSet config for shard_{i}, {len(nodes_updated[str(i)])}/{size_pending_committee} node, account for {int(calculate_percent_pending_committee)}%\n'
        string += f'List nodes updated: {nodes_updated[str(i)]}'
        INFO(string)


def test_get_config():
    INFO()
    string = "Get_config\n"
    with ThreadPoolExecutor() as e:
        thread_pool_beacon = []
        for node in SUT.beacons:
            thread = e.submit(node.get_config_feature)
            thread_pool_beacon.append(thread)
        thread_pool_shard = {}
        for id in range(ChainConfig.ACTIVE_SHARD):
            thread_pool_shard[str(id)] = []
            for node in SUT.shards[id]:
                thread = e.submit(node.get_config_feature)
                thread_pool_shard[str(id)].append(thread)
        thread_pool_staker = []
        for node in SUT.stakers:
            thread = e.submit(node.get_config_feature)
            thread_pool_staker.append(thread)
    for i in range(len(thread_pool_beacon)):
        data = thread_pool_beacon[i].result()
        string += f'Beacon_{i}: {data}\n'
    for id, threads in thread_pool_shard.items():
        for i in range(len(threads)):
            data = threads[i].result()
            string += f'Shard_{id}_{i}: {data}\n'
    for i in range(len(thread_pool_staker)):
        data = thread_pool_staker[i].result()
        string += f'Staker_{i}: {data}\n'

    INFO(string)


def test_set_config():
    INFO()
    name_feature = f'feature_test_2'
    bs = SUT().get_beacon_best_state_info()
    min_trigger = bs.get_beacon_height() + 3
    param = create_param(name_feature, min_trigger, test_percentage)
    SUT().system_rpc().set_auto_enable_feature_config(param)
    with ThreadPoolExecutor() as e:
        for node in SUT.beacons:
            e.submit(node.system_rpc().set_auto_enable_feature_config, param)
        for shard in SUT.shards:
            for node in shard[:-3]:
                e.submit(node.system_rpc().set_auto_enable_feature_config, param)
        # for node in SUT.stakers:
        #
        #     e.submit(node.system_rpc().set_auto_enable_feature_config, param)


def test_update_feature_for_all_nodes():
    INFO()
    param = {}
    triggered_feature = SUT().get_beacon_best_state_info().get_triggered_feature()
    for name, height in triggered_feature.items():
        param[name] = {"MinTriggerBlockHeight": height, "ForceBlockHeight": 1000000000,
                       "RequiredPercentage": 100}
    param_str = json.dumps(param)
    INFO(f'Create param: \n\t{param_str}')
    with ThreadPoolExecutor() as e:
        for node in SUT.beacons:
            e.submit(node.system_rpc().set_auto_enable_feature_config, param_str)
        for id in SUT.shards:
            for node in id:
                e.submit(node.system_rpc().set_auto_enable_feature_config, param_str)
        for node in SUT.stakers:
            e.submit(node.system_rpc().set_auto_enable_feature_config, param_str)


def test_view_stats():
    get_features_stats("feature_test_2")
