import random

import pytest

from IncognitoChain.Configs.Constants import coin, PBNB_ID, Status, PRV_ID, PBTC_ID, ChainConfig
from IncognitoChain.Helpers.Logging import STEP, INFO, ERROR
from IncognitoChain.Helpers.TestHelper import ChainHelper, l6
from IncognitoChain.Helpers.Time import WAIT, get_current_date_time
from IncognitoChain.Objects.AccountObject import PORTAL_FEEDER, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.Objects.PortalObjects import DepositTxInfo, PortingReqInfo
from IncognitoChain.TestCases.Sanity import account_0, account_1, account_11, fixed_validators, auto_stake_list

COIN_MASTER.top_him_up_prv_to_amount_if(coin(3600), coin(3601), account_0)
P___TOKEN = 'e4ee6277935d280728de8724ab24e4aa227d36672ac1aed2153ec5a2c3297b41'
BRD_TOKEN = '0000000000000000000000000000000000000000000000000000000000000100'

PRV_TRADE_AMOUNT = 15323
TOK_BRD_TRADE_AMOUNT = 23363
TOK_P___TRADE_AMOUNT = 62395
DEX_V1_TRADE_AMOUNT = 1098765432
P_TOKEN_INIT_AMOUNT = coin(40000)


@pytest.mark.testnet
def test_01_block_chain_info():
    print('\n')
    STEP(1, 'Check blockchain info: Beacon best state detail')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    epoch = beacon_bsd.get_epoch()
    INFO(f'Current epoch in block chain info is {epoch}')
    assert epoch > 0, 'epoch must be > 0'
    shards_height = beacon_bsd.get_best_shard_height()
    for shard, height in shards_height.items():
        INFO(f'\tShard {shard}, height {height}')
        assert height > 0

    INFO(f"""\n\t\t*** Blockchain INFO ***
         Current Random Number: {beacon_bsd.get_current_random_number()}
         Min:Max Beacon Committee Size: {beacon_bsd.get_min_beacon_committee_size()}:{beacon_bsd.get_max_beacon_committee_size()}
         Min:Max Shard Committee Size: {beacon_bsd.get_min_shard_committee_size()}:{beacon_bsd.get_max_shard_committee_size()}
         Active Shard: {beacon_bsd.get_active_shard()}
    """)

    STEP(2, 'Check blockchain info: Get block chain info')
    blk_chain_info = SUT().get_block_chain_info()
    beacon_info = blk_chain_info.get_beacon_block()
    INFO(f'\tEpoch in beacon block: {beacon_info.get_epoch()}')
    assert beacon_info.get_epoch() >= 1, 'epoch must >= 1'
    num_of_shard = blk_chain_info.get_num_of_shard()
    for shard in range(0, num_of_shard):
        assert blk_chain_info.get_shard_block(shard).get_height() > 0


@pytest.mark.testnet
def test_02_transaction():
    STEP(1, "Transaction: send prv no privacy")
    send_amount = coin(3600)
    sender_bal_b4 = account_0.get_prv_balance()
    receiver_bal_b4 = account_1.get_prv_balance()
    tx_send_no_privacy = \
        account_0.send_prv_to(account_1, send_amount, privacy=0).expect_no_error().subscribe_transaction()
    sender_bal_af = account_0.wait_for_balance_change(from_balance=sender_bal_b4, least_change_amount=-send_amount)
    receiver_bal_af = account_1.wait_for_balance_change(from_balance=receiver_bal_b4, least_change_amount=send_amount)
    assert sender_bal_b4 - tx_send_no_privacy.get_fee() - send_amount == sender_bal_af and INFO(
        'Sender account balance is correct'), ERROR('Sender account balance is wrong')
    assert receiver_bal_b4 + send_amount == receiver_bal_af and INFO('Receiver account balance is correct'), ERROR(
        'Receiver account balance is wrong')
    tx_send_no_privacy.verify_prv_privacy(False)

    STEP(2, "Transaction: send prv with privacy")
    send_amount = coin(1751)
    sender_bal_b4 = account_1.get_prv_balance()
    receiver0_bal_b4 = account_0.get_prv_balance()
    receiver11_bal_b4 = account_11.get_prv_balance()
    tx_send_privacy = account_1.send_prv_to_multi_account({account_0: send_amount, account_11: send_amount}, fee=100,
                                                          privacy=1). \
        expect_no_error(). \
        subscribe_transaction()

    account_0.subscribe_cross_output_coin()
    sender_bal_af = account_1.get_prv_balance()
    receiver0_bal_af = account_0.get_prv_balance()
    receiver11_bal_af = account_11.get_prv_balance()

    assert sender_bal_b4 - tx_send_privacy.get_fee() - send_amount * 2 == sender_bal_af and INFO(
        f'tx fee is: {tx_send_privacy.get_fee()}'), ERROR('Sender account balance INCORRECT')
    assert receiver0_bal_b4 + send_amount == receiver0_bal_af and INFO(f'Receiver0 account balance is CORRECT'), ERROR(
        'Receiver0 account balance INCORRECT')
    assert receiver11_bal_b4 + send_amount == receiver11_bal_af and INFO(
        f'Receiver11 account balance is CORRECT'), ERROR('Receiver11 account balance INCORRECT')
    tx_send_privacy.verify_prv_privacy()


