import random
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import INFO, ERROR
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account, AccountGroup
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS, BEACON_ACCOUNTS, COMMITTEE_ACCOUNTS, ACCOUNTS
from TestCases.Staking_Dynamic_Committee_Size import get_staker_by_tx_id

fix_node = ChainConfig.FIX_BLOCK_VALIDATOR
i = ChainConfig.BLOCK_PER_EPOCH

# list = [Account('112t8ro6boKAoKdCKGtLXRviNJbEw2haeaJLRHQeP883bDnSd4pBJDZYYDBpBVfZPvgUU7kn9YnH5WaptE43NihXdMQC1as7J1V7fx8PrAZL'),
#         Account('112t8rnyGTbiVrewRVeDoeYAj7snx1kX7JMbK4u8RDknxwv4RW9hVjrkmvCav1LxdN6TSrsVd23pLhPfefvaRGaxP9P8xcpWo5uVi74ZGGMd'),
#         Account('112t8roLufU9ZFKdppumVHgMLfmYqBanaKDsY1HtQS8fqyj9jfSFxS5jqtm3eyj76WH5EagPV11nWR2qA9UTStJsFaiRycKijA3sUDmBRptg'),
#         Account('112t8rne61AdLoKfuSBtcq5iLUwVR6Z9Rac6EecQ2336VmJAU8UXcxcXU7YNeU45qC7Wo7P3uUmmhbZEukVhJcTY1P4SnmoBFjNdSUQiVfH2'),
#         Account('112t8roENtmKCM6ytkqGCEGB7A2xje96pwCd1p5db2xHZtXqM5p3VRPWj5WcfZnYp7t541LGfjjwq5fx9APUDvXTedQdtrKqK9u9eQZyv5sV'),
#         Account('112t8ropTXiZCWWBLccJMaE5ZUhwF4cwafawoBfXtfcjMTJaCsoASUpV861sssuRkaGXkGiFoxNNS6qSnvXRKubvKDg78YfwV9uRaejxL3aN'),
#         Account('112t8roG22DTWvqrXruSJncNJrsKcDyJDZ48LhpupBsGHVodHdniSyBvjACLFSE9T3PPZ8pMpHjZ5TM64AHrFwJbs2G3kYcCo2MEB3Pmh6Db'),
#         Account('112t8roKpK8RJmKhUWTYc6So8PfB9uVHAuCXmQacUCGRu3gR5dbEDHygWmrigtnBCULtqmnbJT9j1UNDnUmfTApxWYkzeDYhYwQP2Y5fGbSs'),
#         Account('112t8ro8ErQqjauZj1hJia4hyhsxCZrKS3ED6a4xDjL1jpVd5qvJwGaN9a2Wr1tUy2yhnNQo8yVV7G7SC68MPSD75nL6Zj2wXYXrgJTVM5eZ'),
#         Account('112t8rnpxg8CoGsg7jML69RgR7qoryqcxbXS1Dv82kkbjhnLyDD6vtvRrW2bf2AJoAQoq94Riv3FmgCnsYzsyXuo19EEyZJmQaELqwqG2ctw'),
#         Account('112t8rntvSWTiRL64cj9aLhNFjYWk6TBFdnro3XaDz7uyC7Dn6aZEMGrQaMVuPoEvxNpvFg28b2MakwAfrDuBXvSon7foCdS8WjRP218E7er'),
#         Account('112t8ro8tvnFfJ3VJ7YU5b2bVozdwL5XQK9xoPnj6qEbeHcrBviPC7fxgrUTfuHMSQjN7N9Q7J22CKEw5gSQAKcMBdnaVzMYB1g1sde8SCxY'),
#         Account('112t8roeSXwoVNWmF6YoCuW1bfgdhbpqXVz9E9R65NtvLeX8tFMCkaQ8kRiuzGNRkEJaWTSDSy7hNw7JvdF9FtVuHLSYUTMa8yiXMYoCmRwx'),
#         Account('112t8roEXWibSwnieNVZKMTrwFQzDRJFNaUnFfZbRp37nuWyGGWBUFQkMLWwnAfv5SzYtr3JFKCXxQyq7WZAnsSZT4oUjLAQRNVJWJonBA1r'),
#         Account('112t8roBPJc1amD9YiZYkXBzsUtDcHTMhpARhogLZv5J6sCMSAksD7uzch23ErpoUN8ax9QCvWFQgs9AGbwkLqfi6D78xnvSBx1zK74iyd1a'),
#         Account('112t8roUUNhc2KVMvXy8A59HhURkrnSQUoS9Dq1Xzj9NgistgiH59iJ2hcZd1YtCo2R8vm21SEG42h5HgHMfyoUXvdpxR7YDxY8NM2pXFtdi'),
#         Account('112t8ro13ARE4LxVwLTEtXR64rYxxFK54UxvTVm1mSzUSpbvtrzZ4abZrofjk85LuGHSnY6p2oRrTSN3Tez4gDg9TKj8nxq5AFe2GeaSWAYh'),
#         Account('112t8rohhBp5oZFPkw9cZSdC1U8GQWpni8qNm3eME13LHqDpC84LVqd6c11241Ep64KmBy1ZgZS4ACmkJvs1QUjc15kopf6jG9ZgRKEFrRvV'),
#         Account('112t8rnxRa2N5jENfAgr2T7nh2CZgMkL33nraMCuZPLnhbgv1bJJHo7CA8FeFwAbgHzdMpHq2pqcbQUhn3U7647P4soD3446hikj5s3w291m'),
#         Account('112t8rnzo1ViqbLzYt5AvKKSeooFMyy94N9C9ZCb2wai4toUXFRDxJ3ySTpyP8byG6TppUVwEdXjdUke4ErfTdQu1UQUxJ6MDu3DjYSFkxsp'),
#         Account('112t8roQbvv8mqaLCgkHHFwD1eAarTZTAxyi8DEJhBGu4o5jB8SJ8jB1cQSNSG2EMMjqwjjVFyRFyUaM4x6Hnydks21R1gbzE9jmKmPRgeK2'),
#         Account('112t8rojRcSyjgS8QNzm4pe1tXhCAi1oYLcddiiAXva3gNfUfQ84hzSHDnnJZDqDNPXqK1h6qgsymFVACDXdCYAV9UYQEAgnRSVnEszZ8A1H'),
#         Account('112t8rnitkSVxFYgrPZru4ibfoBfH9n3uvokm7FMzbM4UhJZ4c9r4RjyBdHKsninfYi27jBrbABbcZGqveQLyS2ofWBbW7QZ2gU52urPuD95'),
#         Account('112t8roaSKhogHdQkQx3bsaJsCMrDo7EaDh5raAhCouUsb968MeZ1BBKT1KNiGM7de62RhqYQDLjkdo16nv3qA7DKdyM7uBMRQ8GmgxudawN'),
#         Account('112t8rogHcGcB2ZR31M98vWid8JDWTEwkSGmtZR8AMLA5Gx5xEaLt1Seh5BsHpwj59dhwPUvjzbawtt1DWq4aba1zuJVJDkGjMWW3xZKqJci'),
#         ]
# group_acc = STAKER_ACCOUNTS + BEACON_ACCOUNTS + COMMITTEE_ACCOUNTS + AccountGroup(*list) + ACCOUNTS
group_acc = STAKER_ACCOUNTS + COMMITTEE_ACCOUNTS


