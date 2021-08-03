import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

import pytest
from Configs.Configs import ChainConfig
from Drivers.Response import Response
from Helpers.Logging import INFO, ERROR, STEP
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import BEACON_ACCOUNTS, COMMITTEE_ACCOUNTS, STAKER_ACCOUNTS, ACCOUNTS
from Objects.IncognitoTestCase import SUT

group_acc = BEACON_ACCOUNTS + COMMITTEE_ACCOUNTS + STAKER_ACCOUNTS + ACCOUNTS
list_shard1 = []
list_shard0 = []
for acc in ACCOUNTS:
    if acc.shard % 2 == 0:
        list_shard0.append(acc)
    else:
        list_shard1.append(acc)

shard1_sender1 = list_shard1[0]
shard1_sender2 = list_shard1[1]
shard0_sender = list_shard0[0]
shard1_receiver = list_shard1[2]
shard0_receiver = list_shard0[1]
list_acc_test = [shard1_sender1, shard1_sender2, shard0_sender, shard1_receiver, shard0_receiver]
amount = 1000
node_start_tear_down = []
tx_pending = []
tx_success = []
fee_dict = {}


def no_setup_module():
    defrag = COIN_MASTER.defragment_account(100000000000000000)
    if defrag is not None:
        defrag.subscribe_transaction()
    for acc in [shard1_sender1, shard1_sender2]:
        num = 0
        list_coin = acc.list_unspent_coin()
        for coin in list_coin:
            if int(coin.get_value()) >= amount * 2:
                num += 1
        if num < 2:
            acc.defragment_account()
            COIN_MASTER.send_prv_to(acc, amount * 4)
            WAIT(60)


def teardown_function():
    INFO("Tear down")
    for node in node_start_tear_down:
        node.start_node()


