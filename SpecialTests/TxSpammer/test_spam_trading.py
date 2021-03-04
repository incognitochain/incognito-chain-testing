from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from SpecialTests.TxSpammer import account_1k_shard0


@pytest.mark.parametrize('account_list,token_to_buy', [
    (account_1k_shard0, 'iasdfhasdfjklhgaiudhuedh34y9efgh93212')
])
def test_spam_trade_prv(account_list, token_to_buy):
    trade_amount = 123
    min_acceptable = 0
    get_bal_future = {}
    with ThreadPoolExecutor() as executor:
        for acc in account_list:
            future = executor.submit(acc.get_prv_balance)
            get_bal_future[acc] = future

    ready_to_trade_acc = []
    for acc, future in get_bal_future.items():
        if future.result() >= trade_amount + 100:
            ready_to_trade_acc.append(acc)

    with ThreadPoolExecutor() as executor:
        for acc in ready_to_trade_acc:
            executor.submit(acc.pde_trade_prv, trade_amount, token_to_buy, min_acceptable)
