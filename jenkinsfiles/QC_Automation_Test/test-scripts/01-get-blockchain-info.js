const axios = require('axios');
const assert = require('assert').strict;

const RPC_ENDPOINT = 'http://127.0.0.1:8334/';
const MAXIMUM_WAIT_TIME_MS = 600000;
const WAIT_INTERVAL_MS = 5000;

function sleep(ms) {
    console.log(`Sleep for ${ms} milliseconds`);
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function _getBlockchainInfo() {
    const result = await axios({
        method: 'POST',
        url: RPC_ENDPOINT,
        data: {
            "id": 1,
            "jsonrpc": "1.0",
            "method": "getblockchaininfo",
            "params": []
        }
    });

    if (!result?.data?.Result?.BestBlocks) {
        console.log('\tBestBlocks not found');
        return false;
    }

    const bestBlocks = result?.data?.Result?.BestBlocks;

    for (const [blockKey, blockValue] of Object.entries(bestBlocks)) {
        console.log(`\tChecking BestBlocks[${blockKey}]`);

        if (!blockValue?.Height || blockValue?.Height <= 5) {
            console.log(`\tBestBlocks[${blockKey}] block height assertion error: ` + JSON.stringify(blockValue));
            return false;
        }
        console.log(`\tBestBlocks[${blockKey}].Height=${blockValue?.Height}`);
    }

    return true;
}

async function doCheckBlockchainInfo() {
    const startTime = new Date();
    let isBlockchainNetworkOK = false;

    do {
        isBlockchainNetworkOK = await _getBlockchainInfo();

        if (!isBlockchainNetworkOK) {
            console.log(`\tBlockchain network not ready, retry checking after ${WAIT_INTERVAL_MS}ms.`);
            await sleep(WAIT_INTERVAL_MS);
        }
        else {
            break;
        }

    }
    while ((new Date() - startTime) <= MAXIMUM_WAIT_TIME_MS);

    if (!isBlockchainNetworkOK) {
        throw new Error('\tBlockchain BestBlocks Height is invalid, exiting');
    }
}


async function main() {
    await doCheckBlockchainInfo();
}

main()
    .then(result => {
        console.log('01-get-blockchain-info.js DONE');
        process.exit(0);
    })
    .catch(error => {
        console.log('01-get-blockchain-info.js error', error);
        process.exit(1);
    });