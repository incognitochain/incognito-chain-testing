from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import ChainConfig, coin
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account, AccountGroup, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT

validators = AccountGroup(
    Account(
        "112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db"),
    Account(
        "112t8sw37yYFcpGhQnNLsHMbBDDSbW27t3YPMLDSK2q2ZmmZ6iSc1d1K5QkCsdsZ5L3YFaLz2R1KZzJHrAxQNefukYvc5hvKgVBFgatYaDtU"),
    Account(
        "112t8sw3HuTUHxw9U7agDsiBBzoLcjd3Z4o226QzUYHL9sAdHTo82iJ4TaaKZ5ZJzU6EcquxNjGTpxW5kdfrsx1EeRD7WChepy4y4WeUhvXA"),
    Account(
        "112t8sw3X7XahWjLwAjgBe51nF4AKqubXFMAFeumM5ECDr8RFH1FKoqzjRECkuXbqJDGr3sAM3qREixjtMpMgPrg63XdKBGYikiSaH89A53V"),
    Account(
        "112t8sw3swjDhYme56xtqu2Zc1CsodJAekC6FL5Lj7QpV7ZY9WvnyrDQc1W3Vim74dcHFR9QZLcu9LkUpDaziTX4bF39gKMBegWVgBDn6nv4"),
    Account(
        "112t8sw4G9xiRC151H5MWV4Kb1CfXAugPQuecjrnktU7W3JUVqd8LhCMa4jwiqaqnSSdNQvKRTqibA7W9tSKegn16HveZDJs1UC4GP4LiRTn"),
    Account(
        "112t8sw4ZAc1wwbKog9NhE6VqpEiPii4reg8Zc5AVGu7BkxtPYv95dXRJtzP9CkepgzfUwTseNzgHXRovo9oDb8XrEpb5EgFhKdZhwjzHTbd"),
    Account(
        "112t8sw4ijTH6E6gbPhCF6y36zijFfb7T1JnU8GWVSMmWMP85zzmjkoLRH4fF5HkJR8W7uqfnDQ19ARtW9mDmvCUviNNdZ3i39PDhXztjfgM"),
    Account(
        "112t8sw4uNsCeamWRqU1QLiquPbBfGB7HE8qyd7YsBUjSWf3nhcRmoMfyptRDAatJNWBopRTigciNHcPVoZG3bhMKUhrvv6LSzq8FwSwNvBD"),
    Account(
        "112t8sw5AggHj5K7c2gZFqnuUypfRimgLvoxHK8U6yE33wAeU1bV2DLkRVhVDHycwaM5LFwLeVLyMGBCx97FyBx3NTHimNVb9MwjP2BeSDDd"),
    Account(
        "112t8sw5fAsCpef9kSYwit7deNVmwhLs64R6s2cH49rWna8yhyCybKM85sFmegtVnEarWXuaTjvVaxVEu3rDTrz7dyUQcy5m37o3LekSxAWe"),
    Account(
        "112t8sw5ne46SFtGAvvhDMj31LdhJcqsTnkiSz439WJc7xtLsRDiA8uq2AYaCPhi3a56soeSBdqRSwyWSBajv89GrPsQk2svLUonNBCSvHX9"),
    Account(
        "112t8sw6FFcmpk5XwvnC1jgQSTPeDcvSVQQZpQbodQABHqt2abNSsjBSFummAFrLxnuZzd7KpFbdWg9WX27ECgyczdWog1HUCuQcUWVsXfeS"),
    Account(
        "112t8sw6XHCn6jmMAfC47kvrhRVG4o1zKBA41wxfb53S3tHXLZNyWKZWSgSHnEPAHKyEvvho3b4oKLxfNka5LJttkmmYpzq2Wccn6ohvjvKN"),
    Account(
        "112t8sw6cetGmM3HhBX3M3Sy69HWbHHa3QMmJXAmVs8QwmDJHoWRgkG2a1SWMjRGZ5xQ8vmFqtUnFXGBUH4zk4jva4NL459GPX9BKzgLZGPL"),
    Account(
        "112t8sw6zCUr3AHqEDvEwisiAdvueNXBgxF9FncvX7gvB8AZtgjrrKcimuumszHsv1UdjqrFmfWGwK6wZWKwb3vhcmAkWRjL9t3jj2vZc67W"),
    Account(
        "112t8sw7CFBzQb33w2uZ9s3aEeKVWYx2LEWQNGDLc6aTNEVoWP2dBihDWYs2gcWfKWUVoeVCKKm6WFz1u5V2VqoXrpSZsqguCN3jSG4nAqTR"),
)