# acc = group_acc.find_account_by_key('12a3eHTbYn5mEpHbt9CbNA2UPym6DqwMKHWT1iQShg73VFqEzjx')
# print('112t8roJuymbRGq6n6PopP9nnsfNH93GzHCYidvzph7G6HpniDcmWCsnCXrxZbs3FCou6hJ1ZXYFn6fwHQaaVAtvk3P9GexsWhCtS85PhcRG')

#
# beacon_bsd = SUT().get_beacon_best_state_detail_info()
# while beacon_bsd.get_beacon_height() <= 2761555:
#     WAIT(10)
#     beacon_bsd = SUT().get_beacon_best_state_detail_info()
# # list[1].stk_stop_auto_stake_me().expect_no_error()
# acc_test.stk_un_stake_tx().expect_no_error()
# beacon_bsd = SUT().get_beacon_best_state_detail_info()
# while beacon_bsd.is_he_a_committee(acc_test) is False:
#     WAIT(10)
#     beacon_bsd = SUT().get_beacon_best_state_detail_info()
# print(beacon_bsd.get_beacon_height())
# WAIT(1060)
# print(acc_test.stk_get_reward_amount())
# for acc in STAKER_ACCOUNTS:
#     acc.stk_un_stake_tx()
# print(STAKER_ACCOUNTS[29])
# print(STAKER_ACCOUNTS[29].committee_public_k)
# WAIT(100000)


