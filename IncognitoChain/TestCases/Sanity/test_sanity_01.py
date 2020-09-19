import random

import pytest

from IncognitoChain.Configs.Constants import coin, PBNB_ID, Status, PRV_ID, PBTC_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper, l6
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import DepositTxInfo, PortingReqInfo
from IncognitoChain.TestCases import Staking
from IncognitoChain.TestCases.Sanity import account_0, account_1, account_11
from IncognitoChain.TestCases.Staking import test_STK01
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token

new_ptoken = None


def test_01_block_chain_info():
    STEP(1, 'Check blockchain info: Bacon detail')
    beacon_bsd = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    epoch = beacon_bsd.get_epoch()
    INFO(f'Current epoch in block chain info is {epoch}')
    assert epoch > 0, 'epoch must be > 0'
    shards_height = beacon_bsd.get_best_shard_height()
    for shard, height in shards_height.items():
        INFO(f'Shard {shard}, height {height}')
        assert height > 0

    STEP(2, 'Check blockchain info: Get block chain info')
    blk_chain_info = SUT.REQUEST_HANDLER.get_block_chain_info()
    beacon_info = blk_chain_info.get_beacon_block()
    INFO(f'Epoch in beacon block: {beacon_info.get_epoch()}')
    assert beacon_info.get_epoch() > 1, 'epoch must > 1'
    num_of_shard = blk_chain_info.get_num_of_shard()
    for shard in range(0, num_of_shard):
        assert blk_chain_info.get_shard_block(shard).get_height() > 0


def test_02_transaction():
    STEP(1, "Transaction: send prv no privacy")
    send_amount = 1000
    sender_bal_b4 = account_0.get_prv_balance()
    receiver_bal_b4 = account_1.get_prv_balance()
    send_tx = account_0.send_prv_to(account_1, send_amount, privacy=0)
    send_tx.expect_no_error()
    send_tx = send_tx.subscribe_transaction_obj()
    sender_bal_af = account_0.wait_for_balance_change(from_balance=sender_bal_b4, least_change_amount=-send_amount)
    receiver_bal_af = account_1.wait_for_balance_change(from_balance=receiver_bal_b4, least_change_amount=send_amount)
    assert sender_bal_b4 - send_tx.get_fee() - send_amount == sender_bal_af
    assert receiver_bal_b4 + send_amount == receiver_bal_af

    STEP(2, "Transaction: send prv with privacy")
    sender_bal_b4 = account_1.get_prv_balance()
    receiver_bal_b4 = account_0.get_prv_balance()
    send_tx = account_1.send_prv_to(account_0, send_amount, privacy=0)
    send_tx.expect_no_error()
    send_tx = send_tx.subscribe_transaction_obj()
    sender_bal_af = account_1.wait_for_balance_change(from_balance=sender_bal_b4, least_change_amount=-send_amount)
    receiver_bal_af = account_0.wait_for_balance_change(from_balance=receiver_bal_b4, least_change_amount=send_amount)
    assert sender_bal_b4 - send_tx.get_fee() - send_amount == sender_bal_af
    assert receiver_bal_b4 + send_amount == receiver_bal_af


