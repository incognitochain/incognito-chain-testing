import copy
import random

import pytest

from Configs.Constants import PBNB_ID, Status
from Configs.Configs import ChainConfig
from Helpers.Logging import STEP, INFO, WARNING
from Helpers.TestHelper import l6
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.PortalObjects import RedeemReqInfo, UnlockCollateralReqInfo, RedeemMatchingInfo
from TestCases.Portal import portal_user, cli_pass_phrase, all_custodians, \
    TEST_SETTING_REDEEM_AMOUNT, test_PTL02_create_porting_req, TEST_SETTING_PORTING_AMOUNT

n = 2
full_holding = 'full holding'
any_ = 'redeem amount will be calculated for redeem N custodian'
auto_matching = 'auto matching'
manual_matching = 'manual matching'
valid = 'valid'
invalid = 'invalid'
expire_not_send = 'expire because custodian not send token'
expire_one_send = 'expire because only one custodian send public token'


@pytest.mark.parametrize("token, redeem_amount, redeem_fee, num_of_custodian, custodian_matching, expected", [
    # fee = none means auto get min fee
    # BNB
    # 1 custodian
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, auto_matching, valid),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, auto_matching, invalid),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, manual_matching, valid),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, manual_matching, invalid),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, manual_matching, expire_not_send),  # Test case 23
    (PBNB_ID, full_holding, None, 1, manual_matching, valid),  # test case 20
    (PBNB_ID, full_holding, None, 1, auto_matching, valid),  # test case 20
    # n custodian
    (PBNB_ID, any_, None, n, auto_matching, valid),
    (PBNB_ID, any_, None, n, manual_matching, valid),  # test case 22
    (PBNB_ID, any_, None, n, auto_matching, expire_not_send),  # test case 24
    (PBNB_ID, any_, None, n, manual_matching, expire_not_send),  # test case 24
    (PBNB_ID, any_, None, n, auto_matching, expire_one_send),  # test case 25
    (PBNB_ID, any_, None, n, manual_matching, expire_one_send),  # test case 25

    #
    # # BTC
    # # 1 custodian
    # (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, auto_matching, valid),
    # (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, auto_matching, invalid),
    # (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, manual_matching, valid),
    # (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, manual_matching, invalid),
    # (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, manual_matching, expire_not_send),  # Test case 23
    # # # n custodian
    # (PBTC_ID, any_, None, n, auto_matching, valid),
    # (PBTC_ID, any_, None, n, manual_matching, valid),  # test case 22
    # (PBTC_ID, any_, None, n, auto_matching, expire_not_send),  # test case 24
    # (PBTC_ID, any_, None, n, manual_matching, expire_not_send),  # test case 24
    # (PBTC_ID, any_, None, n, auto_matching, expire_one_send),  # test case 25
    # (PBTC_ID, any_, None, n, manual_matching, expire_one_send),  # test case 25

])
def test_create_redeem_req(token, redeem_amount, redeem_fee, num_of_custodian, custodian_matching, expected):
    PSI_before_test = SUT().get_latest_portal_state_info()
    highest_holding_token_custodian_in_pool = PSI_before_test.help_get_highest_holding_token_custodian(token)
    # check if there are enough custodian holding token for the test to run
    # if not, porting more token
    num_of_holding_custodians = len(PSI_before_test.find_custodian_hold_more_than_amount(token, 0))
    while 0 <= num_of_holding_custodians < num_of_custodian:
        test_PTL02_create_porting_req.test_create_porting_req_1_1(token, TEST_SETTING_PORTING_AMOUNT, portal_user, None,
                                                                  1, 'valid')
        WAIT(1, 'm')
        PSI_before_test = SUT().get_latest_portal_state_info()
        highest_holding_token_custodian_in_pool = PSI_before_test.help_get_highest_holding_token_custodian(token)
        num_of_holding_custodians = len(PSI_before_test.find_custodian_hold_more_than_amount(token, 0))
        INFO(f'Num of holding custodian in chain = {num_of_holding_custodians}')
    if num_of_custodian == n:
        redeem_amount = highest_holding_token_custodian_in_pool.get_holding_token_amount(token) + 1
    if redeem_amount == full_holding:
        redeem_amount = highest_holding_token_custodian_in_pool.get_holding_token_amount(token)
    prv_bal_be4 = portal_user.get_balance()
    tok_bal_be4 = portal_user.get_balance(token)

    STEP(1.1, 'Create redeem req')
    redeem_req_tx = portal_user.portal_req_redeem_my_token(token, redeem_amount, redeem_fee=redeem_fee)
    redeem_req_tx.expect_no_error()
    tx_block = redeem_req_tx.subscribe_transaction()
    redeem_fee = redeem_req_tx.rpc_params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req_tx.rpc_params().get_portal_redeem_req_id()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_balance()

    INFO(f"""Porting req is created with redeem amount            = {redeem_amount} 
                                         redeem fee               = {redeem_fee}
                                         redeem id                = {redeem_id}
                                         tx fee                   = {tx_fee}
                                         tx size                  = {tx_size}
                                         user token bal after req = {portal_user.get_balance(token)}
                                         user prv bal after req   = {portal_user.get_balance()}""")
    STEP(2, "Check req status")
    redeem_info = RedeemReqInfo()
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)

    if expected != invalid:
        assert redeem_info.get_status() == Status.Portal.RedeemStatus.WAITING
    else:  # invalid redeem req
        assert redeem_info.data is None

    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_balance()

    if expected != invalid:  # valid or expire
        STEP(3.1, "Check requester bal")
        assert tok_bal_be4 - redeem_amount == portal_user.get_balance(token)

        matching_custodian(custodian_matching, num_of_custodian, token, redeem_id, PSI_before_test)
        if expected == valid:
            verify_valid_redeem(PSI_before_test, redeem_id, redeem_amount, token, custodian_matching)
        elif expected == expire_not_send:
            verify_expired_redeem_0_custodian_sent(redeem_id, tok_bal_be4, prv_bal_be4, tx_fee, redeem_fee,
                                                   PSI_before_test)
        elif expected == expire_one_send:
            verify_expired_redeem_1_custodian_sent(token, redeem_id, tok_bal_be4, prv_bal_be4, tx_fee, redeem_fee,
                                                   PSI_before_test)
    else:  # case invalid redeem
        STEP(3, "Redeem req reject, wait 60s to return token but not tx and redeem fee. Check requester bal")
        WAIT(60)
        assert tok_bal_be4 == portal_user.get_balance(token)
        assert prv_bal_be4 - tx_fee - redeem_fee == portal_user.get_balance()


