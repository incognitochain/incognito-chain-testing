import pytest

from IncognitoChain.Configs.Constants import PBNB_ID, PortalPortingStatusByPortingId, PortalPortingStatusByTxId, \
    PortalPtokenReqStatus, PRV_ID, coin
from IncognitoChain.Drivers.BnbCli import BnbCli, encode_porting_memo, build_bnb_proof
from IncognitoChain.Helpers.Logging import STEP, INFO, WARNING
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import PortingReqInfo, PTokenReqInfo
from IncognitoChain.TestCases.Portal import portal_user, portal_user_remote_addr, bnb_pass_phrase, \
    TEST_SETTING_PORTING_AMOUNT, all_custodians, big_collateral, fat_custodian_prv, big_bnb_rate, big_porting_amount, \
    init_portal_rate, fat_custodian, TEST_SETTING_DEPOSIT_AMOUNT, PORTAL_REQ_TIME_OUT

n = 'n'


def setup_module():
    INFO("Check if custodian need to add more collateral")
    portal_state = SUT.full_node.get_latest_portal_state()

    for cus in all_custodians.keys():
        cus_stat = cus.portal_get_my_custodian_info(portal_state)

        if cus_stat is None:
            INFO(f'{l6(cus.payment_key)} is not yet custodian, make him one')
            cus.portal_add_collateral(TEST_SETTING_DEPOSIT_AMOUNT, PBNB_ID,
                                      all_custodians[cus]).subscribe_transaction()
        elif cus_stat.get_free_collateral() < TEST_SETTING_DEPOSIT_AMOUNT / 10:
            free_collateral = cus_stat.get_free_collateral()
            INFO(f'{l6(cus.payment_key)} free collateral = {free_collateral} <= {TEST_SETTING_DEPOSIT_AMOUNT} / 10,'
                 f' deposit a bit more of collateral')
            cus.portal_add_collateral(TEST_SETTING_DEPOSIT_AMOUNT - free_collateral, PBNB_ID,
                                      all_custodians[cus]).subscribe_transaction()
        else:
            INFO(f'{l6(cus.payment_key)} '
                 f'{TEST_SETTING_DEPOSIT_AMOUNT} / 10 <= total collateral = {cus_stat.get_total_collateral()} '
                 f'which is fine')