@pytest.mark.testnet
def test_03_portal():
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1), coin(1.5), PORTAL_FEEDER)
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(10), coin(20), account_0)
    STEP(1, 'Portal: deposit collateral')
    deposit_amount = coin(1)
    bal_b4 = account_0.get_prv_balance()
    psi_b4 = SUT().get_latest_portal_state_info()
    deposit_tx = account_0.portal_make_me_custodian(deposit_amount, PBNB_ID). \
        expect_no_error().subscribe_transaction()
    deposit_info = DepositTxInfo().get_deposit_info(deposit_tx.get_tx_id())
    bal_af = account_0.get_prv_balance()
    INFO(f'Deposit status is: {deposit_info.get_status()}')
    assert deposit_info.get_status() == Status.Portal.DepositStatus.ACCEPT
    assert bal_b4 - deposit_amount - deposit_tx.get_fee() == bal_af
    psi_af = SUT().get_latest_portal_state_info()
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(account_0)
    custodian_info_af = psi_af.get_custodian_info_in_pool(account_0)

    total_collateral_b4 = custodian_info_b4.get_total_collateral()
    assert total_collateral_b4 + deposit_amount == custodian_info_af.get_total_collateral()

    STEP(2, 'Portal: create rate')
    portal_rate_to_change = {
        PRV_ID: f'{random.randint(1000, 100000)}',
        PBNB_ID: f'{random.randint(1000, 100000)}',
        PBTC_ID: f'{random.randint(1000, 100000)}'
    }

    rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(portal_rate_to_change).expect_no_error()
    ChainHelper.wait_till_next_beacon_height(num_of_beacon_height_to_wait=2)
    psi_new_rate = SUT().get_latest_portal_state_info()
    for token, rate in portal_rate_to_change.items():
        new_rate = psi_new_rate.get_portal_rate(token)
        INFO(f'New rate of {l6(token)} = {new_rate}')
        assert int(rate) == new_rate

    STEP(3, 'Portal: Register a porting')
    psi_b4 = SUT().get_latest_portal_state_info()
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
    psi_af = SUT().get_latest_portal_state_info()
    custodian = porting_info.get_custodians()[0]  # assume there's only one matched custodian since the amount is small
    custodian_info_b4 = psi_b4.get_custodian_info_in_pool(custodian)
    custodian_info_af = psi_af.get_custodian_info_in_pool(custodian)
    assert custodian_info_b4.get_locked_collateral(porting_token) + estimated_collateral \
           == custodian_info_af.get_locked_collateral(porting_token), "real vs estimate collateral are not matched"


