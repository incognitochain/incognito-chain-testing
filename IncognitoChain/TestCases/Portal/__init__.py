from IncognitoChain.Configs.Constants import coin, pbnb_id, prv_token_id, pbtc_id
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, COIN_MASTER, SUT

portal_user = ACCOUNTS[2]
custodian = ACCOUNTS[4]

deposit_amount = coin(10)
porting_amount = 100
redeem_amount = 10
custodian_remote_address = 'tbnb19cmxazhx5ujlhhlvj9qz0wv8a4vvsx8vuy9cyc'
portal_user_remote_addr = 'tbnb1zyqrky9zcumc2e4smh3xwh2u8kudpdc56gafuk'
bnb_pass_phrase = '123123Az'

all_custodians = {
    custodian: custodian_remote_address,
    ACCOUNTS[5]: 'tbnb1n5lrzass9l28djvv7drst53dcw7y9yj4pyvksf',
    ACCOUNTS[6]: 'tbnb1d90lad6rg5ldh8vxgtuwzxd8n6rhhx7mfqek38',
    ACCOUNTS[3]: 'tbnb172pnrmd0409237jwlq5qjhw2s2r7lq6ukmaeke'
}

init_portal_rate = {
    prv_token_id: 83159,
    pbnb_id: 208525400,
    pbtc_id: 105873200000
}


def find_custodian_account_by_incognito_addr(incognito_addr):
    for acc in all_custodians.keys():
        if acc.payment_key == incognito_addr:
            return acc
    return None


def setup_module():
    INFO()
    INFO('SETUP TEST MODULE')
    INFO("Create portal rate")
    custodian.create_portal_exchange_rate(init_portal_rate)

    portal_state = SUT.full_node.get_latest_portal_state()
    for cus in all_custodians.keys():
        INFO("Check if user has enough prv for portal testing")
        if cus.get_prv_balance() < deposit_amount + coin(1):
            INFO("Balance is too low")
            COIN_MASTER.send_prv_to(cus,
                                    deposit_amount + coin(1) - cus.get_prv_balance_cache()).subscribe_transaction()
            if cus.shard != COIN_MASTER.shard:
                try:
                    cus.subscribe_cross_output_coin()
                except:
                    pass

        cus_stat = cus.get_my_portal_custodian_status(portal_state)

        INFO("Check if custodian need to add more collateral")
        if cus_stat is None:
            INFO(f'{l6(cus.payment_key)} is not custodian')
            cus.add_collateral(deposit_amount, pbnb_id,
                               all_custodians[cus]).subscribe_transaction()
        elif cus_stat.get_total_collateral() > deposit_amount:
            INFO(f'{l6(cus.payment_key)} total collateral = {cus_stat.get_total_collateral()} > {deposit_amount}, '
                 f'withdraw a bit of collateral')
            current_total_collateral = cus_stat.get_total_collateral()
            cus.withdraw_my_portal_collateral(current_total_collateral - deposit_amount).subscribe_transaction()
        else:
            INFO(f'{l6(cus.payment_key)} total collateral = {cus_stat.get_total_collateral()} <= {deposit_amount}, '
                 f'deposit a bit more of collateral')
            cus.add_collateral(deposit_amount - cus_stat.get_total_collateral(), pbnb_id,
                               all_custodians[cus]).subscribe_transaction()


def teardown_module():
    INFO()
    INFO('TEARDOWN TEST MODULE')
    stats = []
    latest_portal_state = SUT.full_node.get_latest_portal_state()
    for cus in all_custodians.keys():
        cus_stat = cus.get_my_portal_custodian_status(latest_portal_state)
        stats.append(cus_stat)

    for stat in stats:
        if stat is not None:
            INFO(f"Custodian {l6(stat.get_incognito_addr())} | "
                 f"Total collat: {stat.get_total_collateral()} | "
                 f"Locked BNB collat: {stat.get_locked_collateral(pbnb_id)} | "
                 f"Hold BNB: {stat.get_holding_token_amount(pbnb_id)} | "
                 f"Locked BTC collat: {stat.get_locked_collateral(pbtc_id)} | "
                 f"Hold BTC : {stat.get_holding_token_amount(pbtc_id)}"
                 )
