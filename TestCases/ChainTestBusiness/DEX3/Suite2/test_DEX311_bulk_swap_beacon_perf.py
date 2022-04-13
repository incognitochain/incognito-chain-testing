"""
Assume that the tokens were minted and the pairs were added using Utils/pdex3_create_test_data.py
"""
import copy
import json
import random
from concurrent.futures import ThreadPoolExecutor

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import PRV_ID, coin, Status
from Configs.TokenIds import pUSDC, pWETH, pUSDT, pETH
from Helpers import Logging
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, AccountGroup
from Objects.IncognitoTestCase import ACCOUNTS, SUT
from TestCases.ChainTestBusiness.DEX3.Suite2 import PATH4, PATH1, PATH5

Logging.INFO("Submitting key to each shard...")
for i in range(len(ACCOUNTS)):
    shard = ACCOUNTS[i].shard % ChainConfig.ACTIVE_SHARD
    node = i % len(SUT.shards[shard])
    ACCOUNTS[i].attach_to_node(SUT.shards[shard][node])  # attaching each account to its own shard
ACCOUNTS.submit_key()


@pytest.mark.parametrize("trade_path, token_sell, token_buy", [
    (PATH1, PRV_ID, pUSDC),
    (PATH4, PRV_ID, pWETH),
])
def test_stress_beacon_bulk_swap_no_split(trade_path, token_sell, token_buy):
    trade_amount = random.randrange(int(1e7), int(1e8))
    trade_fee = int(trade_amount / 10) * len(trade_path)
    Logging.INFO(f"Trade path: \n {trade_path}\n   "
                 f"sell:   {token_sell}\n   "
                 f"buy:    {token_buy}\n   "
                 f"amount: {trade_amount}\n   "
                 f"fee:    {trade_fee}")
    Logging.INFO("Making raw trade tx first...")
    raw_txs = ACCOUNTS.pde3_make_raw_trade_txs(token_sell, token_buy, trade_amount, 1, trade_path, trade_fee)
    blk_chain_info = SUT().get_block_chain_info()
    start_beacon_h = blk_chain_info.get_beacon_block().get_height()
    start_shard_height = blk_chain_info.get_all_height()
    Logging.INFO("Sending created txs...")
    trade_txs = []
    with ThreadPoolExecutor() as tpe:
        for acc in ACCOUNTS:
            proof = raw_txs[acc]
            r = tpe.submit(acc.REQ_HANDLER.send_proof, proof)
            trade_txs.append(r)
    WAIT(ChainConfig.BLOCK_TIME * 4)
    end_beacon_h = SUT().get_block_chain_info().get_beacon_block().get_height() + 10
    SUT().wait_till_beacon_height(end_beacon_h, timeout=600)
    Logging.INFO(f"Shard height before sending trade tx:\n"
                 f"{start_shard_height}")
    summarize([r.result().get_tx_id() for r in trade_txs], start_beacon_h, end_beacon_h)


def test_stress_beacon_bulk_swap_multi_pool_split():
    token_sell1, token_buy1 = PRV_ID, pWETH
    token_sell2, token_buy2 = pUSDT, pETH
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(3), coin(6), token_sell1)
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(3), coin(6), token_sell2)
    trade_amount = random.randrange(int(1e7), int(1e8))
    trade_fee1 = int(trade_amount / 10) * len(PATH4)
    trade_fee2 = int(trade_amount / 10) * len(PATH5)

    Logging.INFO("Making raw trade tx first...")
    first_half = AccountGroup(*ACCOUNTS[:int(len(ACCOUNTS) / 2)])
    second_half = AccountGroup(*ACCOUNTS[int(len(ACCOUNTS) / 2):])
    raw_txs_prv = first_half.pde3_make_raw_trade_txs(
        token_sell1, token_buy1, trade_amount, 1, PATH4, trade_fee1)
    raw_txs_tok = second_half.pde3_make_raw_trade_txs(
        token_sell2, token_buy2, trade_amount, 1, PATH5, trade_fee2)
    blk_chain_info = SUT().get_block_chain_info()
    start_beacon_h = blk_chain_info.get_beacon_block().get_height()
    start_shard_height = blk_chain_info.get_all_height()
    Logging.INFO("Sending created txs...")
    trade_txs = []
    with ThreadPoolExecutor() as tpe:
        for acc, proof in raw_txs_prv.items():
            r = tpe.submit(acc.REQ_HANDLER.send_proof, proof)
            trade_txs.append(r)
        for acc, proof in raw_txs_tok.items():
            r = tpe.submit(acc.REQ_HANDLER.send_proof, proof, 'token')
            trade_txs.append(r)
    WAIT(ChainConfig.BLOCK_TIME * 4)
    end_beacon_h = SUT().get_block_chain_info().get_beacon_block().get_height() + 10
    SUT().wait_till_beacon_height(end_beacon_h, timeout=600)
    Logging.INFO(f"Shard height before sending trade tx:\n"
                 f"{start_shard_height}")
    summarize([r.result().get_tx_id() for r in trade_txs], start_beacon_h, end_beacon_h)