@pytest.mark.parametrize("time_stop", [
    ChainConfig.BLOCK_PER_EPOCH * ChainConfig.BLOCK_TIME,
    70
])
def test_miss_sig(time_stop):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    beacon_height = beacon_bsd.get_beacon_height()
    shard_1_height = beacon_bsd.get_best_shard_height(1)
    shard_1_committees = beacon_bsd.get_shard_committees(1)
    auto_staking = beacon_bsd.get_auto_staking_committees()
    INFO(f'Current have {len(auto_staking)} committee')
    assert len(
        auto_staking) <= ChainConfig.SHARD_COMMITTEE_SIZE * ChainConfig.ACTIVE_SHARD + ChainConfig.BEACON_COMMITTEE_SIZE
    i = 0
    INFO('Check all stakers have run node')
    for committee in auto_staking:
        acc = group_acc.find_account_by_key(committee._inc_public_key)
        validator_k = acc.validator_key
        node = SUT.find_node_by_validator_k(validator_k)
        assert node is not None and INFO(f'Validator {i} run node ok'), ERROR(
            f'Validator key {validator_k} is not run node ')
        i += 1

    INFO('Calculate the numbers of node to kill')
    len_committee_shard = len(shard_1_committees)
    num_node_kill = len_committee_shard - (int(len_committee_shard / 3 * 2))
    node_kill_now = []
    for committee in shard_1_committees[4:(4 + num_node_kill)]:
        acc = group_acc.find_account_by_key(committee._inc_public_key)
        validator_k = acc.validator_key
        node = SUT.find_node_by_validator_k(validator_k)
        if shard_1_committees.index(committee) == (4 + num_node_kill) - 1:
            node_kill_af = node
            break
        node_kill_now.append(node)

    INFO('Get balance before test:')
    bal_b4 = {}
    for account in list_acc_test:
        bal_b4[account] = account.get_balance()

    STEP(1, 'Kill node under 1/3 committee, verify shard active')
    for node in node_kill_now:
        node.kill_node()
        node_start_tear_down.append(node)

    WAIT(50)
    beacon_bsd_af = SUT().get_beacon_best_state_detail_info()
    beacon_height_af = beacon_bsd_af.get_beacon_height()
    shard_1_height_af = beacon_bsd_af.get_best_shard_height(1)
    INFO(f'Beacon: bl_height b4: {beacon_height}, bl_height af: {beacon_height_af}')
    INFO(f'Shard 1: bl_height b4: {shard_1_height}, bl_height af: {shard_1_height_af}')
    assert shard_1_height_af - shard_1_height == beacon_height_af - beacon_height, ERROR(f'Shard 1 active WRONG')
    assert beacon_height_af - beacon_height >= 5 and INFO(beacon_height_af - beacon_height)

    if beacon_height_af % ChainConfig.BLOCK_PER_EPOCH != 1:
        epoch = beacon_bsd_af.get_epoch()
        beacon_height_first = ChainHelper.cal_first_height_of_epoch(epoch + 1)
        ChainHelper.wait_till_beacon_height(beacon_height_first)
        beacon_bsd_af = SUT().get_beacon_best_state_detail_info()
        beacon_height_af = beacon_bsd_af.get_beacon_height()
        shard_1_height_af = beacon_bsd_af.get_best_shard_height(1)

    INFO('Create and send transactions')

    thread_pool = {}
    executor = ThreadPoolExecutor()
    thread_1 = executor.submit(shard1_sender1.send_prv_to, shard1_receiver, amount)
    thread_pool[shard1_sender1] = thread_1
    thread_2 = executor.submit(shard0_sender.send_prv_to, shard1_receiver, amount)
    thread_pool[shard0_sender] = thread_2
    thread_3 = executor.submit(shard1_sender2.send_prv_to, shard0_receiver, amount)
    thread_pool[shard1_sender2] = thread_3

    STEP(2, 'Kill node over 1/3 committee, verify shard not active')
    node_kill_af.kill_node()
    node_start_tear_down.append(node_kill_af)
    executor1 = ThreadPoolExecutor()
    thread = executor1.submit(WAIT, time_stop)

    concurrent.futures.wait(thread_pool.values())
    WAIT(30)
    INFO('Verify transactions')
    for sender, thread in thread_pool.items():
        tx = thread.result()
        tx_id = tx.get_tx_id()
        fee_dict[sender] = tx.get_transaction_by_hash().get_fee()
        block_height = tx.get_transaction_by_hash().get_block_height()
        if block_height:
            tx_success.append(sender)
        else:
            tx_pending.append(tx_id)

    INFO('Check mem pool')
    mem_pool_tx = SUT().get_mem_pool_txs()
    for tx_id in tx_pending:
        assert tx_id in mem_pool_tx
    for acc in tx_success:
        assert acc.get_balance() == bal_b4[acc] - amount - fee_dict[acc]
        bal_b4[acc] = acc.get_balance()

    INFO('Verify create and send transactions when shard not active')

    thread_pool = {}
    with ThreadPoolExecutor() as executor2:
        thread_1 = executor2.submit(shard1_sender1.send_prv_to, shard1_receiver, amount)
        thread_pool[shard1_sender1] = thread_1
        thread_2 = executor2.submit(shard0_sender.send_prv_to, shard1_receiver, amount)
        thread_pool[shard0_sender] = thread_2
        thread_3 = executor2.submit(shard1_sender2.send_prv_to, shard0_receiver, amount)
        thread_pool[shard1_sender2] = thread_3

    WAIT(30)
    for sender, thread in thread_pool.items():
        tx = thread.result()
        tx_id = tx.get_tx_id()
        fee_dict[sender] += tx.get_transaction_by_hash().get_fee()
        block_height = tx.get_transaction_by_hash().get_block_height()
        if block_height:
            tx_success.append(sender)
        else:
            tx_pending.append(tx_id)

    INFO('Check mem pool')
    mem_pool_tx = SUT().get_mem_pool_txs()
    for tx_id in tx_pending:
        assert tx_id in mem_pool_tx

    INFO('Get beacon best state detail')
    beacon_bsd_af_2 = SUT().get_beacon_best_state_detail_info()
    INFO('Get shard 1 best state detail')
    shard_1_bsd = SUT().get_shard_best_state_detail_info(1)

    concurrent.futures.wait([thread])

    beacon_height_af_2 = beacon_bsd_af_2.get_beacon_height()
    INFO(f'Beacon: bl_height b4: {beacon_height_af}, bl_height af: {beacon_height_af_2}')
    assert beacon_height_af_2 - beacon_height_af >= int(time_stop / ChainConfig.BLOCK_TIME) and INFO(
        beacon_height_af_2 - beacon_height_af)
    shard_1_height_af_2 = beacon_bsd_af_2.get_best_shard_height(1)
    INFO(f'Shard 1: bl_height b4: {shard_1_height_af}, bl_height af: {shard_1_height_af_2}')
    assert shard_1_height_af_2 - shard_1_height_af <= 3 and INFO(shard_1_height_af_2 - shard_1_height_af), \
        ERROR(f'WRONG: Shard 1 still active')

    STEP(3, 'Start node')
    for node in [node_kill_af] + node_kill_now:
        node.start_node()
        node_start_tear_down.remove(node)

    WAIT(100)
    INFO('Get beacon best state detail')
    beacon_bsd_af_3 = SUT().get_beacon_best_state_detail_info()
    INFO('Get shard 1 best state detail')
    shard_1_bsd_af = SUT().get_shard_best_state_detail_info(1)

    beacon_height_af_3 = beacon_bsd_af_3.get_beacon_height()
    INFO(f'Beacon: bl_height b4: {beacon_height_af_2}, bl_height af: {beacon_height_af_3}')
    assert beacon_height_af_3 - beacon_height_af_2 >= 10 and INFO(beacon_height_af_3 - beacon_height_af_2)
    shard_1_height_af_3 = beacon_bsd_af_3.get_best_shard_height(1)
    INFO(f'Shard 1: bl_height b4: {shard_1_height_af_2}, bl_height af: {shard_1_height_af_3}')
    assert (shard_1_height_af_3 - shard_1_height_af_2) >= 5 and INFO(shard_1_height_af_3 - shard_1_height_af_2), ERROR(
        f'Shard 1 active WRONG')

    INFO('Check tx leave mem pool')
    mem_pool_tx = SUT().get_mem_pool_txs()
    for tx_id in tx_pending:
        assert tx_id not in mem_pool_tx
        shard_block_height = Response().get_transaction_by_hash(tx_id).get_block_height()
        assert shard_block_height

    INFO('Check balance')
    bal_af = {}
    string = ''
    for account in list_acc_test:
        bal_af[account] = account.get_balance()
        string += f'\tbal_b4 - bal_af : {bal_b4[account]} - {bal_af[account]}\n'
    INFO(string)

    for account in list_acc_test[:3]:
        assert bal_af[account] == bal_b4[account] - fee_dict[account] - amount * 2
    assert bal_af[shard0_receiver] == bal_b4[shard0_receiver] + amount * 2
    assert bal_af[shard1_receiver] == bal_b4[shard1_receiver] + amount * 4

    beacon_height_follow_shard = shard_1_bsd.get_beacon_height()
    beacon_height_af_follow_shard = shard_1_bsd_af.get_beacon_height()
    num_block_beacon = beacon_height_af_follow_shard - beacon_height_follow_shard
    INFO(
        f'Beacon at shard 1: beacon_h b4 {beacon_height_follow_shard} - beacon_h af {beacon_height_af_follow_shard}: {num_block_beacon}')
    assert num_block_beacon > shard_1_height_af_3 - shard_1_height_af_2  # check shard xin lai data
    WAIT(100)
