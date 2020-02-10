import re

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard

sender_account = get_accounts_in_shard(4)[0]
receiver_account = get_accounts_in_shard(4)[1]
init_sender_balance = sender_account.get_prv_balance()
init_receiver_balance = receiver_account.get_prv_balance()


def setup_function():
    """
    double check token balance (total supply) with RPC listalltoken in chain
    double check api of aPhuong, to see which one is decentralized token
    decide token-id to be test
    :return:
    """
    # sender_account.send_all_prv_to(receiver_account).subscribe_transaction()


def teardown_function():
    """
    burn/withdraw decentralize token
    :return:
    """
    # receiver_account.send_prv_to(sender_account, init_sender_balance, privacy=0).subscribe_transaction()


def test_init_centralize_token():
    INFO("Verify send PRV form account balance = 0  to another address X1hard with no privacy")

    STEP(1, "get balance of sender and receiver before sending")
    sender_balance = sender_account.get_prv_balance()
    INFO(f"sender balance: {sender_balance}")

    receiver_balance = receiver_account.get_prv_balance()
    INFO(f"receiver balance: {receiver_balance}")

    # sent with amount >0
    STEP(2, "from address1 send prv to address2 -- amount >0")
    send_result_2 = sender_account.send_prv_to(receiver_account, amount=1, privacy=0)

    assert_true(send_result_2.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed")
    assert_true(re.search(r'-4001: -4001: -1013:', send_result_2.get_error_trace()), "something went so wrong")

    # sent with amount = 0
    STEP(3, "from address1 send prv to address2 -- amount =0")
    send_result_3 = sender_account.send_prv_to(receiver_account, amount=0, privacy=0)
    INFO("StackTrace: " + send_result_3.get_error_msg())
    assert_true(send_result_3.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed")
    assert_true(re.search(r'input value less than output value', send_result_3.get_error_trace()),
                "something went so wrong")

    # sent with amount < 0
    STEP(4, "from address1 send prv to address2 -- amount < 0")
    send_result_4 = sender_account.send_prv_to(receiver_account, amount=-10, privacy=0)

    INFO("StackTrace: " + send_result_4.get_error_trace())
    assert_true(send_result_4.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed")
    assert_true(re.search(r'-4001: -4001: -1013:', send_result_4.get_error_trace()), "something went so wrong")


def test_send_centralize_token_1shard():
    pass


def test_send_centralize_token_xshard():
    pass


def test_burn_centralize_token():
    pass


def test_withdraw_centralize_token():
    pass
