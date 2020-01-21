import pytest

from IncognitoChain.Helpers.Logging import log
from IncognitoChain.Objects.AccountObject import *
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS

"""
Test case: Send PRV
"""


@pytest.mark.parametrize('send_amount,shard_id', [(100, 2)])
def test_05_send_prv_no_privacy_same_shard_auto_fee(send_amount, shard_id):

    account_sender = get_accounts_in_shard(shard_id, account_list=ACCOUNTS)[0]
    account_receiver = get_accounts_in_shard(shard_id, account_list=ACCOUNTS)[1]

    log.STEP(1, "get sender and receiver balance before sending")
    sender_bal = account_sender.get_prv_balance()
    log.info("sender balance before: " + str(sender_bal.get_result()))
    assert sender_bal.is_success(), "get sender balance wrong"

    receiver_bal = account_receiver.get_prv_balance()
    log.info("receiver balance before: " + str(receiver_bal.get_result()))
    assert receiver_bal.is_success(), "get receiver balance wrong"
