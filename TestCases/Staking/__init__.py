"""
this test suite is for testing on local chain only, with the following config
chain_committee_min = 4
chain_committee_max = 6
"""
import random

import pytest

from Configs.Constants import coin, ChainConfig
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO, STEP, ERROR
from Helpers.TestHelper import ChainHelper, l3
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import SUT, ACCOUNTS, STAKER_ACCOUNTS, COMMITTEE_ACCOUNTS, BEACON_ACCOUNTS
from Objects.TransactionObjects import TransactionDetail
from TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

key_list_file = KeyListJson()
fixed_validators = key_list_file.get_shard_fix_validator_accounts()
stakers = key_list_file.get_staker_accounts()
try:
    num_of_auto_stake = ChainConfig.ACTIVE_SHARD * (ChainConfig.SHARD_COMMITTEE_SIZE - ChainConfig.FIX_BLOCK_VALIDATOR)
    auto_stake_list = stakers[:num_of_auto_stake]
    stake_account = stakers[num_of_auto_stake]
    staked_account = stakers[num_of_auto_stake + 1]
    account_a = stakers[num_of_auto_stake + 2]
    account_u = stakers[num_of_auto_stake + 3]
    account_t = stakers[num_of_auto_stake + 4]
except IndexError:
    raise EnvironmentError(f'Not enough staker in keylist file for the test. '
                           f'Check the file, and make sure nodes are run or else chain will be stuck')

token_holder_shard_0 = Account(
    "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E")
token_holder_shard_1 = Account(
    "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx")

amount_stake_under_1750 = random.randint(coin(1), coin(1749))
amount_stake_over_1750 = random.randint(coin(1751), coin(1850))
amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = coin(100000)
token_contribute_amount = coin(10000)
prv_contribute_amount = coin(10000)
token_id = '8c4a05c7dc9cd3949f9bbf41b56198be5478004f739bebbd92368706431d7ee5'
# token_id = None  # if None, the test will automatically mint a new token and use it for testing
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
    wait_need = False
    for committee in auto_stake_list[:num_of_auto_stake]:
        if not beacon_bsd.is_he_a_committee(committee) and beacon_bsd.get_auto_staking_committees(
                committee) is None:
            committee.stake_and_reward_me()
            wait_need = True

    if wait_need:
        ChainHelper.wait_till_next_epoch()

    STEP(0.4, "Verify environment, 6 node per shard")
    committee_state = SUT().get_committee_state()
    for shard_id in range(committee_state.count_num_of_shard()):
        num_committee_in_shard = committee_state.get_shard_committee_size(shard_id)
        assert num_committee_in_shard == ChainConfig.SHARD_COMMITTEE_SIZE, \
            f"shard {shard_id}: {num_committee_in_shard} committees"

    global token_id, tear_down_trx008
    if token_id is None:
        trx008.account_init = token_holder_shard_0
        trx008.prv_contribute_amount = prv_contribute_amount
        trx008.token_contribute_amount = token_contribute_amount
        trx008.token_init_amount = token_init_amount
        trx008.setup_module()
        token_id = trx008.test_init_ptoken()
        INFO(f'Setup module: new token: {token_id}')
        token_holder_shard_0.send_token_to(token_holder_shard_1, token_id, token_contribute_amount / 2, prv_fee=-1,
                                           prv_privacy=0).expect_no_error().subscribe_transaction()
        tear_down_trx008 = True
    else:
        INFO(f'Setup module: use existing token: {token_id}')


def no_teardown_module():
    if tear_down_trx008:
        trx008.teardown_module()

def get_staking_info_of_validator(committee_pub_k, shard_bsd_list):
    """

    @param committee_pub_k: string: committee public key
    @param shard_bsd_list: List[ShardBestStateDetailInfo obj]
    @return: staker - Account obj, validator - Account obj, receiver_reward - Account obj, string
    """
    acc_group = ACCOUNTS + STAKER_ACCOUNTS + COMMITTEE_ACCOUNTS + BEACON_ACCOUNTS
    string = ''
    validator = acc_group.find_account_by_key(committee_pub_k)
    for shard_bsd in shard_bsd_list:
        tx_id = shard_bsd.get_staking_tx(committee_pub_k)
        if tx_id:
            break
    if tx_id:
        response = TransactionDetail().get_transaction_by_hash(tx_id)
        payment_receiver_reward = response.get_meta_data().get_payment_address_reward_receiver()
        receiver_reward = acc_group.find_account_by_key(payment_receiver_reward)
        public_k_staker = response.get_input_coin_pub_key()
        staker = acc_group.find_account_by_key(public_k_staker)
    else:
        receiver_reward = validator
        staker = validator
    for acc in [staker, validator, receiver_reward]:
        assert acc, ERROR(f'committee_pub_k not found: {committee_pub_k}')

    string += f'{l3(staker.private_key)}__{l3(validator.public_key)}__{l3(receiver_reward.payment_key)}'
    return staker, validator, receiver_reward, string
