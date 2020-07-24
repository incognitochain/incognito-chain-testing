import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard, Account

receiver = sender = Account()
send_amount = None


def setup_module():
    global send_amount, sender, receiver
    sender = get_accounts_in_shard(5)[0]
    receiver = get_accounts_in_shard(2)[0]
    send_amount = 1000


@pytest.mark.parametrize('fee,privacy', [(-1, 1), (-1, 0), (2, 1), (2, 0)])
def test_send_prv_cross_shard_with_fee_privacy(fee, privacy):
    INFO(f"Verify send PRV to another address Xshard successfully with fee={fee} privacy={privacy}")
    STEP(1, "Get sender balance")
    sender_bal = sender.get_prv_balance()
    INFO(f"Sender balance before: {sender_bal}")

    STEP(2, "Get receiver balance")
    receiver_bal = receiver.get_prv_balance()
    INFO(f"receiver balance before: {receiver_bal}")

    STEP(3, " send PRV")
    send_transaction = sender.send_prv_to(receiver, send_amount, fee=fee, privacy=privacy)
    INFO("Transaction ID: " + send_transaction.get_tx_id())
    assert send_transaction.get_error_msg() != 'Can not create tx' and INFO(
        "make transaction success"), "transaction failed"

    STEP(4, "Subcribe transaction")
    try:
        send_transaction.subscribe_transaction()
    except TimeoutError:
        ERROR(f"Timeout while subscribing tx: {send_transaction.get_tx_id()}")

    STEP(5, "Subscribe cross transaction by privatekey")
    try:
        receiver.subscribe_cross_output_coin()
    except:
        pass

    STEP(6, "Check sender balance")
    sender_bal_after = sender.get_prv_balance()
    INFO(f"sender balance after: {sender_bal_after}")
    assert sender_bal_after == sender_bal - send_amount - send_transaction.get_transaction_by_hash().get_fee(), \
        "something wrong"  # when privacy=1, ws cannot get fee

    STEP(7, "Check receiver balance")
    receiver_bal_after = receiver.get_prv_balance()
    INFO(f"receiver balance after: {receiver_bal_after}")
    assert receiver_bal_after == receiver_bal + send_amount, \
        f"Receiver balance after={receiver_bal_after}\n\t receiver bal before + send amount = {receiver_bal} + {send_amount}"

    STEP(8, "Check transaction privacy")
    if privacy == 0:
        assert not send_transaction.is_prv_privacy() and INFO("transaction is not privacy"), \
            "transaction must be no privacy "

    if privacy == 1:
        assert send_transaction.is_prv_privacy() and INFO('transaction is privacy'), \
            "transaction must be private "