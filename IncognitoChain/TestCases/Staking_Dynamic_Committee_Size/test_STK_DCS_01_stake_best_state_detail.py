import concurrent

from concurrent.futures.thread import ThreadPoolExecutor
from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Helpers.TestHelper import get_beacon_best_state_detail, get_shard_best_state_detail
from IncognitoChain.TestCases.Staking_Dynamic_Committee_Size import stake_account, \
    stake_and_check_balance_after_stake, find_public_key_in_beacon_best_state_detail, \
    find_public_key_in_shard_best_state_detail


def test_self_stake_and_check_public_key_in_beacon_and_shard_best_state_detail():
    with ThreadPoolExecutor() as executor:
        STEP(1, 'Start beacon, shard and stake threads')
        thread_pool = []
        thread_beacon = executor.submit(get_beacon_best_state_detail)
        thread_pool.append(thread_beacon)
        thread_shard_0 = executor.submit(get_shard_best_state_detail, 0)
        thread_pool.append(thread_shard_0)
        thread_shard_1 = executor.submit(get_shard_best_state_detail, 1)
        thread_pool.append(thread_shard_1)
        thread_stake = executor.submit(stake_and_check_balance_after_stake, stake_account)
        thread_pool.append(thread_stake)

    # Return value of stake_and_check_balance_after_stake method
    balance_after_staking = thread_stake.result()[0]
    tx_staking_id = thread_stake.result()[1]
    stake_at_epoch = thread_stake.result()[2]
    stake_at_beacon_height = thread_stake.result()[3]

    STEP(2, 'Wait until all threads completed')
    concurrent.futures.wait(thread_pool)

    STEP(3, 'Find public key in beacon best state detail')
    find_public_key_in_beacon_best_state_detail(stake_account, balance_after_staking, thread_beacon.result(),
                                                stake_at_epoch, stake_at_beacon_height)

    STEP(4, 'Find public key in shard 0 best state detail')
    find_public_key_in_shard_best_state_detail(stake_account, tx_staking_id, thread_shard_0.result())

    STEP(5, 'Find public key in shard 1 best state detail')
    find_public_key_in_shard_best_state_detail(stake_account, tx_staking_id, thread_shard_1.result())
