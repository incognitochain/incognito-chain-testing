import requests, json, time, sys
from multiprocessing.pool import ThreadPool
from KeyList import *
from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO, filename='tx_test.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

pool = ThreadPool(processes=4)

# api-endpoint
FULLNODEURL = "http://51.83.XXX.XXX:9334"
URL = "http://51.83.XXX.XXX"
PORT = ["20004", "20008", "20012", "20016", "20020", "20024", "20028", "20033"]

# config
NOSHARD = 8
NOTHREAD = 100
NOTX = 1000


def InitPRVToShard(index, value):
    lsTx = {}
    senderIndex = 0
    countErr = 0
    countTx = 0
    for item in paymentAddLs[index]:
        lsTx[item] = value
        if len(lsTx) == 15:
            data = {
                "jsonrpc": "1.0",
                "method": "createandsendtransaction",
                "params": [
                    privKeySenderLs[senderIndex % 8],
                    lsTx,
                    10,
                    1
                ],
                "id": 1
            }
            dataJson = json.dumps(data)

            # r = requests.post(url=URL + ":" + PORT[senderIndex % 8], data=dataJson)
            r = requests.post(url=FULLNODEURL, data=dataJson)
            countTx += 1
            if r.status_code != 200:
                logging.info("============ERROR Code != 200 ===========")
                logging.info(dataJson)
                countErr += 1
            else:
                response = r.json()
                if response["Error"] != None:
                    logging.info("============%s===========", response["Error"]["Message"])
                    logging.info(dataJson)
                    countErr += 1
                else:
                    logging.info("TxID: %s - ShardID: %s", response["Result"]["TxID"], response["Result"]["ShardID"])
            lsTx = {}
            senderIndex += 1
            if senderIndex % 8 == 7:
                time.sleep(60)
    return countTx, countErr


def SendPRVFromShardToShardThread(fromShardID, toShardLsID, epoch, value):
    countTx = 0
    countErr = 0
    counterResult = []
    for i in range(NOTHREAD):
        counterResult.append(pool.apply_async(SendPRVFromShardToShards, (i,
                                                                         fromShardID,
                                                                         toShardLsID,
                                                                         int(NOTX / NOTHREAD),
                                                                         i * (int(NOTX / NOTHREAD)),
                                                                         epoch,
                                                                         value,)))
        time.sleep(5)

    for item in counterResult:
        countTx += item.get()[0]
        countErr += item.get()[1]

    return countTx, countErr

def GetTxonChain(startTime, shardID):
    data = {
        "jsonrpc": "1.0",
        "method": "getblocks",
        "params": [500, shardID],
        "id": 1
    }
    dataJson = json.dumps(data)
    # r = requests.post(url=URL + ":" + PORT[shardID], data=dataJson)
    r = requests.post(url=FULLNODEURL, data=dataJson)
    data = r.json()["Result"]
    totalTx = 0
    for item in data:
        if item["Time"] < startTime:
            break
        totalTx += len(item["TxHashes"])

    return totalTx

def SendPRVFromShardToShards(threadID, fromShardID, toShardLsID, noTx, startIndex, epoch, value):
    countTx = 0
    countErr = 0

    for i in range(noTx):
        lsTx = {}
        count = 3
        flag = 0
        for shardID in toShardLsID:
            if shardID != fromShardID:
                lsTx[paymentAddLs[shardID][startIndex + i]] = value
                flag += 1
                if flag >= count:
                    break

        data = {
            "jsonrpc": "1.0",
            "method": "createandsendtransaction",
            "params": [
                privKeyLs[fromShardID][startIndex + i],
                lsTx,
                10,
                1,
                '',
                str(epoch)
            ],
            "id": 1
        }
        dataJson = json.dumps(data)
        # r = requests.post(url=URL + ":" + PORT[fromShardID], data=dataJson)
        r = requests.post(url=FULLNODEURL, data=dataJson)
        countTx += 1
        if r.status_code != 200:
            logging.info("Error: %s", r.status_code)
            logging.info(dataJson)
            countErr += 1
        else:
            response = r.json()
            if response["Error"] != None:
                logging.info("Error: %s", response["Error"]["Message"])
                logging.info(dataJson)
                countErr += 1

        time.sleep(0.5)

    logging.info("[%s] Done Thread [%s] - #%s Tx and #%s Error Epoch: %s", shardID, threadID, countTx, countErr, int(time.time()))
    return countTx, countErr

def DistrubutePRV(shardID, lsShardID):
    totalTx = 0
    totalErr = 0
    startTime = int(time.time())
    logging.info("Start Time Epoch: %s", startTime)
    noInitTx, noInitErr = InitPRVToShard(shardID, 9000000)
    totalTx += noInitTx

    totalErr += noInitErr

    time.sleep(120)

    logging.info("Send each 1 PRV from address in Shard to 7 addresses in another Shards")
    epoch = int(time.time()) + 9 * 60
    logging.info("Start Epoch: %s", epoch)
    noTx, noErr = SendPRVFromShardToShardThread(shardID, lsShardID, epoch, 3500000)
    totalTx += noTx
    totalErr += noErr

    logging.info("End Time Epoch: %s", int(time.time()))
    logging.info("Total Tx request: %s", totalTx)
    logging.info("Total Tx err: %s", totalErr)

    logging.info("Waiting to count total Tx ...")
    while True:
        time.sleep(30)
        checkTx = GetTxonChain(startTime, shardID)
        logging.info("Total TX: %s", checkTx)
        if checkTx >= totalTx - totalErr - 20:
            break
    logging.info("Done!!!")

testDistrubuteVector = [(0, [1, 2, 3, 4, 5, 6, 7]),
                        (1, [0, 2, 3, 4, 5, 6, 7]),
                        (2, [0, 1, 3, 4, 5, 6, 7]),
                        (3, [0, 2, 1, 4, 5, 6, 7]),
                        (4, [0, 2, 3, 1, 5, 6, 7]),
                        (5, [0, 2, 3, 4, 1, 6, 7]),
                        (6, [0, 2, 3, 4, 5, 1, 7]),
                        (7, [0, 2, 3, 4, 5, 6, 1])
                        ]
for item in testDistrubuteVector:
    DistrubutePRV(item[0], item[1])