@pytest.mark.parametrize("porting_amount,porting_fee,num_of_custodian,desired_status", [
    # 1 custodian
    # (TEST_SETTING_PORTING_AMOUNT, None, 1, "valid"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, None, 1, "expire"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, None, 1, "liquidate"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, 1, 1, "invalid"),
    # (big_porting_amount, None, 1, "valid"),  # this test should be run alone
    # n custodian
    (TEST_SETTING_PORTING_AMOUNT, None, n, "valid"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, None, n, "expire"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, None, n, "liquidate"),  # None means auto calculate fee
    # (TEST_SETTING_PORTING_AMOUNT, 1, n, "invalid"),

])
def test_create_porting_req_1_1(porting_amount, porting_fee, num_of_custodian, desired_status):
    STEP(0, "Preparation before test")
    remote_receiver_dict = {}
    portal_state_info_before_test = SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4_test = portal_user.get_token_balance(PBNB_ID)
    pbnb_rate = portal_state_info_before_test.get_portal_rate(PBNB_ID)
    prv_rate = portal_state_info_before_test.get_portal_rate(PRV_ID)
    estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, pbnb_rate, prv_rate)
    if num_of_custodian == n:
        ps = SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
        highest_free_collateral_in_pool = ps.help_get_highest_free_collateral_custodian().get_free_collateral()
        pbnb_rate = ps.get_portal_rate(PBNB_ID)
        prv_rate = ps.get_portal_rate(PRV_ID)
        porting_amount = PortalHelper.cal_token_amount_from_collateral(highest_free_collateral_in_pool, pbnb_rate,
                                                                       prv_rate) + 10
        estimated_porting_fee = PortalHelper.cal_portal_portal_fee(porting_amount, pbnb_rate, prv_rate)
    if porting_amount == big_porting_amount:  # spacial case, porting large amount, send more prv to custodian and add
        prepare_fat_custodian()
        # create new rate:
        create_rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(big_bnb_rate).subscribe_transaction()
        assert create_rate_tx.get_error_msg() is None, 'fail to create rate'
        # wait for new rate to take effect
        SUT.full_node.help_wait_till_next_epoch()
        # re-estimate porting fee
        estimated_porting_fee = PortalHelper.cal_portal_portal_fee(big_porting_amount, big_bnb_rate[PBNB_ID],
                                                                   init_portal_rate[PRV_ID])
        pbnb_rate = portal_state_info_before_test.get_portal_rate(PBNB_ID)
        prv_rate = portal_state_info_before_test.get_portal_rate(PRV_ID)

    if portal_user.get_prv_balance() < estimated_porting_fee:
        COIN_MASTER.send_prv_to(portal_user,
                                estimated_porting_fee - portal_user.get_prv_balance_cache() + coin(
                                    1)).subscribe_transaction()
        prv_bal_be4 = portal_user.wait_for_balance_change(current_balance=prv_bal_be4)

    STEP(1, f"Create a {desired_status} porting request")
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
    if desired_status == 'valid':
        assert estimated_porting_fee == porting_fee

    STEP(2, "Check req status by Tx id")
    porting_req_info = PortingReqInfo().get_porting_req_by_tx_id(tx_id)
    if porting_req_info.is_none():
        WAIT(40)
        porting_req_info.get_porting_req_by_tx_id(tx_id)

    if desired_status != 'invalid':  # desired_status == valid or liquidate
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.ACCEPTED
    else:  # case req is invalid, reject
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.REJECTED

    STEP(2.2, "Check req status by req id")
    if desired_status != 'invalid':  # desired_status == valid or liquidate
        porting_req_info.get_porting_req_by_porting_id(porting_id)
        assert porting_req_info.get_status() == PortalPortingStatusByPortingId.WAITING
    else:
        pass
    estimated_lock_collateral = PortalHelper.cal_lock_collateral(porting_amount, pbnb_rate,
                                                                 prv_rate)

    if desired_status == 'liquidate':
        STEP(2.3, "Change rate to make the req liquidated, then wait for the rate to apply")
        one_of_custodians = porting_req_info.get_custodians()[0]
        one_of_amount = porting_req_info.get_custodian(one_of_custodians).get_amount()
        one_of_collateral = porting_req_info.get_custodian(one_of_custodians).get_locked_collateral()
        future_holding_token = one_of_custodians.get_holding_token_amount(PBNB_ID) + one_of_amount
        future_lock_collateral = one_of_custodians.get_locked_collateral(PBNB_ID) + one_of_collateral
        new_prv_rate = PortalHelper.cal_rate_to_liquidate_collateral(
            future_holding_token, future_lock_collateral, pbnb_rate, prv_rate, 'prv', 1.1)
        liquidate_rate = {PRV_ID: new_prv_rate}
        PORTAL_FEEDER.portal_create_exchange_rate(liquidate_rate)
        SUT.full_node.help_wait_till_next_epoch()

    STEP(3, 'Verify balance')
    assert prv_bal_be4 - tx_fee - porting_fee == portal_user.get_prv_balance()

    if desired_status == 'invalid':
        STEP(4, "Porting req fail, wait 60s to return porting fee (only take tx fee), verify user balance")
        WAIT(60)
        assert portal_user.get_prv_balance() == prv_bal_be4 - tx_fee
    else:  # desired_status == valid or liquidate
        STEP(4, "Check number of custodian")
        num = len(porting_req_info.get_custodians())
        INFO(f"!!! This req require {num} custodians ")
        if num_of_custodian == 1:
            assert num == num_of_custodian
        else:
            assert num >= 2

        STEP(5, 'Send BNB to custodian')
        for custodian_info in porting_req_info.get_custodians():
            bnb_to_send = custodian_info.get_amount()
            if bnb_to_send < 10:
                WARNING(f"Amount of BNB to send to custodian is {bnb_to_send} < 10")
                bnb_to_send = 10
            remote_receiver_dict[custodian_info.get_remote_address()] = bnb_to_send // 10  # pbnb 10^-9, bnb 10^-8

        memo_encoded = encode_porting_memo(porting_req_info.get_porting_id())
        bnb_cli = BnbCli()
        bnb_send_tx = bnb_cli.send_bnb_to_multi(portal_user_remote_addr, remote_receiver_dict, bnb_pass_phrase,
                                                memo_encoded)

        STEP(6, 'Submit proof to request ported token')
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

        STEP(7, 'Verify user balance')
        balance_after_req = portal_user.wait_for_balance_change(PBNB_ID, balance_before_req_ported_token)
        assert balance_after_req == balance_before_req_ported_token + porting_amount
        assert tok_bal_be4_test == balance_before_req_ported_token

        # calculate lock collateral

        STEP(8, f'Verify lock collateral amount')
        sum_liquidate_collateral = 0
        sum_liquidate_token = 0
        portal_state_info_porting_completed = SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()

        for custodian in porting_req_info.get_custodians():
            # breakpoint()
            # get lock collateral of custodian before test
            custodian_info_before = portal_state_info_before_test.get_custodian_info_in_pool(custodian)
            lock_collateral_before = custodian_info_before.get_locked_collateral(PBNB_ID)
            total_collateral_before = custodian_info_before.get_total_collateral()
            free_collateral_before = custodian_info_before.get_free_collateral()
            collateral_real = porting_req_info.get_custodian(custodian_info_before).get_locked_collateral()
            bnb_rate_be4 = portal_state_info_before_test.get_portal_rate(PBNB_ID)
            prv_rate_be4 = portal_state_info_before_test.get_portal_rate(PRV_ID)

            # get lock collateral of custodian after test
            custodian_info_after = portal_state_info_porting_completed.get_custodian_info_in_pool(custodian)
            lock_collateral_after = custodian_info_after.get_locked_collateral(PBNB_ID)
            total_collateral_after = custodian_info_after.get_total_collateral()
            free_collateral_after = custodian_info_after.get_free_collateral()
            bnb_rate_after = portal_state_info_porting_completed.get_portal_rate(PBNB_ID)
            prv_rate_after = portal_state_info_porting_completed.get_portal_rate(PRV_ID)

            amount = porting_req_info.get_custodian(custodian).get_amount()
            collateral = PortalHelper.cal_lock_collateral(amount, pbnb_rate, prv_rate)
            INFO(f'custodian incognito addr    = {l6(custodian.get_incognito_addr())}\n'
                 f'\t\t lock collateral before-after test  = {lock_collateral_before}-{lock_collateral_after}\n'
                 f'\t\t total collateral before-after test = {total_collateral_before}-{total_collateral_after}\n'
                 f'\t\t free collateral before-after test  = {free_collateral_before}-{free_collateral_after}\n'
                 f'\t\t estimated-real lock collateral     = {collateral}-{collateral_real}\n'
                 f'\t\t prv rate before-after              = {bnb_rate_be4}-{bnb_rate_after}\n'
                 f'\t\t pbnb rate before-after             = {prv_rate_be4}-{prv_rate_after}\n'
                 f'\t\t token amount                       = {amount}')
            porting_req_collateral = porting_req_info.get_custodian(custodian).get_locked_collateral()
            if desired_status == 'valid':
                INFO(f'Real lock amount           {porting_req_collateral}')
                INFO(f'Real estimated lock amount {estimated_lock_collateral}')
                assert lock_collateral_after - lock_collateral_before == estimated_lock_collateral
                assert lock_collateral_after - lock_collateral_before == porting_req_collateral
            else:  # case liquidate
                # breakpoint()
                if custodian_info_before.shall_i_be_liquidize_with_new_rate(PBNB_ID, pbnb_rate, new_prv_rate, amount,
                                                                            collateral):
                    # breakpoint()
                    INFO('Verify custodian collateral and holding token')
                    estimated_liquidated_amount, return_collateral = portal_state_info_before_test. \
                        estimate_liquidation_of_custodian(custodian_info_before, PBNB_ID, pbnb_rate, new_prv_rate,
                                                          amount, collateral)

                    INFO(f'Liquidated amount           {total_collateral_before - total_collateral_after}')
                    INFO(f'Estimated liquidated amount {estimated_liquidated_amount}')

                    # assert lock_collateral_after == lock_collateral_before, "Wrong lock collateral"
                    assert total_collateral_after == total_collateral_before - estimated_liquidated_amount, \
                        "Wrong total collateral"
                    assert free_collateral_after == free_collateral_before - estimated_liquidated_amount, \
                        "wrong return collateral"
                    sum_liquidate_collateral += estimated_liquidated_amount
                    sum_liquidate_token += amount
                else:
                    INFO("This custodian will not be liquidated")

        if desired_status == 'liquidate':
            STEP(9, "Check liquidation pool")
            liquidation_pool_before_req = portal_state_info_before_test.get_liquidation_pool()
            liquidation_pool_after_liquidate = portal_state_info_porting_completed.get_liquidation_pool()
            liquidated = liquidation_pool_after_liquidate - liquidation_pool_before_req
            collateral_added_to_pool = liquidated.get_collateral_amount_of_token(PBNB_ID)
            token_added_too_pool = liquidated.get_public_token_amount_of_token(PBNB_ID)
            assert collateral_added_to_pool == sum_liquidate_collateral
            assert token_added_too_pool == sum_liquidate_token


