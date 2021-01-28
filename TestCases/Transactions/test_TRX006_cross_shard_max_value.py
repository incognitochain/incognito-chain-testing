import re

from Helpers.Logging import *
from Objects.AccountObject import COIN_MASTER, Account
from Objects.IncognitoTestCase import ACCOUNTS

sender = receiver = Account()
send_amount = max_fee = max_send_amount = None


def setup_function():
    global sender, receiver, send_amount, max_fee, max_send_amount
    sender = ACCOUNTS.get_accounts_in_shard(2)[0]
    receiver = ACCOUNTS.get_accounts_in_shard(5)[0]
    send_amount = 10000
    max_fee = 900000000000000
    max_send_amount = 1000000000000000001
    sender_bal = sender.get_prv_balance()
    if sender_bal < max_fee + send_amount:
        COIN_MASTER.send_prv_to(sender, max_fee + send_amount - sender_bal + 10, privacy=0).subscribe_transaction()
        if COIN_MASTER.shard != sender.shard:
            try:
                sender.subscribe_cross_output_coin()
            except:
                pass


def test_send_prv_privacy_x_shard_max_value():
    INFO("""
         Verify send PRV to another address:
         -  > 10 mil PRV unsuccess
         - Tx fee = 100000000000 PRV success
         """)
    STEP(1, "Get sender balance")
    sender_bal_b4 = sender.get_prv_balance()
    INFO(f"Sender Balance: {sender_bal_b4}")
    assert sender_bal_b4 != 0, "Sender balance = 0, stop this testcase" and INFO("Failed")

    STEP(2, "Get receiver balance")
    receiver_bal_b4 = receiver.get_prv_balance()
    INFO(f"Receiver Balance: {receiver_bal_b4}")

    STEP(3, "From address3 send prv to address1 - max value, expect create tx fail")
    # send amount = 1000000000000000000
    step3_result = sender.send_prv_to(receiver, max_send_amount)
    assert step3_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO("Failed")
    assert re.search(r'Not enough coin', step3_result.get_error_trace().get_message()), "something went so wrong" and INFO("Failed")

    STEP(4, 'Skip this step, no longer check for max fee')
    # STEP(4, "From address3 send prv to address1 - max value fee, expect create tx fail")
    # # send with fee = 10000000000000 PRV
    # step4_result = sender.send_prv_to(receiver, send_amount, fee=max_fee)
    # assert step4_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    # assert re.search(r'input value less than output value',
    #                  step4_result.get_error_trace().get_message()), "something went so wrong"

    STEP(5, f"Check balance sender and receiver")
    assert receiver_bal_b4 == receiver.get_prv_balance(), INFO("Failed")
    assert sender_bal_b4 == sender.get_prv_balance(), INFO("Failed")