def test_03_portal():
    STEP(1, 'Portal: deposit collateral')
    deposit_amount = coin(1)
    bal_b4 = account_0.get_prv_balance()
    psi_b4 = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(10), coin(20), account_0)
    deposit_tx = account_0.portal_make_me_custodian(deposit_amount, PBNB_ID)
    deposit_tx.expect_no_error()
    deposit_info = DepositTxInfo().get_deposit_info(deposit_tx.get_tx_id())
    deposit_tx = deposit_tx.subscribe_transaction_obj()
    bal_af = account_0.get_prv_balance()
    INFO(f'Deposit status is: {deposit_info.get_status()}')
    assert deposit_info.get_status() == Status.Portal.DepositStatus.ACCEPT
    assert bal_b4 - deposit_amount - deposit_tx.get_fee() == bal_af
    psi_af = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(account_0)
    custodian_info_af = psi_af.get_custodian_info_in_pool(account_0)
    assert custodian_info_b4.get_total_collateral() + deposit_amount == custodian_info_af.get_total_collateral()

    STEP(2, 'Portal: create rate')
    portal_rate_to_change = {
        PRV_ID: f'{random.randint(1000, 100000)}',
        PBNB_ID: f'{random.randint(1000, 100000)}',
        PBTC_ID: f'{random.randint(1000, 100000)}'
    }

    rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(portal_rate_to_change)
    ChainHelper.wait_till_next_beacon_height()
    psi_new_rate = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    for token, rate in portal_rate_to_change.items():
        new_rate = psi_new_rate.get_portal_rate(token)
        INFO(f'New rate of {l6(token)} = {new_rate}')
        assert int(rate) == new_rate

    STEP(3, 'Portal: Register a porting')
    psi_b4 = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    porting_amount = 100
    porting_token = PBNB_ID
    estimated_collateral = psi_b4.estimate_collateral(porting_amount, porting_token)
    bal_b4 = account_1.get_prv_balance()
    porting_tx = account_1.portal_create_porting_request(porting_token, porting_amount)
    porting_tx.expect_no_error()
    porting_tx = porting_tx.subscribe_transaction_obj()
    porting_info = PortingReqInfo().get_porting_req_by_tx_id(porting_tx.get_hash())
    bal_af = account_1.get_prv_balance()
    assert bal_b4 - porting_tx.get_fee() - porting_info.get_porting_fee() == bal_af
    psi_af = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    custodian = porting_info.get_custodians()[0]  # assume there's only one matched custodian since the amount is small
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(custodian)
    custodian_info_af = psi_af.get_custodian_info_in_pool(custodian)
    assert custodian_info_b4.get_locked_collateral(porting_token) + estimated_collateral \
           == custodian_info_af.get_locked_collateral(porting_token)


def test_04_init_p_token():
    global new_ptoken
    test_STK01.token_id = test_TRX008_init_contribute_send_custom_token.test_init_ptoken


def test_04_init_bridge_token():
    brd_token_id = '0000000000000000000000000000000000000000000000000000000000000100'
    amount = coin(random.randrange(1000, 10000))
    STEP(1, 'Init bridge token')
    prv_bal_b4 = COIN_MASTER.get_prv_balance()
    issue_tx = COIN_MASTER.issue_centralize_token(brd_token_id, 'BRD Sanity Test', amount)
    issue_tx.expect_no_error()
    issue_tx = issue_tx.subscribe_transaction_obj()

    STEP(2, 'Check balance')
    tok_bal_af = COIN_MASTER.get_token_balance(brd_token_id)
    prv_bal_af = COIN_MASTER.get_prv_balance()
    assert tok_bal_af == amount
    assert prv_bal_b4 - issue_tx.get_fee() == prv_bal_af


@pytest.mark.parametrize('stake_funder,staked,auto_stake', [
    (account_0, account_0, True),
    # (account_0, account_1, True),
])
@pytest.mark.dependency()
def test_05_staking(stake_funder, staked, auto_stake):
    Staking.token_holder_shard_0 = test_STK01.token_holder_shard_0 = COIN_MASTER
    Staking.token_holder_shard_1 = test_STK01.token_holder_shard_1 = account_11
    # Staking.token_id = test_STK01.token_id = new_ptoken
    Staking.setup_module()
    global new_ptoken
    test_STK01.token_id = new_ptoken = Staking.token_id
    test_STK01.test_staking(stake_funder, stake_funder, True)
    test_STK01.test_staking(stake_funder, staked, True)


@pytest.mark.parametrize('stake_funder,staked', [
    (account_0, account_0),
    (account_0, account_1),
])
@pytest.mark.dependency(depends=['test_04_staking'])
def test_05_stop_staking(stake_funder, staked):
    STEP(1, 'Send stop auto staking tx')
    unstake_tx = stake_funder.stk_un_stake_him(staked)
    unstake_tx.expect_no_error()
    unstake_tx.subscribe_transaction_obj()

    STEP(2, 'Wait for the staked to be swapped out')
    staked.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(3, 'Check committee again')
    beacon_bsd = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    assert beacon_bsd.is_he_a_committee(staked) is False


@pytest.mark.dependency
def test_05_minting_ptoken():
    pass


def test_06_pdex_v2():
    pass


def transaction_ptoken():
    pass
