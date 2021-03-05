from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from SpecialTests.TxSpammer import account_1k_shard0


@pytest.mark.parametrize("account_group", [
    account_1k_shard0
])
def test_spam_reward_withdraw_req(account_group):
    futures = []
    with ThreadPoolExecutor() as executor:
        for account in account_group:
            future = executor.submit(account.stk_withdraw_reward_to_me)
            # futures.append(future)

