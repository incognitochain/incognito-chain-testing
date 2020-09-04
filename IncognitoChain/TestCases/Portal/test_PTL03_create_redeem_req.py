import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PortalRedeemStatus, PortalUnlockCollateralReqStatus, PBTC_ID
from IncognitoChain.Helpers.Logging import STEP, INFO, WARNING
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.Objects.PortalObjects import RedeemReqInfo, UnlockCollateralReqInfo, RedeemMatchingInfo
from IncognitoChain.TestCases.Portal import portal_user, cli_pass_phrase, \
    TEST_SETTING_REDEEM_AMOUNT, PORTAL_REQ_TIME_OUT, custodian_remote_addr

n = 'n'


@pytest.mark.parametrize("token, redeem_amount, redeem_fee, num_of_custodian, custodian_matching, expected", [
    # fee = none means auto get fee
    # BNB
    # 1 custodian
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'auto', 'valid'),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, 'auto', 'invalid'),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'manual', 'valid'),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, 'manual', 'invalid'),
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'manual', 'expire'),
    # n custodian
    (PBNB_ID, TEST_SETTING_REDEEM_AMOUNT, None, n, 'auto', 'valid'),

    #
    # BTC
    # 1 custodian
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'auto', 'valid'),
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, 'auto', 'invalid'),
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'manual', 'valid'),
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, 1, 1, 'manual', 'invalid'),
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, 1, 'manual', 'expire'),
    # n custodian
    (PBTC_ID, TEST_SETTING_REDEEM_AMOUNT, None, n, 'auto', 'valid'),

])
def test_create_redeem_req_1_1(token, redeem_amount, redeem_fee, num_of_custodian, custodian_matching, expected):
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4 = portal_user.get_token_balance(token)
    PSI_before_test = SUT.full_node.get_latest_portal_state_info()
    if num_of_custodian == n:
        highest_holding_token_custodian_in_pool = PSI_before_test.help_get_highest_holding_token_custodian(token)
        redeem_amount = highest_holding_token_custodian_in_pool.get_holding_token_amount(token) + 1

    STEP(1.1, 'Create redeem req')
    redeem_req_tx = portal_user.portal_req_redeem_my_token(token, redeem_amount, redeem_fee=redeem_fee)
    redeem_req_tx.expect_no_error()
    tx_block = redeem_req_tx.subscribe_transaction()
    redeem_fee = redeem_req_tx.params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req_tx.params().get_portal_redeem_req_id()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    INFO(f"""Porting req is created with redeem amount            = {redeem_amount} 
                                         redeem fee               = {redeem_fee}
                                         redeem id                = {redeem_id}
                                         tx fee                   = {tx_fee}
                                         tx size                  = {tx_size}
                                         user token bal after req = {portal_user.get_token_balance(token)}
                                         user prv bal after req   = {portal_user.get_prv_balance()}""")
    STEP(2, "Check req status")
    redeem_info = RedeemReqInfo()
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)

    if expected == 'valid' or expected == 'expire':
        assert redeem_info.get_status() == PortalRedeemStatus.WAITING
        SUT.full_node.get_latest_portal_state_info()
    else:
        assert redeem_info.data is None

    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    if expected != 'invalid':  # valid or expire
        STEP(3.1, "Check requester bal")
        assert tok_bal_be4 - redeem_amount == portal_user.get_token_balance(token)

        matching_custodian(custodian_matching, token, redeem_id, PSI_before_test)

        if expected == 'valid':
            # todo: not yet cover case redeem 1_n expire and invalid, update the verify function below for that
            verify_valid_redeem(PSI_before_test, redeem_id, redeem_amount, token, custodian_matching)
        elif expected == 'expire':
            verify_expired_redeem(token, redeem_id, tok_bal_be4, prv_bal_be4, tx_fee, redeem_fee)
    else:  # case invalid redeem
        STEP(3, "Redeem req reject, wait 60s to return token but not tx and redeem fee. Check requester bal")
        WAIT(60)
        assert tok_bal_be4 == portal_user.get_token_balance(token)
        assert prv_bal_be4 - tx_fee - redeem_fee == portal_user.get_prv_balance()