@pytest.mark.parametrize('stake_funder,the_staked,auto_stake', [
    (account_0, account_0, True),
    (account_0, account_1, True),
])
@pytest.mark.dependency()
def test_04_staking(stake_funder, the_staked, auto_stake):
    STEP(0.1, 'Check current fixed validators to make sure that this test wont be running on testnet')
    beacon_state = SUT().get_beacon_best_state_detail_info()
    all_shard_committee = beacon_state.get_shard_committees()
    list_fixed_validator_public_k = []
    for shard, committees in fixed_validators.items():
        for committee in committees:
            list_fixed_validator_public_k.append(committee.public_key)

    count_fixed_validator_in_beacon_state = 0
    for shard, committees in all_shard_committee.items():
        for committee in committees:
            if committee.get_inc_public_key() in list_fixed_validator_public_k:
                count_fixed_validator_in_beacon_state += 1

    if count_fixed_validator_in_beacon_state < len(list_fixed_validator_public_k):
        msg = 'Suspect that this chain is TestNet. Skip staking tests to prevent catastrophic disaster'
        INFO(msg)
        pytest.skip(msg)

    STEP(0.2, 'Top up committees')
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1850), auto_stake_list + [stake_funder, the_staked])

    STEP(0.3, 'Stake and wait till becoming committee')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for committee in auto_stake_list:
        if beacon_bsd.is_he_a_committee(committee) is False:
            committee.stake_and_reward_me()

    for committee in auto_stake_list:
        committee.stk_wait_till_i_am_committee()

    epoch = SUT().help_get_current_epoch()
    ChainHelper.wait_till_next_epoch(epoch + 2)

    STEP(0.4, "Verify environment, 6 node per shard")
    number_committee_shard_0 = SUT().help_count_committee_in_shard(0, refresh_cache=True)
    number_committee_shard_1 = SUT().help_count_committee_in_shard(1, refresh_cache=False)
    assert number_committee_shard_0 == 6, f"shard 0: {number_committee_shard_0} committee"
    assert number_committee_shard_1 == 6, f"shard 1: {number_committee_shard_1} committee"

    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1750), coin(1850), stake_funder)
    STEP(0, 'check if the staked is already a committee')
    beacon_state = SUT().get_beacon_best_state_detail_info()
    if beacon_state.is_he_a_committee(the_staked):
        pytest.skip("User is already a committee, skip the test")

    STEP(1, 'Get epoch number')
    blk_chain_info = SUT().get_block_chain_info()
    beacon_height = blk_chain_info.get_beacon_block().get_height()
    epoch_number = blk_chain_info.get_beacon_block().get_epoch()

    while beacon_height % ChainConfig.BLOCK_PER_EPOCH >= (ChainConfig.BLOCK_PER_EPOCH / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % ChainConfig.BLOCK_PER_EPOCH}')
        WAIT((ChainConfig.BLOCK_PER_EPOCH - (beacon_height % ChainConfig.BLOCK_PER_EPOCH)) * 10)
        blk_chain_info = SUT().get_block_chain_info()
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
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(the_staked)
    assert staked_shard is not False

    STEP(4, "Calculate avg PRV reward per epoch")
    epoch_x = ChainHelper.wait_till_next_epoch()
    prv_reward = the_staked.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')


