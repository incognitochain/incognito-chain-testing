"""
this test suite is for testing on local chain only, with the following config
block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6
"""
from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import INFO, STEP
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

committee_list = {
    "0": [
        Account(
            '112t8rnqijhT2AqiS8NBVgifb86sqjfwQwf4MHLMAxK3gr1mwxMaeUWQtR1MfxHscrKQ2MsyQMvJ3LEu49LEcZzTzoJCkCiewQ9p6wN5SrG1'),
        Account(
            '112t8rnud1R3of9rPkdKHWy8mQ5gMpXuBjLGhVrNurvHC93fF6qfiaEC8Nf7AHRbgrn1KF33akoNMNqUEUdSU7caXYvRL4uT58fhCuDV2Qs8'),
        Account(
            '112t8rnw7XyoehhKAUbNTqtVcda1eki89zrD2PfGMBKoYHvdE94ApWvXDtJvgotQohRot8yV52RZz2JjPtYGh4xsxb3gahn7RRWocEtW2Vei'),
        Account(
            '112t8ro1sHxz5xDkTs9i9VHA4cXVb5iqwCq2H2ffYYbGRh2wUHSHRRbnSQEMSnGiMvZAFLCccNzjZV9bSrphwGxxgtskVcauKNdgTEqA9bsf'),
        Account(
            '112t8ro424gNfJkKqDj25PjgWqCFTgG83TRERX1djUVr2wgJB6Lwk7NFi4pU8KxWSHsb4xK7UwPVYJ48FEGTzrB9jM58WfyvaJGCsT83jfNs'),
        Account(
            '112t8ro719sBgnX2GouVjLEZUvVwaepg8FkG35GtrFiFHeuE3y47PjXBbxHQdX1z87AAtEH5WCMZ8GUbhaZL3DbJuLqj7AAxGoc85damvB4J')
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
        Account(
            '112t8rnkSY1EtXtfZNGTKU6CFhfrdQ2YqLbLpfFEUGzVfoQeC6d47M5jWwv542aHJgEdtBKxmr2aikjxibL75rqGXEyKfUPXg1yp3xnCpL7D'),
        Account(
            '112t8rnmCktTnBnX866sSj5BzU33bUNZozJRes9xL7GPqSTQX9gsqG3qkiizsZuzV7BFs7CtpqNhcWfEMUZkkT7JnzknDB49jD2UBUemdnbK')
    ]
}
auto_stake_list = [
    # shard 0
    Account(
        "112t8ro424gNfJkKqDj25PjgWqCFTgG83TRERX1djUVr2wgJB6Lwk7NFi4pU8KxWSHsb4xK7UwPVYJ48FEGTzrB9jM58WfyvaJGCsT83jfNs",
        "12S3zVjHAKzQpdCAbH5oK9ebbpNpjiPaAybYK2dnkHDb27eiCmbNodKSMeDx57fVo3SJm129uzxgAgAwbmVXR7FhP6gbSS98Xc7R9TV",
        validator_key="1gEDr5m5sFrbtMEs3ewDHuadQrUDgxenYq27dzDFrsAH5nfgMu",
        shard=0),
    Account(
        "112t8ro719sBgnX2GouVjLEZUvVwaepg8FkG35GtrFiFHeuE3y47PjXBbxHQdX1z87AAtEH5WCMZ8GUbhaZL3DbJuLqj7AAxGoc85damvB4J",
        "12S4yFjgt4ZB4hthHLA2zw3jsUuMoEc2Sd9gEAmyLutM6Z2PDPyH2A1HBG5ikhwubVMGgDLGkvZt2ViyaUkdax3yR92HnDxFtTHxGgU",
        validator_key="1h8ndvctJZ1UeYUf6V2w3TJQW4zbx1w3wVVyGF9u5hoHgPpRSW",
        shard=0),
    # shard 1
    Account(
        "112t8rnkSY1EtXtfZNGTKU6CFhfrdQ2YqLbLpfFEUGzVfoQeC6d47M5jWwv542aHJgEdtBKxmr2aikjxibL75rqGXEyKfUPXg1yp3xnCpL7D",
        "12S2CAREWHLabMJBEhFe4yjC8mfVsNoMV1iykPnurvTKfoz9DbPTWXN3Wz4Qo7Zz2NFqcKexP5bxgvyhCEwpM7k3iKAxJE4QoG8ngjn",
        validator_key="12Rs8gEzq4xiNydunM6pKvRZBG7N5vgwjpNHdxVSK7B9v1VjMgn",
        shard=1),
    Account(
        "112t8rnmCktTnBnX866sSj5BzU33bUNZozJRes9xL7GPqSTQX9gsqG3qkiizsZuzV7BFs7CtpqNhcWfEMUZkkT7JnzknDB49jD2UBUemdnbK",
        "12S6rtLu99JTCVFAmDGMofo5Tk83nJUYXuUbCBTRiDjUbU4JKLmg54LESZ75qfMW8hZhFdHPJDyR4AzxoEbbvQKfXV7jbRhM8JJzHvK",
        validator_key="12bkVKaxqZE2aXLxmaFHPwvpbPjojkq6RPNzxw48yNWbYNDPSor",
        shard=1)

]

token_holder_shard_0 = Account(
    "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
    "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr",
    shard=0)
token_holder_shard_1 = Account(
    "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx",
    "12RqmK5woGNeBTy16ouYepSw4QEq28gsv2m81ebcPQ82GgS5S8PHEY37NU2aTacLRruFvjTqKCgffTeMDL83snTYz5zDp1MTLwjVhZS",
    shard=1)