def verify_valid_redeem(psi_b4, redeem_id, redeem_amount, token, matching):
    redeem_info = RedeemReqInfo()
    STEP(3.3, 'Verify that the request move on to Matched `redeem list')
    WAIT(40)
    redeem_info_b4_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    PSI_after_match = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    matched_redeem_reqs = PSI_after_match.get_redeem_matched_req(token)
    assert redeem_id in [matched_redeem_req.get_redeem_id() for matched_redeem_req in matched_redeem_reqs], \
        f'Not found redeem id {redeem_id} in matched list'

    if matching == 'manual':
        custodian_b4_re_match = redeem_info_b4_re_match.get_redeem_matching_custodians()[0].get_incognito_addr()
        verify_rematching_test_19(token, redeem_id, psi_b4, custodian_b4_re_match)

    STEP(4, 'Custodian send BNB to user')
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    send_public_token_tx_list = {}
    custodians_of_this_req = redeem_info.get_redeem_matching_custodians()
    for custodian_info in custodians_of_this_req:
        custodian_incognito_addr = custodian_info.get_incognito_addr()
        amount = custodian_info.get_amount()
        memo = (redeem_id, custodian_incognito_addr)
        send_amount = max(amount // 10, 1)
        custodian_acc = custodian_remote_addr.get_accounts(custodian_incognito_addr)
        send_public_token_tx = custodian_acc.send_public_token(token, send_amount, portal_user, cli_pass_phrase, memo)
        send_public_token_tx_list[custodian_acc] = send_public_token_tx

    STEP(5, 'Submit proof to request unlock collateral')
    sum_estimated_unlock_collateral = 0
    unlock_collateral_txs = []
    PSI_after_req = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    for custodian_acc, tx in send_public_token_tx_list.items():
        proof = tx.build_proof()
        INFO(f'=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
             f'Custodian submit proof: {custodian_acc.get_remote_addr(token)}')
        custodian_info = redeem_info.get_custodian(custodian_acc)
        redeem_amount_of_this_custodian = custodian_info.get_amount()
        custodian_status_after_req = PSI_after_req.get_custodian_info_in_pool(custodian_acc)
        locked_collateral_before = custodian_status_after_req.get_locked_collateral(token)
        holding_token_after_req = custodian_status_after_req.get_holding_token_amount(token)
        sum_waiting_porting_req_lock_collateral = PSI_after_req.sum_collateral_porting_waiting(token, custodian_acc)
        sum_waiting_redeem_req_holding_tok = PSI_after_req.sum_holding_token_matched_redeem_req(token, custodian_acc)
        estimated_unlock_collateral_of_1_custodian = \
            redeem_amount_of_this_custodian * (locked_collateral_before - sum_waiting_porting_req_lock_collateral) // (
                holding_token_after_req + redeem_amount_of_this_custodian + sum_waiting_redeem_req_holding_tok)
        INFO(f"""Status before req unlock collateral:
                                redeem amount     = {redeem_amount_of_this_custodian}
                                locked collateral = {locked_collateral_before}
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
        assert unlock_collateral_req_info.get_status() == PortalUnlockCollateralReqStatus.ACCEPTED

    STEP(6, 'Wait 60s for collateral to be unlocked then verify custodian collateral')
    WAIT(60)
    sum_actual_unlock_collateral = 0
    sum_delta_holding_token = 0
    PSI_after_submit_proof = SUT.REQUEST_HANDLER.get_latest_portal_state_info()
    for custodian_info in custodians_of_this_req:
        custodian_status_after_req = PSI_after_submit_proof.get_custodian_info_in_pool(custodian_info)
        locked_collateral_after = custodian_status_after_req.get_locked_collateral(token)
        holding_token_after = custodian_status_after_req.get_holding_token_amount(token)

        custodian_status_before = psi_b4.get_custodian_info_in_pool(custodian_info)
        locked_collateral_before = custodian_status_before.get_locked_collateral(token)
        holding_token_before = custodian_status_before.get_holding_token_amount(token)

        unlock_collateral_amount = locked_collateral_before - locked_collateral_after
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


def verify_expired_redeem(token, redeem_id, tok_bal_b4, prv_bal_b4, tx_fee, redeem_fee):
    redeem_info = RedeemReqInfo()
    STEP(4, f'Wait {PORTAL_REQ_TIME_OUT + 0.5} min for the req to be expired')
    WAIT(PORTAL_REQ_TIME_OUT + 0.5)

    STEP(5, "Check req status")
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    assert redeem_info.get_status() == PortalRedeemStatus.REJECTED_BY_LIQUIDATION

    STEP(6, "Must return ptoken to user")
    assert tok_bal_b4 == portal_user.get_token_balance(token)

    STEP(7, "No return any fee (tx and portal fee)")
    assert prv_bal_b4 - tx_fee - redeem_fee == portal_user.get_prv_balance()


def matching_custodian(matching_mode, token, redeem_id, psi_b4):
    if matching_mode == 'auto':
        STEP(3.2, f'Wait 10 min for custodian auto pick')
        WAIT(10.5 * 60)
    else:  # manual matching
        highest_holding_custodian = psi_b4.help_get_highest_holding_token_custodian(token)
        custodian = custodian_remote_addr.get_accounts(highest_holding_custodian.get_incognito_addr())
        STEP(3.2, f"Self-picking custodian: {l6(custodian.payment_key)}")
        custodian.portal_let_me_take_care_this_redeem(redeem_id)


def verify_rematching_test_19(token, redeem_id, psi_b4, custodian_info_b4):
    redeem_info = RedeemReqInfo()
    STEP(3.4, 'Matching again with custodian has no holding token expect error')  # Test case 19
    custodian_has_no_holding = psi_b4.find_custodian_with_holding_token_amount(token, 0)
    if custodian_has_no_holding is None:
        WARNING("There's no custodian with 0 holding token")
    else:
        poor_custodian = custodian_remote_addr.get_accounts(custodian_has_no_holding.get_incognito_addr())
        matching_tx = poor_custodian.portal_let_me_take_care_this_redeem(redeem_id, do_assert=False)
        assert RedeemMatchingInfo().get_matching_info_by_tx(matching_tx.get_tx_id()).is_rejected()

    STEP(3.5, f'Make sure matched custodian must not change')
    redeem_info_af_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    custodian_af_re_match = redeem_info_af_re_match.get_redeem_matching_custodians()[
        0].get_incognito_addr()
    assert custodian_af_re_match == custodian_info_b4