@pytest.mark.dependency()
@pytest.mark.testnet
def test_05_init_token_privacy_n_bridge():
    global P___TOKEN

    STEP(1.1, "Initial new token")
    custom_token_symbol = f'token_symbol_{random.randrange(1, 10000)}'
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    tx_init = COIN_MASTER.init_custom_token_self(custom_token_symbol, P_TOKEN_INIT_AMOUNT).expect_no_error()
    P___TOKEN = tx_init.get_token_id()
    INFO(f"Token id: {P___TOKEN}")
    tx_init = tx_init.subscribe_transaction()

    STEP(1.2, "Check prv and custom token balance")
    bal_tok_af_init = COIN_MASTER.get_token_balance(P___TOKEN)
    bal_prv_af_init = COIN_MASTER.get_prv_balance()
    assert bal_tok_af_init == P_TOKEN_INIT_AMOUNT, f'init amount vs balance not match'
    assert bal_prv_b4 - tx_init.get_fee() == bal_prv_af_init, f'PRV balance must subtract init fee'

    STEP(2, f'Send ptoken')
    receivers = {account_0: random.randrange(1500000000, 2000000000),  # 1.5 to 2 coin
                 account_1: random.randrange(1500000000, 2000000000)}
    bal_tok_b4_0 = account_0.get_token_balance(P___TOKEN)
    bal_tok_b4_1 = account_1.get_token_balance(P___TOKEN)
    tx_send = COIN_MASTER.send_token_multi_output(receivers, P___TOKEN, prv_fee=-1, prv_privacy=1).expect_no_error(). \
        subscribe_transaction()

    tx_send.verify_prv_privacy()

    bal_tok_af_0 = account_0.wait_for_balance_change(P___TOKEN, bal_tok_b4_0)
    bal_tok_af_1 = account_1.wait_for_balance_change(P___TOKEN, bal_tok_b4_1)
    assert bal_tok_af_init - sum(receivers.values()) == COIN_MASTER.get_token_balance(P___TOKEN)
    assert bal_tok_b4_0 + receivers[account_0] == bal_tok_af_0
    assert bal_tok_b4_1 + receivers[account_1] == bal_tok_af_1

    STEP(3, 'Init bridge token')
    amount = coin(random.randrange(5000, 10000))
    prv_bal_b4 = COIN_MASTER.get_prv_balance()
    tok_bal_b4 = COIN_MASTER.get_token_balance(BRD_TOKEN)
    issue_tx = COIN_MASTER.issue_centralize_token(BRD_TOKEN, 'BRD Sanity Test', amount)
    issue_tx.expect_no_error()
    issue_tx = issue_tx.subscribe_transaction()

    STEP(3.1, 'Check balance')
    tok_bal_af = COIN_MASTER.wait_for_balance_change(BRD_TOKEN)
    prv_bal_af = COIN_MASTER.get_prv_balance()
    assert tok_bal_af == amount + tok_bal_b4
    assert prv_bal_b4 - issue_tx.get_fee() == prv_bal_af

    STEP(4.1, 'Send bridge token')
    sender_tok_bal_b4 = tok_bal_af
    sender_prv_bal_b4 = prv_bal_af
    account_0.get_token_balance(BRD_TOKEN)
    account_1.get_token_balance(BRD_TOKEN)

    receivers = {
        account_0: random.randrange(1000, 10000),
        account_1: random.randrange(1000, 10000)
    }
    sum_send_amount = sum([amount for amount in receivers.values()])
    send_tx = COIN_MASTER.send_token_multi_output(receivers, BRD_TOKEN, prv_fee=-1). \
        expect_no_error().subscribe_transaction()

    STEP(4.2, 'Check sender token and prv balance')
    sender_tok_bal_af = COIN_MASTER.get_token_balance(BRD_TOKEN)
    sender_prv_bal_af = COIN_MASTER.get_prv_balance()
    assert sender_tok_bal_b4 - sum_send_amount == sender_tok_bal_af
    assert sender_prv_bal_b4 - send_tx.get_fee() == sender_prv_bal_af

    STEP(4.3, 'Verify receiver balance')
    for account, amount in receivers.items():
        tok_bal_b4 = account.get_token_balance_cache(BRD_TOKEN)
        tok_bal_af = account.wait_for_balance_change(BRD_TOKEN, tok_bal_b4)
        assert tok_bal_b4 + amount == tok_bal_af


