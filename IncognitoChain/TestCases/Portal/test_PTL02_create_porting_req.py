import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PRV_ID, coin, PBTC_ID, Status, ChainConfig
from IncognitoChain.Helpers.Logging import STEP, INFO, WARNING, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import PortingReqInfo, PTokenReqInfo
from IncognitoChain.TestCases.Portal import portal_user, cli_pass_phrase, \
    TEST_SETTING_PORTING_AMOUNT, custodian_remote_addr, big_collateral, fat_custodian_prv, big_rate, \
    big_porting_amount, init_portal_rate, fat_custodian, TEST_SETTING_DEPOSIT_AMOUNT

n = 'n'


def setup_module():
    INFO("Check if custodian need to add more collateral")
    PSI = SUT.full_node.get_latest_portal_state_info()
    deposit_amount = 0
    COIN_MASTER.top_him_up_prv_to_amount_if(deposit_amount * 2, deposit_amount * 2 + 1,
                                            custodian_remote_addr.get_accounts())

    for cus in custodian_remote_addr.get_accounts():
        cus_stat = cus.portal_get_my_custodian_info(PSI)

        if cus_stat is None:
            INFO(f'{l6(cus.payment_key)} is not yet custodian, make him one')
            deposit_amount = TEST_SETTING_DEPOSIT_AMOUNT
        elif cus_stat.get_free_collateral() < TEST_SETTING_DEPOSIT_AMOUNT / 10:
            free_collateral = cus_stat.get_free_collateral()
            deposit_amount = TEST_SETTING_DEPOSIT_AMOUNT
            INFO(f'{l6(cus.payment_key)} free collateral = {free_collateral} <= {TEST_SETTING_DEPOSIT_AMOUNT} / 10,'
                 f' deposit a bit more of collateral')
        else:
            deposit_amount = 0
            INFO(f'{l6(cus.payment_key)} '
                 f'{TEST_SETTING_DEPOSIT_AMOUNT} / 10 <= total collateral = {cus_stat.get_total_collateral()} '
                 f'which is fine')

        if deposit_amount > 0:
            try:
                cus.portal_add_collateral(deposit_amount, PBNB_ID).subscribe_transaction()
                cus.portal_add_collateral(deposit_amount, PBNB_ID).subscribe_transaction()
            except:
                pass

    if deposit_amount > 0:
        INFO_HEADLINE("WAIT FOR THE DEPOSIT TO TAKE EFFECT")
        SUT.full_node.help_wait_till_next_epoch()


@pytest.mark.parametrize("token, porting_amount, user, porting_fee, num_of_custodian, desired_status",
                         [  # fee = None means auto calculate fee
                             # big amount porting test should be run alone
                             # BNB
                             # 1 custodian
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "valid"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "expire"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "liquidate"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, 1, 1, "invalid"),
                             (PBNB_ID, big_porting_amount, None, 1, portal_user, "valid"),
                             # n custodian
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "valid"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "expire"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "liquidate"),
                             (PBNB_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, 1, n, "invalid"),
                             #
                             # BTC
                             # 1 custodian
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "valid"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "expire"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, 1, "liquidate"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, 1, 1, "invalid"),
                             (PBTC_ID, big_porting_amount, None, 1, portal_user, "valid"),
                             # n custodian
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "valid"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "expire"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, None, n, "liquidate"),
                             (PBTC_ID, TEST_SETTING_PORTING_AMOUNT, portal_user, 1, n, "invalid"),

                         ])
