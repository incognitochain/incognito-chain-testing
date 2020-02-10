import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard

sender_account = get_accounts_in_shard(4)[0]
receiver_account = get_accounts_in_shard(4)[1]
send_amount = 1000


@pytest.mark.parametrize('fee,privacy', [(-1, 0), (2, 0), (-1, 1), (2, 1)])
def test_send_prv_1shard_with_fee_privacy(fee, privacy):
    INFO(f"Verify send PRV to another address in same Shard successfully with privacy={privacy} and fee={fee}")
    STEP(1, "get sender and receiver balance before sending")
    balance1b = sender_account.get_prv_balance()
    INFO(f"Sender balance before: {balance1b}")

    balance2b = receiver_account.get_prv_balance()
    INFO(f"Receiver balance before: {balance2b}")

    STEP(2, "send PRV")
    send_transaction = sender_account.send_prv_to(receiver_account, send_amount, fee=fee, privacy=privacy)
    assert send_transaction.get_error_msg() is None and INFO("make transaction success"), "transaction failed"

    STEP(3, " subcribe transaction")
    transaction_result = send_transaction.subscribe_transaction()

    STEP(4, "check sender balance")
    balance1a = sender_account.get_prv_balance()
    INFO(f" Sender balance after: {balance1a}")
    # Balance after = balance before - amount - fee
    assert balance1a == balance1b - send_amount - transaction_result.get_fee(), \
        "sender balance output incorrect"

    STEP(5, "check receiver balance")
    balance2a = receiver_account.get_prv_balance()
    INFO(f"receiver balance after: {balance2a}")
    # Balance after = balance before + amount
    assert balance2a == balance2b + send_amount, "receiver balance output incorrect"

    STEP(6, "Check transaction privacy")
    if privacy == 0:
        assert not send_transaction.is_private_transaction() and INFO(
            "transaction is no privacy"), "transaction must be no privacy "
    if privacy == 1:
        assert send_transaction.is_private_transaction() and INFO(
            "transaction is privacy"), "transaction must be privacy "

    STEP(7, "Return the money")
    receiver_account.send_prv_to(sender_account, send_amount).subscribe_transaction()
