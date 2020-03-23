"""
this test suite is for testing on local chain only, with the following config
block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6
"""
from IncognitoChain.Configs.Constants import ONE_COIN
from IncognitoChain.Helpers.Logging import INFO, STEP
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

auto_stake_acc = [
    Account(),
    Account(),
    Account(),
    Account(),
]

token_sender = Account()
token_receiver = Account()
stake_account = Account()
staked_account = Account()

block_per_epoch = 40
chain_committee_min = 4
chain_committee_max = 6

amount_token_send = 10
amount_token_fee = 1000000
token_init_amount = 100000 * ONE_COIN
token_contribute_amount = 10000 * ONE_COIN
prv_contribute_amount = 10000 * ONE_COIN
token_id = None


def setup_module():
    trx008.account_init = token_sender
    trx008.prv_contribute_amount = prv_contribute_amount
    trx008.token_contribute_amount = token_contribute_amount
    trx008.token_init_amount = token_init_amount
    trx008.setup_module()
    trx008.test_init_ptoken()
    INFO(trx008.custom_token_id)
    global token_id
    token_id = trx008.custom_token_id

    STEP(0, "Verify environment, 6 node per shard")
    number_committee_shard_0 = SUT.full_node.system_rpc().help_count_committee_in_shard(0, refresh_cache=True)
    number_committee_shard_1 = SUT.full_node.system_rpc().help_count_committee_in_shard(1, refresh_cache=False)
    assert number_committee_shard_0 == 6
    assert number_committee_shard_1 == 6


def teardown_module():
    trx008.teardown_module()