@pytest.mark.parametrize("num_of_custodian", [
    1,
    'n',
])
def test_porting_req_expired(num_of_custodian):
    STEP(0, "before test")
    portal_state_info_before_test = SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
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
    estimated_collateral = PortalHelper.cal_lock_collateral(porting_amount, pbnb_rate, prv_rate)

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
    if porting_req_info_after_req.is_none():
        WAIT(40)
        porting_req_info_after_req.get_porting_req_by_tx_id(tx_id)

    assert porting_req_info_after_req.get_status() == PortalPortingStatusByTxId.ACCEPTED

    STEP(2.2, "Check req status by req id")
    porting_req_info_after_req.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info_after_req.get_status() == PortalPortingStatusByPortingId.WAITING

    STEP(3, 'Verify balance')
    assert user_prv_bal_be4_test - porting_fee - tx_fee == portal_user.get_prv_balance()

    STEP(4, f'Wait {PORTAL_REQ_TIME_OUT + 0.5} for the req to be expired')
    WAIT((PORTAL_REQ_TIME_OUT + 0.5) * 60)
    STEP(5, "Check req status")
    porting_req_info_after_req.get_porting_req_by_porting_id(porting_id)
    assert porting_req_info_after_req.get_status() == PortalPortingStatusByPortingId.EXPIRED

    # todo handle 1_n case
    STEP(6, "Custodian collateral must be unlock")
    custodians_info = porting_req_info_after_req.get_custodians()
    INFO(f'Number of custodian for this req = {len(custodians_info)}')
    if num_of_custodian == 1:
        assert len(custodians_info) == 1
    else:
        assert len(custodians_info) > 1

    portal_state_info_after_expired = SUT.full_node.get_latest_portal_state().get_portal_state_info_obj()
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
