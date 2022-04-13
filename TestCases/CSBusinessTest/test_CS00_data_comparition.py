import deepdiff
import pytest

from APIs.BackEnd.CoinService.CoinService import CoinServiceApi
from Configs.Configs import CoinServiceConfig
from Helpers import Logging
from TestCases import ota_key_list

CS_prod = CoinServiceApi(CoinServiceConfig.PROD_ENDPOINT)
CS_beta = CoinServiceApi(CoinServiceConfig.BETA_ENDPOINT)


def setup_method():
    Logging.INFO("""
    Comparing production to beta
    """)


def test_compare_token_list():
    token_list_prod = CS_prod.get_token_list().expect_no_error()
    token_list_beta = CS_beta.get_token_list().expect_no_error()
    assert token_list_prod == token_list_beta


def test_compare_list_pool():
    pool_list_prod = CS_prod.get_list_pool().expect_no_error()
    pool_list_beta = CS_beta.get_list_pool().expect_no_error()
    assert pool_list_prod == pool_list_beta


def test_compare_pending_order():
    list_pool = CS_prod.get_list_pool().get_pool_info("PoolID")
    for pool in list_pool:
        dd = deepdiff.DeepDiff(CS_prod.get_pending_order(pool), CS_beta.get_pending_order(pool))
        assert not dd


@pytest.mark.parametrize("ota_key", ota_key_list)
def test_compare_key_info(ota_key):
    key_info_prod = CS_prod.get_key_info(ota_key)
    key_info_beta = CS_beta.get_key_info(ota_key)
    dd = deepdiff.DeepDiff(key_info_prod, key_info_beta, exclude_regex_paths="LastScanned")


@pytest.mark.parametrize("ota_key", ota_key_list)
def test_compare_key_info(ota_key):
    NFTs = CS_prod.get_key_info(ota_key)
