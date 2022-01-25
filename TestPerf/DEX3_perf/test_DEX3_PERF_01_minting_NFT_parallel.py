from concurrent.futures import ThreadPoolExecutor

from Configs.Constants import coin
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS, SUT

COIN_MASTER.attach_to_node(SUT())
COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(1), coin(5))
# ACCOUNTS.submit_key()
# WAIT(60)

thread_results = []

prv_k = [acc.private_key for acc in ACCOUNTS]
with ThreadPoolExecutor() as e:
    f = SUT().dex_v3().mint_nft
    for k in prv_k:
        print(f"++++ {k}")
        res = e.submit(f, k, coin(1))
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