@pytest.mark.dependency(depends=['test_05_init_token_privacy_n_bridge'])
@pytest.mark.testnet
def test_06_dex_v1():
    PDE_RATE_V1 = {P___TOKEN: coin(10000),
                   BRD_TOKEN: coin(3000)}

    STEP(0, 'Get pde state before')
    pde_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()

    STEP(1, 'Contribue ptoken')
    pair_id = f'{l6(P___TOKEN)}-{l6(BRD_TOKEN)}-{get_current_date_time()}'
    tx1 = COIN_MASTER.pde_contribute(P___TOKEN, PDE_RATE_V1[P___TOKEN], pair_id).expect_no_error(). \
        subscribe_transaction()

    STEP(2, 'Contribute bridge token')
    tx2 = COIN_MASTER.pde_contribute(BRD_TOKEN, PDE_RATE_V1[BRD_TOKEN], pair_id).expect_no_error(). \
        subscribe_transaction()

    STEP(3, 'Verify rate')
    WAIT(40)
    pde_af_contribute = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_b4 = pde_b4.get_rate_between_token(P___TOKEN, BRD_TOKEN)
    rate_af = pde_af_contribute.get_rate_between_token(P___TOKEN, BRD_TOKEN)
    assert rate_b4[0] + PDE_RATE_V1[P___TOKEN] == rate_af[0]
    assert rate_b4[1] + PDE_RATE_V1[BRD_TOKEN] == rate_af[1]

    STEP(4, 'Trade')
    COIN_MASTER.top_him_up_token_to_amount_if(BRD_TOKEN, DEX_V1_TRADE_AMOUNT, DEX_V1_TRADE_AMOUNT + 1000, account_0)
    bal_brd_b4 = account_0.get_token_balance(BRD_TOKEN)
    bal_p___b4 = account_0.get_token_balance(P___TOKEN)
    trade_tx = account_0.pde_trade(BRD_TOKEN, DEX_V1_TRADE_AMOUNT, P___TOKEN, 1).expect_no_error(). \
        subscribe_transaction()
    est_receive = pde_af_contribute.cal_trade_receive_v1(BRD_TOKEN, P___TOKEN, DEX_V1_TRADE_AMOUNT)
    bal_p___af = account_0.wait_for_balance_change(P___TOKEN, bal_p___b4)
    bal_brd_af = account_0.wait_for_balance_change(BRD_TOKEN, bal_brd_b4)
    assert bal_brd_b4 - DEX_V1_TRADE_AMOUNT == bal_brd_af, "balance of selling token is wrong"
    assert bal_p___b4 + est_receive == bal_p___af, "balance of buying token is wrong"


