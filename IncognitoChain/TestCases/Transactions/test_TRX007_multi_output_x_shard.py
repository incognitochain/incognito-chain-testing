import copy
import random

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS

sender_account = Account()
is_sent = None
receiver_account_list_before = []
total_sent_amount = 0
receiver_account_n_amount_dict = dict()


def setup_module():
    global receiver_account_list_before, is_sent, sender_account
    sender_account = ACCOUNTS[0]
    is_sent = False

    # create receiver list
    receiver_account_list_before = copy.deepcopy(ACCOUNTS)
    receiver_account_list_before.remove(sender_account)


def setup_function():
    global total_sent_amount, receiver_account_list_before, sender_account, receiver_account_n_amount_dict
    for account in receiver_account_list_before:  # create a {receiver: receive amount} dictionary
        amount_to_be_received = random.randint(1000, 2000)
        total_sent_amount += amount_to_be_received
        receiver_account_n_amount_dict[account] = amount_to_be_received

    COIN_MASTER.top_him_up_prv_to_amount_if(total_sent_amount + 1000, total_sent_amount + 1000)


def test_send_prv_multi_output_privacy_x_shard_no_auto_fee():
    INFO("""
            Verify send PRV ( privacy - noAuto fee ) to another address x Shard successfully
         """)

    STEP(1, "get sender balance before sending")
    sender_bal_b4 = sender_account.get_prv_balance()
    INFO(f"Sender balance before: {sender_bal_b4}")

    STEP(2, "get receiver balance before sending")
    dict_receiver_bal_b4 = {}
    for acc in receiver_account_list_before:
        balance_b4 = acc.get_prv_balance()
        dict_receiver_bal_b4[acc] = balance_b4
        INFO(f"{acc.payment_key} balance = {balance_b4}")

    STEP(3, "send PRV to multi output")
    send_result = sender_account.send_prv_to_multi_account(receiver_account_n_amount_dict)
    assert send_result.get_error_msg() != "Can not create tx" and INFO(
        "make successfull transaction"), "transaction fail" and INFO("Failed")

    STEP(4, "subcribe transaction")
    transaction_result = send_result.subscribe_transaction()
    global is_sent
    is_sent = True
    WAIT(100)
    STEP(5, "check sender balance after send")
    sender_balance_after = sender_account.get_prv_balance()
    INFO(f"sender balance after : {sender_balance_after}")

    # Balance after = balance before - (amount x n_payment)  - fee
    assert sender_balance_after == sender_bal_b4 - total_sent_amount - transaction_result.get_fee() and INFO(
        "balance of sender correct"), "balance of sender wrong" and INFO("Failed")

    STEP(6, "check receivers balance")
    for acc_before in receiver_account_list_before:
        acc_before: Account
        balance_receiver_af = acc_before.get_prv_balance()
        balance_receiver_b4 = dict_receiver_bal_b4[acc_before]
        sent_amount = receiver_account_n_amount_dict[acc_before]
        assert balance_receiver_af == balance_receiver_b4 + sent_amount and INFO(
            f"{acc_before.payment_key} received {sent_amount}"), INFO("Failed")

    STEP(7, "check transaction privacy")
    transaction_result.verify_prv_privacy()


def teardown_function():
    if is_sent:  # if money was sent in the test, return it
        for acc in receiver_account_n_amount_dict.keys():
            acc: Account
            acc.send_prv_to(sender_account, receiver_account_n_amount_dict[acc] + 100)
        WAIT(100)
