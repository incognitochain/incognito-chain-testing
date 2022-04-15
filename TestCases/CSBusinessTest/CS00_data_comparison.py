import deepdiff
import pytest

from APIs.BackEnd.CoinService.CoinService import CoinServiceApi
from Configs.Configs import CoinServiceConfig
from Helpers import Logging

CS_prod = CoinServiceApi(CoinServiceConfig.PROD_ENDPOINT)
CS_beta = CoinServiceApi(CoinServiceConfig.BETA_ENDPOINT)
LIST_OTA_KEYS = [
    "14y6Kq1kid5BeERKF3RibWVThi1frNJXJFi8XCih748ejZWf58eRiazaC8Rcn46DPkmYTQNrA19w9MRB7htvJetyK77NGT8jyCMi127",
    "14y8u9PnJXk5jY9JqtUmPQppKHVVKQxULLye1f7DRmRDwqE5C6Y2AvPtMpk3TzHNy4yF1qaskAnZ77FETDcBuUSUjzv2XDQG2AeE7zz",
    "14yHnUBFi4JFHbWY8MFAd94pNo3UVZLoauyoXqsS4U4fXfqZiiorCwEhPW1XWHdUXFYsEUYqzgNUJb8fmX4QPB94yXGoHaZoimk2Dh9",
    "14yDtWojEdvZrWjfSPqDZishNkQxZLVegPAokpVA99HzZRv7RMdvBXY9nCr1ShSK5C1zJ7uUBJAA3t4nWGftGBKn8n2jtjWknvjPrBo"]
NFT_IDS = []
for ota_key in LIST_OTA_KEYS:
    NFT_IDS += CS_prod.get_key_info(ota_key).get_nft_id()
LIST_ALL_POOLS = CS_prod.get_list_pool().get_pool_info("PoolID")


def compare_compare_token_list():
    Logging.INFO("""    Comparing production to beta    """)
    token_list_prod = CS_prod.get_token_list()
    token_list_beta = CS_beta.get_token_list()
    assert token_list_prod == token_list_beta


def compare_compare_list_pool():
    pool_list_prod = sorted(CS_prod.get_list_pool().get_result(), key=lambda item: item["PoolID"])
    pool_list_beta = sorted(CS_beta.get_list_pool().get_result(), key=lambda item: item["PoolID"])
    dd = deepdiff.DeepDiff(pool_list_prod, pool_list_beta, math_epsilon=1)
    assert not dd


def compare_compare_pending_order():
    list_pool = CS_prod.get_list_pool().get_pool_info("PoolID")
    for pool in list_pool:
        assert CS_prod.get_pending_order(pool) == CS_beta.get_pending_order(pool)


def compare_compare_key_info():
    key_info_prod = CS_prod.get_key_info(ota_key)
    key_info_beta = CS_beta.get_key_info(ota_key)
    assert key_info_prod == key_info_beta


@pytest.mark.parametrize("pool", LIST_ALL_POOLS)
def compare_order_history_of_account(pool):
    for nft_id in NFT_IDS:
        history_prod = CS_prod.get_order_book_history(pool, nft_id)
        history_beta = CS_beta.get_order_book_history(pool, nft_id)
        assert history_prod == history_beta


def compare_contribute_history_of_account():
    for nft_id in NFT_IDS:
        history_prod = CS_prod.get_contribute_history(nft_id)
        history_beta = CS_beta.get_contribute_history(nft_id)
        assert history_prod == history_beta


def compare_withdraw_fee_history_of_account():
    for nft_id in NFT_IDS:
        history_prod = CS_prod.get_withdraw_fee_history(nft_id)
        history_beta = CS_beta.get_withdraw_fee_history(nft_id)
        assert history_prod == history_beta


def compare_withdraw_history_of_account():
    for nft_id in NFT_IDS:
        history_prod = CS_prod.get_withdraw_history(nft_id)
        history_beta = CS_beta.get_withdraw_history(nft_id)
        assert history_prod == history_beta


def compare_trade_history_of_account():
    history_prod = CS_prod.get_trade_history(ota_key)
    history_beta = CS_beta.get_trade_history(ota_key)
    assert history_prod == history_beta


def compare_pool_share():
    for nft_id in NFT_IDS:
        history_prod = CS_prod.get_pool_share(nft_id)
        history_beta = CS_beta.get_pool_share(nft_id)
        assert history_prod == history_beta
