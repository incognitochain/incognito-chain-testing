# run like a normal test case: ./run.sh [testbed] [testdata] path/to/this/script
#                          or: ./run.sh [testbed] - path/to/this/script
#                         to ignore [testdata] since it won't be used
import pytest

from Configs.Constants import PDEX_ID
from Objects.AccountObject import *
from Objects.IncognitoTestCase import SUT

COIN_MASTER.req_to(SUT())
submit_key_status = SUT().transaction().submit_key_info(COIN_MASTER.ota_k)
if submit_key_status.get_result() == Status.SubmitKey.NOT_SUBMITTED:
    COIN_MASTER.submit_key()
    WAIT(60)


def amp(num):
    return int(num * ChainConfig.Dex3.AMP_DECIMAL)


def d9(num):
    return int(num * 1e9)


def d6(num):
    return int(num * 1e6)


pDAI = '0000000000000000000000000000000000000000000000000000000000000da1'
pBTC = '0000000000000000000000000000000000000000000000000000000000000b7c'
pXMR = '0000000000000000000000000000000000000000000000000000000000011112'
pBNB = '000000000000000000000000000000000000000000000000000000000000b11b'
pETH = '000000000000000000000000000000000000000000000000000000000000e776'
pWETH = '000000000000000000000000000000000000000000000000000000000111e776'
pBUSD = '00000000000000000000000000000000000000000000000000000000000b115d'
pUSDC = '00000000000000000000000000000000000000000000000000000000000115dc'
pUSDT = '00000000000000000000000000000000000000000000000000000000000115d7'


def mint_tokens():
    TOK = [{'id': pDAI, 'name': 'pDai'}, {'id': pBTC, 'name': 'pBTC'}, {'id': pXMR, 'name': 'pXMR'},
           {'id': pBNB, 'name': 'pBNB'}, {'id': pETH, 'name': 'pETH'}, {'id': pWETH, 'name': 'pWETH'},
           {'id': pBUSD, 'name': 'pBUSD'}, {'id': pUSDC, 'name': 'pUSDC'}, {'id': pUSDT, 'name': 'pUSDT'}]
    for t in TOK:
        token_ids, token_name = t['id'], t['name']
        if not COIN_MASTER.sum_my_utxo(token_ids):
            tx = COIN_MASTER.issue_centralize_token(COIN_MASTER, token_ids, token_name,
                                                    pow(2, 62)).get_transaction_by_hash()
    for t in TOK:
        COIN_MASTER.wait_for_balance_change(t['id'], 0)


def contribute(contrib_data, test=False):
    pde = SUT().pde3_get_state()
    COIN_MASTER.pde3_get_my_nft_ids(pde)
    if not COIN_MASTER.nft_ids:
        COIN_MASTER.pde3_mint_nft()
        WAIT(ChainConfig.BLOCK_TIME * 3)
    for c in contrib_data:
        pool_size, a = c['size'], c['amp']
        t1, t2 = pool_size.keys()
        contrib_id = f'{t1[-8:]}_{t2[-8:]}'
        skip = False
        if pde.get_pool_pair(size=pool_size, amp=a):
            print(f'{pool_size}, {a} EXISTED !!!!')
            continue
        for t, amount in pool_size.items():
            print(f'{t}, {contrib_id}, {amount}, {a}')
            COIN_MASTER.pde3_add_liquidity(t, amount, a, contrib_id).get_transaction_by_hash() if not test else None


def print_pair_id(contrib_data):
    pde = SUT().pde3_get_state()
    pairs = []
    for c in contrib_data:
        pool_size = c['size']
        a = c['amp']
        token_ids = list(pool_size.keys())
        try:
            pair_id = pde.get_pool_pair(size=pool_size, amp=a)[0].get_pool_pair_id()
            pairs.append(pair_id)
        except:
            pair_id = f"try again: {token_ids}"
        print(f"ID: {pair_id}")
    return pairs


contrib = [
    {"size": {PRV_ID: d9(175438.4211), pUSDC: d6(333333)}, 'amp': amp(2)},
    {"size": {PRV_ID: d9(175438.4211), pDAI: d9(333333)}, 'amp': amp(2)},
    {"size": {PRV_ID: d9(175438.4211), pBUSD: d9(333333)}, 'amp': amp(2)},
    {"size": {pBTC: d9(7.01754386), pUSDT: d6(400000)}, 'amp': amp(3)},
    {"size": {pETH: d9(114.2857143), pUSDT: d6(400000)}, 'amp': amp(2.5)},
    {"size": {pXMR: d9(1428.571429), pUSDT: d6(400000)}, 'amp': amp(2)},
    {"size": {pBNB: d9(888.8888889), pUSDT: d6(400000)}, 'amp': amp(2.5)},
    {"size": {pUSDT: d6(100000), pUSDC: d6(100000)}, 'amp': amp(200)},
    {"size": {pUSDT: d6(100000), pDAI: d9(100000)}, 'amp': amp(200)},
    {"size": {pUSDT: d6(100000), pBUSD: d9(100000)}, 'amp': amp(200)},
    {"size": {pETH: d9(25), pWETH: d9(25)}, 'amp': amp(200)},
]

contrib_2 = [
    {"size": {PRV_ID: d9(175438.4211), pUSDC: d6(333333)}, 'amp': amp(2.2)},
    {"size": {PRV_ID: d9(175438.4211), pDAI: d9(333333)}, 'amp': amp(2.2)},
    {"size": {PRV_ID: d9(175438.4211), pBUSD: d9(333333)}, 'amp': amp(2.2)},
    {"size": {PRV_ID: d9(263157.8947), PDEX_ID: d9(5000000)}, 'amp': amp(3)},
    {"size": {pBTC: d9(7.01754386), pUSDT: d6(400000)}, 'amp': amp(3)},
    {"size": {pETH: d9(114.2857143), pUSDT: d6(400000)}, 'amp': amp(2.5)},
    {"size": {pXMR: d9(1428.571429), pUSDT: d6(400000)}, 'amp': amp(2)},
    {"size": {pBNB: d9(888.8888889), pUSDT: d6(400000)}, 'amp': amp(2.5)},
    {"size": {pUSDT: d6(100000), pUSDC: d6(100000)}, 'amp': amp(100)},
    {"size": {pUSDT: d6(100000), pDAI: d9(100000)}, 'amp': amp(100)},
    {"size": {pUSDT: d6(100000), pBUSD: d9(100000)}, 'amp': amp(100)},
    {"size": {pETH: d9(25), pWETH: d9(25)}, 'amp': amp(100)},
]


# MAIN
@pytest.mark.parametrize("contribute_data", [
    contrib_2,
])
def test_create_data(contribute_data):
    mint_tokens()
    contribute(contribute_data, test=False)
    WAIT(ChainConfig.BLOCK_TIME * 5)
    return print_pair_id(contribute_data)