@pytest.mark.testnet
def test_07_dex_v2():
    PDE_RATE_V2_RPV_TOK = {PRV_ID: coin(20000),
                           P___TOKEN: coin(10000), }

    PDE_RATE_V2_BRD_TOK = {P___TOKEN: coin(10000),
                           BRD_TOKEN: coin(20000)}

    STEP(1.1, f'Contribute dex v2 token {l6(PRV_ID)}_{l6(P___TOKEN)}, expect success')
    pde_b4 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    pair_id = f'{l6(PRV_ID)}-{l6(P___TOKEN)}-{get_current_date_time()}'
    contribute_tx_1 = COIN_MASTER.pde_contribute_v2(PRV_ID, PDE_RATE_V2_RPV_TOK[PRV_ID], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)
    INFO(f'Check pde state, make sure the token is in waiting contribution list')
    pde_state_1 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_1.find_waiting_contribution_of_user(COIN_MASTER, pair_id, PRV_ID) != [], \
        "not found in waiting contribution list"

    contribute_tx_2 = COIN_MASTER.pde_contribute_v2(P___TOKEN, PDE_RATE_V2_RPV_TOK[P___TOKEN], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)
    INFO(f'Check pde state, pair id must be out of waiting list')
    pde_state_2 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_2.find_waiting_contribution_of_user(COIN_MASTER, pair_id=pair_id) == []

    STEP(1.2, f'Check pde pool pair')
    real_contrib_prv, real_contrib_tok, refund_prv, refund_tok = pde_b4.cal_contribution(PDE_RATE_V2_RPV_TOK)
    pde_af = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    rate_af = pde_af.get_rate_between_token(PRV_ID, P___TOKEN)
    rate_b4 = pde_b4.get_rate_between_token(PRV_ID, P___TOKEN)
    INFO(f'Rate b4 and after: {rate_b4} - {rate_af}')
    assert abs(rate_b4[0] + real_contrib_prv - rate_af[0] <= 1), f'prv in pool after contribution is not as estimated'
    assert abs(rate_b4[1] + real_contrib_tok - rate_af[1] <= 1), f'token in pool after contribution is not as estimated'

    # --------------------------------------
    bal_brd_b4 = COIN_MASTER.get_token_balance(BRD_TOKEN)
    bal_ptk_b4 = COIN_MASTER.get_token_balance(P___TOKEN)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()

    STEP(2.1, f'Contribute dex v2 token {l6(BRD_TOKEN)}_{l6(P___TOKEN)}, '
              f'expect refund, dex v2 not support token-token pool')
    pair_id = f'{l6(BRD_TOKEN)}-{l6(P___TOKEN)}-{get_current_date_time()}'
    contribute_tx_1 = COIN_MASTER.pde_contribute_v2(BRD_TOKEN, PDE_RATE_V2_BRD_TOK[BRD_TOKEN], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)
    INFO(f'Check pde state, make sure the token is in waiting contribution list')
    pde_state_1 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_1.find_waiting_contribution_of_user(COIN_MASTER, pair_id, BRD_TOKEN) != []
    INFO(f'Contribute token {l6(P___TOKEN)}')
    contribute_tx_2 = COIN_MASTER.pde_contribute_v2(P___TOKEN, PDE_RATE_V2_BRD_TOK[P___TOKEN], pair_id). \
        expect_no_error().subscribe_transaction()
    WAIT(30)
    INFO(f'Check pde state, pair id must be out of waiting list')
    pde_state_2 = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    assert pde_state_2.find_waiting_contribution_of_user(COIN_MASTER, pair_id=pair_id) == []

    STEP(2.2, f'Check balance')
    bal_brd_af = COIN_MASTER.wait_for_balance_change(BRD_TOKEN)
    bal_ptk_af = COIN_MASTER.wait_for_balance_change(P___TOKEN)
    bal_prv_af = COIN_MASTER.get_prv_balance()
    assert bal_brd_b4 == bal_brd_af
    assert bal_ptk_b4 == bal_ptk_af
    assert bal_prv_b4 - contribute_tx_1.get_fee() - contribute_tx_2.get_fee() == bal_prv_af

    # dex_v1 test has already contribute this pair, so comment these line only if test dex v1 is skipped
    # STEP(2.3, 'Check pool pair')
    # assert not pde_state_2.is_pair_existed(BRD_TOKEN, P___TOKEN)

    # -------------------------------------- trade
    STEP(3, f'Trade v2 prv with token {l6(P___TOKEN)}, expect success')
    pde_b4_trade = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    bal_prv_b4_trade = COIN_MASTER.get_prv_balance()
    bal_tok_b4_trade = COIN_MASTER.get_token_balance(P___TOKEN)
    trading_fee = random.randrange(1000, 10000)
    trade_tx = COIN_MASTER.pde_trade_v2(PRV_ID, PRV_TRADE_AMOUNT, P___TOKEN, trading_fee). \
        expect_no_error().subscribe_transaction()
    bal_prv_af_trade = COIN_MASTER.get_prv_balance()
    bal_tok_af_trade = COIN_MASTER.wait_for_balance_change(P___TOKEN, bal_tok_b4_trade)
    assert bal_prv_b4_trade - PRV_TRADE_AMOUNT - trade_tx.get_fee() - trading_fee == bal_prv_af_trade
    assert bal_tok_b4_trade + pde_b4_trade.cal_trade_receive_v1(PRV_ID, P___TOKEN, PRV_TRADE_AMOUNT) \
           == bal_tok_af_trade

    STEP(5.1, "init new token")
    tok_symbol = f'tok_sym_{get_current_date_time()}'
    init_tx = COIN_MASTER.init_custom_token_self(tok_symbol, coin(20000)).expect_no_error()
    custom_token_id = init_tx.get_token_id()
    INFO(f"Token id: {custom_token_id}")
    init_tx.subscribe_transaction()

    STEP(5.2, f'Trade v2 token {l6(custom_token_id)}-{l6(BRD_TOKEN)}, '
              f'which is not possible since the pair {l6(custom_token_id)}-PRV is not existed in DEX')
    bal_tok_b4_trade = COIN_MASTER.get_token_balance(custom_token_id)
    bal_brd_b4_trade = COIN_MASTER.get_token_balance(BRD_TOKEN)
    trade_tx = COIN_MASTER.pde_trade_v2(custom_token_id, TOK_P___TRADE_AMOUNT, BRD_TOKEN, 0).expect_no_error()
    bal_brd_af_trade = COIN_MASTER.wait_for_balance_change(BRD_TOKEN, bal_brd_b4_trade)
    bal_tok_af_trade = COIN_MASTER.get_token_balance(custom_token_id)
    assert bal_brd_b4_trade == bal_brd_af_trade
    assert bal_tok_b4_trade == bal_tok_af_trade