def test_create_porting_req_1_1(token, porting_amount, user, porting_fee, num_of_custodian, desired_status):
    STEP(0, "Preparation before test")
    remote_receiver_dict = {}
    PSI_before_test = SUT.full_node.get_latest_portal_state_info()
    prv_bal_be4_test = user.get_prv_balance()
    tok_bal_be4_test = user.get_token_balance(token)
    tok_rate = PSI_before_test.get_portal_rate(token)
    prv_rate = PSI_before_test.get_portal_rate(PRV_ID)
    estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, tok_rate, prv_rate)
    if num_of_custodian == n:
        ps = SUT.full_node.get_latest_portal_state_info()
        highest_free_collateral_in_pool = ps.help_get_highest_free_collateral_custodian().get_free_collateral()
        tok_rate = ps.get_portal_rate(token)
        prv_rate = ps.get_portal_rate(PRV_ID)
        porting_amount = PortalHelper.cal_token_amount_from_collateral(highest_free_collateral_in_pool, tok_rate,
                                                                       prv_rate) + 10
        estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, tok_rate, prv_rate)
    if porting_amount == big_porting_amount:  # spacial case, porting large amount, send more prv to custodian and add
        prepare_fat_custodian()
        # create new rate:
        create_rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(big_rate).subscribe_transaction()
        assert create_rate_tx.get_error_msg() is None, 'fail to create rate'
        # wait for new rate to take effect
        SUT.full_node.help_wait_till_next_epoch()
        # re-estimate porting fee
        estimated_porting_fee = PortalHelper.cal_portal_portal_fee(big_porting_amount, big_rate[token],
                                                                   init_portal_rate[PRV_ID])
        PSI_before_test = SUT.full_node.get_latest_portal_state_info()
        tok_rate = PSI_before_test.get_portal_rate(token)
        prv_rate = PSI_before_test.get_portal_rate(PRV_ID)

    if user.get_prv_balance() < estimated_porting_fee:
        COIN_MASTER.send_prv_to(user,
                                estimated_porting_fee - user.get_prv_balance_cache() + coin(1)).subscribe_transaction()
        prv_bal_be4_test = user.wait_for_balance_change(from_balance=prv_bal_be4_test)

    STEP(1, f"Create a {desired_status} porting request")
    porting_req = user.portal_create_porting_request(token, porting_amount, porting_fee=porting_fee)
    porting_id = porting_req.params().get_portal_register_id()
    porting_fee = porting_req.params().get_portal_porting_fee()
    tx_block = porting_req.subscribe_transaction()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    tx_id = porting_req.get_tx_id()
    estimated_total_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, tok_rate, prv_rate)
    INFO(f"""Porting req is created with 
            amount                         = {porting_amount}
            porting fee                    = {porting_fee},
            porting id                     = {porting_id}, 
            tx fee                         = {tx_fee}, 
            tx size                        = {tx_size}
            prv bal after req              = {user.get_prv_balance()}
            estimate total lock collateral = {estimated_total_lock_collateral}""")
    STEP(1.2, 'verify porting fee')
    if desired_status == 'valid':
        assert estimated_porting_fee == porting_fee

    STEP(2, "Check req status by Tx id")
    porting_req_info = PortingReqInfo().get_porting_req_by_tx_id(tx_id)

    if desired_status != 'invalid':  # desired_status == valid or liquidate
        assert porting_req_info.get_status() == Status.Portal.PortingStatusByTxId.ACCEPTED
    else:  # case req is invalid, reject
        assert porting_req_info.get_status() == Status.Portal.PortingStatusByTxId.REJECTED

    STEP(3, "Check req status by req id")
    if desired_status != 'invalid':  # desired_status == valid or liquidate
        porting_req_info.get_porting_req_by_porting_id(porting_id)
        assert porting_req_info.get_status() == Status.Portal.PortingStatusByPortingId.WAITING
    else:
        pass
    PSI_after_req = SUT.full_node.get_latest_portal_state_info()
    if desired_status == 'liquidate':
        STEP(3.1, "Change rate to make the req liquidated, then wait for the rate to apply")
        one_of_custodians = porting_req_info.get_custodians()[0]
        one_of_amount = porting_req_info.get_custodian(one_of_custodians).get_amount()
        one_of_collateral = porting_req_info.get_custodian(one_of_custodians).get_locked_collateral()
        future_holding_token = one_of_custodians.get_holding_token_amount(token) + one_of_amount
        future_lock_collateral = one_of_custodians.get_locked_collateral(token) + one_of_collateral
        new_prv_rate = PortalHelper.cal_rate_to_liquidate_collateral(
            future_holding_token, future_lock_collateral, tok_rate, prv_rate, 'prv', 1.1)
        liquidate_rate = {PRV_ID: new_prv_rate}
        PORTAL_FEEDER.portal_create_exchange_rate(liquidate_rate)
        SUT.full_node.help_wait_till_next_epoch()

    if desired_status == 'invalid':
        STEP(4, "Porting req fail, wait 60s to return porting fee (only take tx fee), verify user balance")
        WAIT(60)
        assert user.get_prv_balance() == prv_bal_be4_test - tx_fee
    elif desired_status == 'expire':
        verify_expire_porting(user, porting_id, token, num_of_custodian, PSI_before_test, prv_bal_be4_test, tx_fee,
                              porting_fee)
    else:  # desired_status == valid or liquidate
        STEP(4, "Check number of custodian")
        num = len(porting_req_info.get_custodians())
        INFO(f"!!! This req require {num} custodians ")
        if num_of_custodian == 1:
            assert num == num_of_custodian
        else:
            assert num >= 2

        STEP(5, 'Send Token to custodian')
        for custodian_info in porting_req_info.get_custodians():
            tok_amount_to_send = custodian_info.get_amount()
            if tok_amount_to_send < 10:
                WARNING(f"Amount of token to send to custodian is {tok_amount_to_send} < 10")
                tok_amount_to_send = 10
            remote_receiver_dict[
                custodian_info.get_remote_address()] = tok_amount_to_send // 10  # pbtc,pbnb 10^-9, while btc,bnb 10^-8

        memo = porting_req_info.get_porting_id()
        send_public_token_tx = user.send_public_token_multi(token, remote_receiver_dict, cli_pass_phrase, memo)

        STEP(6, 'Submit proof to request ported token')
        balance_before_req_ported_token = user.get_token_balance(token)
        proof = send_public_token_tx.build_proof()
        req_tx = user.portal_req_ported_ptoken(porting_id, token, porting_amount, proof)
        req_tx.subscribe_transaction()
        WAIT(90)  # wait for the req to be processed
        token_req_info = PTokenReqInfo(req_tx.get_result())
        ported_token_req = token_req_info.get_ptoken_req_by_tx_id(req_tx.get_tx_id())
        ported_token_req_status = ported_token_req.get_status()
        assert ported_token_req_status == Status.Portal.PtokenReqStatus.ACCEPTED, \
            f'Req for ported token is rejected. CODE = {ported_token_req_status}'

        STEP(7, 'Verify user balance')
        balance_after_req = user.wait_for_balance_change(token, balance_before_req_ported_token)
        assert balance_after_req == balance_before_req_ported_token + porting_amount
        assert tok_bal_be4_test == balance_before_req_ported_token

        # calculate lock collateral

        STEP(8, f'Verify lock collateral amount')
        sum_liquidate_collateral = 0
        sum_liquidate_token = 0
        PSI_porting_completed = SUT.full_node.get_latest_portal_state_info()

        for custodian in porting_req_info.get_custodians():
            # get lock collateral of custodian before test
            custodian_info_after_req = PSI_after_req.get_custodian_info_in_pool(custodian)
            lock_collateral_after_req = custodian_info_after_req.get_locked_collateral(token)
            total_collateral_after_req = custodian_info_after_req.get_total_collateral()
            free_collateral_after_req = custodian_info_after_req.get_free_collateral()
            collateral_real = porting_req_info.get_custodian(custodian_info_after_req).get_locked_collateral()
            bnb_rate_be4 = PSI_before_test.get_portal_rate(token)
            prv_rate_be4 = PSI_before_test.get_portal_rate(PRV_ID)

            # get lock collateral of custodian after test
            custodian_info_after = PSI_porting_completed.get_custodian_info_in_pool(custodian)
            lock_collateral_after = custodian_info_after.get_locked_collateral(token)
            total_collateral_after = custodian_info_after.get_total_collateral()
            free_collateral_after = custodian_info_after.get_free_collateral()
            bnb_rate_after = PSI_porting_completed.get_portal_rate(token)
            prv_rate_after = PSI_porting_completed.get_portal_rate(PRV_ID)

            amount = porting_req_info.get_custodian(custodian).get_amount()
            collateral_each_estimate = PortalHelper.cal_lock_collateral(amount, tok_rate, prv_rate)
            INFO('----------------------------------------------------------------------------------------')
            INFO(f'custodian incognito addr    = {l6(custodian.get_incognito_addr())}\n'
                 f'\t\t lock collateral after: req - test  = {lock_collateral_after_req} - {lock_collateral_after}\n'
                 f'\t\t total collateral after: req - test = {total_collateral_after_req} - {total_collateral_after}\n'
                 f'\t\t free collateral after: req - test  = {free_collateral_after_req} - {free_collateral_after}\n'
                 f'\t\t estimated-real lock collateral     = {collateral_each_estimate} - {collateral_real}\n'
                 f'\t\t PBNB rate after: req - test        = {bnb_rate_be4} - {bnb_rate_after}\n'
                 f'\t\t PRV rate after: req - test         = {prv_rate_be4} - {prv_rate_after}\n'
                 f'\t\t token amount                       = {amount}')
            porting_req_collateral = porting_req_info.get_custodian(custodian).get_locked_collateral()
            if desired_status == 'valid':
                custodian_info_before = PSI_before_test.get_custodian_info_in_pool(custodian)
                lock_collateral_before = custodian_info_before.get_locked_collateral(token)
                assert lock_collateral_after - lock_collateral_before == collateral_each_estimate
                assert lock_collateral_after - lock_collateral_before == porting_req_collateral
            else:  # case liquidate
                if PSI_after_req.will_custodian_be_liquidated_with_new_rate(custodian, token, tok_rate,
                                                                            new_prv_rate):
                    INFO(f'Verify custodian {l6(custodian.get_incognito_addr())} collateral and holding token')
                    estimated_liquidated_amount, return_collateral = PSI_porting_completed. \
                        estimate_liquidation_of_custodian(custodian, token, tok_rate, new_prv_rate,
                                                          amount, collateral_each_estimate)

                    INFO(f'Liquidated amount           {total_collateral_after_req - total_collateral_after}')
                    INFO(f'Estimated liquidated amount {estimated_liquidated_amount}')
                    INFO(f'Return collateral           {return_collateral}')

                    # breakpoint()
                    assert collateral_each_estimate == porting_req_collateral, "Wrong lock collateral"
                    assert total_collateral_after == total_collateral_after_req - estimated_liquidated_amount, \
                        "Wrong total collateral"
                    assert free_collateral_after == free_collateral_after_req + return_collateral, \
                        "wrong return collateral"
                    sum_liquidate_collateral += estimated_liquidated_amount
                    sum_liquidate_token += amount
                else:
                    INFO("This custodian will not be liquidated")
            INFO('----------------------------------------------------------------------------------------')

        if desired_status == 'liquidate':
            STEP(9, "Check liquidation pool")
            liquidation_pool_before_req = PSI_before_test.get_liquidation_pool()
            liquidation_pool_after_liquidate = PSI_porting_completed.get_liquidation_pool()
            liquidated = liquidation_pool_after_liquidate - liquidation_pool_before_req
            collateral_added_to_pool = liquidated.get_collateral_amount_of_token(token)
            token_added_too_pool = liquidated.get_public_token_amount_of_token(token)
            assert collateral_added_to_pool == sum_liquidate_collateral and INFO(
                f'Liquidated collateral{collateral_added_to_pool}'), 'wrong liquidate collateral'
            assert token_added_too_pool == sum_liquidate_token and INFO(
                f'Liquidated token {token_added_too_pool}'), 'wrong liquidate token'


