import random

import pytest

from IncognitoChain.Configs.Constants import coin, PBNB_ID, Status, PRV_ID, PBTC_ID, ChainConfig
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import ChainHelper, l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import DepositTxInfo, PortingReqInfo
from IncognitoChain.TestCases import Staking
from IncognitoChain.TestCases.Sanity import account_0, account_1
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token

new_ptoken = '1fdc8235f3c7170b5b860dd2d9f19cde094bfea3d86b9a3540612a11bc8e6530'
brd_token_id = '0000000000000000000000000000000000000000000000000000000000000100'
pde_rate = {new_ptoken: coin(1500),
            brd_token_id: coin(1000)}

prv_trade_amount = 15323
tok_brd_trade_amount = 23363
tok_new_trade_amount = 62395


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
    assert beacon_info.get_epoch() >= 1, 'epoch must >= 1'
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
    send_tx = send_tx.subscribe_transaction()
    sender_bal_af = account_0.wait_for_balance_change(from_balance=sender_bal_b4, least_change_amount=-send_amount)
    receiver_bal_af = account_1.wait_for_balance_change(from_balance=receiver_bal_b4, least_change_amount=send_amount)
    assert sender_bal_b4 - send_tx.get_fee() - send_amount == sender_bal_af
    assert receiver_bal_b4 + send_amount == receiver_bal_af

    STEP(2, "Transaction: send prv with privacy")
    sender_bal_b4 = account_1.get_prv_balance()
    receiver_bal_b4 = account_0.get_prv_balance()
    send_tx = account_1.send_prv_to(account_0, send_amount, privacy=0)
    send_tx.expect_no_error()
    send_tx = send_tx.subscribe_transaction()
    sender_bal_af = account_1.wait_for_balance_change(from_balance=sender_bal_b4, least_change_amount=-send_amount)
    receiver_bal_af = account_0.wait_for_balance_change(from_balance=receiver_bal_b4, least_change_amount=send_amount)
    assert sender_bal_b4 - send_tx.get_fee() - send_amount == sender_bal_af
    assert receiver_bal_b4 + send_amount == receiver_bal_af


def test_03_portal():
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1), coin(1.5), PORTAL_FEEDER)
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(10), coin(20), account_0)
    STEP(1, 'Portal: deposit collateral')
    deposit_amount = coin(1)
    bal_b4 = account_0.get_prv_balance()
    psi_b4 = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    deposit_tx = account_0.portal_make_me_custodian(deposit_amount, PBNB_ID). \
        expect_no_error().subscribe_transaction()
    deposit_info = DepositTxInfo().get_deposit_info(deposit_tx.get_tx_id())
    bal_af = account_0.get_prv_balance()
    INFO(f'Deposit status is: {deposit_info.get_status()}')
    assert deposit_info.get_status() == Status.Portal.DepositStatus.ACCEPT
    assert bal_b4 - deposit_amount - deposit_tx.get_fee() == bal_af
    psi_af = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(account_0)
    custodian_info_af = psi_af.get_custodian_info_in_pool(account_0)

    total_collateral_b4 = 0 if custodian_info_b4 is None else custodian_info_b4.get_total_collateral()
    assert total_collateral_b4 + deposit_amount == custodian_info_af.get_total_collateral()

    STEP(2, 'Portal: create rate')
    portal_rate_to_change = {
        PRV_ID: f'{random.randint(1000, 100000)}',
        PBNB_ID: f'{random.randint(1000, 100000)}',
        PBTC_ID: f'{random.randint(1000, 100000)}'
    }

    rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(portal_rate_to_change).expect_no_error()
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
    porting_tx = porting_tx.subscribe_transaction()
    porting_info = PortingReqInfo().get_porting_req_by_tx_id(porting_tx.get_hash())
    bal_af = account_1.get_prv_balance()
    assert bal_b4 - porting_tx.get_fee() - porting_info.get_porting_fee() == bal_af
    psi_af = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    custodian = porting_info.get_custodians()[0]  # assume there's only one matched custodian since the amount is small
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(custodian)
    custodian_info_af = psi_af.get_custodian_info_in_pool(custodian)
    assert custodian_info_b4.get_locked_collateral(porting_token) + estimated_collateral \
           == custodian_info_af.get_locked_collateral(porting_token)


