"""
This test was already re-implement for improvement.
keep this back up for a few weeks just in case
"""
import pytest

from Configs.Constants import PBNB_ID, PRV_ID, PBTC_ID, Status, ChainConfig
from Helpers.Logging import STEP, INFO, WARNING
from Helpers.PortalHelper import PortalHelper
from Helpers.TestHelper import l6
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.PortalObjects import RedeemReqInfo, UnlockCollateralReqInfo, RedeemMatchingInfo
from TestCases.Portal import portal_user, cli_pass_phrase, \
    TEST_SETTING_REDEEM_AMOUNT, all_custodians


@pytest.mark.parametrize("token, redeem_fee, custodian_picking, expected", [
    # fee = none means auto get fee
    # BNB
    (PBNB_ID, None, 'auto', 'valid'),
    (PBNB_ID, 1, 'auto', 'invalid'),
    (PBNB_ID, None, 'manual', 'valid'),
    (PBNB_ID, 1, 'manual', 'invalid'),
    #
    # BTC
    (PBTC_ID, None, 'auto', 'valid'),
    (PBTC_ID, 1, 'auto', 'invalid'),
    (PBTC_ID, None, 'manual', 'valid'),
    (PBTC_ID, 1, 'manual', 'invalid'),
])
def test_create_redeem_req_1_1(token, redeem_fee, custodian_picking, expected):
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4 = portal_user.get_token_balance(token)
    test_redeem_amount = TEST_SETTING_REDEEM_AMOUNT
    PSI_before_test = SUT().get_latest_portal_state_info()
    highest_holding_custodian = PSI_before_test.help_get_highest_holding_token_custodian(token)

    STEP(1.1, 'Create redeem req')
    redeem_req_tx = portal_user.portal_req_redeem_my_token(token, test_redeem_amount,
                                                           redeem_fee=redeem_fee)
    tx_block = redeem_req_tx.subscribe_transaction()
    redeem_fee = redeem_req_tx.params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req_tx.params().get_portal_redeem_req_id()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    INFO(f"""Porting req is created with redeem amount            = {test_redeem_amount} 
                                         redeem fee               = {redeem_fee}
                                         redeem id                = {redeem_id}
                                         tx fee                   = {tx_fee}
                                         tx size                  = {tx_size}
                                         user token bal after req = {portal_user.get_token_balance(token)}
                                         user prv bal after req   = {portal_user.get_prv_balance()}""")
    STEP(2, "Check req status")
    redeem_info = RedeemReqInfo()
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)

    if expected == 'valid':
        assert redeem_info.get_status() == Status.Portal.RedeemStatus.WAITING
        SUT().get_latest_portal_state_info()
    else:
        assert redeem_info.data is None

    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    if expected == 'valid':
        STEP(3.1, "Check requester bal")
        assert tok_bal_be4 - test_redeem_amount == portal_user.get_token_balance(token)

        if custodian_picking == 'auto':
            STEP(3.2, 'Wait 10 min for custodian auto pick')
            WAIT(10.5 * 60)
        else:  # manual matching
            custodian = all_custodians.find_account_by_key(highest_holding_custodian.get_incognito_addr())
            STEP(3.2, f"Self-picking custodian: {l6(custodian.payment_key)}")
            custodian.portal_let_me_take_care_this_redeem(redeem_id)

        STEP(3.3, 'Verify that the request move on to Matched redeem list')
        WAIT(40)
        redeem_info_b4_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
        custodian_b4_re_match = redeem_info_b4_re_match.get_redeem_matching_custodians()[
            0].get_incognito_addr()
        PSI_after_match = SUT().get_latest_portal_state_info()
        matched_redeem_reqs = PSI_after_match.get_redeem_matched_req(token)
        assert redeem_id in [matched_redeem_req.get_redeem_id() for matched_redeem_req in matched_redeem_reqs], \
            f'Not found redeem id {redeem_id} in matched list'

        STEP(3.4, 'Matching again with custodian has no holding token expect error')
        custodian_has_no_holding = PSI_before_test.find_custodian_with_holding_token_amount(token, 0)
        if custodian_has_no_holding is None:
            WARNING("There's no custodian with 0 holding token")
        else:
            poor_custodian = all_custodians.find_account_by_key(custodian_has_no_holding.get_incognito_addr())
            matching_tx = poor_custodian.portal_let_me_take_care_this_redeem(redeem_id, do_assert=False)
            assert RedeemMatchingInfo().get_matching_info_by_tx(matching_tx.get_tx_id()).is_rejected()

        STEP(3.5, f'Make sure matched custodian must not change')
        redeem_info_af_re_match = redeem_info.get_redeem_status_by_redeem_id(redeem_id)
        custodian_af_re_match = redeem_info_af_re_match.get_redeem_matching_custodians()[
            0].get_incognito_addr()
        assert custodian_af_re_match == custodian_b4_re_match

        STEP(4, 'Custodian send BNB to user')
        SUT().get_latest_portal_state_info()
        redeem_info.get_redeem_status_by_redeem_id(redeem_id)
        custodian_incognito_addr = redeem_info.get_redeem_matching_custodians()[0].get_incognito_addr()
        memo = (redeem_id, redeem_info.get_redeem_matching_custodians()[0].get_incognito_addr())
        send_amount = test_redeem_amount // 10
        custodian = all_custodians.find_account_by_key(custodian_incognito_addr)
        send_public_token_tx = custodian.send_public_token(token, send_amount, portal_user, cli_pass_phrase, memo)

        STEP(5, 'Submit proof to request unlock collateral')
        proof = send_public_token_tx.build_proof()
        custodian_account = all_custodians.find_account_by_key(
            redeem_info.get_redeem_matching_custodians()[0].get_incognito_addr())

        custodian_status_after_req = custodian_account.portal_get_my_custodian_info()
        locked_collateral_before = custodian_status_after_req.get_locked_collateral(token)
        holding_token_after_req = custodian_status_after_req.get_holding_token_amount(token)
        sum_waiting_porting_req_lock_collateral = custodian_account.portal_sum_my_waiting_porting_req_locked_collateral(
            token)
        sum_waiting_redeem_req_holding_tok = custodian_account.portal_sum_my_matched_redeem_req_holding_token(token)
        estimated_unlock_collateral = \
            test_redeem_amount * (locked_collateral_before - sum_waiting_porting_req_lock_collateral) // (
                    holding_token_after_req + test_redeem_amount + sum_waiting_redeem_req_holding_tok)
        INFO(f"""Status before req unlock collateral:
                    redeem amount     = {test_redeem_amount}
                    locked collateral = {locked_collateral_before}
                    holding token     = {holding_token_after_req}
                    sum waiting colla = {sum_waiting_porting_req_lock_collateral}
                    sum holding token = {sum_waiting_redeem_req_holding_tok} 
                    estimated unlock  = {estimated_unlock_collateral}""")
        unlock_collateral_tx = custodian_account.portal_req_unlock_collateral(token, test_redeem_amount, redeem_id,
                                                                              proof)
        unlock_collateral_tx.subscribe_transaction()

        unlock_collateral_req_info = UnlockCollateralReqInfo()
        unlock_collateral_req_info.get_unlock_collateral_req_stat(unlock_collateral_tx.get_tx_id())

        assert unlock_collateral_req_info.get_status() == Status.Portal.UnlockCollateralReqStatus.ACCEPTED

        STEP(6, 'Wait 60s for collateral to be unlocked then verify custodian collateral')
        WAIT(60)
        custodian_status_after_req = custodian_account.portal_get_my_custodian_info()
        locked_collateral_after = custodian_status_after_req.get_locked_collateral(token)
        holding_token_after = custodian_status_after_req.get_holding_token_amount(token)

        INFO(f"""Status after req unlock collateral:
                            redeem amount     = {test_redeem_amount}
                            locked collateral = {locked_collateral_after}
                            holding token     = {holding_token_after}
                            unlock amount     = {unlock_collateral_req_info.get_unlock_amount()}""")
        assert locked_collateral_before - locked_collateral_after == estimated_unlock_collateral, \
            'wrong unlock collateral'

    else:
        STEP(3, "Redeem req reject, wait 60s to return token but not tx and redeem fee. Check requester bal")
        WAIT(60)
        assert tok_bal_be4 == portal_user.get_token_balance(token)
        assert prv_bal_be4 - tx_fee - redeem_fee == portal_user.get_prv_balance()


