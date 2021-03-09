const axios = require('axios');
const assert = require('assert').strict;

const RPC_ENDPOINT = 'http://127.0.0.1:8334/';

const MAXIMUM_TRANSACTION_WAIT_MS = 600000;
const TRANSACTION_WAIT_INTERVAL_MS = 5000;

function sleep(ms) {
    console.log(`Sleep for ${ms} milliseconds`);
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function _createAndSendTransaction() {
    console.log('createandsendtransaction');
    const createTransactionRPCResult = await axios({
        method: 'POST',
        url: RPC_ENDPOINT,
        data: {
            "id": 1,
            "jsonrpc": "1.0",
            "method": "createandsendtransaction",
            "params": [
                "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or",
                {
                    "12Rtdi54JhcJsDBYvgCFCb8Dmwhpt5S8AiRD2RQvqJFKUDLA4R2jyM2tnmBir5bRp2w1Ydp1Y85yN86ni9t2GbMNx5LaE3VmwDftjE1": 1750000000100,
                    "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756": 1000000000000999,
                    "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5": 1750000000100,
                    "12Rxy3sVosEnN5FJdHGYV41GkDinGLwUudr5k7vCfLJ9Rk7KijzJhgDPuKu4THtD8RBNYyzb462iiEh1W13niiQHbfmHdNedycb7keF": 3500000000200,
                    "12Rrgnrh5KDKLZgQvX13MrjsXQr8NMmWcspzcRKVBwB7YuyRmJsm4aJeGwpnXoeeNtKP9FMt2ExeSCAe2yUuA4yAbUfMQEpSNT1Aju5": 1750000000100,
                    "12RtmpqwyzghGQJHXGRhXnNqs7SDhx1wXemgAZNC2xePj9DNpxcTZfpwCeNoBvvyxNU8n2ChVijPhSsNhGCDmFmiwXSjQEMSef4cMFG": 1750000000100,
                    "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr": 1750000000100,
                    "12S1DR4dMETwoGVz3KmYpVCeVYDpsjSMEjqQTJwwjoX3Gi41Ue56o6faB6LCrHQ78wXauVSNs2zjYNPWsJ32mx6QYkBAjUdJkHpPHES": 1750000000100,
                    "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci": 1000000000000999,
                    "12RvFuCs3hLm886pfA6KHyuD1MGqD663g8XtaiAQuSk611kuAv8zyS52CRD2uhxF5L2xjCNn4hbjkyc86L64vTyjXCEHAsRkpSMGJ6D": 1750000000100
                },
                -1,
                0
            ]
        }
    });

    if (!createTransactionRPCResult?.data?.Result?.TxID) {
        console.log('createTransactionRPCResult', JSON.stringify(createTransactionRPCResult?.data, null, 2));
        throw new Error('TxID not found');
    }
    const transactionHash = createTransactionRPCResult?.data?.Result?.TxID;

    return transactionHash;
}

async function _getTransactionByHash(transactionHash) {
    console.log(`gettransactionbyhash TX ${transactionHash}`);
    const getTransactionRPCResult = await axios({
        method: 'POST',
        url: RPC_ENDPOINT,
        data: {
            "jsonrpc": "1.0",
            "method": "gettransactionbyhash",
            "params": [transactionHash],
            "id": 1
        }
    });

    if (!getTransactionRPCResult?.data?.Result?.BlockHeight) {
        console.log(`\tTX ${transactionHash} BlockHeight is undefined`);
        return null;
    }

    if (getTransactionRPCResult?.data?.Result?.BlockHeight === '') {
        console.log(`\tTX ${transactionHash} BlockHeight is empty`);
        return null;
    }

    return getTransactionRPCResult?.data;
}

async function doCheckGetTransactionByHash(transactionHash) {
    const startTime = new Date();
    let transactionData = null;

    do {
        transactionData = await _getTransactionByHash(transactionHash);

        if (!transactionData) {
            console.log(`\tTransaction data not ready, retry checking after ${TRANSACTION_WAIT_INTERVAL_MS}ms.`);
            await sleep(TRANSACTION_WAIT_INTERVAL_MS);
        }
        else {
            break;
        }

    }
    while ((new Date() - startTime) <= MAXIMUM_TRANSACTION_WAIT_MS);

    if (!transactionData) {
        throw new Error('\tTransaction BlockHeight is invalid, exiting');
    }
}


async function main() {

    const transactionHash = await _createAndSendTransaction();

    await doCheckGetTransactionByHash(transactionHash);
}

main()
    .then(result => {
        console.log('02-create-and-send-transactions.js DONE');
        process.exit(0);
    })
    .catch(error => {
        console.log('02-create-and-send-transactions.js error', error);
        process.exit(1);
    });