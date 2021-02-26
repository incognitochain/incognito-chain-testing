import random
import copy
from concurrent.futures.thread import ThreadPoolExecutor

from Helpers.Logging import INFO
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS


def test_send_bulk_transactions():
    i = 0
    while i < 100:
        for sender in ACCOUNTS:
            receiver_account_list_before = copy.deepcopy(ACCOUNTS)
            receiver_account_list_before.remove(sender)
            thread_list = []
            with ThreadPoolExecutor() as executor:
                for receiver in receiver_account_list_before:
                    amount = random.randrange(9900000, 10000000)
                    response = executor.submit(sender.send_prv_to, receiver, amount)
                    thread_list.append(response)
            with ThreadPoolExecutor() as executor1:
                for thread in thread_list:
                    j = thread.result()
                    executor1.submit(j.subscribe_transaction)
        i += 1
