from Configs.Constants import coin
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS

list_staker_to_test = []
beacon_bsd = SUT().get_beacon_best_state_detail_info()
for staker in STAKER_ACCOUNTS[36:]:
    if beacon_bsd.get_auto_staking_committees(staker) is None:
        list_staker_to_test.append(staker)
stakers = list_staker_to_test[36:100]
COIN_MASTER.top_up_if_lower_than(stakers, coin(1751), coin(1850))
beacon_bsd = SUT().get_beacon_best_state_detail_info()
for staker in stakers[:20]:
    beacon_bsd.get_auto_staking_committees(staker)
    result = staker.stake(auto_re_stake=True)
    if result.get_result() is None:
        print(f"ERROR: {stakers.index(staker)}")
