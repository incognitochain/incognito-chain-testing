import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PortalPortingStatusByPortingId, PortalPortingStatusByTxId, \
    PortalPtokenReqStatus, PRV_ID, coin
from IncognitoChain.Drivers.BnbCli import BnbCli, encode_porting_memo, build_bnb_proof
from IncognitoChain.Helpers.Logging import STEP, INFO, WARNING
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import PortingReqInfo, PTokenReqInfo, PortalStateInfo
from IncognitoChain.TestCases.Portal import portal_user, portal_user_remote_addr, bnb_pass_phrase, \
    find_custodian_account_by_incognito_addr, TEST_SETTING_PORTING_AMOUNT, all_custodians, big_collateral, \
    fat_custodian_prv, big_bnb_rate, big_porting_amount, init_portal_rate, fat_custodian

is_special_case = False


@pytest.mark.parametrize("porting_amount,porting_fee,expected", [
    (TEST_SETTING_PORTING_AMOUNT, None, "valid"),  # None means auto calculate fee
    (TEST_SETTING_PORTING_AMOUNT, 1, "invalid"),
    # (big_porting_amount, None, "valid"),  # this test should be run alone
])
def test_create_porting_req_1_1(porting_amount, porting_fee, expected):
    STEP(0, "before test")
    portal_state_before_test = SUT.full_node.get_latest_portal_state()
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4_test = portal_user.get_token_balance(PBNB_ID)
    custodian_pool_info_before = SUT.full_node.help_get_portal_custodian_pool(portal_state_before_test)
    portal_state_info_before_test = PortalStateInfo(portal_state_before_test.get_result())
    pbnb_rate = portal_state_info_before_test.get_portal_rate(PBNB_ID)
    prv_rate = portal_state_info_before_test.get_portal_rate(PRV_ID)
    estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, pbnb_rate, prv_rate)
    # spacial case, porting large amount
    if porting_amount == big_porting_amount:
        if fat_custodian.get_prv_balance_cache() < big_collateral:
            COIN_MASTER.send_prv_to(fat_custodian,
                                    fat_custodian_prv - fat_custodian.get_prv_balance_cache(),
                                    privacy=0).subscribe_transaction()
            if COIN_MASTER.shard != fat_custodian.shard:
                try:
                    fat_custodian.subscribe_cross_output_coin()
                except:
                    pass

        # deposit big collateral
        deposit_tx = fat_custodian.portal_make_me_custodian((big_collateral + 1), PBNB_ID,
                                                            all_custodians[fat_custodian])
        err = deposit_tx.get_error_msg()
        assert err is None, "Custodian deposit fail"
        deposit_tx.subscribe_transaction()

        # create new rate:
        create_rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(big_bnb_rate).subscribe_transaction()
        assert create_rate_tx.get_error_msg() is None, 'fail to create rate'
        # wait for new rate to take effect
        SUT.full_node.help_wait_till_next_epoch()
        # re-estimate porting fee
        estimated_porting_fee = PortalHelper.cal_portal_portal_fee(big_porting_amount, big_bnb_rate[PBNB_ID],
                                                                   init_portal_rate[PRV_ID])

    if portal_user.get_prv_balance() < estimated_porting_fee:
        COIN_MASTER.send_prv_to(portal_user,
                                estimated_porting_fee - portal_user.get_prv_balance_cache() + coin(
                                    1)).subscribe_transaction()
        prv_bal_be4 = portal_user.wait_for_balance_change(current_balance=prv_bal_be4)

    STEP(1, f"Create a {expected} porting request")
    porting_req = portal_user.portal_create_porting_request(PBNB_ID, porting_amount, porting_fee=porting_fee)
    porting_id = porting_req.params().get_portal_register_id()
    porting_fee = porting_req.params().get_portal_porting_fee()
    tx_block = porting_req.subscribe_transaction()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    tx_id = porting_req.get_tx_id()
    INFO(f"""Porting req is created with 
            amount            = {porting_amount}
            porting fee       = {porting_fee},
            porting id        = {porting_id}, 
            tx fee            = {tx_fee}, 
            tx size           = {tx_size}
            prv bal after req = {portal_user.get_prv_balance()}""")
    STEP(1.2, 'verify porting fee')
    if expected == 'valid':
        assert estimated_porting_fee == porting_fee

    STEP(2, "Check req status")
    porting_req_info = PortingReqInfo()
    WAIT(90)
    porting_req_info.get_porting_req_by_tx_id(tx_id)
    portal_state_after_req_accepted = None
    if expected == 'valid':
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.ACCEPTED

        STEP(2.2, "Check req status by req id")
        porting_req_info.get_porting_req_by_porting_id(porting_id)
        assert porting_req_info.get_status() == PortalPortingStatusByPortingId.WAITING
        portal_state_after_req_accepted = SUT.full_node.get_latest_portal_state()
    else:
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.REJECTED

    STEP(3, 'Verify balance')
    assert prv_bal_be4 - porting_fee - tx_fee == portal_user.get_prv_balance()

    if expected == 'valid':
        STEP(4, 'Send BNB to custodian')
        memo_encoded = encode_porting_memo(porting_req_info.get_porting_id())
        custodian_info = porting_req_info.get_custodians()[0]
        bnb_cli = BnbCli()
        bnb_send_amount = porting_amount // 10
        bnb_send_tx = bnb_cli.send_bnb_to(portal_user_remote_addr, custodian_info.get_remote_address(),
                                          bnb_send_amount, bnb_pass_phrase, memo_encoded)

        STEP(5, 'Submit proof to request ported token')
        balance_before_req_ported_token = portal_user.get_token_balance(PBNB_ID)
        proof = build_bnb_proof(bnb_send_tx.get_tx_hash())
        req_tx = portal_user.portal_req_ported_ptoken(porting_id, PBNB_ID, porting_amount, proof)
        req_tx.subscribe_transaction()
        WAIT(90)  # wait for the req to be processed
        token_req_info = PTokenReqInfo(req_tx.get_result())
        ported_token_req = token_req_info.get_ptoken_req_by_tx_id(req_tx.get_tx_id())
        ported_token_req_status = ported_token_req.get_status()
        assert ported_token_req_status == PortalPtokenReqStatus.ACCEPTED, \
            f'Req for ported token is rejected. CODE = {ported_token_req_status}'

        STEP(6, 'Verify user balance')
        balance_after_req = portal_user.wait_for_balance_change(PBNB_ID, balance_before_req_ported_token)
        assert balance_after_req == balance_before_req_ported_token + porting_amount
        assert tok_bal_be4_test == balance_before_req_ported_token

        STEP(7, f'Verify lock collateral amount')
        custodian_account = None

        # get lock collateral of custodian before test
        for _info in custodian_pool_info_before:
            if _info.get_incognito_addr() == custodian_info.get_incognito_addr():
                custodian_account = find_custodian_account_by_incognito_addr(_info.get_incognito_addr())
                break
        lock_collateral_before = custodian_account.portal_get_my_custodian_info(
            portal_state_before_test).get_locked_collateral(PBNB_ID)
        lock_collateral_before = 0 if lock_collateral_before is None else lock_collateral_before

        # get lock collateral of custodian after test
        portal_state_after_test = SUT.full_node.get_latest_portal_state()
        custodian_pool_info_after = SUT.full_node.help_get_portal_custodian_pool(portal_state_after_test)
        for _info in custodian_pool_info_after:
            if _info.get_incognito_addr() == custodian_info.get_incognito_addr():
                custodian_account = find_custodian_account_by_incognito_addr(_info.get_incognito_addr())
                break
        lock_collateral_after = custodian_account.portal_get_my_custodian_info(
            portal_state_after_test).get_locked_collateral(PBNB_ID)

        # calculate lock collateral
        portal_state_info = PortalStateInfo(portal_state_after_req_accepted.get_result())
        portal_rate_bnb = portal_state_info.get_portal_rate(PBNB_ID)
        portal_rate_prv = portal_state_info.get_portal_rate(PRV_ID)
        estimated_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, portal_rate_bnb, portal_rate_prv)

        INFO(f'custodian incognito add     = {l6(custodian_info.get_incognito_addr())}\n'
             f'lock collateral before test = {lock_collateral_before}\n'
             f'lock collateral after test  = {lock_collateral_after}\n'
             f'estimated lock collateral   = {estimated_lock_collateral}\n'
             f'prv rate                    = {portal_rate_prv}\n'
             f'pbnb rate                   = {portal_rate_bnb}\n'
             f'porting amount              = {porting_amount}')
        porting_req_collateral = porting_req_info.get_custodians()[0].get_locked_collateral()
        assert lock_collateral_after - lock_collateral_before == estimated_lock_collateral
        assert lock_collateral_after - lock_collateral_before == porting_req_collateral

    else:
        STEP(4, "Porting req fail, wait 60s to return porting fee (only take tx fee), verify user balance")
        WAIT(60)
        assert portal_user.get_prv_balance() == prv_bal_be4 - tx_fee