@pytest.mark.parametrize("num_of_custodian", [
    1,
    'n',
])
def est_porting_req_expired(num_of_custodian):
    """
    already merged to upper test case, just keep it here for backup,
    might delete this test in the future
    """
    STEP(0, "before test")
    portal_state_info_before_test = SUT.full_node.get_latest_portal_state_info()
    pbnb_rate = portal_state_info_before_test.get_portal_rate(PBNB_ID)
    prv_rate = portal_state_info_before_test.get_portal_rate(PRV_ID)

    if num_of_custodian == 'n':
        custodian_has_highest_free_collateral_in_pool = portal_state_info_before_test. \
            help_get_highest_free_collateral_custodian()
        highest_collateral = custodian_has_highest_free_collateral_in_pool.get_free_collateral()
        porting_amount = PortalHelper.cal_token_amount_from_collateral(highest_collateral, pbnb_rate, prv_rate) + 10

        if portal_user.get_prv_balance() < coin(5):
            COIN_MASTER.send_prv_to(portal_user, coin(5) - portal_user.get_prv_balance_cache(),
                                    privacy=0).subscribe_transaction()
            portal_user.wait_for_balance_change(PRV_ID, portal_user.get_prv_balance_cache())

    else:
        porting_amount = TEST_SETTING_PORTING_AMOUNT
    user_prv_bal_be4_test = portal_user.get_prv_balance()
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
    porting_req_info_after_req = PortingReqInfo()
    porting_req_info_after_req.get_porting_req_by_tx_id(tx_id)

    assert porting_req_info_after_req.get_status() == Status.Portal.PortingStatusByTxId.ACCEPTED

    STEP(2.2, "Check req status by req id")
    porting_req_info_after_req.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info_after_req.get_status() == Status.Portal.PortingStatusByPortingId.WAITING

    STEP(3, 'Verify balance')
    assert user_prv_bal_be4_test - porting_fee - tx_fee == portal_user.get_prv_balance()

    STEP(4, f'Wait {ChainConfig.Portal.REQ_TIME_OUT + 0.5} for the req to be expired')
    WAIT(ChainConfig.Portal.REQ_TIME_OUT + 0.5, 'm')
    STEP(5, "Check req status")
    porting_req_info_after_req.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info_after_req.get_status() == Status.Portal.PortingStatusByPortingId.EXPIRED

    STEP(6, "Custodian collateral must be unlock")
    custodians_info = porting_req_info_after_req.get_custodians()
    INFO(f'Number of custodian for this req = {len(custodians_info)}')
    if num_of_custodian == 1:
        assert len(custodians_info) == 1
    else:
        assert len(custodians_info) > 1

    portal_state_info_after_expired = SUT.full_node.get_latest_portal_state_info()
    for custodian in custodians_info:
        state_before_test = portal_state_info_before_test.get_custodian_info_in_pool(custodian)
        state_after_expire = portal_state_info_after_expired.get_custodian_info_in_pool(custodian)
        INFO(f'Custodian info before: \n{state_before_test}')
        INFO(f'Custodian info after : \n{state_after_expire}')
        assert state_before_test.get_locked_collateral() == state_after_expire.get_locked_collateral()
        assert state_before_test.get_free_collateral() == state_after_expire.get_free_collateral()
        assert state_before_test.get_total_collateral() == state_after_expire.get_total_collateral()
        assert state_before_test.get_holding_token_amount(PBNB_ID) == state_after_expire.get_holding_token_amount(
            PBNB_ID)

    STEP(7, "Verify user balance, porting fee and tx fee will not be returned")
    user_prv_bal_after_test = portal_user.get_prv_balance()
    assert user_prv_bal_be4_test - tx_fee - porting_fee == user_prv_bal_after_test


