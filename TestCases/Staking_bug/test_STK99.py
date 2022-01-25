from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO, WARNING
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import AccountGroup, COIN_MASTER
from Objects.IncognitoTestCase import SUT
from Objects.TestBedObject import TestBed

key_list_file = KeyListJson()
# number of node which already run,
# if this number is higher than the real running node, it might cause the chain not working
num_of_stakers = 12
validators = AccountGroup(*(key_list_file.get_staker_accounts()[:num_of_stakers]))

SHARD0 = 0
SHARD1 = 1
NUM_OF_SHARD = 2
NUM_OF_COMMITTEE_SWAP_OUT = 2


def setup_module():
    # preparation, if validators not yet stake, stake them
    bbi = SUT().get_beacon_best_state_info()
    not_yet_stake_list = []
    for validator in validators:
        if bbi.is_he_a_committee(validator) is False \
                and bbi.is_in_shard_pending_list(validator) is False \
                and bbi.get_auto_staking_committees(validator) is None:
            not_yet_stake_list.append(validator)
    if not not_yet_stake_list:
        return

    COIN_MASTER.top_up_if_lower_than(not_yet_stake_list, coin(1751), coin(1755))

    def staking_action(account):
        account.stake_and_reward_me().expect_no_error()

    with ThreadPoolExecutor() as executor:
        for acc in not_yet_stake_list:
            executor.submit(staking_action, acc)

    # Wait for 2 epochs
    SUT().wait_till_next_epoch(2)


@pytest.mark.parametrize("shard_committee,shard_origin", [
    (SHARD0, SHARD1),
    # (SHARD1, SHARD0),
])
def test_stop_auto_staking_not_work__committee_shard_0(shard_committee, shard_origin):
    """
    stake account must be from shard 1 and is a committee of shard 0
    @return:
    """
    INFO()
    INFO(f'Get all account originate from shard {shard_origin}')
    accounts_from_shard1 = AccountGroup()
    for i in range(shard_origin, 8, NUM_OF_SHARD):
        # account belong to the shard , not account of committee of the shard
        accounts_from_shard1 += validators.get_accounts_in_shard(i % ChainConfig.ACTIVE_SHARD)

    INFO(f'Change request handler to shard {shard_committee}, which user is a committee')
    TestBed.REQUEST_HANDLER = SUT.shards[shard_committee].get_representative_node()
    INFO(f'Get shard best state detail, get epoch, beacon height')
    shard0_state_detail = SUT().get_shard_best_state_detail_info(shard_committee)
    shard0_committees = shard0_state_detail.get_shard_committee()
    committee_4th_0 = shard0_committees[ChainConfig.FIX_BLOCK_VALIDATOR]
    committee_5th_0 = shard0_committees[ChainConfig.FIX_BLOCK_VALIDATOR + 1]
    acc_committee_4th = accounts_from_shard1.find_account_by_key(committee_4th_0.get_inc_public_key())
    acc_committee_5th = accounts_from_shard1.find_account_by_key(committee_5th_0.get_inc_public_key())
    acc_stop_stake = acc_committee_4th if acc_committee_4th is not None else acc_committee_5th
    assert acc_stop_stake is not None, f'Can not find any account which originate from shard{shard_origin} and is a' \
                                       f'committee for shard{shard_committee}. Please run this test again another time'
    acc_stop_stake.attach_to_node(SUT.shards[shard_origin].get_representative_node())
    epoch = shard0_state_detail.get_epoch()
    if ChainConfig.PRIVACY_VERSION == 2:
        acc_stop_stake.submit_key()
        epoch_b4_submit = shard0_state_detail.get_epoch()
        shard0_state_detail = SUT().get_shard_best_state_detail_info(shard_committee)

        if epoch != epoch_b4_submit:
            pytest.skip("epoch changed, run again")

    current_height = shard0_state_detail.get_beacon_height()
    last_height = ChainHelper.cal_last_height_of_epoch(epoch) - 1
    second_till_last_height = (last_height - current_height) * ChainConfig.BLOCK_TIME
    INFO(f"""
        Current epoch: {epoch}, last height of epoch: {last_height}
        Current beacon height {current_height}, calculated last height of epoch: {last_height}""")

    INFO(f"COMMITTEE origin: {acc_stop_stake}")
    if acc_stop_stake is None:
        pytest.skip(f' expect committee is from shard 1 and is a committee of shard 0, but cannot find one like that')

    INFO(f'Wait till last beacon height then send stop auto staking to shard {shard_origin}, '
         f'from which user originates')
    WAIT(second_till_last_height)
    shard0_state_detail = SUT().get_shard_best_state_detail_info(shard_committee)
    current_height = shard0_state_detail.get_beacon_height()
    INFO(f"Current beacon height {current_height}")
    if last_height != current_height:
        pytest.skip(f"Current beacon height {current_height} is not the last height of epoch, skip the test")
    bal_b4_un_stake = acc_stop_stake.get_balance()

    INFO(f'Send stop auto staking to user originated shard')
    un_stake_tx = acc_stop_stake.stk_stop_auto_stake_me().expect_no_error().attach_to_node(
        SUT.full_node).subscribe_transaction()
    assert un_stake_tx.get_block_height() > 0
    acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()

    INFO(f'Get beacon best state from full node')
    TestBed.REQUEST_HANDLER = SUT.full_node
    BBI = SUT().get_beacon_best_state_info()

    auto_stake_status = BBI.get_auto_staking_committees(acc_stop_stake)
    if shard_committee == SHARD0:
        # committee of shard 0 will be swapped out and refund staking amount right in next epoch
        if auto_stake_status is not None:
            WARNING(f'Expect auto staking status to be removed, got {auto_stake_status} instead'
                    f'However, to be sure, wait for another round and check again')
            acc_stop_stake.stk_wait_till_i_am_committee()
            acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()
            BBI = SUT().get_beacon_best_state_info()
            auto_stake_status = BBI.get_auto_staking_committees(acc_stop_stake)
            assert auto_stake_status is None, f'Expect auto staking status to be removed, ' \
                                              f'got {auto_stake_status} instead'
        else:
            assert auto_stake_status is None, f'Expect auto staking status to be removed, got {auto_stake_status} instead'

    else:  # other shard, committee must complete another round
        # before get completely remote of committee list and refund staking amount
        if auto_stake_status is not False:
            WARNING(f'Expect auto staking status to be removed, got {auto_stake_status} instead.')
            assert auto_stake_status is None, f'Expect auto staking status to be removed, ' \
                                              f'got {auto_stake_status} instead'
        else:
            assert auto_stake_status is False, f'Expect auto staking status to be False, ' \
                                               f'got {auto_stake_status} instead'
            acc_stop_stake.stk_wait_till_i_am_committee()
            acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()
            BBI = SUT().get_beacon_best_state_info()
            auto_stake_status = BBI.get_auto_staking_committees(acc_stop_stake)
            assert auto_stake_status is None, f'Expect auto staking status to be removed, ' \
                                              f'got {auto_stake_status} instead'

    bal_af_un_stake = acc_stop_stake.wait_for_balance_change(from_balance=bal_b4_un_stake)
    INFO(f"Bal before - after unstake: {bal_b4_un_stake} - {bal_af_un_stake}")
    assert bal_af_un_stake == bal_b4_un_stake + ChainConfig.STK_AMOUNT - un_stake_tx.get_fee()