# list_acc = [
#     Account('112t8rnX8kLtpqqFxHT2VEipSAvqCRTMRZKoK9LBAxGcQAYc2NM7pTuaK9ds3sToeMvFZ78S3c2kMG6TJGbbPE1r94GGqBbGEiPNDJJh8vQL'),
#     Account('112t8rnnoxUQ63ZWJDV817RdpxWBgnJYwUJEPZ8GjBwwmFsmLpTvkFAikCV65a8HTjJX5SHNUrt6ytBuLAzUgeR7Yxyq1TjGQEzMpsubsZBc'),
#     Account('112t8roP32U1T4kL8K7jfFuArDPEkWVXfHoQAM86mZRubuX6bNDj5GVTBa2YfCSP6MTuxvWtNJ1Lhgfd14iUFmTBxEVJaXdhUME2fx6rNRoR'),
#     Account('112t8rp1bGi6uvhNtfWmfxHn8uSrUypgiUUvqSh87o7bGXfzf5d2LB2HupYv9fN64Wwfwr4UEXwVnJ1EMsdv3iMRoYLduBwuYHZpJUc49x8i'),
#     Account('112t8rpeSduEHqnwH9iaQsyHLUZTEWNy9ZZP5LyMpW2LdxZnxzSzrL85xfNbizedfHskGzg3BqeGU9dFvbVPiH5JaNxqc3Rumith74wkMDVr'),
#     Account('112t8rqHCwSpRk2YaoHRep6gdYRSEQDFKgwzetbCXPnuVuywSJTcbwzBdSYihYHENj6MtGfNdMUDRr3JbBXiZx3jV1sKfpccNKeenVhEwTXu'),
#     Account('112t8rqv2pCqqdWzywK7DK6cu261ScBNBkBwQoVSoazApKpLAYLSyyUQNH7MqbdsYqDkTFTKfygKsNx3Csczjwy9DykPKAq54AjyZ6JNkvKL'),
#     Account('112t8rrYwuGf4M8ScwF2hRyvVDyTJyMNLJSd6P2Jd17dvYyMGR4G7W9TJZzZiJ8HNyD4tVPEmAUgsLuvEbefmbgBDjjSBSpGib9EpvSkgeCS'),
#     Account('112t8rsBhv7QQZ18wLSnkg1v9hcmyutDBzzoGNEoTEmCwFXgKLR9AuapVBNywtjyfQ4SujLB3u4T8v8PqiSkVfj4GzZDrLXNoG75J68QYp2b'),
# ]
# beacon_bsd = SUT().get_beacon_best_state_detail_info()
# for acc in list_acc:
#     print(beacon_bsd.get_auto_staking_committees(acc))
#     # acc.stk_un_stake_tx()
#     # print(acc.public_key)
# STAKER_ACCOUNTS[2].stk_stop_auto_stake_me()
# WAIT(1000000)


def test_draft():
    # acc = STAKER_ACCOUNTS[23]
    # INFO(acc)
    # INFO(acc.committee_public_k)
    # beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # for acc in STAKER_ACCOUNTS:
    # #     acc.stake().expect_no_error()
    # #     acc.convert_token_to_v2()
    #     beacon_bsd.get_auto_staking_committees(acc)
    # # INFO()
    i = 0
    for acc in STAKER_ACCOUNTS:
        print(f'{acc.committee_public_k} => staker {i}.log\n\n')
        i += 1
    # #     INFO(acc.private_key)
    # #     INFO()


