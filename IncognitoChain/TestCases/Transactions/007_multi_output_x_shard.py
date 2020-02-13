import copy
import random

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS

sender_account = ACCOUNTS[0]
is_sent = False

# create receiver list
receiver_account_list_before = ACCOUNTS.copy()
receiver_account_list_before.remove(sender_account)

# Generate dict of account : amount to send
total_sent_amount = 0
receiver_account_dict_to_send = dict()
for account in receiver_account_list_before:
    amount_to_be_received = random.randint(1000, 2000)
    total_sent_amount += amount_to_be_received
    receiver_account_dict_to_send[copy.deepcopy(account)] = amount_to_be_received


def test_send_prv_multi_output_privacy_x_shard_no_auto_fee():
    INFO("""
            Verify send PRV ( privacy - noAuto fee ) to another address x Shard successfully
         """)

    STEP(1, "get sender balance before sending")
    sender_balance = sender_account.get_prv_balance()
    INFO(f"Sender balance before: {sender_balance}")

    STEP(2, "get receiver balance before sending")
    for acc in receiver_account_list_before:
        balance = acc.get_prv_balance()
        INFO(f"{acc.payment_key} balance = {balance}")

    STEP(3, "send PRV to multi output")
    send_result = sender_account.send_prv_to_multi_account(receiver_account_dict_to_send)
    assert send_result.get_error_msg() != "Can not create tx" and INFO(
        "make successfull transaction"), "transaction fail"

    STEP(4, "subcribe transaction")
    transaction_result = send_result.subscribe_transaction()
    global is_sent
    is_sent = True

    STEP(5, "check sender balance after send")
    sender_balance_after = sender_account.get_prv_balance()
    INFO(f"sender balance after : {sender_balance_after}")

    # Balance after = balance before - (amount x n_payment)  - fee
    assert sender_balance_after == sender_balance - total_sent_amount - transaction_result.get_fee() \
           and INFO("balance of sender correct"), "balance of sender wrong"

    STEP(6, "check receivers balance")
    for acc_before in receiver_account_list_before:
        for acc_after in receiver_account_dict_to_send.keys():
            if acc_before == acc_after:
                if sender_account.shard != acc_after.shard:
                    try:
                        acc_after.subscribe_cross_output_coin(timeout=360)
                    except Exception:
                        pass
                acc_after.get_prv_balance()
                sent_amount = receiver_account_dict_to_send[acc_after]
                assert acc_after.prv_balance == acc_before.prv_balance + sent_amount and INFO(
                    f"{acc_after.payment_key} received {sent_amount}")
                receiver_account_list_before.remove(acc_before)

    STEP(7, "check transaction privacy")
    assert send_result.is_private_transaction() and INFO(
        "transaction is privacy"), "transaction must be privacy"


def teardown_function():
    if is_sent:  # if money was sent in the test, return it
        for acc in receiver_account_dict_to_send.keys():
            acc.send_prv_to(sender_account, receiver_account_dict_to_send[acc]).subscribe_transaction()
