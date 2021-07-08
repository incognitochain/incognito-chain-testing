import pytest

from Helpers.Logging import *
from Objects.AccountObject import *
from Objects.IncognitoTestCase import SUT

"""
Test case: Send PRV
"""


@pytest.mark.parametrize('send_amount,shard_id', [(100, 2), (1000, 4), (1010, 4)])
@pytest.mark.run
def test_05_send_prv_no_privacy_same_shard_auto_fee(send_amount, shard_id):
    account_sender = get_accounts_in_shard(shard_id)[0]
    account_receiver = get_accounts_in_shard(shard_id)[1]
    full_node = SUT.full_node

    print("""
               Verify send PRV ( no privacy - Auto fee )to another address 1Shard successfully with no privacy
               """)
    STEP(1, "get sender and receiver balance before sending")
    sender_bal = account_sender.get_balance()
    INFO("sender balance before: " + str(sender_bal))
    assert sender_bal.is_success(), "get sender balance wrong"

    receiver_bal = account_receiver.get_balance()
    INFO("receiver balance before: " + str(receiver_bal))
    assert receiver_bal.is_success(), "get receiver balance wrong"

    STEP(2, "send PRV")
    send_result = account_sender.send_prv_to(account_receiver, send_amount, privacy=0)
    INFO("transaction id: " + send_result.get_tx_id())
    assert send_result.is_success(), "make transaction success"

    STEP(3, "subscribe transaction")
    send_transaction_info = send_result.subscribe_transaction()

    STEP(4, "check sender balance")
    sender_bal_after = account_sender.get_balance()
    INFO("sender balance after: " + str(sender_bal_after))
    # Balance after = balance before - amount - fee
    assert sender_bal_after == sender_bal - send_amount - send_transaction_info.get_fee(), \
        "sender balance output incorrect"

    STEP(5, "check receiver balance")
    receiver_bal_after = account_receiver.get_balance()
    INFO("receiver balance after: " + str(receiver_bal_after))
    # Balance after = balance before + amount
    assert receiver_bal_after.get_result() == receiver_bal.get_result() + send_amount, "receiver balance output incorrect"

    STEP(6, "Check transaction privacy")
    step6_result = full_node.transaction().get_tx_by_hash(send_result.get_tx_id())
    assert not step6_result.get_privacy(), "transaction is no privacy"


def setup_function():
    print('this function will run before each test function in the same module')


def setup_module():
    print('this ')


def teardown_function():
    pass


def teardown_module():
    pass
