import math
from concurrent.futures import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.TestHelper import l6
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS

swapPercent = 8
shard_committee_size = ChainConfig.SHARD_COMMITTEE_SIZE
block_per_epoch = ChainConfig.BLOCK_PER_EPOCH
send_finish = False


def test_tracking_time_join_pending():
    INFO()

    def find_cycle_join_committee_by_tx_id(tx_id, account):
        trx_detail = SUT().get_tx_by_hash(tx_id)
        shard_height_stake = trx_detail.get_block_height()
        shard_id = trx_detail.get_shard_id()
        beacon_height_stake = SUT().get_shard_block_by_height(shard_id, shard_height_stake).get_beacon_height()
        height = beacon_height_stake
        beacon_height_in_next_candidate = 0
        beacon_height_in_syncpool = 0
        beacon_height_in_pending = 0
        committee_shard_id = None
        committee_state = None
        while True:
            INFO(f'Get committee state {height}')
            height += 1
            b4_committee_state = committee_state
            committee_state = SUT().get_committee_state(height)
            while committee_state.is_none():
                global send_finish
                if send_finish and committee_shard_id is not None:
                    SUT.shards[0].get_node().system_rpc().send_finish_sync(account.validator_key,
                                                                           account.committee_public_k,
                                                                           int(committee_shard_id))
                    send_finish = False
                    shard_height = SUT().get_shard_best_state_info(committee_shard_id).get_shard_height()
                    WAIT(ChainConfig.BLOCK_TIME)
                    block = SUT().get_latest_beacon_block(height).get_shard_states(
                        committee_shard_id).get_biggest_block_height()
                    while block < shard_height:
                        WAIT(ChainConfig.BLOCK_TIME)
                        height += 1
                        block = SUT().get_latest_beacon_block(height).get_shard_states(
                            committee_shard_id).get_biggest_block_height()
                    beacon_height_finish_sync = height
                    committee_state = SUT().get_committee_state(height)
                    continue
                WAIT(ChainConfig.BLOCK_TIME)
                committee_state = SUT().get_committee_state(height)
            if not beacon_height_in_next_candidate:
                INFO(f'Find beacon_height_in_next_candidate: {height}')
                if account.committee_public_k in committee_state.get_next_candidate():
                    beacon_height_in_next_candidate = height
                    INFO(f'Staker in next_candidate at height {height}')
                continue
            if not beacon_height_in_syncpool:
                INFO(f'Find beacon_height_in_syncpool: {height}')
                for shard_id in range(ChainConfig.ACTIVE_SHARD):
                    if account.committee_public_k in committee_state.get_syncing(shard_id):
                        beacon_height_in_syncpool = height
                        beacon_height_finish_sync = beacon_height_in_syncpool
                        committee_shard_id = shard_id
                        INFO(f'Staker in syncpool at height {height}, shard id {shard_id}')
                continue
            INFO(f'Find beacon_height_in_pending: {height}')
            if account.committee_public_k in committee_state.get_pending(committee_shard_id):
                beacon_height_in_pending = height
                shard_pending_size = len(b4_committee_state.get_pending(committee_shard_id))
                INFO(f'Staker in pending at height {height}, shard id {shard_id}')
                break
        half_pending_cycle = math.ceil(
            1 / 2 * (shard_pending_size / int(shard_committee_size / swapPercent))) * block_per_epoch
        string = f"""
                STAKER_ACCOUNT_{[*STAKER_ACCOUNTS].index(account)}
                Beacon height stake: {beacon_height_stake}
                Join waiting for random: {beacon_height_in_next_candidate}
                Join sync_pool in height: {beacon_height_in_syncpool} _ Committee shard_id {committee_shard_id}
                Beacon_height_finish_sync = {beacon_height_finish_sync}
                Join pending height: {beacon_height_in_pending}
                half_pending_cycle = math.ceil(1 / 2 * ({shard_pending_size} / int({shard_committee_size} / {swapPercent}))) * {block_per_epoch}
                Half pending cycle: {half_pending_cycle}
                Actual time waited: {beacon_height_in_pending - beacon_height_finish_sync}
                Expected time waited: {max(block_per_epoch, (half_pending_cycle - (beacon_height_finish_sync - beacon_height_in_next_candidate)))}
                """
        return string

    acc_group = STAKER_ACCOUNTS[66:76]
    bs = SUT().get_beacon_best_state_info()
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        for acc in acc_group:
            tx_staking = bs.get_staking_tx(acc)
            if tx_staking:
                thread = executor.submit(find_cycle_join_committee_by_tx_id, tx_staking, acc)
                thread_pool.append(thread)
    for thread in thread_pool:
        result = thread.result()
        INFO()
        INFO(result)