def test_04_init_n_contribute_p_token():
    global new_ptoken
    test_TRX008_init_contribute_send_custom_token.account_init = COIN_MASTER
    test_TRX008_init_contribute_send_custom_token.setup_module()
    new_ptoken = test_TRX008_init_contribute_send_custom_token.test_init_ptoken()


def test_04_init_bridge_token_n_send():
    amount = coin(random.randrange(1000, 10000))
    STEP(1, 'Init bridge token')
    prv_bal_b4 = COIN_MASTER.get_prv_balance()
    tok_bal_b4 = COIN_MASTER.get_token_balance(brd_token_id)
    issue_tx = COIN_MASTER.issue_centralize_token(brd_token_id, 'BRD Sanity Test', amount)
    issue_tx.expect_no_error()
    issue_tx = issue_tx.subscribe_transaction()

    STEP(2, 'Check balance')
    tok_bal_af = COIN_MASTER.wait_for_balance_change(brd_token_id)
    prv_bal_af = COIN_MASTER.get_prv_balance()
    assert tok_bal_af == amount + tok_bal_b4
    assert prv_bal_b4 - issue_tx.get_fee() == prv_bal_af

    STEP(3, 'Send bridge token')
    sender_tok_bal_b4 = tok_bal_af
    sender_prv_bal_b4 = prv_bal_af
    account_0.get_token_balance(brd_token_id)
    account_1.get_token_balance(brd_token_id)

    receivers = {
        account_0: random.randrange(1000, 10000),
        account_1: random.randrange(1000, 10000)
    }
    sum_send_amount = sum([amount for amount in receivers.values()])
    send_tx = COIN_MASTER.send_token_multi_output(receivers, brd_token_id, prv_fee=-1). \
        expect_no_error().subscribe_transaction()

    STEP(4, 'Check sender token and prv balance')
    sender_tok_bal_af = COIN_MASTER.get_token_balance(brd_token_id)
    sender_prv_bal_af = COIN_MASTER.get_prv_balance()
    assert sender_tok_bal_b4 - sum_send_amount == sender_tok_bal_af
    assert sender_prv_bal_b4 - send_tx.get_fee() == sender_prv_bal_af

    STEP(5, 'Verify receiver balance')
    for account, amount in receivers.items():
        tok_bal_b4 = account.get_token_balance_cache(brd_token_id)
        tok_bal_af = account.wait_for_balance_change(brd_token_id, tok_bal_b4)
        assert tok_bal_b4 + amount == tok_bal_af


