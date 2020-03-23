"""
1. keep chain data after run the previous tc
2. as step2. accountU stake for A. verify account U -1750PRV -tx_fee
3.4.5.6.8 as previous. 7. AccountU +1750PRV
9. run all step of case1 (skip step1) with account A
10. run all step of case1 (skip step1) with account T
11. run all step of case1 (skip step1) with account U
"""

from IncognitoChain.TestCases.Staking.test_STK01 import test_self_stake_n_stake_other as do_stake


def test_stake_complex():
    do_stake(account_u, acount_a)
    do_stake(account_a, acount_a)
    do_stake(account_t, acount_t)
    do_stake(account_u, acount_u)
