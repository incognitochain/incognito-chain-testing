from concurrent.futures import ThreadPoolExecutor

from Configs.Constants import coin
from Helpers import TestHelper
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS, SUT

COIN_MASTER.req_to(SUT())
COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(1), coin(5))
ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()
# ACCOUNTS.submit_key()
# WAIT(60)

thread_results = []
PAIR_ID = '0000000000000000000000000000000000000000000000000000000000000004-' \
          '0000000000000000000000000000000000000000000000000000000000000006-' \
          '808d6a8992cf72dbb5e6e52440b9e64bacca5a61d01c59d95d2b1da1fad5c528'
AMP = 10000
T = "0000000000000000000000000000000000000000000000000000000000000004"
amount = 100

with ThreadPoolExecutor() as e:
    f = SUT().dex_v3().add_liquidity
    pair_hash = TestHelper.make_random_word(8, 10)
    for acc in ACCOUNTS:
        print(f"++++ {acc.private_key}")
        res = e.submit(f, acc.private_key, T, amount, AMP, PAIR_ID, pair_hash, acc.nft_ids[0])
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