def test_convert():
    # acc.convert_token_to_v2()
    tokens = ["ffd8d42dc40a8d166ea4848baf8b5f6e9fe0e9c30d60062eb7d44a8df9e00854",
              "c7545459764224a000a9b323850648acf271186238210ce474b505cd17cc93a0",
              "1d74e5e225e1f09ae38c496d3102aef464dcbd04ad3ac071e6e44077b8a740c9",
              "d1b4c73821edc76963fdeda2236fe89478249a1f7b952de2a7135c0bc0cbe6dc",
              "d6644f62d0ef0475335ae7bb6103f358979cbfcd2b85481e3bde2b82101a095c",
              "d0379b8ccc25e4940d5b94ace07dcfa3656a20814279ddf2674f6d7180f65440",
              "27322fa7fce2c4d4d5a0022d595a0eec56d7735751a3ba8bc7f10b358ab938bc",
              "3c115c066028bb682af410c594546b58026095ff149dc30c061749ee163d9051",
              "d6644f62d0ef0475335ae7bb6103f358979cbfcd2b85481e3bde2b82101a095c",
              "06ce44eae35daf57b9b8158ab95c0cddda9bac208fc380236a318ef40f3ac2ef",
              "414a6459526e827321cedb6e574d2ba2eb267c5735b0a65991602a405fb753b7",
              "06ce44eae35daf57b9b8158ab95c0cddda9bac208fc380236a318ef40f3ac2ef",
              "61e1efbf6be9decc46fdf8250cdae5be12bee501b65f774a58af4513b645f6a3",
              "4fb87c00dbe3933ae73c4dc37a37db0bca9aa9f55a2776dbd59cca2b02e72fc4",
              "641e37731c151e8b93ed48f6044836edac1e21d518b11c491774ba10b89ca5e5",
              "f3c421e4d7520936f3916a878ab361ef3fd6a831e81063ca3e7b80ab4d15a84e"]
    for tok in tokens:
        COIN_MASTER.convert_token_to_v2(tok)
        Account(
            '112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj').convert_token_to_v2(
            tok)
    COIN_MASTER.convert_token_to_v2()
    Account(
        '112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj').convert_token_to_v2()


def test_check_bal():
    # for acc in STAKER_ACCOUNTS:
    #     acc.convert_token_to_v2()
    # WAIT(40)
    thread_pool = {}
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    with ThreadPoolExecutor() as executor:
        for acc in STAKER_ACCOUNTS:
            # for acc in list:
            # for acc in ACCOUNTS:
            bal_thread = executor.submit(acc.get_balance)
            # bal_thread = 0
            thread_pool[acc] = bal_thread
    dict_receiver = {}
    list_receivers = []
    expected_amount = coin(1750)*2 + 1000
    for acc, thread in thread_pool.items():
        amount = 0
        # if acc == STAKER_ACCOUNTS[15]:
        #     INFO('Begin acc 15th')
        bal = thread.result()
        # bal = thread
        # INFO(acc.private_key)
        INFO(beacon_bsd.get_auto_staking_committees(acc))
        INFO(f'{acc.shard}: {bal}')
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            if bal > expected_amount + 100:
                acc.send_prv_to(COIN_MASTER, bal - expected_amount)
            elif bal <= expected_amount - 100:
                amount = expected_amount - bal
        else:
            if bal > expected_amount - coin(1750) + 100:
                acc.send_prv_to(COIN_MASTER, bal - (expected_amount - coin(1750)))
            elif bal <= expected_amount - coin(1750) - 100:
                amount = (expected_amount - coin(1750)) - bal
        if len(dict_receiver) < 20 and amount != 0:
            dict_receiver[acc] = amount
        elif amount != 0:
            list_receivers.append(dict_receiver)
            dict_receiver = {acc: amount}
    list_receivers.append(dict_receiver)

    if list_receivers[0]:
        for receivers in list_receivers:
            COIN_MASTER.send_prv_to_multi_account(receivers, privacy=0).expect_no_error().subscribe_transaction()
    WAIT(50)
    with ThreadPoolExecutor() as executor:
        for acc in STAKER_ACCOUNTS:
            # for acc in list:
            # for acc in ACCOUNTS:
            bal_thread = executor.submit(acc.get_balance)
            thread_pool[acc] = bal_thread
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc, thread in thread_pool.items():
        bal = thread.result()
        INFO(beacon_bsd.get_auto_staking_committees(acc))
        INFO(f'{acc.shard}: {bal}')
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            assert bal in range(expected_amount - 100, expected_amount + 100), INFO(acc)
        else:
            assert bal in range(expected_amount - coin(1750) - 100, expected_amount - coin(1750) + 100)
    INFO('--------------STAKING-------------')
    test_staking()


