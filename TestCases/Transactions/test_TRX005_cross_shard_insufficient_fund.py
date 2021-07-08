import re

import pytest

from Helpers.Logging import *
from Objects.AccountObject import get_accounts_in_shard, Account

sender = receiver = Account()


def setup_module():
    global sender, receiver
    sender = get_accounts_in_shard(5)[0]
    receiver = get_accounts_in_shard(2)[0]


def setup_function():
    try:
        sender.defragment_account().subscribe_transaction()
    except:
        pass


@pytest.mark.parametrize('privacy', [0, 1])
def test_send_prv_privacy_x_shard_insufficient_fund(privacy):
    INFO("""Verify send PRV to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        """)

    STEP(1, "Get receiver balance")
    receiver_bal = receiver.get_balance()
    INFO("receiver balance before: " + str(receiver_bal))

    STEP(2, "Get sender balance")
    sender_bal = sender.get_balance()
    INFO("sender balance before: " + str(sender_bal))

    STEP(3, "send PRV - Not enough coin")
    # send current balance + 10
    step3_result = sender.send_prv_to(receiver, sender_bal + 10, privacy=privacy)
    assert step3_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO(
        "Failed")
    assert re.search(r'Not enough coin',
                     step3_result.get_error_trace().get_message()), "something went so wrong" and INFO("Failed")
    assert sender_bal == sender.get_balance(), INFO("Failed")

    STEP(4, "send all PRV - auto fee")
    # send current balance (auto fee)
    step4_result = sender.send_prv_to(receiver, sender_bal, privacy=privacy)
    assert step4_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO(
        "Failed")
    step4_result.expect_error()
    assert sender_bal == sender.get_balance(), INFO("Failed")
    fee, size = sender.get_estimate_fee_and_size(receiver, sender_bal - 100)
    INFO(f'''EstimateFeeCoinPerKb = {fee}, EstimateTxSizeInKb = {size}''')

    STEP(5, "send PRV - success")
    # send current balance - fee
    step5_result = sender.send_prv_to(receiver, sender_bal - 100, int(100 / (size + 1)),
                                      privacy).expect_no_error()

    STEP(6, "Subcribe transaction")
    send_transaction = step5_result.subscribe_transaction()

    STEP(7, "Subcribe cross transaction by privatekey")
    try:
        receiver.subscribe_cross_output_coin()
    except:
        pass

    STEP(8, "Check receiver balance")
    receiver_bal_after = receiver.get_balance()
    assert receiver_bal_after == receiver_bal + sender_bal - 100, "something wrong" and INFO("Failed")

    STEP(9, "Check sender balance")
    sender_bals_after = sender.get_balance()
    INFO(f"sender balance after: {sender_bals_after}")
    assert sender_bals_after < 100, "something wrong" and INFO("Failed")

    STEP(10, f"Check transaction privacy, it must be {privacy}")
    send_transaction.verify_prv_privacy(privacy)

    STEP(11, "Return the money")
    receiver.send_prv_to(sender, sender_bal + 100).subscribe_transaction()
    if sender.shard != receiver.shard:
        try:
            sender.subscribe_cross_output_coin()
        except:
            pass
