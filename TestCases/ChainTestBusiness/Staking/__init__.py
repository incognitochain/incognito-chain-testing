"""
this test suite is for testing on local chain only, with the following config
chain_committee_min = 4
chain_committee_max = 6
"""
import random
from concurrent.futures import ThreadPoolExecutor

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO, STEP
from Objects.AccountObject import Account, AccountGroup, COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS

key_list_file = KeyListJson()
fixed_validators = key_list_file.get_shard_fix_validator_accounts()
stakers = key_list_file.get_staker_accounts().attach_to_node(SUT())

try:
    num_of_auto_stake = ChainConfig.ACTIVE_SHARD * (ChainConfig.SHARD_COMMITTEE_SIZE - ChainConfig.FIX_BLOCK_VALIDATOR)
    auto_stake_list = AccountGroup(*(stakers[:num_of_auto_stake]))
    account_x = stakers[num_of_auto_stake]
    account_y = stakers[num_of_auto_stake + 1]
    account_a = stakers[num_of_auto_stake + 2]
    account_u = stakers[num_of_auto_stake + 3]
    account_t = stakers[num_of_auto_stake + 4]
    group_staker = AccountGroup(account_x, account_y, account_a, account_u, account_t)
except IndexError:
    raise EnvironmentError(f'Not enough staker in keylist file for the test. '
                           f'Check the file, and make sure nodes are run or else chain will be stuck')
COIN_MASTER.top_up_if_lower_than(group_staker, coin(1), coin(5))
token_receiver = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')
token_receiver.attach_to_node(SUT())
token_receiver.submit_key()
list_acc_x_shard = AccountGroup()
for i in range(ChainConfig.ACTIVE_SHARD):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard.append(acc)
    except IndexError:
        INFO(f'Not found account in shard {i}')
token_owner = list_acc_x_shard[0]

token_owner.submit_key()
auto_stake_list.submit_key()
group_staker.submit_key()
list_acc_x_shard.submit_key()

amount_stake_under_1750 = random.randint(coin(1), coin(1749))
amount_stake_over_1750 = random.randint(coin(1751), coin(1850))
amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = coin(100000)
token_contribute_amount = coin(10000)
prv_contribute_amount = coin(10000)
# setup_module function below will check if this token is existed in chain, if not, init new token
token_id = '5a0df1204de635d5604b4e20fc9845b731a4dd13d12d60db2ce09a991810654a'
tear_down_trx008 = False


def setup_module():
    INFO("SETUP MODULE")
    STEP(0.1, 'Check current fixed validators to make sure that this test wont be running on testnet')
    beacon_state = SUT().get_beacon_best_state_detail_info()
    all_shard_committee = beacon_state.get_shard_committees()
    list_fixed_validator_public_k = []
    for shard, committees in fixed_validators.items():
        for committee in committees:
            list_fixed_validator_public_k.append(committee.public_key)

    count_fixed_validator_in_beacon_state = 0
    for shard, committees in all_shard_committee.items():
        for committee in committees:
            if committee.get_inc_public_key() in list_fixed_validator_public_k:
                count_fixed_validator_in_beacon_state += 1

    if count_fixed_validator_in_beacon_state < len(list_fixed_validator_public_k):
        msg = 'Suspect that this chain is TestNet. Skip staking tests to prevent catastrophic disaster'
        INFO(msg)
        pytest.skip(msg)

    STEP(0.3, 'Top up, stake and wait till becoming committee')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    wait_list = [acc for acc in auto_stake_list if beacon_bsd.get_auto_staking_committees(acc) is None]
    # breakpoint()
    COIN_MASTER.top_up_if_lower_than(wait_list, coin(1750), coin(1751))
    with ThreadPoolExecutor() as executor:
        def stake_n_check(acc):
            acc.stake_and_reward_me().get_transaction_by_hash()

        for acc in wait_list:
            executor.submit(stake_n_check, acc)
    with ThreadPoolExecutor() as executor:
        for acc in wait_list:
            executor.submit(acc.stk_wait_till_i_am_committee)

    STEP(0.4, "Verify environment, 6 node per shard")
    committee_state = SUT().get_committee_state()
    for shard_id in range(committee_state.count_num_of_shard()):
        num_committee_in_shard = committee_state.get_shard_committee_size(shard_id)
        assert num_committee_in_shard == ChainConfig.SHARD_COMMITTEE_SIZE, \
            f"shard {shard_id}: {num_committee_in_shard} committees"

    all_ptoken_in_chain = SUT().get_all_token_in_chain_list()
    global token_id, tear_down_trx008
    if not all_ptoken_in_chain.get_tokens_info(id=token_id) \
            or (token_owner.get_balance(token_id) == 0 and all_ptoken_in_chain.get_tokens_info(id=token_id)):
        tx_init = token_owner.init_custom_token_new_flow(token_init_amount)
        token_id = tx_init.get_token_id()
        tx_init.get_transaction_by_hash()
        token_owner.wait_for_balance_change(token_id, 0)
        INFO(f'Setup module: new token: {token_id}')
    else:
        INFO(f'Setup module: use existing token: {token_id}')
    token_owner.top_up_if_lower_than(list_acc_x_shard, 10e9, 11e9, token_id)