@pytest.mark.parametrize('stake_funder,the_staked,auto_stake', [
    (account_0, account_0, True),
    (account_0, account_1, True),
])
@pytest.mark.dependency()
def test_05_staking(stake_funder, the_staked, auto_stake):
    Staking.setup_module()
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1850), stake_funder)
    STEP(0, 'check if the staked is already a committee')
    beacon_state = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    if beacon_state.is_he_a_committee(the_staked):
        pytest.skip("User is already a committee, skip the test")

    STEP(1, 'Get epoch number')
    blk_chain_info = SUT.REQUEST_HANDLER.get_block_chain_info()
    beacon_height = blk_chain_info.get_beacon_block().get_height()
    epoch_number = blk_chain_info.get_beacon_block().get_epoch()

    while beacon_height % ChainConfig.BLOCK_PER_EPOCH >= (ChainConfig.BLOCK_PER_EPOCH / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % ChainConfig.BLOCK_PER_EPOCH}')
        WAIT((ChainConfig.BLOCK_PER_EPOCH - (beacon_height % ChainConfig.BLOCK_PER_EPOCH)) * 10)
        blk_chain_info = SUT.REQUEST_HANDLER.get_block_chain_info()
        beacon_height = blk_chain_info.get_beacon_block().get_height()
        epoch_number = blk_chain_info.get_beacon_block().get_epoch()

    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Stake and check balance after stake')
    bal_before_stake = stake_funder.get_prv_balance()
    stake_response = stake_funder.stake_someone_reward_him(the_staked, auto_re_stake=auto_stake).expect_no_error()
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    assert stake_funder.get_prv_balance_cache() == stake_funder.get_prv_balance() + stake_fee + coin(1750)

    STEP(3, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
    epoch_plus_n = the_staked.stk_wait_till_i_am_committee()
    beacon_bsd = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(the_staked)
    assert staked_shard is not False

    STEP(4, "Calculate avg PRV reward per epoch")
    epoch_x = ChainHelper.wait_till_next_epoch()
    prv_reward = the_staked.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')


def test_06_dex_v2():
    global pde_rate
    pde_rate = {new_ptoken: coin(1500),
                brd_token_id: coin(1000)}
    bal_brd_b4 = COIN_MASTER.get_token_balance(brd_token_id)
    bal_ptk_b4 = COIN_MASTER.get_token_balance(new_ptoken)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    STEP(1, f'Contribute token {l6(brd_token_id)}')
    pair_id = f'{l6(brd_token_id)}-{l6(new_ptoken)}'
    contribute_tx_1 = COIN_MASTER.pde_contribute_token(brd_token_id, pde_rate[brd_token_id], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)

    STEP(2, f'Check pde state, make sure the token is in waiting contribution list')
    pde_state_1 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_1.find_waiting_contribution_of_user(COIN_MASTER, pair_id, brd_token_id) != []

    STEP(3, f'Contribute token {l6(new_ptoken)}')
    contribute_tx_2 = COIN_MASTER.pde_contribute_token(new_ptoken, pde_rate[new_ptoken], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)

    STEP(4, f'Check pde state')
    pde_state_2 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_2.find_waiting_contribution_of_user(COIN_MASTER, pair_id=pair_id) == []

    STEP(5, f'Check balance')
    bal_brd_af = COIN_MASTER.get_token_balance(brd_token_id)
    bal_ptk_af = COIN_MASTER.get_token_balance(new_ptoken)
    bal_prv_af = COIN_MASTER.get_prv_balance()
    assert bal_brd_b4 - pde_rate[brd_token_id] == bal_brd_af
    assert bal_ptk_b4 - pde_rate[new_ptoken] == bal_ptk_af
    assert bal_prv_b4 - contribute_tx_1.get_fee() - contribute_tx_2.get_fee() == bal_prv_af

    STEP(6, 'Check pool pair')
    assert pde_state_2.is_pair_existed(brd_token_id, new_ptoken)

    STEP(7, f'Trade v2 prv with token {l6(new_ptoken)}')
    pde_b4_trade = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    bal_prv_b4_trade = COIN_MASTER.get_prv_balance()
    bal_tok_b4_trade = COIN_MASTER.get_token_balance(new_ptoken)
    trading_fee = random.randrange(1000, 10000)
    trade_tx = COIN_MASTER.pde_trade_v2(PRV_ID, prv_trade_amount, new_ptoken, trading_fee). \
        expect_no_error().subscribe_transaction()
    bal_prv_af_trade = COIN_MASTER.get_prv_balance()
    bal_tok_af_trade = COIN_MASTER.wait_for_balance_change(new_ptoken, bal_tok_b4_trade)
    assert bal_prv_b4_trade - prv_trade_amount - trade_tx.get_fee() - trading_fee == bal_prv_af_trade
    assert bal_tok_b4_trade + pde_b4_trade.cal_trade_receive(PRV_ID, new_ptoken, prv_trade_amount) == bal_tok_af_trade

    STEP(8, f'Trade v2 token {l6(new_ptoken)}-{l6(brd_token_id)}')
    pde_b4_trade = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    bal_tok_b4_trade = COIN_MASTER.get_token_balance(new_ptoken)
    bal_brd_b4_trade = COIN_MASTER.get_token_balance(brd_token_id)
    random_fee = random.randrange(10000, 100000)
    trade_tx = COIN_MASTER.pde_trade_v2(new_ptoken, tok_new_trade_amount, brd_token_id, random_fee). \
        expect_no_error().subscribe_transaction()

    bal_tok_af_trade = COIN_MASTER.wait_for_balance_change(new_ptoken, bal_tok_b4_trade)
    bal_brd_af_trade = COIN_MASTER.get_token_balance(brd_token_id)
    assert bal_tok_b4_trade - tok_new_trade_amount == bal_tok_af_trade
    assert bal_brd_b4_trade + pde_b4_trade.cal_trade_receive(new_ptoken, brd_token_id, tok_new_trade_amount) \
           == bal_brd_af_trade

    STEP(9, f'Trade v2 token {l6(new_ptoken)}-{l6(brd_token_id)}')
    bal_tok_b4_trade = COIN_MASTER.get_token_balance(new_ptoken)
    bal_brd_b4_trade = COIN_MASTER.get_token_balance(brd_token_id)
    trade_tx = COIN_MASTER.pde_trade_v2(new_ptoken, tok_new_trade_amount, brd_token_id, 0).expect_no_error()
    bal_brd_af_trade = COIN_MASTER.wait_for_balance_change(brd_token_id, bal_brd_b4_trade)
    bal_tok_af_trade = COIN_MASTER.get_token_balance(new_ptoken)
    assert bal_brd_b4_trade == bal_brd_af_trade
    assert bal_tok_b4_trade == bal_tok_af_trade


@pytest.mark.parametrize('token, privacy', [
    ('new_ptoken', 0),
    ('new_ptoken', 1),
    (brd_token_id, 0),
    (brd_token_id, 1),
])
def test_07_transaction_ptoken(token, privacy):
    # pytest passes test parameter at load time instead of at execution time
    # this cause the new_ptoken value which has been update at test_04_init_n_contribute_p_token will not be passed into
    # this test but the original value which was declared at the top instead, while tester's desire is to use the
    # newly created ptoken at test_04_init_n_contribute_p_token
    # following line of code is to handle pytest limitation mention above
    token = new_ptoken if token == 'new_ptoken' else token
    # __________________________________________________

    pde = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    if not pde.is_pair_existed(token, PRV_ID):
        pytest.skip(f'token-PRV is not existed in pde pool, cannot use token to pay fee')

    send_amounts = {account_0: random.randrange(1000, 10000),
                    account_1: random.randrange(1000, 10000)}
    bal_receiver_b4 = {account_0: account_0.get_token_balance(token),
                       account_1: account_1.get_token_balance(token)}
    bal_sender_b4 = COIN_MASTER.get_token_balance(token)
    STEP(1, 'Send token multi output')
    send_tx = COIN_MASTER.send_token_multi_output(send_amounts, token, token_privacy=privacy, token_fee=100). \
        expect_no_error().subscribe_transaction()

    if privacy == 0:
        assert not send_tx.is_privacy_custom_token()
    else:
        assert send_tx.is_privacy_custom_token()

    STEP(2, 'Balance check')
    bal_sender_af = COIN_MASTER.get_token_balance(token)
    assert bal_sender_b4 - sum(send_amounts.values()) - send_tx.get_privacy_custom_token_fee() == bal_sender_af

    for acc, amount in send_amounts.items():
        bal_b4 = bal_receiver_b4[acc]
        bal_af = acc.wait_for_balance_change(token, from_balance=bal_b4)
        assert bal_b4 + amount == bal_af


def test_08_pdex_withdraw_contribution():
    STEP(1, f'Withdraw all contribution of {l6(brd_token_id)}-{l6(new_ptoken)}')
    bal_brd_b4 = COIN_MASTER.get_token_balance(brd_token_id)
    bal_ptk_b4 = COIN_MASTER.get_token_balance(new_ptoken)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    pde_state = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    pde_pool = pde_state.get_rate_between_token(brd_token_id, new_ptoken)
    pde_share = pde_state.get_pde_shares_amount(COIN_MASTER, brd_token_id, new_ptoken)
    withdraw_tx = COIN_MASTER.pde_withdraw_contribution(
        brd_token_id, new_ptoken, pde_share).expect_no_error().subscribe_transaction()

    WAIT(30)
    bal_brd_af = COIN_MASTER.wait_for_balance_change(brd_token_id, bal_brd_b4)
    bal_ptk_af = COIN_MASTER.wait_for_balance_change(new_ptoken, bal_ptk_b4)
    bal_prv_af = COIN_MASTER.wait_for_balance_change(from_balance=bal_prv_b4)
    assert bal_brd_b4 + pde_pool[0] == bal_brd_af
    assert bal_ptk_b4 + pde_pool[1] == bal_ptk_af
    assert bal_prv_b4 - withdraw_tx.get_fee() == bal_prv_af
    COIN_MASTER.pde_withdraw_contribution(PRV_ID, new_ptoken, coin(100000000000)). \
        expect_no_error().subscribe_transaction()
    COIN_MASTER.wait_for_balance_change(least_change_amount=1000)

    STEP(2, f'Withdraw reward {l6(PRV_ID)}-{l6(new_ptoken)}')
    WAIT(30)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    pde_state = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    reward_amount = pde_state.get_contributor_reward(COIN_MASTER, PRV_ID, new_ptoken)
    withdraw_tx = COIN_MASTER.pde_withdraw_reward_v2(PRV_ID, new_ptoken, 1000000000). \
        expect_no_error().subscribe_transaction()
    bal_prv_af = COIN_MASTER.wait_for_balance_change(from_balance=bal_prv_b4)

    assert bal_prv_b4 + reward_amount - withdraw_tx.get_fee() == bal_prv_af


@pytest.mark.parametrize('stake_funder,the_staked', [
    (account_0, account_0,),
    (account_0, account_1),
])
@pytest.mark.dependency(depends=['test_04_staking'])
def test_09_stop_staking(stake_funder, the_staked):
    STEP(1, 'Send stop auto staking tx')
    unstake_tx = stake_funder.stk_un_stake_him(the_staked)
    unstake_tx.expect_no_error()
    unstake_tx.subscribe_transaction()

    STEP(2, 'Wait for the staked to be swapped out')
    the_staked.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(3, 'Check committee again')
    beacon_bsd = SUT.REQUEST_HANDLER.get_beacon_best_state_detail_info()
    assert beacon_bsd.is_he_a_committee(the_staked) is False


@pytest.mark.parametrize('committee, reward_token', [
    (account_1, new_ptoken),
    (account_1, brd_token_id),
])
def test_10_withdraw_reward(committee, reward_token):
    STEP(1, 'Withdraw PRV reward and verify balance')
    prv_bal_b4_withdraw_reward = committee.get_prv_balance()
    prv_reward_amount = committee.stk_get_reward_amount()
    committee.stk_withdraw_reward_to_me().subscribe_transaction()
    prv_bal_after_withdraw_reward = committee.wait_for_balance_change(from_balance=prv_bal_b4_withdraw_reward,
                                                                      timeout=180)
    INFO(f'Expect reward amount to received {prv_reward_amount}')
    assert prv_bal_b4_withdraw_reward == prv_bal_after_withdraw_reward - prv_reward_amount

    STEP(2, 'Withdraw token reward and verify balance')
    token_bal_b4_withdraw_reward = committee.get_token_balance(reward_token)
    token_reward_amount = committee.stk_get_reward_amount(reward_token)
    committee.stk_withdraw_reward_to_me(reward_token).subscribe_transaction()
    token_bal_after_withdraw_reward = committee.wait_for_balance_change(reward_token, timeout=180,
                                                                        from_balance=token_bal_b4_withdraw_reward)
    INFO(f'Expect reward amount to received {token_reward_amount}')
    assert token_bal_b4_withdraw_reward == token_bal_after_withdraw_reward - token_reward_amount
