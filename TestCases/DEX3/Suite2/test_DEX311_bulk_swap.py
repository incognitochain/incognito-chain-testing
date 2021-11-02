"""
Assume that the tokens were minted and the pairs were added using Utils/pdex3_create_test_data.py
"""
import json

from Helpers import Logging
from Objects.IncognitoTestCase import ACCOUNTS
from Utils.pdex3_create_test_data import *

Logging.INFO_HEADLINE("Setup bulk swap")
pde = SUT().pde3_get_state()
PATH1 = [pde.get_pool_pair(tokens=[PRV_ID, pUSDC])[0].get_pool_pair_id()]
trace5 = [PRV_ID, pDAI, pUSDT, pETH, pWETH]
trace6 = [pUSDT, pDAI, PRV_ID, pUSDC, pUSDT, pETH]
PATH4 = []
PATH5 = []
Logging.INFO("Making path 5")
for i in range(len(trace5) - 1):
    token1, token2 = trace5[i], trace5[i + 1]
    PATH4.append(pde.get_pool_pair(tokens=[token1, token2])[0].get_pool_pair_id())

Logging.INFO("Making path 6")
for i in range(len(trace6) - 1):
    token1, token2 = trace6[i], trace6[i + 1]
    PATH5.append(pde.get_pool_pair(tokens=[token1, token2])[0].get_pool_pair_id())

Logging.INFO_HEADLINE("Setup bulk swap. DONE!")


@pytest.mark.parametrize("trade_path, token_sell, token_buy", [
    (PATH1, PRV_ID, pUSDT),
    (PATH4, PRV_ID, pWETH),
])
def test_bulk_swap(trade_path, token_sell, token_buy):
    trade_amount = random.randrange(int(1e7), int(1e8))
    trade_fee = int(trade_amount / 10) * len(trade_path)
    trade_txs = []
    with ThreadPoolExecutor() as tpe:
        for acc in ACCOUNTS:
            r = tpe.submit(SUT().dex_v3().trade, acc.private_key, token_sell, token_buy, trade_amount, 1, trade_path,
                           trade_fee)
            trade_txs.append(r)
    summarize(trade_txs)


def test_bulk_swap_multi_pool_split():
    token_sell1, token_buy1 = PRV_ID, pWETH
    token_sell2, token_buy2 = pUSDT, pETH
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(3), coin(6), token_sell1)
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(3), coin(6), token_sell2)
    trade_amount = random.randrange(int(1e7), int(1e8))
    trade_fee1 = int(trade_amount / 10) * len(PATH4)
    trade_fee2 = int(trade_amount / 10) * len(PATH5)
    trade_txs = []
    with ThreadPoolExecutor() as tpe:
        for i in range(int(len(ACCOUNTS) / 2)):
            acc = ACCOUNTS[i]
            r = tpe.submit(SUT().dex_v3().trade, acc.private_key, token_sell1, token_buy1, trade_amount, 1, PATH4,
                           trade_fee1)
            trade_txs.append(r)
        for i in range(int(len(ACCOUNTS) / 2), len(ACCOUNTS)):
            acc = ACCOUNTS[i]
            r = tpe.submit(SUT().dex_v3().trade, acc.private_key, token_sell2, token_buy2, trade_amount, 1, PATH5,
                           trade_fee2)
            trade_txs.append(r)

    summarize(trade_txs)


def summarize(tpe_results):
    CONFIRM_SUM = {}
    for tx in tpe_results:
        confirmed_block = tx.result().get_transaction_by_hash().get_block_height()
        try:
            CONFIRM_SUM[confirmed_block] += 1
        except KeyError:
            CONFIRM_SUM[confirmed_block] = 1

    WAIT(ChainConfig.BLOCK_TIME * 4)
    TRADE_STATUS = {}
    TRADE_STATUS_COUNT = {"Success": 0, "Fail": 0}
    for tx in tpe_results:
        status = SUT().dex_v3().get_trade_status(tx.result().get_tx_id()).get_status()
        TRADE_STATUS[tx.result().get_tx_id()] = status
        if status == Status.DexV3.Trade.SUCCESS:
            TRADE_STATUS_COUNT["Success"] += 1
        elif status == Status.DexV3.Trade.REJECT:
            TRADE_STATUS_COUNT["Fail"] += 1

    Logging.INFO(f"SUMMARY: \n"
                 f"Trade tx in blocks: \n"
                 f"{json.dumps(CONFIRM_SUM, indent=3)}\n"
                 f"Trade tx status: success={Status.DexV3.Trade.SUCCESS}, reject={Status.DexV3.Trade.REJECT}\n"
                 f"{json.dumps(TRADE_STATUS_COUNT, indent=3)}\n"
                 f"{json.dumps(TRADE_STATUS, indent=3)}")
