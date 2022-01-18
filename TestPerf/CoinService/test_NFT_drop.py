import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from APIs.BackEnd.CoinService.CoinService import CoinServiceApi
from Objects.AccountObject import AccountGroup
from Objects.NodeObject import Node

logger = logging.getLogger(__name__)
file_path = f"{os.path.dirname(os.path.realpath(__file__))}/accounts"
file_path = "TestPerf/CoinService/accounts"

testnet2_fullnode = Node(url="http://testnet.incognito.org:9334")
testnet2_cs_endpoint = 'https://api-coinservice-staging.incognito.org'
ACC_LIST = AccountGroup().load_from_file(file_path).change_req_handler(testnet2_fullnode)
MAX_WORKER = 50


def test(accounts: AccountGroup, timeout=600):
    cs = CoinServiceApi(testnet2_cs_endpoint)
    logger.info(f"Submit ota keys to CS...")
    with ThreadPoolExecutor(max_workers=MAX_WORKER) as tpe:
        for acc in accounts:
            tpe.submit(CoinServiceApi(testnet2_cs_endpoint).submit_ota_key, acc.ota_k, acc.shard)

    logger.info("Wait for 30s")
    time.sleep(30)

    T_START, T_END, SUMMARY_REQ = send_nft_req(accounts)
    RECEIVED_COUNT, accounts_not_receive, mile_stones = wait_for_nft_drop(accounts, T_START, timeout=timeout)

    REPORT = f"!!!!!! SUMMARY !!!!!!: \n" \
             f"Shard count {json.dumps(accounts.get_shard_dispersion(), indent=3)}\n" \
             f"Send @ {T_START}, done @ {T_END}, wasted: {T_END - T_START} \n" \
             f"Request status count {json.dumps(SUMMARY_REQ, indent=3)} \n" \
             f"Requested: {len(accounts)} account. Receive: {RECEIVED_COUNT} NFT id\n" \
             f"Mile stones: {json.dumps(mile_stones, indent=3)}"
    logger.info(REPORT)
    return REPORT


def send_nft_req(accounts):
    requested = {}
    time0 = datetime.now()
    with ThreadPoolExecutor(max_workers=MAX_WORKER) as tpe:
        logger.info(f"Sending NFT drop requests @ {time0}...")
        for acc in accounts:
            requested[acc] = tpe.submit(CoinServiceApi(testnet2_cs_endpoint).request_drop_nft, acc.payment_key)
    time1 = datetime.now()
    logger.info(f"Request NFT drop requests done @ {time1}, wasted {time1 - time0}...")
    summary_req = {}
    for acc, r in requested.items():
        mint_req_status = r.result().get_result()
        try:
            summary_req[mint_req_status] += 1
        except KeyError:
            summary_req[mint_req_status] = 1
    logger.info(f"Request result: {json.dumps(summary_req, indent=3)}")
    return time0, time1, summary_req


def wait_for_nft_drop(accounts, time_zero: datetime = 0, timeout=300):
    acc_wait_drop = accounts
    time0 = datetime.now()
    time_zero = time_zero if time_zero else time0
    received_count = 0
    mile_stones = {}
    logger.info(f"Get key info looking for NFT")
    while True:
        threads = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKER) as tpe:
            for acc in acc_wait_drop:
                threads[acc] = tpe.submit(CoinServiceApi(testnet2_cs_endpoint).get_key_info, acc.ota_k)

        acc_wait_drop = AccountGroup()
        for acc, r in threads.items():
            nft = r.result().get_result("nftindex")
            if not nft:
                acc_wait_drop.append(acc)
            else:
                received_count += 1

        time1 = datetime.now()
        wasted_time = time1 - time0
        delta_time = time1 - time_zero
        if received_count > 0 and not mile_stones.get(received_count):
            mile_stones[received_count] = str(delta_time)
        if wasted_time.seconds > timeout:
            logger.info(f"Time out, received {received_count} NTFs")
            break
        if received_count >= len(accounts):
            break
        logger.info(f"{delta_time} since request, received {received_count} NFTs. Wait for 30s then check again")
        time.sleep(30)
    return received_count, acc_wait_drop, mile_stones


def count_nft_in_chain(accounts: AccountGroup):
    pde3 = testnet2_fullnode.pde3_get_state(key_filter='NftIDs')
    accounts.pde3_get_nft_ids(pde3)
    return sum([len(acc.nft_ids) for acc in accounts])


test(ACC_LIST, 900)
