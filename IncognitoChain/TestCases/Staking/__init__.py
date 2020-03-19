"""
this test suite is for testing on local chain only, with the following config
block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6
"""
from IncognitoChain.Objects.AccountObject import Account

auto_stake_acc = [
    Account(),
    Account(),
    Account(),
    Account(),
]

account_t = Account()
account_b = Account()

stake = Account()