@pytest.mark.parametrize('token', [
    PBNB_ID,
    PBTC_ID,
])
def test_create_redeem_req_1_n(token):
    STEP(0, "before test")

    PSI_before_test = SUT().get_latest_portal_state_info()
    highest_holding_token_custodian_in_pool = PSI_before_test.help_get_highest_holding_token_custodian(token)
    pbnb_rate = PSI_before_test.get_portal_rate(token)
    prv_rate = PSI_before_test.get_portal_rate(PRV_ID)
    redeem_amount = highest_holding_token_custodian_in_pool.get_holding_token_amount(token) + 1

    estimated_redeem_fee = PortalHelper.cal_portal_portal_fee(redeem_amount, pbnb_rate, prv_rate)

    custodian_account_list_of_this_req = []

    # if portal_user.get_prv_balance() < coin(5):
    #     COIN_MASTER.send_prv_to(portal_user, coin(5) - portal_user.get_prv_balance_cache(),
    #                             privacy=0).subscribe_transaction()
    #     portal_user.wait_for_balance_change(prv_token_id, portal_user.get_prv_balance_cache())

    prv_bal_be4_test = portal_user.get_prv_balance()
    tok_bal_be4_test = portal_user.get_token_balance(token)

    STEP(1.1, 'Create redeem req')
    redeem_req_tx = portal_user.portal_req_redeem_my_token(token, redeem_amount)
    tx_block = redeem_req_tx.subscribe_transaction()
    redeem_fee = redeem_req_tx.params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req_tx.params().get_portal_redeem_req_id()
    PSI_after_porting_req = SUT().get_latest_portal_state_info()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert prv_bal_be4_test - redeem_fee - tx_fee == portal_user.get_prv_balance()

    INFO(f"""Porting req is created with redeem amount            = {redeem_amount} 
                                             redeem fee               = {redeem_fee}
                                             redeem id                = {redeem_id}
                                             tx fee                   = {tx_fee}
                                             tx size                  = {tx_size}
                                             user token bal after req = {portal_user.get_token_balance(token)}
                                             user prv bal after req   = {portal_user.get_prv_balance()}""")
    assert estimated_redeem_fee == redeem_fee

    STEP(2, "Check req status")
    redeem_req_info = RedeemReqInfo()
    redeem_req_info.get_redeem_status_by_redeem_id(redeem_id)
    if redeem_req_info.is_none():
        INFO("No matching custodian")
        assert False

    num_of_custodian_for_this_req = len(redeem_req_info.get_redeem_matching_custodians())
    assert redeem_req_info.get_status() == Status.Portal.RedeemStatus.WAITING
    assert prv_bal_be4_test - redeem_fee - tx_fee == portal_user.get_prv_balance()
    assert num_of_custodian_for_this_req >= 2 and INFO(
        f'This redeem req require {num_of_custodian_for_this_req} custodians')

    STEP(3, "Check requester bal")
    assert tok_bal_be4_test - redeem_amount == portal_user.get_token_balance(token)

    STEP(4, 'Custodian send BNB to user')
    send_public_token_txs = {}
    custodians_info_of_req = redeem_req_info.get_redeem_matching_custodians()
    for custodian_info in custodians_info_of_req:
        memo = (redeem_id, custodian_info.get_incognito_addr())
        custodian_remote_address = custodian_info.get_remote_address()
        custodian_acc = all_custodians.find_account_by_key(custodian_info.get_incognito_addr())
        amount_to_send = custodian_info.get_amount()
        if amount_to_send < 10:
            WARNING(f"Amount of BNB to send from custodian is {amount_to_send} < 10")
            amount_to_send = 10
        send_public_token_tx = custodian_acc.send_public_token(token, amount_to_send, portal_user, cli_pass_phrase,
                                                               memo)
        send_public_token_txs[custodian_remote_address] = send_public_token_tx

    STEP(5, 'Submit proofs to request unlock collateral')
    sum_estimated_unlock_collateral = 0
    unlock_collateral_txs = []
    for bnb_addr in send_public_token_txs.keys():
        INFO(f'=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n'
             f'Custodian submit proof: {bnb_addr}')
        send_public_token_tx = send_public_token_txs[bnb_addr]
        proof = send_public_token_tx.build_proof()
        # find custodian which has remote addr = bnb_addr
        custodian_info = None
        for custodian_info in redeem_req_info.get_redeem_matching_custodians():
            if custodian_info.get_remote_address() == bnb_addr:
                break

        custodian_account = all_custodians.find_account_by_key(custodian_info.get_incognito_addr())
        redeem_amount_of_this_custodian = custodian_info.get_amount()
        custodian_account_list_of_this_req.append(custodian_account)
        custodian_status_after_redeem_req = PSI_after_porting_req.get_custodian_info_in_pool(custodian_account)
        locked_collateral_before = custodian_status_after_redeem_req.get_locked_collateral(token)
        holding_token_before_test = custodian_status_after_redeem_req.get_holding_token_amount(token)
        sum_waiting_porting_req_lock_collateral_before_test = \
            PSI_before_test.sum_holding_token_matched_redeem_req(token, custodian_account)
        sum_waiting_redeem_req_holding_tok = custodian_account.portal_sum_my_matched_redeem_req_holding_token(token)
        estimated_unlock_collateral_of_1_custodian = redeem_amount_of_this_custodian * (
                locked_collateral_before - sum_waiting_porting_req_lock_collateral_before_test) // (
                                                             holding_token_before_test + sum_waiting_redeem_req_holding_tok)
        custodian_bnb_send_amount = redeem_req_info.get_custodian(custodian_account).get_amount()
        INFO(f"""Status before req unlock collateral of {l6(custodian_info.get_incognito_addr())}:
                redeem amount          = {redeem_amount_of_this_custodian}
                locked collateral      = {locked_collateral_before}
                holding token          = {holding_token_before_test}
                sum waiting collateral = {sum_waiting_porting_req_lock_collateral_before_test}
                sum holding token      = {sum_waiting_redeem_req_holding_tok} 
                estimated unlock       = {estimated_unlock_collateral_of_1_custodian}""")
        unlock_collateral_tx = custodian_account.portal_req_unlock_collateral(token, custodian_bnb_send_amount,
                                                                              redeem_id,
                                                                              proof)
        unlock_collateral_tx.subscribe_transaction()
        unlock_collateral_txs.append(unlock_collateral_tx)
        sum_estimated_unlock_collateral += estimated_unlock_collateral_of_1_custodian

    for tx in unlock_collateral_txs:
        unlock_collateral_req_info = UnlockCollateralReqInfo()
        unlock_collateral_req_info.get_unlock_collateral_req_stat(tx.get_tx_id())
        assert unlock_collateral_req_info.get_status() == Status.Portal.UnlockCollateralReqStatus.ACCEPTED

    STEP(6, 'Wait 60s for collateral to be unlocked then verify custodian collateral')
    WAIT(60)
    sum_actual_unlock_collateral = 0
    sum_delta_holding_token = 0
    for custodian_account in custodian_account_list_of_this_req:
        custodian_status_latest = custodian_account.portal_get_my_custodian_info()
        locked_collateral_latest = custodian_status_latest.get_locked_collateral(token)
        holding_token_latest = custodian_status_latest.get_holding_token_amount(token)

        custodian_status_before = PSI_before_test.get_custodian_info_in_pool(custodian_account)
        locked_collateral_before = custodian_status_before.get_locked_collateral(token)
        holding_token_before = custodian_status_before.get_holding_token_amount(token)

        unlock_collateral_amount = locked_collateral_before - locked_collateral_latest
        release_token_amount = holding_token_before - holding_token_latest
        INFO(f"""Status after req unlock collateral: {l6(custodian_account.payment_key)}
                                           redeem amount     = {redeem_amount}
                                           locked collateral = {locked_collateral_latest}
                                           holding token     = {holding_token_latest}
                                           unlock amount     = {unlock_collateral_amount}""")
        sum_actual_unlock_collateral += unlock_collateral_amount
        sum_delta_holding_token += release_token_amount

    assert sum_actual_unlock_collateral == sum_estimated_unlock_collateral
    assert sum_delta_holding_token == redeem_amount


