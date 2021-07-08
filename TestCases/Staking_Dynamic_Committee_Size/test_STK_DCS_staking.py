from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import coin
from Helpers.Logging import INFO
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS
from TestCases.Staking import test_STK01_staking as STK01, test_STK03_stake_reject as STK03, \
    test_STK04_stake_for_multi_validator as STK04, test_STK06_un_stake_staking_flowV2 as STK06

list_staker_to_test = []
beacon_bsd = SUT().get_beacon_best_state_detail_info()
for staker in STAKER_ACCOUNTS[:35]:
    if beacon_bsd.get_auto_staking_committees(staker) is None:
        list_staker_to_test.append(staker)


def test_staking():
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        account_y = list_staker_to_test[0]
        thread = executor.submit(STK01.test_staking, account_y, account_y, account_y, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[1]
        account_x = list_staker_to_test[2]
        thread = executor.submit(STK01.test_staking, account_y, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[3]
        account_y = list_staker_to_test[4]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[5]
        account_y = list_staker_to_test[6]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_y, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[7]
        account_y = list_staker_to_test[8]
        account_t = list_staker_to_test[9]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_t, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[10]
        thread = executor.submit(STK01.test_staking, account_y, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[11]
        account_y = list_staker_to_test[12]
        thread = executor.submit(STK01.test_staking, account_y, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[13]
        account_y = list_staker_to_test[14]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[15]
        account_y = list_staker_to_test[16]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[17]
        account_y = list_staker_to_test[18]
        account_t = list_staker_to_test[19]
        thread = executor.submit(STK01.test_staking, account_x, account_y, account_t, True)
        thread_pool.append(thread)

    for i in range(len(thread_pool)):
        try:
            result = thread_pool[i].result()
            INFO(f'Case_{i}: {result}')
        except:
            INFO(f'Case_{i}: {thread_pool[i]}')


def test_stake_under_over_1750_prv():
    amount_stake = {"amount_stake_under_1750": coin(1749), "amount_stake_over_1750": coin(1751)}
    STK03.account_y = list_staker_to_test[0]
    COIN_MASTER.top_up_if_lower_than(STK03.account_y, coin(1800), coin(1850))
    for key, amount in amount_stake.items():
        try:
            STK03.test_stake_under_over_1750_prv(amount)
            INFO(f'Stake with {key}: Passed')
        except:
            INFO(f'Stake with {key}: Failed')


def test_stake_same_validator():
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        account_y = list_staker_to_test[0]
        thread = executor.submit(STK03.test_stake_same_validator, account_y, account_y, account_y)
        thread_pool.append(thread)
        account_y = list_staker_to_test[1]
        account_t = list_staker_to_test[2]
        thread = executor.submit(STK03.test_stake_same_validator, account_y, account_t, account_y)
        thread_pool.append(thread)
        account_x = list_staker_to_test[3]
        account_y = list_staker_to_test[4]
        account_t = list_staker_to_test[4]
        thread = executor.submit(STK03.test_stake_same_validator, account_x, account_y, account_t)
        thread_pool.append(thread)
    for i in range(len(thread_pool)):
        try:
            result = thread_pool[i].result()
            INFO(f'Case_{i}: {result}')
        except:
            INFO(f'Case_{i}: {thread_pool[i]}')


def test_stake_for_multi_validator():
    STK04.account_a = list_staker_to_test[0]
    STK04.account_u = list_staker_to_test[1]
    STK04.account_t = list_staker_to_test[2]
    STK04.account_y = list_staker_to_test[3]
    STK04.test_stake_for_multi_validator()


def test_un_stake_when_waiting():
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        account_y = list_staker_to_test[0]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_y, account_y, account_y, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[1]
        account_x = list_staker_to_test[2]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_y, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[3]
        account_y = list_staker_to_test[4]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[5]
        account_y = list_staker_to_test[6]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_y, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[7]
        account_y = list_staker_to_test[8]
        account_t = list_staker_to_test[9]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_t, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[10]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_y, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[11]
        account_y = list_staker_to_test[12]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_y, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[13]
        account_y = list_staker_to_test[14]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[15]
        account_y = list_staker_to_test[16]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[17]
        account_y = list_staker_to_test[18]
        account_t = list_staker_to_test[19]
        thread = executor.submit(STK06.test_un_stake_when_waiting, account_x, account_y, account_t, True)
        thread_pool.append(thread)

    for i in range(len(thread_pool)):
        try:
            result = thread_pool[i].result()
            INFO(f'Case_{i}: {result}')
        except:
            INFO(f'Case_{i}: {thread_pool[i]}')


def test_un_stake_when_exist_pending():
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        account_y = list_staker_to_test[0]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_y, account_y, account_y, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[1]
        account_x = list_staker_to_test[2]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_y, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[3]
        account_y = list_staker_to_test[4]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[5]
        account_y = list_staker_to_test[6]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_y, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[7]
        account_y = list_staker_to_test[8]
        account_t = list_staker_to_test[9]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_t, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[10]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_y, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[11]
        account_y = list_staker_to_test[12]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_y, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[13]
        account_y = list_staker_to_test[14]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[15]
        account_y = list_staker_to_test[16]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[17]
        account_y = list_staker_to_test[18]
        account_t = list_staker_to_test[19]
        thread = executor.submit(STK06.test_un_stake_when_exist_pending, account_x, account_y, account_t, True)
        thread_pool.append(thread)

    for i in range(len(thread_pool)):
        try:
            result = thread_pool[i].result()
            INFO(f'Case_{i}: {result}')
        except:
            INFO(f'Case_{i}: {thread_pool[i]}')


def test_un_stake_when_exist_shard_committee():
    thread_pool = []
    with ThreadPoolExecutor() as executor:
        account_y = list_staker_to_test[0]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_y, account_y, account_y, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[1]
        account_x = list_staker_to_test[2]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_y, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[3]
        account_y = list_staker_to_test[4]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_x, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[5]
        account_y = list_staker_to_test[6]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_y, False)
        thread_pool.append(thread)
        account_x = list_staker_to_test[7]
        account_y = list_staker_to_test[8]
        account_t = list_staker_to_test[9]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_t, False)
        thread_pool.append(thread)
        account_y = list_staker_to_test[10]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_y, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[11]
        account_y = list_staker_to_test[12]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_y, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[13]
        account_y = list_staker_to_test[14]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_x, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[15]
        account_y = list_staker_to_test[16]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_y, True)
        thread_pool.append(thread)
        account_x = list_staker_to_test[17]
        account_y = list_staker_to_test[18]
        account_t = list_staker_to_test[19]
        thread = executor.submit(STK06.test_un_stake_when_exist_shard_committee, account_x, account_y, account_t, True)
        thread_pool.append(thread)

    for i in range(len(thread_pool)):
        try:
            result = thread_pool[i].result()
            INFO(f'Case_{i}: {result}')
        except:
            INFO(f'Case_{i}: {thread_pool[i]}')
