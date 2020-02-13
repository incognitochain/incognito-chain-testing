from IncognitoChain.Configs import Constants
from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Helpers.Time import get_current_date_time, WAIT
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT

amount_init_token = 1000000 * 1000000000
account_init = ACCOUNTS[0]
custom_token_symbol = get_current_date_time()
custom_token_id = None
contribute_success = False


def teardown_function():
    if contribute_success:
        account_init.withdraw_contribution(Constants.prv_token_id, custom_token_id,
                                           amount_init_token).subscribe_transaction()
    global contribute_success
    contribute_success = False


def test_init_ptoken():
    INFO('''
    Init a pToken
    Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
    ''')

    STEP(1, "Initial new token")
    step1_result = account_init.init_custom_token_self(custom_token_symbol, amount_init_token)

    assert step1_result.get_error_msg() is None and INFO("Success to init new token"), "Failed to init new token"
    global custom_token_id
    custom_token_id = step1_result.get_token_id()
    INFO(f"Token id: {custom_token_id}")

    STEP(2, "subscribe transaction")
    step1_result.subscribe_transaction()

    STEP(3, "Get custom token balance")
    token_balance = account_init.get_token_balance(custom_token_id)
    INFO(f"Token balance: {token_balance}")

    STEP(4, "contribute token & PRV")
    # Contribute TOKEN:
    contribute_token_result = account_init.contribute_token(custom_token_id, amount_init_token, "token1_1prv")
    INFO(f"Contribute {custom_token_id} +  Success, TxID: {contribute_token_result.get_tx_id()}")
    INFO("Subscribe contribution transaction")
    contribute_token_result.subscribe_transaction()
    # Contribute PRV:
    contribute_prv_result = account_init.contribute_prv(amount_init_token, "token1_1prv")

    INFO("Contribute PRV Success, TxID: " + contribute_prv_result.get_tx_id())
    INFO("Subscribe contribution transaction")
    contribute_prv_result.subscribe_transaction()
    global contribute_success
    contribute_success = True

    STEP(5, "Verify Contribution")
    rate = []
    for _ in range(0, 10):
        WAIT(10)
        rate = SUT.full_node.get_latest_rate_between(Constants.prv_token_id, custom_token_id)
        if rate == [amount_init_token, amount_init_token]:
            break
    INFO(f"rate prv vs token: {rate}")
    assert rate == [amount_init_token, amount_init_token], "Contribution Failed"
