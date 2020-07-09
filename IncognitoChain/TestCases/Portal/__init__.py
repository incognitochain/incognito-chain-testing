from IncognitoChain.Configs.Constants import coin, PBNB_ID, PRV_ID, PBTC_ID
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import l6, PortalHelper
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, COIN_MASTER, SUT, PORTAL_FEEDER
from IncognitoChain.Objects.PortalObjects import PortalStateInfo

portal_user = ACCOUNTS[1]
self_pick_custodian = ACCOUNTS[6]

PORTAL_REQ_TIME_OUT = 60  # minutes
TEST_SETTING_DEPOSIT_AMOUNT = coin(5)
TEST_SETTING_PORTING_AMOUNT = 100
TEST_SETTING_REDEEM_AMOUNT = 10
custodian_remote_address = 'tbnb1d90lad6rg5ldh8vxgtuwzxd8n6rhhx7mfqek38'
portal_user_remote_addr = 'tbnb1zyqrky9zcumc2e4smh3xwh2u8kudpdc56gafuk'
bnb_pass_phrase = '123123Az'
just_another_remote_addr = 'tbnb1hmgztqgx62t3gldsk7n9wt4hxg2mka0fdem3ss'

all_custodians = {
    ACCOUNTS[3]: 'tbnb172pnrmd0409237jwlq5qjhw2s2r7lq6ukmaeke',
    ACCOUNTS[4]: 'tbnb19cmxazhx5ujlhhlvj9qz0wv8a4vvsx8vuy9cyc',
    ACCOUNTS[5]: 'tbnb1n5lrzass9l28djvv7drst53dcw7y9yj4pyvksf',
    self_pick_custodian: custodian_remote_address
}

init_portal_rate = {
    PRV_ID: '83159',
    PBNB_ID: '208525400',
    PBTC_ID: '105873200000'
}

# special case
fat_custodian = Account()
# fat_custodian.get_prv_balance()
big_porting_amount = coin(10)
big_rate = {PBNB_ID: '105873200000',
            PBTC_ID: '105873200000'}
# 19097127190081650
# 37772966455153490
# 37772966455153487

for acc in all_custodians:  # find account which has most PRV
    if fat_custodian.get_prv_balance_cache() is None:
        fat_custodian = acc
    elif acc.get_prv_balance_cache() >= fat_custodian.get_prv_balance_cache():
        fat_custodian = acc
big_collateral = PortalHelper.cal_lock_collateral(big_porting_amount, big_rate[PBNB_ID],
                                                  init_portal_rate[PRV_ID])
fat_custodian_prv = big_collateral + coin(1)


def find_custodian_account_by_incognito_addr(incognito_addr):
    for acc in all_custodians.keys():
        if acc.payment_key == incognito_addr:
            return acc
    return None


def setup_module():
    INFO()
    INFO('SETUP TEST MODULE')
    INFO("Check rate")
    PSI_current = SUT.full_node.get_latest_portal_state_info()
    for k, v in init_portal_rate.items():
        if PSI_current.get_portal_rate(k) != int(v):
            INFO("Create portal rate")
            PORTAL_FEEDER.portal_create_exchange_rate(init_portal_rate).subscribe_transaction()
            SUT.full_node.help_wait_till_next_epoch()
            break

    for cus in all_custodians.keys():
        INFO("Check if user has enough prv for portal testing")
        if cus.get_prv_balance() < TEST_SETTING_DEPOSIT_AMOUNT * 2:
            INFO("Balance is too low")
            COIN_MASTER.send_prv_to(cus, TEST_SETTING_DEPOSIT_AMOUNT * 2 + coin(
                1) - cus.get_prv_balance_cache()).subscribe_transaction()
            if cus.shard != COIN_MASTER.shard:
                try:
                    cus.subscribe_cross_output_coin()
                except:
                    pass

    if PORTAL_FEEDER.get_prv_balance() < 100:
        COIN_MASTER.send_prv_to(PORTAL_FEEDER, coin(1), privacy=0).subscribe_transaction()
        if PORTAL_FEEDER.shard != COIN_MASTER.shard:
            try:
                PORTAL_FEEDER.subscribe_cross_output_coin()
            except:
                pass


def teardown_module():
    breakpoint()
    INFO_HEADLINE(f'TEST MODULE TEAR DOWN: Withdraw all free collateral')
    latest_portal_state = SUT.full_node.get_latest_portal_state()
    for cus in all_custodians.keys():
        cus_stat = cus.portal_get_my_custodian_info(latest_portal_state)
        cus.portal_withdraw_my_collateral(cus_stat.get_free_collateral()).subscribe_transaction()

    # clean up redeem special case: big fat custodian send back prv to COIN_MASTER and return rate back to default
    # if not fat_custodian.is_empty:
    #     assert fat_custodian.withdraw_my_portal_collateral(big_collateral).get_error_msg() is None, "must redeem first"
    #     fat_custodian.send_prv_to(COIN_MASTER, fat_custodian.get_prv_balance() - coin(2),
    #                               privacy=0).subscribe_transaction()
    #     PORTAL_FEEDER.create_portal_exchange_rate(init_portal_rate)


def setup_function():
    INFO_HEADLINE('Portal Info before test')
    portal_state = SUT.full_node.get_latest_portal_state()
    portal_state_info = PortalStateInfo(portal_state.get_result())
    custodian_pool_info = portal_state_info.get_custodian_pool()
    sum_total_collateral = 0
    sum_free_collateral = 0
    for custodian_info in custodian_pool_info:
        if custodian_info is not None:
            sum_total_collateral += custodian_info.get_total_collateral()
            sum_free_collateral += custodian_info.get_free_collateral()
            INFO(f"--------------------------------------------------------------\n"
                 f"\t\tCustodian             : {l6(custodian_info.get_incognito_addr())}\n"
                 f"\t\tTotal collateral      : {custodian_info.get_total_collateral()}\n"
                 f"\t\tFree collateral       : {custodian_info.get_free_collateral()}\n"
                 f"\t\tLocked BNB collateral : {custodian_info.get_locked_collateral(PBNB_ID)}\n"
                 f"\t\tHold BNB              : {custodian_info.get_holding_token_amount(PBNB_ID)} \n"
                 f"\t\tLocked BTC collateral : {custodian_info.get_locked_collateral(PBTC_ID)} \n"
                 f"\t\tHold BTC              : {custodian_info.get_holding_token_amount(PBTC_ID)}")
    INFO(f"--------------------------------------------------------------\n"
         f"\t\tSum total collateral: {sum_total_collateral}\n"
         f"\t\tSum free collateral : {sum_free_collateral}")
    INFO_HEADLINE('End of portal Info before test')
