from concurrent.futures import ThreadPoolExecutor

from Configs.Constants import coin
from Helpers import TestHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS, SUT

# COIN_MASTER.req_to(SUT())
# COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(1), coin(5))
# ACCOUNTS.submit_key()
# WAIT(60)

thread_results = []

with ThreadPoolExecutor() as e:
    f = SUT().transaction().send_transaction
    for acc in ACCOUNTS:
        print(f"++++ {acc.private_key}")
        res = e.submit(f, acc.private_key, {acc.payment_key: 1000})
        thread_results.append(res)

fail_count = 0
for res in thread_results:
    if res.result().get_error_msg():
        fail_count += 1
        print(f"{'=' * 80}\n"
              f"{res.result().get_error_msg()}\n"
              f"{res.result().get_error_trace().get_message()}\n"
              f"{res.result().rpc_params().data}")
print(f"+++ len = {len(thread_results)} | fail = {fail_count}")
