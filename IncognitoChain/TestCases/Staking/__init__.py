"""
this test suite is for testing on local chain only, with the following config
chain_committee_min = 4
chain_committee_max = 6
"""
import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import INFO, STEP
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

beacon_list = [
    Account(
        '112t8rncBDbGaFrAE7MZz14d2NPVWprXQuHHXCD2TgSV8USaDFZY3MihVWSqKjwy47sTQ6XvBgNYgdKH2iDVZruKQpRSB5JqxDAX6sjMoUT6'),
    Account(
        '112t8rnfXYskvWnHAXKs8dXLtactxRqpPTYJ6PzwkVHnF1begkenMviATTJVM6gVAgSdXsN5DEpTkLFPHtFVnS5RePi6aqTSth6dP4frcJUT'),
    Account(
        '112t8rngZ1rZ3eWHZucwf9vrpD1DNUAmrTTARSsptNDFrEoHv3QsDY3dZe8LXy3GeKXmeso8nUPsNwUM2qmZibQVXxGzstF4vZsYzJ83scFL'),
    Account(
        '112t8rnpXg6CLjvBg2ZiyMDgpgQoZuAjYGzbm6b2eXVSHUKjZUyb2LVJmJDPw4yNaP5M14DomzC514joTH3EVknRwnnGViWuH2HJuN6cpNhz')]

fixed_validators = {
    "0": [
        Account(
            '112t8rnqijhT2AqiS8NBVgifb86sqjfwQwf4MHLMAxK3gr1mwxMaeUWQtR1MfxHscrKQ2MsyQMvJ3LEu49LEcZzTzoJCkCiewQ9p6wN5SrG1'),
        Account(
            '112t8rnud1R3of9rPkdKHWy8mQ5gMpXuBjLGhVrNurvHC93fF6qfiaEC8Nf7AHRbgrn1KF33akoNMNqUEUdSU7caXYvRL4uT58fhCuDV2Qs8'),
        Account(
            '112t8rnw7XyoehhKAUbNTqtVcda1eki89zrD2PfGMBKoYHvdE94ApWvXDtJvgotQohRot8yV52RZz2JjPtYGh4xsxb3gahn7RRWocEtW2Vei'),
        Account(
            '112t8ro1sHxz5xDkTs9i9VHA4cXVb5iqwCq2H2ffYYbGRh2wUHSHRRbnSQEMSnGiMvZAFLCccNzjZV9bSrphwGxxgtskVcauKNdgTEqA9bsf'),
    ],

    "1": [
        Account(
            '112t8rncy1vEiCMxvev5EkUQyfH9HLeManjS4kbcsSiMgp4FEiddsiMunhYL2pa8wciCAWxYtt9USgCv21fe2PkSxfnRkiq4AmDvJe33wtgV'),
        Account(
            '112t8rndMXjgDEGkuUmVedQxVYuZsQK5UvM9ZR1aZximBuNNJKpBn9j93MRqLBS17mHoCdLQNMmoYyuERZ1M3pRMG8SQj3NraHsG9eZPbbRK'),
        Account(
            '112t8rngznzWowvtXKyTnE9avawQGJCVgfJounHDT5nWucoVFv43TYu9PyjiGpPXXXQbCVEzxxCSfDmPNEBknK5B8n5qFiaddStg2M9pCYkZ'),
        Account(
            '112t8rnk4jduDzQGcmzKXr6r1F69TeQtHqDBCehDXPpwQTo7eDkEKFGMDGar46Jy4gmqSZDgwyUwpnxGkCnE2oEXmQ5FQpQJ4iMpDqLkgzwy'),
    ]
}
auto_stake_list = [
    # shard 0
    Account(
        "112t8ro424gNfJkKqDj25PjgWqCFTgG83TRERX1djUVr2wgJB6Lwk7NFi4pU8KxWSHsb4xK7UwPVYJ48FEGTzrB9jM58WfyvaJGCsT83jfNs"),
    Account(
        "112t8ro719sBgnX2GouVjLEZUvVwaepg8FkG35GtrFiFHeuE3y47PjXBbxHQdX1z87AAtEH5WCMZ8GUbhaZL3DbJuLqj7AAxGoc85damvB4J"),
    # shard 1
    Account(
        "112t8rnkSY1EtXtfZNGTKU6CFhfrdQ2YqLbLpfFEUGzVfoQeC6d47M5jWwv542aHJgEdtBKxmr2aikjxibL75rqGXEyKfUPXg1yp3xnCpL7D"),
    Account(
        "112t8rnmCktTnBnX866sSj5BzU33bUNZozJRes9xL7GPqSTQX9gsqG3qkiizsZuzV7BFs7CtpqNhcWfEMUZkkT7JnzknDB49jD2UBUemdnbK")

]

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
token_id = None  # if None, the test will automatically mint a new token and use it for testing
# token_id = '6c345aaaf93107a205240e1245171adcbcf5a45a89609cdd2e3a36b9bb39da41'
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
    for committee in auto_stake_list:
        if beacon_bsd.is_he_a_committee(committee) is False:
            committee.stake_and_reward_me()

    with ThreadPoolExecutor(max_workers=len(auto_stake_list)) as executor:
        for committee in auto_stake_list:
            executor.submit(committee.stk_wait_till_i_am_committee)

    STEP(0.4, "Verify environment, 6 node per shard")
    number_committee_shard_0 = SUT().help_count_committee_in_shard(0, refresh_cache=True)
    number_committee_shard_1 = SUT().help_count_committee_in_shard(1, refresh_cache=False)
    assert number_committee_shard_0 == 6, f"shard 0: {number_committee_shard_0} committee"
    assert number_committee_shard_1 == 6, f"shard 1: {number_committee_shard_1} committee"

    # breakpoint()
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


def teardown_module():
    if tear_down_trx008:
        trx008.teardown_module()
