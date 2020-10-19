import sys
from ctypes import ArgumentError

from IncognitoChain.Objects.AccountObject import Account, AccountGroup
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.TestBedObject import TestBed

try:
    # noinspection PyProtectedMember
    full_node_url = sys._xoptions.get('fullNodeUrl')
    # noinspection PyProtectedMember
    ws_port = int(sys._xoptions.get('wsPort'))
    if not full_node_url:
        raise ArgumentError('Must specify a full node url to run the test')

    SUT = TestBed()
    SUT.full_node = Node().parse_url(full_node_url)
    SUT.full_node.set_web_socket_port(ws_port)
    SUT.REQUEST_HANDLER = SUT.full_node
    Account.SYSTEM = SUT
except:
    pass

account_0 = Account(
    '112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv'). \
    set_remote_addr('tbnb1hmgztqgx62t3gldsk7n9wt4hxg2mka0fdem3ss')
account_1 = Account(
    '112t8rnZ9qPE7C6RbrK6Ygat1H94kEkYGSd84fAGiU396yQHu8CBHmV1DDHE947d7orfHnDtKA9WCffDk7NS5zUu5CMCUHK8nkRtrv4nw6uu')
account_11 = Account(
    '112t8rnaK4C17Chu8rEAPXHUaPYNeGz8VsjV7BzdeLA9VBc8oiYwQXNrc6XEABb4uNEfG9LFgvVfi4KQmVpQrwMWph4E1YoVS1m37HwrFDsE')
ACCOUNTS = AccountGroup(account_0, account_1, account_11)

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
