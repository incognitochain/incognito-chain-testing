"""
this test suite is for testing on local chain only, with the following config
chain_committee_min = 4
chain_committee_max = 6
"""
import logging
import random

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.KeyListJson import KeyListJson
from Objects.AccountObject import Account, AccountGroup, COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS

logger = logging.getLogger(__name__)
key_list_file = KeyListJson()
fixed_validators = key_list_file.get_shard_fix_validator_accounts()
stakers = key_list_file.get_staker_accounts().attach_to_node(SUT())
stakers.submit_key()
stake_acc = AccountGroup()
token_receiver = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')
token_receiver.attach_to_node(SUT())
token_receiver.submit_key()
list_acc_x_shard = AccountGroup()
for i in range(ChainConfig.ACTIVE_SHARD):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard.append(acc)
    except IndexError:
        logger.info(f'Not found account in shard {i}')
token_owner = list_acc_x_shard[0]

token_owner.submit_key()
list_acc_x_shard.submit_key()

amount_stake_under_1750 = random.randint(coin(1), coin(1749))
amount_stake_over_1750 = random.randint(coin(1751), coin(1850))
amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = coin(100000)
token_contribute_amount = coin(10000)
prv_contribute_amount = coin(10000)
# setup_module function below will check if this token is existed in chain, if not, init new token
token_id = '5a0df1204de635d5604b4e20fc9845b731a4dd13d12d60db2ce09a991810654a'
tear_down_trx008 = False

logger.info("SETUP MODULE")
logger.info("Stake until shard committee is full")
bbsd = SUT().get_beacon_best_state_detail_info()
total_shard_committee = bbsd.committee_count_total()
total_max_shard_committee = bbsd.get_max_shard_committee_size() * bbsd.get_active_shard()
num_staker_needed = total_max_shard_committee - total_shard_committee
index = 0
for staker in stakers:
    if bbsd.where_is_he(staker) != "not any list":
        index += 1
while index < num_staker_needed:
    COIN_MASTER.top_up_if_lower_than(stakers[index], coin(1751), coin(1755))
    tx = stakers[index].stake_and_reward_me().expect_no_error()
    index += 1

logger.info("Wait for stakers to be assigned to shards")
while total_max_shard_committee > SUT().get_beacon_best_state_detail_info().committee_count_total():
    SUT().wait_till_next_beacon_height()

logger.info("check if each shard committee is full, stake more if not")
while True:
    more_staked = 0
    bbsd = SUT().get_beacon_best_state_detail_info()
    if bbsd.is_full_committee():
        logger.info("Shards committee is full")
        break
    while more_staked < bbsd.committee_need_fill_num():
        COIN_MASTER.top_up_if_lower_than(stakers[index], coin(1751), coin(1755))
        tx = stakers[index].stake_and_reward_me().expect_no_error()
        index += 1
        more_staked += 1
    logger.info(f"Shards committee is not full, staked {more_staked} more")
    while bbsd.committee_count_total() + more_staked > SUT().get_beacon_best_state_detail_info().committee_count_total():
        SUT().wait_till_next_beacon_height()

logger.info("Prepare acc for testing")
# global stake_acc
try:
    auto_stake_list = AccountGroup(*(stakers[:index]))
    [stake_acc.append(a) for a in stakers[index:index + 5]]
except IndexError:
    raise EnvironmentError(f'Not enough staker in keylist file for the test. '
                           f'Check the file, and make sure nodes are run or else chain will be stuck')
auto_stake_list.submit_key()
stake_acc.submit_key()
COIN_MASTER.top_up_if_lower_than(stake_acc, coin(1), coin(5))

logger.info("MINT TOKEN FOR TESTING")
all_ptoken_in_chain = SUT().get_all_token_in_chain_list()
# global token_id, tear_down_trx008
if not all_ptoken_in_chain.get_tokens_info(id=token_id) \
        or (token_owner.get_balance(token_id) == 0 and all_ptoken_in_chain.get_tokens_info(id=token_id)):
    tx_init = token_owner.init_custom_token_new_flow(token_init_amount)
    token_id = tx_init.get_token_id()
    tx_init.get_transaction_by_hash()
    token_owner.wait_for_balance_change(token_id, 0)
    logger.info(f'Setup module: new token: {token_id}')
else:
    logger.info(f'Setup module: use existing token: {token_id}')
token_owner.top_up_if_lower_than(list_acc_x_shard, 10e9, 11e9, token_id)
