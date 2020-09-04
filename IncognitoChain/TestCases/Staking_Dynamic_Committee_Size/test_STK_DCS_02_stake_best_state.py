import concurrent

from concurrent.futures.thread import ThreadPoolExecutor
from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Helpers.TestHelper import get_beacon_best_state, get_shard_best_state
from IncognitoChain.TestCases.Staking_Dynamic_Committee_Size import stake_account, \
    stake_and_check_balance_after_stake, find_committee_public_key_in_beacon_best_state, find_committee_public_key_in_shard_best_state


def test_self_stake_and_check_committee_public_key_in_beacon_and_shard_best_state():
    with ThreadPoolExecutor() as executor:
        STEP(1, 'Start beacon, shard and stake threads')
        thread_pool = []
        thread_beacon = executor.submit(get_beacon_best_state)
        thread_pool.append(thread_beacon)
        thread_shard_0 = executor.submit(get_shard_best_state, 0)
        thread_pool.append(thread_shard_0)
        thread_shard_1 = executor.submit(get_shard_best_state, 1)
        thread_pool.append(thread_shard_1)
        thread_stake = executor.submit(stake_and_check_balance_after_stake, stake_account)
        thread_pool.append(thread_stake)

    STEP(2, 'Wait until all threads completed')
    concurrent.futures.wait(thread_pool)

    STEP(3, 'Find committee public key in beacon best state')
    find_committee_public_key_in_beacon_best_state(stake_account, thread_stake.result()[0], thread_beacon.result())

    STEP(4, 'Find committee public key in shard 0 best state')
    find_committee_public_key_in_shard_best_state(stake_account, thread_stake.result()[1], thread_shard_0.result())

    STEP(5, 'Find committee public key in shard 1 best state')
    find_committee_public_key_in_shard_best_state(stake_account, thread_stake.result()[1], thread_shard_1.result())