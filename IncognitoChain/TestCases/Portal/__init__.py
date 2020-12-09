from IncognitoChain.Configs.Constants import coin, PBNB_ID, PRV_ID, PBTC_ID
from IncognitoChain.Drivers.NeighborChainCli import BnbCli
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import PortalHelper, ChainHelper
from IncognitoChain.Objects.AccountObject import AccountGroup, PORTAL_FEEDER, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT

# ---- import BNB key for testing
cli_pass_phrase = '123123Az'
BNB_MNEMONIC_LIST = [
    'web dwarf series matrix promote verb ahead topple blue maple vicious must useful then ice slice useless teach skate fork giraffe bamboo undo answer',
    'orbit endless sample emotion black armor duck erosion next grow apart envelope inform museum aspect task buddy salt adjust bag eyebrow involve void unfair',
    'place gas monkey narrow leaf cross electric hero minimum nothing improve soul slow casual fun clerk muffin piece wool admit immense search response miracle',
    'enemy moral minute rude field seven setup odor address salad state select board useful punch fault mass flip culture duty metal much priority joy',
    'luggage guide power apple transfer swarm mammal raw super bubble buffalo thunder sister insane veteran sheriff sport body crack belt outdoor grit drama range',
]

cli = BnbCli()
cli.import_mnemonics('user', cli_pass_phrase, BNB_MNEMONIC_LIST)
bnb_address_list = list(cli.list_user_addresses().values())
# ----------------------------------------------------------------------------------------------------------------------

TEST_SETTING_DEPOSIT_AMOUNT = coin(5)
TEST_SETTING_PORTING_AMOUNT = 100
TEST_SETTING_REDEEM_AMOUNT = 10

self_pick_custodian = ACCOUNTS[6].set_remote_addr(bnb_address_list[0], 'mgdwpAgvYNuJ2MyUimiKdTYsu2vpDZNpAa')
portal_user = ACCOUNTS[1].set_remote_addr(bnb_address_list[1], 'mhpTRAPdmyB1PUvXR2yqaSBK8ZJhEQ8rEw')
all_custodians = AccountGroup(
    ACCOUNTS[3].set_remote_addr(bnb_address_list[2], 'mg3me76RFFWeRuYqM6epwjMHHMTaouYLDe'),
    ACCOUNTS[4].set_remote_addr(bnb_address_list[3], 'mkgT1mphBPX1C3tn9yRK7HmVSYkVEn7VzY'),
    ACCOUNTS[5].set_remote_addr(bnb_address_list[4], 'myo25dPxQNqk94HwFLeFr42cH8VbwTGbBm'),
    self_pick_custodian
)
another_bnb_addr = 'tbnb1hmgztqgx62t3gldsk7n9wt4hxg2mka0fdem3ss'
another_btc_addr = 'mytWP2jW6Hsj5YdPvucm8Kkop9789adjQn'

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
            ChainHelper.wait_till_next_epoch()
            break

    global big_collateral, fat_custodian_prv

    big_collateral = PortalHelper.cal_lock_collateral(big_porting_amount, big_rate[PBNB_ID],
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
