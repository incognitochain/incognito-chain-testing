"""
- check_bal: dùng để verify prv balance của các staker cần dao động quanh ~ coin(1750)
- staking: stake các acc trong acc_group
- top_up_amount_prv: get balance và top-up bal = expected_amount = coin(1750) + 1000, nếu chain mới build cần nhớ setsubmit=True,
bal=0 (để tiết kiệm time).
- test_unstake_at_transfer_epoch: dùng để unstake/stop auto stake (line 155) tại thời điểm chuyển giao epoch.
- test_stake_at_random: dùng để stake tại thời điểm random
- test_unstake_at_random: dùng để un-stake tại thời điểm random
- test_check_auto_stake: kiểm tra autostaking của các acc trong acc_group
NOTE for: Khi chạy test_unstake_at_transfer_epoch, test_stake_at_random, test_unstake_at_random
    - Tùy thuộc vào máy và set-up chain mà cần chỉnh điều kiện while (action trước thời điểm chuyển giao bao nhiêu epoch)
để xảy ra được case mong muốn.
    - Khi chạy những testcase này cần chạy cùng TestCases/ChainTestBusiness/Consensus/test_view_dynamic_committee_size.py.
Vì script này chỉ produce testcase, chưa auto-check. Những testcase đặc biệt này chủ yếu chỉ cần check không gây đứng chain.
**** Sau khi test qua tất cả các testcase trong file, chạy lại test_check_bal() để verify balance của các node đúng sau
khi stake, unstake, swap-out, slashing.

"""


from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, AccountGroup
from Objects.IncognitoTestCase import STAKER_ACCOUNTS, SUT
from TestCases.ChainTestBusiness.Consensus import get_staker_by_tx_id

bl_per_e = ChainConfig.BLOCK_PER_EPOCH
fix_node = ChainConfig.FIX_BLOCK_VALIDATOR
expected_amount = coin(1750) + 1000
thread_pool = {}


def check_bal(acc_group):
    INFO()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    with ThreadPoolExecutor() as executor:
        for acc in acc_group:
            bal_thread = executor.submit(acc.get_balance)
            thread_pool[acc] = bal_thread
    for acc, thread in thread_pool.items():
        bal = thread.result()
        INFO(beacon_bsd.get_auto_staking_committees(acc))
        INFO(f'{acc.shard}: {bal}')
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            assert bal in range(expected_amount - 10000, expected_amount + 10000), INFO(acc)
        else:
            assert bal in range(expected_amount - coin(1750) - 10000, expected_amount - coin(1750) + 10000), INFO(acc)


def staking(acc_group):
    INFO('--------------STAKING-------------')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    list_b = []
    for acc in acc_group:
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            try:
                acc.stake().expect_no_error()
            except:
                list_b.append(STAKER_ACCOUNTS.account_list.index(acc))
    print(f'Len(list_stake_unsuccessful): {len(list_b)}')
    for acc in list_b:
        print(acc)


def top_up_amount_prv(acc_group, bal_0=False, submit_k=False, convert=False):
    INFO()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if submit_k:
        with ThreadPoolExecutor() as e:
            for acc in acc_group:
                e.submit(acc.submit_key)
                # e.submit(acc.submit_key_authorize)
        WAIT(60)
    if convert:
        with ThreadPoolExecutor() as e:
            for acc in acc_group:
                e.submit(acc.convert_token_to_v2)
        WAIT(50)
    dict_receiver = {}
    list_receivers = []
    if not bal_0:
        with ThreadPoolExecutor() as executor:
            for acc in acc_group:
                bal_thread = executor.submit(acc.get_balance)
                thread_pool[acc] = bal_thread
    for acc in acc_group:
        amount = 0
        if bal_0:
            bal = 0
        else:
            bal = thread_pool[acc].result()
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
            WAIT(60)


def test_check_bal():
    acc_group = STAKER_ACCOUNTS[:12]+STAKER_ACCOUNTS[35:]
    check_bal(acc_group)


def test_staking():
    acc_group = STAKER_ACCOUNTS[:12] + STAKER_ACCOUNTS[35:]
    staking(acc_group)


def test_top_up_amount_prv():
    acc_group = STAKER_ACCOUNTS[:12]+STAKER_ACCOUNTS[35:]
    top_up_amount_prv(acc_group)


def test_topup_bal_and_stake():
    acc_group = STAKER_ACCOUNTS[:12]+STAKER_ACCOUNTS[35:]
    INFO("Top-up 1750 prv to stakers")
    top_up_amount_prv(acc_group, submit_k=True, bal_0=True)
    WAIT(ChainConfig.BLOCK_TIME * 6)
    INFO("Verify balance of stakers")
    check_bal(acc_group)
    # ####### Staking ##########
    staking(acc_group)


def test_unstake_at_transfer_epoch():
    INFO()
    list_acc = []
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    while beacon_bsd.get_beacon_height() % bl_per_e != (bl_per_e-2):
        WAIT(5)
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
    committee_shard = beacon_bsd.get_shard_committees()
    for committees in committee_shard.values():
        num = int(1 / 8 * len(committees))
        # num = 3
        for committee in committees[fix_node:fix_node + num]:
            if beacon_bsd.get_auto_staking_committees(committee) is True:
                acc = STAKER_ACCOUNTS.find_account_by_key(committee.get_inc_public_key())
                # tx = beacon_bsd.get_staking_tx(committee)
                # staker = get_staker_by_tx_id(tx)
                staker = acc
                if staker is not None and acc is not None:
                    # staker.stk_un_stake_tx(acc).expect_no_error()
                    staker.stk_stop_auto_stake_him(acc).expect_no_error()
                    INFO(f'Unstake STAKER_ACCOUNTS_{STAKER_ACCOUNTS.account_list.index(staker)}')
                    INFO()
                    list_acc.append(staker)
                    # WAIT(4)
    # WAIT(100)
    # # Re-stake
    # for acc in list_acc:
    #     acc.stake()


def test_stake_at_random():
    INFO()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    while beacon_bsd.get_beacon_height() % bl_per_e != (bl_per_e/2 - 1):
        WAIT(5)
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in STAKER_ACCOUNTS:
        if beacon_bsd.get_auto_staking_committees(acc) is None:
            acc.stake().expect_no_error()


def test_unstake_at_random():
    INFO()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    while beacon_bsd.get_beacon_height() % bl_per_e != (bl_per_e / 2 - 2):
        WAIT(5)
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
    waitting_next_random = beacon_bsd.get_candidate_shard_waiting_next_random()
    for com in waitting_next_random:
        acc = AccountGroup(*STAKER_ACCOUNTS).find_account_by_key(com.get_inc_public_key())
        # tx = beacon_bsd.get_staking_tx(com)
        # staker = get_staker_by_tx_id(tx)
        acc.stk_un_stake_tx(acc).expect_no_error()
        # acc.stk_stop_auto_stake_me().expect_no_error()
        # WAIT(4)


def test_check_auto_stake():
    """

    @return:
    """
    INFO()
    i = 0
    acc_group = STAKER_ACCOUNTS
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for acc in acc_group:
        string = f'{beacon_bsd.get_auto_staking_committees(acc)} => staker {i}\n'
        INFO(string)
        i += 1