@pytest.mark.parametrize('token, privacy', [
    ('new_ptoken', 0),
    ('new_ptoken', 1),
    (BRD_TOKEN, 0),
    (BRD_TOKEN, 1),
])
@pytest.mark.testnet
def test_08_transaction_ptoken(token, privacy):
    # pytest passes test parameter at load time instead of at execution time
    # this cause the new_ptoken value which has been update at test_04_init_n_contribute_p_token will not be passed into
    # this test but the original value which was declared at the top instead, while tester's desire is to use the
    # newly created ptoken at test_04_init_n_contribute_p_token
    # following line of code is to handle pytest limitation mention above
    token = P___TOKEN if token == 'new_ptoken' else token
    # __________________________________________________

    pde = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    if not pde.can_token_use_for_fee(token):
        pytest.skip(f'Cannot use token to pay fee')

    send_amounts = {account_0: random.randrange(1000, 10000),
                    account_1: random.randrange(1000, 10000)}
    bal_receiver_b4 = {account_0: account_0.get_token_balance(token),
                       account_1: account_1.get_token_balance(token)}
    bal_sender_b4 = COIN_MASTER.get_token_balance(token)
    STEP(1, 'Send token multi output')
    send_tx = COIN_MASTER.send_token_multi_output(send_amounts, token, token_privacy=privacy, token_fee=10000). \
        expect_no_error('Token-PRV pair existed').subscribe_transaction()

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


@pytest.mark.testnet
def test_07_pdex_withdraw_contribution():
    STEP(1, f'Withdraw all contribution of {l6(BRD_TOKEN)}-{l6(P___TOKEN)}')
    bal_brd_b4 = COIN_MASTER.get_token_balance(BRD_TOKEN)
    bal_ptk_b4 = COIN_MASTER.get_token_balance(P___TOKEN)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    pde_state = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    pde_pool = pde_state.get_rate_between_token(BRD_TOKEN, P___TOKEN)
    pde_share = pde_state.get_pde_shares_amount(COIN_MASTER, BRD_TOKEN, P___TOKEN)
    withdraw_tx = COIN_MASTER.pde_withdraw_contribution(
        BRD_TOKEN, P___TOKEN, coin(99999999999999)).expect_no_error().subscribe_transaction()

    WAIT(30)
    bal_brd_af = COIN_MASTER.wait_for_balance_change(BRD_TOKEN, bal_brd_b4)
    bal_ptk_af = COIN_MASTER.wait_for_balance_change(P___TOKEN, bal_ptk_b4)
    bal_prv_af = COIN_MASTER.wait_for_balance_change(from_balance=bal_prv_b4)
    assert bal_brd_b4 + pde_pool[0] == bal_brd_af
    assert bal_ptk_b4 + pde_pool[1] == bal_ptk_af
    assert bal_prv_b4 - withdraw_tx.get_fee() == bal_prv_af

    STEP(2, f'Withdraw reward {l6(PRV_ID)}-{l6(P___TOKEN)}')
    WAIT(30)
    bal_prv_b4 = COIN_MASTER.get_prv_balance()
    pde_state = SUT.REQUEST_HANDLER.get_latest_pde_state_info()
    reward_amount = pde_state.get_contributor_reward(COIN_MASTER, PRV_ID, P___TOKEN)
    withdraw_tx = COIN_MASTER.pde_withdraw_reward_v2(PRV_ID, P___TOKEN, reward_amount). \
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
    (account_1, P___TOKEN),
    (account_1, BRD_TOKEN),
])
@pytest.mark.dependency(depends=['test_04_staking'])
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