ChainConfig.BLOCK_PER_EPOCH = 20
ChainConfig.BLOCK_TIME = 10
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

    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1751), coin(1755), not_yet_stake_list)

    def staking_action(account):
        return account.stake_and_reward_me().expect_no_error()

    with ThreadPoolExecutor() as executor:
        for acc in not_yet_stake_list:
            executor.submit(staking_action, acc)

    ChainHelper.wait_till_next_epoch()


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
        accounts_from_shard1 += validators.get_accounts_in_shard(i)

    INFO(f'Change request handler to shard {shard_committee}, which user is a committee')
    SUT.REQUEST_HANDLER = SUT.shards[shard_committee].get_representative_node()

    INFO(f'Get shard best state detail, get epoch, beacon height')
    shard0_state_detail = SUT().get_shard_best_state_detail_info(shard_committee)
    epoch = shard0_state_detail.get_epoch()
    current_height = shard0_state_detail.get_beacon_height()
    last_height = ChainHelper.cal_last_height_of_epoch(epoch) - 1
    second_till_last_height = (last_height - current_height) * ChainConfig.BLOCK_TIME
    INFO(f"Current beacon height {current_height}, calculated last height of epoch: {last_height}")

    shard0_committees = shard0_state_detail.get_shard_committee()
    committee_4th_0 = shard0_committees[4]
    committee_5th_0 = shard0_committees[5]
    acc_committee_4th = accounts_from_shard1.find_account_by_public_k(committee_4th_0.get_inc_public_key())
    acc_committee_5th = accounts_from_shard1.find_account_by_public_k(committee_5th_0.get_inc_public_key())
    acc_stop_stake = acc_committee_4th if acc_committee_4th is not None else acc_committee_5th
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
    bal_b4_un_stake = acc_stop_stake.get_prv_balance()

    INFO(f'Send stop auto staking to user originated shard')
    acc_stop_stake.REQ_HANDLER = SUT.shards[shard_origin].get_representative_node()
    un_stake_tx = acc_stop_stake.stk_un_stake_me().expect_no_error().subscribe_transaction()
    assert un_stake_tx.get_block_height() > 0
    acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()

    INFO(f'Get beacon best state from full node')
    SUT.REQUEST_HANDLER = SUT.full_node
    BBI = SUT().get_beacon_best_state_info()

    auto_stake_status = BBI.get_auto_staking_committees(acc_stop_stake)
    # if shard_committee == SHARD0:
    #   # committee of shard 0 will be swapped out and refund staking amount right in next epoch
    # assert auto_stake_status is None, f'Expect auto staking status to be removed, got {auto_stake_status} instead'
    # else:
    # other shard, committee must complete another round
    # before get completely remote of committee list and refund staking amount
    assert auto_stake_status is False, f'Expect auto staking status to be False, got {auto_stake_status} instead'
    acc_stop_stake.stk_wait_till_i_am_committee()
    acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()
    BBI = SUT().get_beacon_best_state_info()
    auto_stake_status = BBI.get_auto_staking_committees(acc_stop_stake)
    assert auto_stake_status is None, f'Expect auto staking status to be removed, got {auto_stake_status} instead'

    bal_af_un_stake = acc_stop_stake.get_prv_balance()
    INFO(f"Bal before - after unstake: {bal_b4_un_stake} - {bal_af_un_stake}")
    assert bal_af_un_stake == bal_b4_un_stake + ChainConfig.STK_AMOUNT - un_stake_tx.get_fee()
