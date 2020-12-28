"""
this test suite is for testing on local chain only, with the following config
chain_committee_min = 4
chain_committee_max = 6
"""
import random

import pytest

from IncognitoChain.Configs.Constants import coin, ChainConfig
from IncognitoChain.Helpers.KeyListJson import KeyListJson
from IncognitoChain.Helpers.Logging import INFO, STEP
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

key_list_file = KeyListJson()

fixed_validators = key_list_file.get_shard_fix_validator_accounts()
auto_stake_list = key_list_file.get_staker_accounts()

token_holder_shard_0 = Account(
    "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E")
token_holder_shard_1 = Account(
    "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx")
stake_account = Account(
    "112t8rowNCSCcPcT6JNHqNLHJsPJTk5t9c9fu8eCVCXXoAsFgdxH2xXCjit3oumU1bdQYsWQP72Z1djfMvg77GfysH2ftYJz88EpyZbEdxvq")
staked_account = Account(
    "112t8roAjzuJQvmH9PBEunsPRrdpfxXh768DBrhrnit3GxamwdcyFmgXxvP4ZaGr3uikLkUJWV7b2gmTBuBnNVQQzCpJkp3yVXXXeXsxdAL3")

account_a = Account(
    "112t8ropXTnh4BAjMLidgzVB4KGxd1rQiXrPsJsDELd5sfXyUFXVpebB2KgMRexv1Uab7p1Y2TGfqDT9iQyqW8MNd5ZC72rbAee2J8nkUiA7")
account_u = Account(
    "112t8rop2yLXRJyKi4WsKTi3cqHgRQuG73zBBExm5QVoRbSgK1qEEgoTpZTQVz5dJeLfbzmx4K4FUJzDCSAkbAuF29U2Q3yngD7RstxYuWmT")
account_t = Account(
    "112t8roADWxdSoEnc9bjCBvZTzVGpw2ejL3QvoCfBPkMmmKmDqH8Mk6JYEx2HqCtCtF2fMo9eRL4NuodKoLmVpXwJYpUxMPGxHtF6sdtrSTw")

amount_stake_under_1750 = random.randint(coin(1), coin(1749))
amount_stake_over_1750 = random.randint(coin(1751), coin(1850))
amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = coin(100000)
token_contribute_amount = coin(10000)
prv_contribute_amount = coin(10000)
token_id = '6385e00c6db9f6bfba8d235da8436ce9ab60339ad30fbc0696d055818bf75292'
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

    STEP(0.2, 'Top up committees')
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1850), auto_stake_list + [stake_account, staked_account])

    STEP(0.3, 'Stake and wait till becoming committee')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    wait_need = False
    num_of_auto_stake = ChainConfig.ACTIVE_SHARD * (ChainConfig.SHARD_COMMITTEE_SIZE - ChainConfig.FIX_BLOCK_VALIDATOR)
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