def prepare_fat_custodian():
    COIN_MASTER.top_him_up_prv_to_amount_if(big_collateral * 2, fat_custodian_prv * 2, fat_custodian)
    # deposit big collateral
    deposit_tx = fat_custodian.portal_make_me_custodian((big_collateral + 1), PBNB_ID,
                                                        custodian_remote_addr.get_remote_addr(fat_custodian))
    deposit_tx.expect_no_error()
    deposit_tx.subscribe_transaction()

    deposit_tx = fat_custodian.portal_make_me_custodian((big_collateral + 1), PBTC_ID,
                                                        custodian_remote_addr.get_remote_addr(fat_custodian))
    deposit_tx.expect_no_error()
    deposit_tx.subscribe_transaction()

    SUT.full_node.help_wait_till_next_epoch()


def verify_expire_porting(user, porting_id, token, num_of_custodian, psi_b4, prv_bal_b4, tx_fee, porting_fee):
    STEP(4, f'Wait {ChainConfig.Portal.REQ_TIME_OUT + 0.5} for the req to be expired')
    WAIT(ChainConfig.Portal.REQ_TIME_OUT + 0.5, 'm')
    STEP(5, "Check req status")
    porting_req_info = PortingReqInfo().get_porting_req_by_porting_id(porting_id)
    assert porting_req_info.get_status() == Status.Portal.PortingStatusByPortingId.EXPIRED

    STEP(6, "Custodian collateral must be unlock")
    custodians_info = porting_req_info.get_custodians()
    INFO(f'Number of custodian for this req = {len(custodians_info)}')
    if num_of_custodian == 1:
        assert len(custodians_info) == 1
    else:
        assert len(custodians_info) > 1

    PSI_after_expired = SUT.full_node.get_latest_portal_state_info()
    for custodian in custodians_info:
        state_before_test = psi_b4.get_custodian_info_in_pool(custodian)
        state_after_expire = PSI_after_expired.get_custodian_info_in_pool(custodian)
        INFO(f'Custodian info before: \n{state_before_test}')
        INFO(f'Custodian info after : \n{state_after_expire}')
        assert state_before_test.get_locked_collateral() == state_after_expire.get_locked_collateral()
        assert state_before_test.get_free_collateral() == state_after_expire.get_free_collateral()
        assert state_before_test.get_total_collateral() == state_after_expire.get_total_collateral()
        assert state_before_test.get_holding_token_amount(token) == state_after_expire.get_holding_token_amount(
            token)

    STEP(7, "Verify user balance, porting fee and tx fee will not be returned")
    user_prv_bal_after_test = user.get_prv_balance()
    assert prv_bal_b4 - tx_fee - porting_fee == user_prv_bal_after_test