def summarize(tx_hashes, start_beacon_h, end_beacon_h):
    Logging.INFO("Summarizing trading")
    CONFIRM_SHARD_BLOCK = {}

    Logging.INFO("Getting transactions details...")
    tx_result = []
    with ThreadPoolExecutor() as tpe:
        for h in tx_hashes:
            tx_result.append(tpe.submit(SUT().get_tx_by_hash, h))

    for r in tx_result:
        tx_detail = r.result()
        confirmed_block = tx_detail.get_block_height()
        confirmed_shard = tx_detail.get_shard_id()
        try:
            CONFIRM_SHARD_BLOCK[confirmed_shard][confirmed_block] += 1
        except KeyError:
            if CONFIRM_SHARD_BLOCK.get(confirmed_shard):
                CONFIRM_SHARD_BLOCK[confirmed_shard][confirmed_block] = 1
            else:
                CONFIRM_SHARD_BLOCK[confirmed_shard] = {confirmed_block: 1}
    Logging.INFO(f"Getting beacon block info from {start_beacon_h} to {end_beacon_h}")
    beacon_blocks = {h: SUT().get_latest_beacon_block(h) for h in range(start_beacon_h, end_beacon_h + 1)}

    TRADE_STATUS = {}
    TRADE_STATUS_COUNT = {"Success": 0, "Fail": 0}
    Logging.INFO(f'Checking trade status ...')
    trade_status_result = {}
    with ThreadPoolExecutor() as tpe:
        for h in tx_hashes:
            trade_status_result[h] = tpe.submit(SUT().dex_v3().get_trade_status, h)
    for h, r in trade_status_result.items():
        status = r.result().get_status()
        TRADE_STATUS[h] = status
        if status == Status.DexV3.Trade.SUCCESS:
            TRADE_STATUS_COUNT["Success"] += 1
        elif status == Status.DexV3.Trade.REJECT:
            TRADE_STATUS_COUNT["Fail"] += 1
    INST_COUNT = count_by_inst_in_beacon_block(tx_hashes, beacon_blocks)
    SHARD_STATE_COUNT = count_by_shard_state_in_beacon_block(CONFIRM_SHARD_BLOCK, beacon_blocks)
    Logging.INFO(f"SUMMARY: \n"
                 f"Trade tx in shard blocks: \n"
                 f"{json.dumps(CONFIRM_SHARD_BLOCK, indent=3)}\n"
                 f"Instruction count: \n{json.dumps(INST_COUNT, indent=3)} sum: {sum(INST_COUNT.values())}\n"
                 f"Shard state count: \n{json.dumps(SHARD_STATE_COUNT, indent=3)} sum: {sum(SHARD_STATE_COUNT.values())}\n"
                 f"Trade tx status: success={Status.DexV3.Trade.SUCCESS}, reject={Status.DexV3.Trade.REJECT}\n"
                 f"{json.dumps(TRADE_STATUS_COUNT, indent=3)}\n"
                 # f"{json.dumps(TRADE_STATUS, indent=3)}"
                 )


def count_by_inst_in_beacon_block(tx_hashes, beacon_blocks):
    instruction_count = {}
    for h in tx_hashes:
        found = False
        for b_height, bb in beacon_blocks.items():
            trade_inst = bb.get_pde3_trade_instructions()
            for inst in trade_inst:
                if h != inst.dict_data[3]:
                    continue
                try:
                    instruction_count[b_height] += 1
                except KeyError:
                    instruction_count[b_height] = 1
                found = True
                print(f" {h} found in beacon block {b_height}")
                break
        if not found:
            print(f" {h} not found in beacon block")
    return {k: v for k, v in sorted(instruction_count.items())}


def count_by_shard_state_in_beacon_block(confirmed_shard_block, beacon_blocks):
    shard_state_count = {}
    _CSB = copy.deepcopy(confirmed_shard_block)
    for shard, h_and_count in _CSB.items():
        print(f'{"=" * 50}\nloop 0: shard {shard}, height n count {h_and_count}')
        for shard_height in h_and_count.keys():
            count = h_and_count[shard_height]
            print(f'   loop 1: shard height: {shard_height}, count {count}')
            for beacon_height, bb in beacon_blocks.items():
                print(f"      loop 2, checking shard states in beacon block {beacon_height}")
                shard_state = bb.get_shard_states(shard)
                if not shard_state:
                    print("      shard state is empty, skip loop 2")
                    continue
                for inf in shard_state.get_blocks_info():
                    print(f'         loop 3: checking inf shard state height {inf.get_height()}')
                    if inf.get_height() >= shard_height:
                        try:
                            shard_state_count[beacon_height] += count
                            print(
                                f"         BB stat after add {count} to bheight {beacon_height}: {shard_state_count}")
                        except KeyError:
                            if count > 0:
                                shard_state_count[beacon_height] = count
                            print(
                                f"         BB stat new bheight {beacon_height} count = {count}: {shard_state_count}")
                        print(f"         reset h n count {h_and_count}")
                        count = 0
                        h_and_count[shard_height] = 0
    return {k: v for k, v in sorted(shard_state_count.items())}
