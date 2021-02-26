import pytest

from Helpers.Logging import *
from Objects.AccountObject import get_accounts_in_shard, Account

sender: Account = None
sender_balance_init = None
receiver: Account = None
receiver_balance = None


def setup_module():
    global sender, sender_balance_init, receiver, receiver_balance
    sender = get_accounts_in_shard(2)[0]
    sender_balance_init = sender.get_prv_balance()

    receiver = get_accounts_in_shard(5)[0]
    receiver_balance = receiver.get_prv_balance()


def setup_function():
    sender_balance = sender.get_prv_balance()
    if sender_balance == 0:
        return
    sender.send_all_prv_to(receiver)
    if sender.shard != receiver.shard:
        try:
            receiver.subscribe_cross_output_coin()
        except:
            pass


def teardown_function():
    receiver.send_prv_to(sender, sender_balance_init+1)
    try:
        sender.subscribe_cross_output_coin()
    except:
        pass

@pytest.mark.parametrize('fee,privacy', [
    (-1, 0),
    (2, 0),
    (-1, 1),
    (2, 1)
])
def test_send_prv_cross_shard_0_balance_with_privacy_is(fee, privacy):
    INFO(f"Verify send PRV form account balance = 0  to another address XShard with privacy={privacy} fee={fee}")
    STEP(1, "get sender and receiver balance before sending")
    balance1b = sender.get_prv_balance()
    INFO(f"sender balance: {balance1b}")
    assert balance1b == 0, f'Sender balance must = 0 before running this test, got {balance1b} instead' and INFO("Failed")   # add info to debug testcases specific

    balance2b = receiver.get_prv_balance()
    INFO("receiver balance: " + str(balance2b))

    # sent with amount >0
    STEP(2, "send PRR -- amount >0")
    step2_result = sender.send_prv_to(receiver, 190, fee=fee, privacy=privacy)

    assert step2_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO("Failed")
    assert 'not enough output coin' in step2_result.get_error_trace().get_message(), INFO("Failed")

    # sent with amount = 0
    STEP(3, "send PRV -- amount =0")
    step3_result = sender.send_prv_to(receiver, 0, fee=fee, privacy=privacy)
    assert step3_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO("Failed")
    step3_result.expect_error()

    # sent with amount < 0
    STEP(4, "Send PRV -- amount < 0")
    step4_result = sender.send_prv_to(receiver, -1, fee=fee, privacy=privacy)
    assert step4_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed" and INFO("Failed")
    step3_result.expect_error()
