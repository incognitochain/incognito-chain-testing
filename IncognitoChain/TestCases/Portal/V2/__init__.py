from IncognitoChain.Configs.Constants import coin, PBNB_ID, PRV_ID, PBTC_ID
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.PortalHelper import PortalMath
from IncognitoChain.Helpers.TestHelper import ChainHelper
from IncognitoChain.Objects.AccountObject import PORTAL_FEEDER, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Portal import all_custodians, TEST_SETTING_DEPOSIT_AMOUNT

init_portal_rate = {
    PRV_ID: '83159',
    PBNB_ID: '208525400',
    PBTC_ID: '105873200000'
}


# special case
def find_fat_custodian(psi=None, expected_collateral_amount_to_be=None):
    if expected_collateral_amount_to_be is None:
        expected_collateral_amount_to_be = big_collateral
    if psi is None:
        psi = SUT().get_latest_portal_state_info()
    fat_custodian = all_custodians[0]
    for cus in all_custodians[1:]:
        fat_top_up_amount = expected_collateral_amount_to_be - psi.get_custodian_info_in_pool(
            fat_custodian).get_free_collateral()
        cus_top_up_amount = expected_collateral_amount_to_be - psi.get_custodian_info_in_pool(cus).get_free_collateral()

        if cus_top_up_amount < fat_top_up_amount:
            fat_custodian = cus
    INFO(f' FAT CUSTODIAN \n'
         f'{fat_custodian}')
    return fat_custodian


big_collateral = fat_custodian_prv = 1
big_porting_amount = coin(10)
big_rate = {PBNB_ID: '105873200000',
            PBTC_ID: '105873200000'}


# 19097127190081650
# 37772966455153490
# 37772966455153487

def setup_module():
    INFO()
    INFO('SETUP TEST MODULE, TOP UP PRV FOR CUSTODIAN AND PORTAL FEEDER')
    COIN_MASTER.top_him_up_prv_to_amount_if(TEST_SETTING_DEPOSIT_AMOUNT * 4, TEST_SETTING_DEPOSIT_AMOUNT * 4 + coin(1),
                                            all_custodians)
    COIN_MASTER.top_him_up_prv_to_amount_if(100, coin(1), PORTAL_FEEDER)
    INFO("Check rate")
    PSI_current = SUT().get_latest_portal_state_info()
    for k, v in init_portal_rate.items():
        if PSI_current.get_portal_rate(k) != int(v):
            INFO("Create portal rate")
            create_rate_tx = PORTAL_FEEDER.portal_create_exchange_rate(init_portal_rate)
            create_rate_tx.expect_no_error()
            create_rate_tx.subscribe_transaction()
            ChainHelper.wait_till_next_beacon_height(2)
            break

    global big_collateral, fat_custodian_prv

    big_collateral = PortalMath.cal_lock_collateral(big_porting_amount, big_rate[PBNB_ID],
                                                    init_portal_rate[PRV_ID])
    fat_custodian_prv = big_collateral + coin(1)


def noteardown_module():
    INFO_HEADLINE(f'TEST MODULE TEAR DOWN: Withdraw all free collateral')
    PSI = SUT().get_latest_portal_state_info()
    for cus in all_custodians:
        cus_stat = PSI.get_custodian_info_in_pool(cus)
        if cus_stat is not None:
            cus.portal_withdraw_my_collateral(cus_stat.get_free_collateral()).subscribe_transaction()

    # clean up redeem special case: big fat custodian send back prv to COIN_MASTER and return rate back to default
    # if not fat_custodian.is_empty:
    #     assert fat_custodian.portal_withdraw_my_collateral(big_collateral).get_error_msg() is None, "must redeem first"
    #     fat_custodian.send_prv_to(COIN_MASTER, fat_custodian.get_prv_balance() - coin(2),
    #                               privacy=0).subscribe_transaction()
    #     PORTAL_FEEDER.create_portal_exchange_rate(init_portal_rate)


def setup_function():
    INFO_HEADLINE('Portal Info before test')
    SUT().get_latest_portal_state_info().print_state()