def test_staking():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # while beacon_bsd.get_beacon_height() % i != (i/2 - 4):
    #     WAIT(5)
    #     beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # for acc in STAKER_ACCOUNTS:
    #     acc.convert_token_to_v2()
    # WAIT(40)
    for acc in STAKER_ACCOUNTS:
        # for acc in ACCOUNTS:
        # for acc in list:
        # print(beacon_bsd.get_auto_staking_committees(acc))
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            acc.stake().expect_no_error()
            # WAIT(5)
            # acc.stk_stop_auto_stake_me()
    # print(STAKER_ACCOUNTS[-1])
    # INFO()
    # INFO(acc)
    # INFO()
    # WAIT(4)


def test_stake_list():
    list_staker = [STAKER_ACCOUNTS[20], STAKER_ACCOUNTS[9], STAKER_ACCOUNTS[0], STAKER_ACCOUNTS[7]]
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    while beacon_bsd.get_beacon_height() % 50 != 1:
        WAIT(5)
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in list_staker:
        print(beacon_bsd.get_auto_staking_committees(acc))
        acc.stake()
        WAIT(5)


def test_test_a():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    list_a = []
    for acc in ACCOUNTS:
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            list_a.append(acc)
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750) * 3, coin(1750) * 3, list_a[0])
    WAIT(30)
    list_a[0].stake(validator=list_a[0], auto_re_stake=False).expect_no_error()
    WAIT(30)
    list_a[0].stake(validator=list_a[1], auto_re_stake=False).expect_no_error()


def test_stop_auto_stake():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # for acc in STAKER_ACCOUNTS[17:35]:
    for acc in ACCOUNTS:
        INFO(beacon_bsd.get_auto_staking_committees(acc))
        if beacon_bsd.get_auto_staking_committees(acc) is True:
            tx = beacon_bsd.get_staking_tx(acc)
            staker = get_staker_by_tx_id(tx)
            staker.stk_stop_auto_stake_him(acc).expect_no_error()
        #     staker.stake(acc).expect_error()
        # if beacon_bsd.get_auto_staking_committees(acc) is False:
        #     tx = beacon_bsd.get_staking_tx(acc)
        #     staker = get_staker_by_tx_id(tx)
        #     staker.stk_stop_auto_stake_him(acc).expect_error()
        #     staker.stake(acc).expect_error()


def test_unstake_stake():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # while beacon_bsd.get_beacon_height() % 20 != 18:
    #     WAIT(5)
    #     beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in STAKER_ACCOUNTS[35:]:
        # for acc in ACCOUNTS + STAKER_ACCOUNTS[:35]:
        if beacon_bsd.get_auto_staking_committees(acc) is not None:
            acc.stk_un_stake_tx().expect_no_error()
            # acc.stk_stop_auto_stake_me()
            # WAIT(5)
        # WAIT(20000)
        # for acc in list:
    #     if beacon_bsd.get_auto_staking_committees(acc) is None:
    #         acc.stake().expect_no_error()


def test_unstaking():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in STAKER_ACCOUNTS:
        if beacon_bsd.get_auto_staking_committees(acc) is not None:
            tx = beacon_bsd.get_staking_tx(acc)
            staker = get_staker_by_tx_id(tx)
            staker.stk_un_stake_tx(acc)
            # staker.stake(acc)
        # if beacon_bsd.get_auto_staking_committees(acc) is False:
        #     tx = beacon_bsd.get_staking_tx(acc)
        #     staker = get_staker_by_tx_id(tx)
        #     # staker.stake(acc).expect_error()
        #     staker.stk_un_stake_tx(acc)
        # print(beacon_bsd.get_auto_staking_committees(acc))


def test_unstake_at_random():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    while beacon_bsd.get_beacon_height() % i != (i / 2 - 4):
        WAIT(5)
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
    waitting_next_random = beacon_bsd.get_candidate_shard_waiting_next_random()
    for com in waitting_next_random:
        acc = group_acc.find_account_by_key(com.get_inc_public_key())
        # tx = beacon_bsd.get_staking_tx(com)
        # staker = get_staker_by_tx_id(tx)
        acc.stk_un_stake_tx(acc).expect_no_error()
        # acc.stk_stop_auto_stake_me().expect_no_error()
        WAIT(5)