stake_account = Account(
    "112t8rowNCSCcPcT6JNHqNLHJsPJTk5t9c9fu8eCVCXXoAsFgdxH2xXCjit3oumU1bdQYsWQP72Z1djfMvg77GfysH2ftYJz88EpyZbEdxvq",
    "12RyxZRnMSMJSXvR56A5f9vVYqEdFWu4rcN641xvJ2VkkArXevSBUQRfNdy1XFSdUTHJgEWSafs6XPepTtseSUNb7dpw8XVJDyH4icn",
    validator_key="12X6gd8uFVTZFKQ39ZYGoKqgUj5EXcfWKGbGmrweaAMZmW59P39",
    shard=0)
staked_account = Account(
    "112t8roAjzuJQvmH9PBEunsPRrdpfxXh768DBrhrnit3GxamwdcyFmgXxvP4ZaGr3uikLkUJWV7b2gmTBuBnNVQQzCpJkp3yVXXXeXsxdAL3",
    "12RxviU2JFFSDop8y3ihfBx6UG8NZNKuhbDvtWu5TsRqELinFcHywi4VteZTptt9QzLW2t3ieuKSJomLkABNUfc9md42JXrpJPExc3d",
    validator_key="12i58s9bCzhfec5nNJdniDPggxS8az6Mj7WaSCr2Uqio1u4dEFY",
    shard=1)

account_a = Account(
    "112t8ropXTnh4BAjMLidgzVB4KGxd1rQiXrPsJsDELd5sfXyUFXVpebB2KgMRexv1Uab7p1Y2TGfqDT9iQyqW8MNd5ZC72rbAee2J8nkUiA7",
    "12Rq3nYu17UfkVS173qGa4HsdPYHHSM9nZNiL46SdryLQgTWF7bErt5QiWhFprgUbbXPy7fG3CP1uHVd3DRXY5b8oUVbEUjdwYVL9Sv",
    validator_key="12we3GBdhRaTtdxR1Dn5wGJaWs9VzuMsHEpCKCSWQ637yg56oDz")
account_u = Account(
    "112t8rop2yLXRJyKi4WsKTi3cqHgRQuG73zBBExm5QVoRbSgK1qEEgoTpZTQVz5dJeLfbzmx4K4FUJzDCSAkbAuF29U2Q3yngD7RstxYuWmT",
    "12RpWN3mmDzCiDEcnt5aQDoBrqkJdxCwikvEnoBCE8V8Xe3orAeYgzcArVxyn9jmRAH8R7uzs5bCE9or3Q2Hawpq7VSKFb25onkW8Uc",
    validator_key="1HTH7f2b53LjMe9bru11Jprn23rx5YfY63H1DzPTZiTHyidkZx")
account_t = Account(
    "112t8roADWxdSoEnc9bjCBvZTzVGpw2ejL3QvoCfBPkMmmKmDqH8Mk6JYEx2HqCtCtF2fMo9eRL4NuodKoLmVpXwJYpUxMPGxHtF6sdtrSTw",
    "12S1QeLwrQRNQ8CbnJ6u7ydqFZsZbBs5rHFgfYPcoBjvECsn11HV8Pjexp16ZqwYqnmgsFy5BSLyebDTbTDTsc69usPpkd8WtcWdaGe",
    validator_key="12JZUz6GN8JnwfoGLa7SpaUYuKnphhbRqsbYr3BAH6yf9mR1bz")

block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6

amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = coin(100000)
token_contribute_amount = coin(10000)
prv_contribute_amount = coin(10000)
token_id = None


def setup_module():
    INFO("SETUP MODULE")
    for account in auto_stake_list + [stake_account, staked_account]:
        if account.get_prv_balance() <= coin(1750) and account.am_i_a_committee() is False:
            COIN_MASTER.send_prv_to(account, coin(1850) - account.get_prv_balance_cache(),
                                    privacy=0).subscribe_transaction()
            if COIN_MASTER.shard != account.shard:
                account.subscribe_cross_output_coin()
    for committee in auto_stake_list:
        if committee.am_i_a_committee() is False:
            committee.stake_and_reward_me()

    for committee in auto_stake_list:
        committee.wait_till_i_am_committee()

    # epoch = SUT.full_node.system_rpc().help_get_current_epoch()
    # SUT.full_node.system_rpc().help_wait_till_epoch(epoch + 2)

    STEP(0, "Verify environment, 6 node per shard")
    number_committee_shard_0 = SUT.full_node.system_rpc().help_count_committee_in_shard(0, refresh_cache=True)
    number_committee_shard_1 = SUT.full_node.system_rpc().help_count_committee_in_shard(1, refresh_cache=False)
    assert number_committee_shard_0 == 6
    assert number_committee_shard_1 == 6

    # breakpoint()
    trx008.account_init = token_holder_shard_0
    trx008.prv_contribute_amount = prv_contribute_amount
    trx008.token_contribute_amount = token_contribute_amount
    trx008.token_init_amount = token_init_amount
    trx008.setup_module()
    trx008.test_init_ptoken()
    global token_id
    token_id = trx008.custom_token_id
    INFO(f'Setup module: Token: {token_id}')
    token_holder_shard_0.send_token_to(token_holder_shard_1, token_id, token_contribute_amount / 2, prv_fee=-1,
                                       prv_privacy=0)


def teardown_module():
    trx008.teardown_module()
