import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from APIs.CoinService.CoinService import CoinServiceApi
from Objects.AccountObject import AccountGroup
from TestPerf.CoinService import ACC_LIST

testnet2_cs_endpoint = 'https://api-coinservice-staging.incognito.org'


def test(accounts: AccountGroup, timeout=600):
    cs = CoinServiceApi(testnet2_cs_endpoint)
    with ThreadPoolExecutor() as tpe:
        for acc in accounts:
            tpe.submit(CoinServiceApi(testnet2_cs_endpoint).submit_ota_key, acc.ota_k, acc.shard)

    time.sleep(60)
    requested = {}
    time0 = datetime.now()
    with ThreadPoolExecutor() as tpe:
        print(f"Sending NFT drop requests...")
        for acc in accounts:
            requested[acc] = tpe.submit(CoinServiceApi(testnet2_cs_endpoint).request_drop_nft, acc.payment_key)
    time1 = datetime.now()
    delta_time = (time1 - time0).total_seconds()
    SUMMARY_REQ = {}
    for acc, r in requested.items():
        mint_req_status = r.result().get_result()
        try:
            SUMMARY_REQ[mint_req_status] += 1
        except KeyError:
            SUMMARY_REQ[mint_req_status] = 1
    print(f"Request result: {json.dumps(SUMMARY_REQ, indent=3)}")

    RECEIVED_COUNT, accounts_not_receive, mile_stone = wait_for_nft_drop(accounts, timeout)

    print(f"Summary: \n"
          f"{json.dumps(accounts.get_shard_dispersion(), indent=3)}\n"
          f"Send and response in: {delta_time} \n"
          f"{json.dumps(SUMMARY_REQ, indent=3)} \n"
          f"Requested: {len(accounts)} Receive: {RECEIVED_COUNT}\n"
          f"Time: {json.dumps(mile_stone,indent=3)}")


def wait_for_nft_drop(accounts, timeout=300):
    acc_wait_drop = accounts
    time0 = datetime.now()
    received_count = 0
    mile_stone = {}
    while True:
        threads = {}
        print(f"Get key info looking for NFT")
        with ThreadPoolExecutor() as tpe:
            for acc in acc_wait_drop:
                threads[acc] = tpe.submit(CoinServiceApi(testnet2_cs_endpoint).get_key_info, acc.ota_k)

        acc_wait_drop = AccountGroup()
        for acc, r in threads.items():
            nft = r.result().get_result("nftindex")
            if not nft:
                acc_wait_drop.append(acc)
            else:
                received_count += 1

        if received_count >= len(accounts):
            break
        time1 = datetime.now()
        delta_time = time1 - time0
        if received_count > 0 and not mile_stone.get(str(delta_time)):
            mile_stone[str(delta_time)] = received_count
        if delta_time.seconds > timeout:
            print(f"Time out, received {received_count} NTFs")
            break
        print(f"Waited {delta_time}, received {received_count} NFTs. Wait for 30s then check again")
        time.sleep(30)
    return received_count, acc_wait_drop, mile_stone


test(ACC_LIST, 3600)
