from Objects.AccountObject import AccountGroup
from Objects.IncognitoTestCase import SUT

stakers_list = AccountGroup([])

bbsd = SUT().get_beacon_best_state_detail_info()
bbs = SUT().get_beacon_best_state_info()
validator_com_pub_k = bbs.get_shard_committees(0, 0)
val_acc = stakers_list.find_account_by_key(validator_com_pub_k)
sbsd = SUT().get_shard_best_state_detail_info()
sbsd.get_staking_tx()


bbsd.get
