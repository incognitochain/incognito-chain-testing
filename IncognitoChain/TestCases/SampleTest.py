import pytest

from IncognitoChain.Objects.AccountObject import *
from IncognitoChain.Objects.IncognitoTestCase import SUT
from libs.AutoLog import STEP, INFO

"""
Test case: Send PRV
"""


@pytest.mark.run
def test_05_send_prv_no_privacy_same_shard_auto_fee():
    print("""
                    Verify send PRV form account balance = 0  to another address X1hard with no privacy
                    """)
    shard_id = 2
    shard = SUT.shards[shard_id]
    account_a = get_accounts_in_shard(shard_id)[0]
    account_b = get_accounts_in_shard(shard_id)[1]
    send_amount = 100

    print("""
               Verify send PRV ( no privacy - Auto fee )to another address 1Shard successfully with no privacy
               """)
    STEP(1, "get sender and receiver balance before sending")
    balance1b = account_a.get_prv_balance()
    INFO("sender balance before: " + str(balance1b.get_result()))
    assert balance1b.is_success(), "get sender balance wrong"

    balance2b = account_b.get_prv_balance()
    INFO("receiver balance before: " + str(balance2b.get_result()))
    assert balance2b.is_success(), "get receiver balance wrong"

    STEP(2, "send PRV")
    send_result = account_a.send_prv_to(account_b, send_amount, privacy=0)
    INFO("transaction id: " + send_result.get_tx_id())
    assert send_result.is_success(), "make transaction success"

    STEP(3, " subscribe transaction")
    sub = shard.get_node(3).subscription().open_web_socket()
    ws_res = sub.subscribe_pending_transaction(send_result.get_tx_id())

    STEP(4, "check sender balance")
    balance1a = account_b.get_prv_balance()
    INFO("sender balance after: " + str(balance1a.get_result()))
    # Balance after = balance before - amount - fee
    assert balance1a.get_result() == balance1b.get_result() - send_amount - ws_res.get_fee(), \
        "sender balance output incorrect"

    STEP(5, "check receiver balance")
    balance2a = account_b.get_prv_balance()
    INFO("receiver balance after: " + str(balance2a.get_result()))
    # Balance after = balance before + amount
    assert balance2a.get_result() == balance2b.get_result() + send_amount, "receiver balance output incorrect"

    STEP(6, "Check transaction privacy")
    step6_result = shard.get_node(3).transaction().get_tx_by_hash(send_result.get_tx_id())
    assert step6_result.get_privacy(), "transaction is no privacy"
