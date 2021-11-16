"""
HOW TO RUN: URL=[node url] python3 -m pytest [path to this file]
"""
import os

from Configs.Constants import PBNB_ID
from Objects.AccountObject import Account, AccountGroup
from Objects.IncognitoTestCase import SUT
from Objects.NodeObject import Node
from Objects.TestBedObject import TestBed

SUT()
full_node_url = os.getenv('URL')
TestBed.REQUEST_HANDLER = Node().parse_url(full_node_url)
account_0 = Account(  # must in SHARD 0
    '112t8rnbNst56EFVhefVgQcJVqASQPevVGmkb2Mdnhm61uyktU5ZuWbZ1KGAp7w7U4fUyz4XZxBVmaUifsjsLxYbkhtkff5YwQptNxELRVcX'). \
    set_remote_addr({PBNB_ID: 'tbnb1hmgztqgx62t3gldsk7n9wt4hxg2mka0fdem3ss'})
account_1 = Account(  # must in SHARD 1
    '112t8rnbqC92JnAE3bqthKUezcaG9oESKoNxawJZJii7q3JUZWVwWHyaKPoWqUmA8QRGiNpY5zg7XpYgQxmBz8LkLQutPh57HqLFQGFKgi7W')
account_11 = Account(  # must in SHARD 1
    '112t8rneoGyBMorQEefPyb24e9dJrxcLPBiHcVe93c5MxhXDfL3ztocqM9r6gwJ5Ko3jJmC3EAsubBxEG5g6DjJ4S1tjVKKDrNAq4sJ5LRfq')
ACCOUNTS = AccountGroup(account_0, account_1, account_11)  # must include all accounts aboves

fixed_validators = {
    "0": AccountGroup(
        Account(
            '112t8rnqijhT2AqiS8NBVgifb86sqjfwQwf4MHLMAxK3gr1mwxMaeUWQtR1MfxHscrKQ2MsyQMvJ3LEu49LEcZzTzoJCkCiewQ9p6wN5SrG1'),
        Account(
            '112t8rnud1R3of9rPkdKHWy8mQ5gMpXuBjLGhVrNurvHC93fF6qfiaEC8Nf7AHRbgrn1KF33akoNMNqUEUdSU7caXYvRL4uT58fhCuDV2Qs8'),
        Account(
            '112t8rnw7XyoehhKAUbNTqtVcda1eki89zrD2PfGMBKoYHvdE94ApWvXDtJvgotQohRot8yV52RZz2JjPtYGh4xsxb3gahn7RRWocEtW2Vei'),
        Account(
            '112t8ro1sHxz5xDkTs9i9VHA4cXVb5iqwCq2H2ffYYbGRh2wUHSHRRbnSQEMSnGiMvZAFLCccNzjZV9bSrphwGxxgtskVcauKNdgTEqA9bsf'),
    ),

    "1": AccountGroup(
        Account(
            '112t8rncy1vEiCMxvev5EkUQyfH9HLeManjS4kbcsSiMgp4FEiddsiMunhYL2pa8wciCAWxYtt9USgCv21fe2PkSxfnRkiq4AmDvJe33wtgV'),
        Account(
            '112t8rndMXjgDEGkuUmVedQxVYuZsQK5UvM9ZR1aZximBuNNJKpBn9j93MRqLBS17mHoCdLQNMmoYyuERZ1M3pRMG8SQj3NraHsG9eZPbbRK'),
        Account(
            '112t8rngznzWowvtXKyTnE9avawQGJCVgfJounHDT5nWucoVFv43TYu9PyjiGpPXXXQbCVEzxxCSfDmPNEBknK5B8n5qFiaddStg2M9pCYkZ'),
        Account(
            '112t8rnk4jduDzQGcmzKXr6r1F69TeQtHqDBCehDXPpwQTo7eDkEKFGMDGar46Jy4gmqSZDgwyUwpnxGkCnE2oEXmQ5FQpQJ4iMpDqLkgzwy'),
    )
}
auto_stake_list = AccountGroup(
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
)
