import pytest

from IncognitoChain.Configs.Constants import ChainConfig
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account, AccountGroup
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

# COIN_MASTER.top_him_up_prv_to_amount_if(coin(1751), coin(1755), validators)
# for validator in validators:
#     validator.stake_and_reward_me().subscribe_transaction()

ChainConfig.BLOCK_PER_EPOCH = 20
ChainConfig.BLOCK_TIME = 10
SHARD0 = 0
SHARD1 = 1
NUM_OF_SHARD = 2
NUM_OF_COMMITTEE_SWAP_OUT = 2


# todo: setup, stake if not yet staked, for now, must stake the validators above manually

def test_stop_auto_staking_not_work():
    """
    stake account must be from shard 1 and is a committee of shard 0
    @return:
    """
    INFO()
    INFO(f'Get all account originate from shard {SHARD1}')
    accounts_from_shard1 = AccountGroup()
    for i in range(SHARD1, 8, NUM_OF_SHARD):
        # account belong to the shard , not account of committee of the shard
        accounts_from_shard1 += validators.get_accounts_in_shard(i)

    INFO(f'Change request handler to shard {SHARD0}')
    SUT.REQUEST_HANDLER = SUT.shards[SHARD0].get_representative_node()

    INFO(f'Get shard best state detail, get epoch, beacon height')
    shard0_state_detail = SUT.REQUEST_HANDLER.get_shard_best_state_detail_info(SHARD0)
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

    INFO(f'Wait till last beacon height then send stop auto staking to shard {SHARD1}')
    # breakpoint()
    WAIT(second_till_last_height)
    shard0_state_detail = SUT.REQUEST_HANDLER.get_shard_best_state_detail_info(SHARD0)
    current_height = shard0_state_detail.get_beacon_height()
    INFO(f"Current beacon height {current_height}")
    if last_height != current_height:
        pytest.skip(f"Current beacon height {current_height} is not the last height of epoch, skip the test")
    acc_stop_stake.REQ_HANDLER = SUT.shards[SHARD1].get_representative_node()
    acc_stop_stake.stk_un_stake_me()
    acc_stop_stake.stk_wait_till_i_am_swapped_out_of_committee()
    SUT.REQUEST_HANDLER = SUT.full_node

    BBD = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    BBD.is_he_a_committee(acc_stop_stake)
    BBD.is_this_committee_auto_stake(acc_stop_stake)