def test_create_porting_req_1_n():
    STEP(0, "before test")
    portal_state_before_test = SUT.full_node.get_latest_portal_state()
    highest_free_collateral_in_pool = SUT.full_node.help_get_highest_free_collateral_custodian(
        portal_state_before_test)
    portal_state_info = PortalStateInfo(portal_state_before_test.get_result())
    pbnb_rate = portal_state_info.get_portal_rate(PBNB_ID)
    prv_rate = portal_state_info.get_portal_rate(PRV_ID)
    porting_amount = (PortalHelper.cal_portal_exchange_prv_to_tok(highest_free_collateral_in_pool.get_free_collateral(),
                                                                  prv_rate, pbnb_rate) * 100 // 150) + 10
    estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, pbnb_rate, prv_rate)

    remote_receiver_dict = {}

    custodian_pool_info_before = SUT.full_node.help_get_portal_custodian_pool(portal_state_before_test)

    # if portal_user.get_prv_balance() < coin(5):
    #     COIN_MASTER.send_prv_to(portal_user, coin(5) - portal_user.get_prv_balance_cache(),
    #                             privacy=0).subscribe_transaction()
    #     portal_user.wait_for_balance_change(prv_token_id, portal_user.get_prv_balance_cache())

    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4_test = portal_user.get_token_balance(PBNB_ID)
    STEP(1.2, f"Create a valid porting request")
    porting_req = portal_user.portal_create_porting_request(PBNB_ID, porting_amount)
    porting_id = porting_req.params().get_portal_register_id()
    porting_fee = porting_req.params().get_portal_porting_fee()
    tx_block = porting_req.subscribe_transaction()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    tx_id = porting_req.get_tx_id()
    INFO(f"""Porting req is created with amount = {porting_amount},
                                         porting fee = {porting_fee},
                                         porting id = {porting_id},
                                         tx fee = {tx_fee},
                                         tx size = {tx_size}
                                         prv bal after req = {portal_user.get_prv_balance()}""")

    STEP(1.2, 'verify porting fee')
    assert estimated_porting_fee == porting_fee

    STEP(2.1, "Check req status by tx id")
    porting_req_info = PortingReqInfo()
    porting_req_info.get_porting_req_by_tx_id(tx_id)
    assert porting_req_info.get_status() == PortalPortingStatusByTxId.ACCEPTED

    STEP(2.2, "Check req status by req id")
    porting_req_info.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info.get_status() == PortalPortingStatusByPortingId.WAITING
    portal_state_after_req_accepted = SUT.full_node.get_latest_portal_state()

    STEP(3, 'Verify balance')
    assert prv_bal_be4 - porting_fee - tx_fee == portal_user.get_prv_balance()

    STEP(4, 'Check that porting req require 2 or more custodian')
    custodians_info_in_porting_req = porting_req_info.get_custodians()
    assert len(custodians_info_in_porting_req) >= 2 and INFO(
        f"!!! This req require {len(custodians_info_in_porting_req)} custodians ")

    STEP(5, 'Send BNB to custodian')
    for custodian_info in custodians_info_in_porting_req:
        bnb_to_send = custodian_info.get_amount()
        if bnb_to_send < 10:
            WARNING(f"Amount of BNB to send to custodian is {bnb_to_send} < 10")
            bnb_to_send = 10
        remote_receiver_dict[custodian_info.get_remote_address()] = bnb_to_send // 10  # pbnb 10^-9, bnb 10^-8

    memo_encoded = encode_porting_memo(porting_req_info.get_porting_id())
    bnb_cli = BnbCli()
    bnb_send_tx = bnb_cli.send_bnb_to_multi(portal_user_remote_addr, remote_receiver_dict, bnb_pass_phrase,
                                            memo_encoded)

    STEP(6.1, 'Submit proof to request ported token')
    balance_before_req_ported_token = portal_user.get_token_balance(PBNB_ID)
    proof = build_bnb_proof(bnb_send_tx.get_tx_hash())
    req_tx = portal_user.portal_req_ported_ptoken(porting_id, PBNB_ID, porting_amount, proof)
    req_tx.subscribe_transaction()
    token_req_info = PTokenReqInfo(req_tx.get_result())
    ported_token_req = token_req_info.get_ptoken_req_by_tx_id(req_tx.get_tx_id())
    ported_token_req_status = ported_token_req.get_status()
    assert ported_token_req_status == PortalPtokenReqStatus.ACCEPTED, \
        f'Req for ported token is rejected. CODE = {ported_token_req_status}'

    STEP(6.2, 'Verify user balance')
    balance_after_req = portal_user.wait_for_balance_change(PBNB_ID, balance_before_req_ported_token)
    assert balance_after_req == balance_before_req_ported_token + porting_amount
    assert tok_bal_be4_test == balance_before_req_ported_token

    STEP(7, f'verify lock collateral amount')
    sum_lock_collateral_change = 0
    sum_lock_collateral_of_req = 0

    for _info_after_req in custodians_info_in_porting_req:
        custodian_account = None
        # find change amount of lock collateral
        for _info_before_req in custodian_pool_info_before:
            if _info_before_req.get_incognito_addr() == _info_after_req.get_incognito_addr():
                custodian_account = find_custodian_account_by_incognito_addr(_info_before_req.get_incognito_addr())
                break
        lock_collateral_before = custodian_account.portal_get_my_custodian_info(
            portal_state_before_test).get_locked_collateral(PBNB_ID)
        INFO(f'lock collateral before test: '
             f'{l6(custodian_account.payment_key)} : {l6(PBNB_ID)} : {lock_collateral_before}')
        change_amount = custodian_account.wait_my_portal_lock_collateral_to_change(PBNB_ID, lock_collateral_before)
        sum_lock_collateral_change += change_amount

    portal_state_info = PortalStateInfo(portal_state_after_req_accepted.get_result())
    portal_rate_bnb = portal_state_info.get_portal_rate(PBNB_ID)
    portal_rate_prv = portal_state_info.get_portal_rate(PRV_ID)
    estimated_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, portal_rate_bnb, portal_rate_prv)

    INFO(f'custodian incognito add     \n'
         f'lock collateral change      = {sum_lock_collateral_change}\n'
         f'estimated lock collateral   = {estimated_lock_collateral}\n'
         f'prv rate                    = {portal_rate_prv}\n'
         f'pbnb rate                   = {portal_rate_bnb}\n'
         f'porting amount              = {porting_amount}')
    # get lock collateral req
    custodian_info_in_rq = porting_req_info.get_custodians()
    for _info_after_req in custodian_info_in_rq:
        sum_lock_collateral_of_req += _info_after_req.get_locked_collateral()
    assert sum_lock_collateral_change == estimated_lock_collateral
    assert sum_lock_collateral_change == sum_lock_collateral_of_req