@pytest.mark.parametrize('token', [
    PBNB_ID,
    PBTC_ID,
])
def test_redeem_req_expired(token):
    """
    TimeOutCustodianReturnPubToken must be set to 30min or less
    :return:
    """
    user_prv_bal_be4_test = portal_user.get_prv_balance()
    user_tok_bal_be4_test = portal_user.get_token_balance(token)
    test_redeem_amount = 10

    STEP(1.1, 'Create redeem req')
    redeem_req = portal_user.portal_req_redeem_my_token(token, test_redeem_amount)
    tx_block = redeem_req.subscribe_transaction()
    redeem_fee = redeem_req.params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req.params().get_portal_redeem_req_id()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert user_prv_bal_be4_test - redeem_fee - tx_fee == portal_user.get_prv_balance()

    INFO(f"""Porting req is created with redeem amount            = {test_redeem_amount} 
                                            redeem fee               = {redeem_fee}
                                            redeem id                = {redeem_id}
                                            tx fee                   = {tx_fee}
                                            tx size                  = {tx_size}
                                            user token bal after req = {portal_user.get_token_balance(token)}
                                            user prv bal after req   = {portal_user.get_prv_balance()}""")

    STEP(2, "Check req status")
    redeem_info = RedeemReqInfo()
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)

    if redeem_info.is_none():
        assert False, 'No matching custodian found'

    assert redeem_info.get_status() == Status.Portal.RedeemStatus.WAITING
    assert user_prv_bal_be4_test - redeem_fee - tx_fee == portal_user.get_prv_balance()

    STEP(3, "Check requester bal")
    assert user_tok_bal_be4_test - test_redeem_amount == portal_user.get_token_balance(token)

    STEP(4, f'Wait {ChainConfig.Portal.REQ_TIME_OUT + 0.5} min for the req to be expired')
    WAIT(ChainConfig.Portal.REQ_TIME_OUT + 0.5)

    STEP(5, "Check req status")
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    assert redeem_info.get_status() == Status.Portal.RedeemStatus.LIQUIDATED

    STEP(6, "Must return ptoken to user")
    assert user_tok_bal_be4_test == portal_user.get_token_balance(token)

    STEP(7, "No return any fee (tx and portal fee)")
    assert user_prv_bal_be4_test - tx_fee - redeem_fee == portal_user.get_prv_balance()

# def test_redeem_from_liquidation_pool():
#     portal_user.portalrede
