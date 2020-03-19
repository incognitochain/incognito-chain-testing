import re

import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard

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
    receiver_bal = receiver.get_prv_balance()
    INFO("receiver balance before: " + str(receiver_bal))

    STEP(2, "Get sender balance")
    sender_bal = sender.get_prv_balance()
    INFO("sender balance before: " + str(sender_bal))

    STEP(3, "send PRV - Not enough coin")
    # send current balance + 10
    step3_result = sender.send_prv_to(receiver, sender_bal + 10, privacy=privacy)
    assert step3_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'Not enough coin', step3_result.get_error_trace().get_message()), "something went so wrong"
    assert sender_bal == sender.get_prv_balance()

    STEP(4, "send all PRV - auto fee")
    # send current balance (auto fee)
    step4_result = sender.send_prv_to(receiver, sender_bal, privacy=privacy)
    assert step4_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'Wrong input transaction',
                     step4_result.get_error_trace().get_message()), "something went so wrong"
    assert sender_bal == sender.get_prv_balance()
    estimated_fee = step4_result.get_error_trace().get_estimated_fee()
    INFO("Estimated fee: " + estimated_fee)

    STEP(5, "send PRV - success")
    # send current balance - fee
    step5_result = sender.send_prv_to(receiver, sender_bal - int(estimated_fee), privacy=privacy)
    if step5_result.get_error_msg() is None:  # if tx success, then nothing happens
        INFO("TxID 1 : " + step5_result.get_tx_id())
    else:  # if tx failure, send again with new estimates fee
        estimated_fee = step5_result.get_error_trace().get_estimated_fee()
        INFO("NEW estimated fee: " + estimated_fee)
        step5_result = sender.send_prv_to(receiver, sender_bal - int(estimated_fee), privacy=privacy)

    STEP(6, "Subcribe transaction")
    send_transaction = step5_result.subscribe_transaction()

    STEP(7, "Subcribe cross transaction by privatekey")
    receiver.subscribe_cross_output_coin()

    STEP(8, "Check receiver balance")
    receiver_bal_after = receiver.get_prv_balance()
    assert receiver_bal_after == receiver_bal + sender_bal - send_transaction.get_fee(), "something wrong"

    STEP(9, "Check sender balance")
    sender_bals_after = sender.get_prv_balance()
    INFO(f"sender balance after: {sender_bals_after}")
    assert sender_bals_after == 0, "something wrong"

    STEP(10, f"Check transaction privacy, it must be {privacy}")
    if privacy == 1:
        is_privacy = step5_result.is_prv_privacy()
        assert is_privacy and INFO("transaction is privacy"), "transaction must be privacy "
    else:  # privacy =0
        is_privacy = step5_result.is_prv_privacy()
        assert not is_privacy and INFO("transaction is not privacy"), "transaction must not be privacy "

    STEP(11, "Return the money")
    receiver.send_prv_to(sender, sender_bal).subscribe_transaction()
    sender.subscribe_cross_output_coin()
