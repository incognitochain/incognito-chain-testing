from Helpers.KeyListJson import KeyListJson
from Objects.AccountObject import *
from Objects.IncognitoTestCase import *

kl = KeyListJson()
stakers = kl.get_staker_accounts()
bbs = SUT().get_beacon_best_state_info()
pending_validator = bbs.get_shard_pending_validator(0)[0]
unstaker = stakers.find_account_by_key(pending_validator)
bal_b4 = unstaker.get_prv_balance()
unstaker.stk_un_stake_me().expect_no_error().subscribe_transaction()
unstaker.stk_wait_till_i_am_swapped_out_of_committee()
bal_af = unstaker.wait_for_balance_change(from_balance=bal_b4)

########## dummy #############
Account()

WAIT(10)
ChainConfig


class A:
    def __str__(self):
        print('string of A')
        return 'class A'


a = A()

for i in range(100):
    a is None

for c in committee:
    c.stake_and_reward_me().expect_no_error()