def test_porting_req_expired():
    """
    in order to run this test, must set TimeOutWaitingPortingRequest to 30min or less
    :return:
    """
    STEP(0, "before test")
    portal_state_before_test = SUT.full_node.get_latest_portal_state()
    user_prv_bal_be4_test = portal_user.get_prv_balance()
    porting_amount = TEST_SETTING_PORTING_AMOUNT
    portal_state_info_before_test = PortalStateInfo(portal_state_before_test.get_result())
    pbnb_rate = portal_state_info_before_test.get_portal_rate(PBNB_ID)
    prv_rate = portal_state_info_before_test.get_portal_rate(PRV_ID)
    estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, pbnb_rate, prv_rate)

    STEP(1, f"Create a valid porting request")
    porting_req = portal_user.portal_create_porting_request(PBNB_ID, porting_amount)
    porting_id = porting_req.params().get_portal_register_id()
    porting_fee = porting_req.params().get_portal_porting_fee()
    tx_block = porting_req.subscribe_transaction()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    tx_id = porting_req.get_tx_id()
    INFO(f"""Porting req is created with porting fee = {porting_fee},
                                             porting id = {porting_id}, 
                                             tx fee = {tx_fee}, 
                                             tx size = {tx_size}
                                             prv bal after req = {portal_user.get_prv_balance()}""")
    STEP(1.2, 'verify porting fee')
    assert estimated_porting_fee == porting_fee

    STEP(2, "Check req status")
    porting_req_info = PortingReqInfo()
    porting_req_info.get_porting_req_by_tx_id(tx_id)
    assert porting_req_info.get_status() == PortalPortingStatusByTxId.ACCEPTED

    STEP(2.2, "Check req status by req id")
    porting_req_info.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info.get_status() == PortalPortingStatusByPortingId.WAITING

    STEP(3, 'Verify balance')
    assert user_prv_bal_be4_test - porting_fee - tx_fee == portal_user.get_prv_balance()

    STEP(4, 'Wait 31min for the req to be expired')
    WAIT(31 * 60)

    STEP(5, "Check req status")
    porting_req_info.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info.get_status() == PortalPortingStatusByPortingId.EXPIRED

    STEP(6, "Custodian collateral must be unlock")
    custodian_acc = find_custodian_account_by_incognito_addr(porting_req_info.get_custodians()[0].get_incognito_addr())
    state_before_test = custodian_acc.portal_get_my_custodian_info(portal_state_before_test)
    state_after_expire = custodian_acc.portal_get_my_custodian_info()
    assert state_before_test.get_locked_collateral() == state_after_expire.get_locked_collateral()
    assert state_before_test.get_free_collateral() == state_after_expire.get_free_collateral()
    assert state_before_test.get_total_collateral() == state_after_expire.get_total_collateral()
    assert state_before_test.get_holding_token_amount(PBNB_ID) == state_after_expire.get_holding_token_amount(PBNB_ID)

    STEP(7, "Return porting fee, not tx fee")
    assert user_prv_bal_be4_test - tx_fee == portal_user.get_prv_balance()