def test_unstake_all_committees():
    list_acc = ""
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    committee_shard = beacon_bsd.get_shard_committees()
    pending_shard = beacon_bsd.get_shard_pending_validator()
    for committees in committee_shard.values():
        for committee in committees:
            if beacon_bsd.get_auto_staking_committees(committee) is True:
                acc = group_acc.find_account_by_key(committee.get_inc_public_key())
                tx = beacon_bsd.get_staking_tx(committee)
                staker = get_staker_by_tx_id(tx)
                if staker is not None and acc is not None:
                    staker.stk_un_stake_tx(acc).expect_no_error()
                    list_acc += f'Account("{acc.private_key}"),'
    for committees in pending_shard.values():
        for committee in committees:
            if beacon_bsd.get_auto_staking_committees(committee) is True:
                acc = group_acc.find_account_by_key(committee.get_inc_public_key())
                tx = beacon_bsd.get_staking_tx(committee)
                staker = get_staker_by_tx_id(tx)
                if staker is not None and acc is not None:
                    staker.stk_un_stake_tx(acc).expect_no_error()
                    list_acc += f'Account("{acc.private_key}"),'
    print(list_acc)


def test_unstake_at_transfer_epoch():
    list_acc = []
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    # while beacon_bsd.get_beacon_height() % i != (i-2):
    #     WAIT(5)
    #     beacon_bsd = SUT().get_beacon_best_state_detail_info()
    j = 0
    committee_shard = beacon_bsd.get_shard_committees()
    for committees in committee_shard.values():
        num = int(1 / 8 * len(committees))
        # num = 3
        for committee in committees[fix_node:fix_node + num]:
            if beacon_bsd.get_auto_staking_committees(committee) is True:
                # acc = group_acc.find_account_by_key(committee.get_inc_public_key())
                acc = STAKER_ACCOUNTS.find_account_by_key(committee.get_inc_public_key())
                # tx = beacon_bsd.get_staking_tx(committee)
                # staker = get_staker_by_tx_id(tx)
                staker = acc
                if staker is not None and acc is not None:
                    staker.stk_un_stake_tx(acc).expect_no_error()
                    # INFO(staker.private_key)
                    INFO(acc.private_key)
                    INFO()
                    # staker.stk_stop_auto_stake_him(acc).expect_no_error()
                    # list_acc.append(staker)
                    # WAIT(5)
        # j += num
        # if j >= 5:
        #     break
    # WAIT(1000)
    # for acc in list_acc:
    #     acc.stake().expect_no_error()


def test_kill_node():
    test_check_run_node()
    list_node_kill = []
    list_name_node = []
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    committee_shard = beacon_bsd.get_shard_committees()
    committees = committee_shard['0']
    num = int(1 / 3 * len(committees)) + 1
    # for committee in committees[-num:]:
    for committee in committees:
        acc = group_acc.find_account_by_key(committee.get_inc_public_key())
        try:
            validator_k = acc.validator_key
        except:
            print(committee.get_inc_public_key())
        node = SUT.find_node_by_validator_k(validator_k)
        list_node_kill.append(node)
    for node in list_node_kill:
        node.kill_node()
        list_name_node.append(node._node_name)
    print(list_name_node)

    # WAIT(10 * 50 * 5)
    #
    # for node in list_node_kill:
    #     node.start_node()


def test_staker_validator():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in STAKER_ACCOUNTS[:35]:
        tx = beacon_bsd.get_staking_tx(acc)
        staker = get_staker_by_tx_id(tx)
        if staker != acc:
            staker.stk_un_stake_tx(acc).expect_no_error()


def test_check_run_node():
    i = 0
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    committees = beacon_bsd.get_shard_committees()['0']
    for committee in committees:
        group_acc = STAKER_ACCOUNTS + BEACON_ACCOUNTS + COMMITTEE_ACCOUNTS
        acc = group_acc.find_account_by_key(committee.get_inc_public_key())
        validator_k = acc.validator_key
        node = SUT.find_node_by_validator_k(validator_k)
        try:
            assert node is not None and INFO(f'Validator {i} run node ok'), ERROR(
                f'Validator key {validator_k} is not run node ')
        except:
            pass
        i += 1