def verify_valid_redeem(psi_b4, redeem_id, redeem_amount, token, matching):
    redeem_info = RedeemReqInfo()
    STEP(3.3, 'Verify that the request move on to Matched redeem list')
    WAIT(40)
    redeem_info_b4_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    PSI_after_match = SUT().get_latest_portal_state_info()
    matched_redeem_reqs = PSI_after_match.get_redeem_matched_req(token)
    assert redeem_id in [matched_redeem_req.get_redeem_id() for matched_redeem_req in matched_redeem_reqs], \
        f'Not found redeem id {redeem_id} in matched list'

    if matching == manual_matching:
        custodian_b4_re_match = redeem_info_b4_re_match.get_redeem_matching_custodians()[0].get_incognito_addr()
        verify_rematching_custodian_with_0_holding(token, redeem_id, psi_b4, custodian_b4_re_match)

    STEP(4, 'Custodian send BNB to user')
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    send_public_token_tx_list = {}
    custodians_of_this_req = redeem_info.get_redeem_matching_custodians()
    for custodian_info in custodians_of_this_req:
        custodian_incognito_addr = custodian_info.get_incognito_addr()
        amount = custodian_info.get_amount()
        memo = (redeem_id, custodian_incognito_addr)
        send_amount = max(amount // 10, 1)
        custodian_acc = all_custodians.find_account_by_key(custodian_incognito_addr)
        send_public_token_tx = custodian_acc.send_public_token(token, send_amount, portal_user, cli_pass_phrase, memo)
        send_public_token_tx_list[custodian_acc] = send_public_token_tx

    STEP(5, 'Submit proof to request unlock collateral')
    sum_estimated_unlock_collateral = 0
    unlock_collateral_txs = []
    PSI_after_req = SUT().get_latest_portal_state_info()
    for custodian_acc, tx in send_public_token_tx_list.items():
        proof = tx.build_proof()
        INFO(f'=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
             f'Custodian submit proof: {custodian_acc.get_remote_addr(token)}')
        custodian_info = redeem_info.get_custodian(custodian_acc)
        redeem_amount_of_this_custodian = custodian_info.get_amount()
        custodian_status_af_req = PSI_after_req.get_custodian_info_in_pool(custodian_acc)
        custodian_status_b4_req = psi_b4.get_custodian_info_in_pool(custodian_acc)
        locked_collateral_b4 = custodian_status_b4_req.get_locked_collateral(token)
        holding_token_after_req = custodian_status_af_req.get_holding_token_amount(token)
        sum_waiting_porting_req_lock_collateral = PSI_after_req.sum_collateral_porting_waiting(token, custodian_acc)
        sum_waiting_redeem_req_holding_tok = PSI_after_req.sum_holding_token_matched_redeem_req(token, custodian_acc)
        estimated_unlock_collateral_of_1_custodian = \
            psi_b4.estimate_custodian_collateral_unlock(custodian_info, redeem_amount_of_this_custodian, token)

        INFO(f"""Status before req unlock collateral:
                                redeem amount     = {redeem_amount_of_this_custodian}
                                locked collateral = {locked_collateral_b4}
                                holding token     = {holding_token_after_req}
                                sum waiting colla = {sum_waiting_porting_req_lock_collateral}
                                sum holding token = {sum_waiting_redeem_req_holding_tok} 
                                estimated unlock  = {estimated_unlock_collateral_of_1_custodian}""")
        unlock_collateral_tx = custodian_acc.portal_req_unlock_collateral(token, redeem_amount_of_this_custodian,
                                                                          redeem_id, proof)
        unlock_collateral_tx.subscribe_transaction()
        sum_estimated_unlock_collateral += estimated_unlock_collateral_of_1_custodian
        unlock_collateral_txs.append(unlock_collateral_tx)

    for tx in unlock_collateral_txs:
        unlock_collateral_req_info = UnlockCollateralReqInfo()
        unlock_collateral_req_info.get_unlock_collateral_req_stat(tx.get_tx_id())
        assert unlock_collateral_req_info.get_status() == Status.Portal.UnlockCollateralReqStatus.ACCEPTED

    STEP(6, 'Wait 60s for collateral to be unlocked then verify custodian collateral')
    WAIT(60)
    sum_actual_unlock_collateral = 0
    sum_delta_holding_token = 0
    PSI_after_submit_proof = SUT().get_latest_portal_state_info()
    for custodian_info in custodians_of_this_req:
        custodian_status_af_req = PSI_after_submit_proof.get_custodian_info_in_pool(custodian_info)
        locked_collateral_after = custodian_status_af_req.get_locked_collateral(token)
        holding_token_after = custodian_status_af_req.get_holding_token_amount(token)

        custodian_status_before = psi_b4.get_custodian_info_in_pool(custodian_info)
        locked_collateral_b4 = custodian_status_before.get_locked_collateral(token)
        holding_token_before = custodian_status_before.get_holding_token_amount(token)

        unlock_collateral_amount = locked_collateral_b4 - locked_collateral_after
        release_token_amount = holding_token_before - holding_token_after

        INFO(f"""Status after req unlock collateral: {l6(custodian_info.get_incognito_addr())}
                     redeem amount of this custodian only = {custodian_info.get_amount()}
                                        locked collateral = {locked_collateral_after}
                                            holding token = {holding_token_after}
                                     actual unlock amount = {unlock_collateral_amount}""")
        sum_actual_unlock_collateral += unlock_collateral_amount
        sum_delta_holding_token += release_token_amount

    assert sum_actual_unlock_collateral == sum_estimated_unlock_collateral
    assert sum_delta_holding_token == redeem_amount


def verify_expired_redeem_0_custodian_sent(redeem_id, tok_bal_b4, prv_bal_b4, tx_fee, redeem_fee, psi_b4):
    STEP(4, f'Wait {ChainConfig.Portal.REQ_TIME_OUT + 0.5} min for the req to be expired')
    WAIT(ChainConfig.Portal.REQ_TIME_OUT + 0.5, 'm')

    STEP(5.1, "Check req status")
    redeem_info = RedeemReqInfo().get_redeem_status_by_redeem_id(redeem_id)
    assert redeem_info.get_status() == Status.Portal.RedeemStatus.LIQUIDATED

    STEP(5.2, "Must return 105% of 150% locked collateral to user, the rest 45%: unlock custodian collateral.\
     No return any fee (tx and portal fee)")
    psi_after = SUT().get_latest_portal_state_info()
    prv_bal_af = portal_user.wait_for_balance_change(from_balance=prv_bal_b4, timeout=1800, check_interval=60)
    prv_return_amount = psi_b4.verify_unlock_collateral_custodian_redeem_expire(psi_after, redeem_info)
    assert prv_bal_b4 - tx_fee - redeem_fee + prv_return_amount == prv_bal_af

    STEP(5.3, "User token balance must -redeem amount")
    assert tok_bal_b4 - redeem_info.get_redeem_amount() == portal_user.get_balance(redeem_info.get_token_id())


def verify_expired_redeem_1_custodian_sent(token, redeem_id, tok_bal_b4, prv_bal_b4, tx_fee, redeem_fee, psi_b4):
    redeem_info = RedeemReqInfo().get_redeem_status_by_redeem_id(redeem_id)
    custodians_of_this_req = redeem_info.get_redeem_matching_custodians()
    random_index = random.randrange(0, len(custodians_of_this_req))
    one_custodian_of_req = custodians_of_this_req[random_index]
    runaway_custodians = copy.deepcopy(custodians_of_this_req)
    runaway_custodians.pop(random_index)

    memo = (redeem_id, one_custodian_of_req.get_incognito_addr())
    custodian_acc = all_custodians.find_account_by_key(one_custodian_of_req.get_incognito_addr())
    STEP(4.1, "Only one of the custodians send public token to user")
    send_tx = custodian_acc.send_public_token(token, one_custodian_of_req.get_amount(), portal_user, cli_pass_phrase,
                                              memo)

    STEP(4.2, 'Request unlock collateral for this custodian and verify')
    psi_b4_expire = SUT().get_latest_portal_state_info()
    proof = send_tx.build_proof()
    custodian_acc.portal_req_unlock_collateral(token, one_custodian_of_req.get_amount(), redeem_id, proof)
    WAIT(40)  # wait for collateral to be unlock
    psi_af_unlock = SUT().get_latest_portal_state_info()

    # calculate unlock amount base on current custodian locked collateral and holding amount
    estimated_unlock_amount = psi_b4.estimate_custodian_collateral_unlock(one_custodian_of_req,
                                                                          one_custodian_of_req.get_amount(), token)
    real_unlock_amount = psi_b4_expire.get_custodian_info_in_pool(custodian_acc).get_locked_collateral(token) - \
                         psi_af_unlock.get_custodian_info_in_pool(custodian_acc).get_locked_collateral(token)
    assert real_unlock_amount == estimated_unlock_amount
    STEP(4.3, f'Wait {ChainConfig.Portal.REQ_TIME_OUT} min for the req to be expired')
    WAIT(ChainConfig.Portal.REQ_TIME_OUT, 'm')

    STEP(5.1, "Must return 105% of 150% locked collateral to user, the rest 45%: unlock custodian collateral.\
         No return any fee (tx and portal fee)")
    psi_after = SUT().get_latest_portal_state_info()
    prv_bal_af = portal_user.wait_for_balance_change(from_balance=prv_bal_b4, timeout=1800, check_interval=60)
    prv_return_amount = psi_b4.verify_unlock_collateral_custodian_redeem_expire(psi_after, redeem_info,
                                                                                runaway_custodians)
    assert prv_bal_b4 - tx_fee - redeem_fee + prv_return_amount == prv_bal_af

    STEP(5.2, "User token balance must -redeem amount")
    assert tok_bal_b4 - redeem_info.get_redeem_amount() == portal_user.get_balance(redeem_info.get_token_id())


def matching_custodian(matching_mode, num_of_custodian, token, redeem_id, psi_b4):
    if matching_mode == auto_matching:
        STEP(3.2, f'Wait 10 min for custodian auto pick')
        WAIT(10.5, 'm')
    else:  # manual matching
        STEP(3.2, f"Self-matching custodian")
        custodian_pool = psi_b4.help_sort_custodian_by_holding_token_desc(token)
        for i in range(0, num_of_custodian):
            custodian_info = custodian_pool[i]
            custodian = all_custodians.find_account_by_key(custodian_info.get_incognito_addr())
            custodian.portal_let_me_take_care_this_redeem(redeem_id)
            if i != num_of_custodian - 1:  # when the last custodian is matched, status will change to accept instead
                # Test case 21
                redeem_info = RedeemReqInfo().get_redeem_status_by_redeem_id(redeem_id)
                assert redeem_info.get_status() == Status.Portal.RedeemStatus.WAITING


def verify_rematching_custodian_with_0_holding(token, redeem_id, psi_b4, custodian_info_b4):
    redeem_info = RedeemReqInfo()
    STEP(3.4, 'Matching again with custodian has no holding token expect error')  # Test case 19
    custodian_has_no_holding = psi_b4.find_custodian_with_holding_token_amount(token, 0)
    if custodian_has_no_holding is None:
        WARNING("There's no custodian with 0 holding token")
    else:
        poor_custodian = all_custodians.find_account_by_key(custodian_has_no_holding.get_incognito_addr())
        if poor_custodian is not None:
            matching_tx = poor_custodian.portal_let_me_take_care_this_redeem(redeem_id, do_assert=False)
            assert RedeemMatchingInfo().get_matching_info_by_tx(matching_tx.get_tx_id()).is_rejected()
        else:
            WARNING(f'Account with following payment key not exist in test data '
                    f'{custodian_has_no_holding.get_incognito_addr()}. \n'
                    f'Skip rematch with custodian has no holding test step')

    STEP(3.5, f'Make sure matched custodian must not change')
    redeem_info_af_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    custodian_af_re_match = redeem_info_af_re_match.get_redeem_matching_custodians()[0].get_incognito_addr()
    assert custodian_af_re_match == custodian_info_b4
