import json
from concurrent.futures import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Configs.Constants import PRV_ID
from Configs.TokenIds import pUSDC
from Helpers import Logging
from Helpers.Time import get_current_date_time, WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from TestCases.ChainTestBusiness.DEX3.Suite2 import PATH1

TRADER = ACCOUNTS[0]
BOOKER = ACCOUNTS[1]
HOLDER = ACCOUNTS[2]


def no_setup_function():
    pde = SUT().pde3_get_state()
    try:
        pair_id = pde.get_pool_pair(nft_id=COIN_MASTER.nft_ids[0], tokens=[PRV_ID, pUSDC])[0].get_pool_pair_id()
    except IndexError:
        pass
        # contribute
        # contrib_id = f"DAO_contrib_RPV_pUSDC_setup_{get_current_date_time()}"
        # COIN_MASTER.pde3_add_liquidity()


def test_multiple_tx_type_in_a_block():
    pde_b4 = SUT().pde3_get_state()
    COIN_MASTER.pde3_get_my_nft_ids()
    ACCOUNTS.pde3_get_nft_ids(pde_b4)
    ACCOUNTS.pde3_mint_nft()
    pde_param = pde_b4.get_pde_params()

    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, int(10e9), int(20e9), pUSDC)
    contrib_id = f"multi_inst_contrib_RPV_pUSDC_{get_current_date_time()}"
    contrib_amount_prv = int(10000e9)
    contrib_amount_pusdc = int(20000e9)
    new_dex_param = {}
    tpf = []
    b_height_b4 = SUT().help_get_beacon_height()
    with ThreadPoolExecutor() as tpe:
        tpf.append(tpe.submit(COIN_MASTER.pde3_modify_param, pde_param.get_configs()))
        tpf.append(tpe.submit(BOOKER.pde3_add_order, pUSDC, PRV_ID, PATH1[0], 1000, 2000))
        tpf.append(tpe.submit(TRADER.pde3_trade, pUSDC, PRV_ID, int(1.34e8), 1, PATH1, int(1.34e6)))
        tpf.append(tpe.submit(HOLDER.pde3_add_liquidity, PRV_ID, int(2e9), 20000, contrib_id, pool_pair_id=PATH1[0]))

    tx_hashes = [r.result().expect_no_error().get_tx_id() for r in tpf]
    for tx in tx_hashes:
        SUT().get_tx_by_hash(tx)
    WAIT(ChainConfig.BLOCK_TIME * 3)
    b_height_af = SUT().help_get_beacon_height()
    beacon_blocks = {height: SUT().get_beacon_block(height) for height in range(b_height_b4, b_height_af + 1)}
    INST_COUNT = {}
    for height, bb in beacon_blocks.items():
        for tx in tx_hashes:
            if bb.is_tx_in_instructions(tx):
                try:
                    INST_COUNT[height] += 1
                except KeyError:
                    INST_COUNT[height] = 1
    Logging.INFO(f" SUMMARY:\n"
                 f"{json.dumps(INST_COUNT, indent=3)}")
