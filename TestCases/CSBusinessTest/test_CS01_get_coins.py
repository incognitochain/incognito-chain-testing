import pytest

from APIs.BackEnd.CoinService import CoinService
from Configs.Constants import PRV_ID
from Objects.AccountObject import COIN_MASTER
from TestCases import END_POINT


@pytest.mark.parametrize("account, token_id, get_coin_version, offset, limit, key_type, key_value", [
    (COIN_MASTER, PRV_ID, 1, 0, 1000, CoinService.K_TYPE_PAYMENT, COIN_MASTER.payment_key),
    # (COIN_MASTER, PRV_ID, 2, 0, 1000, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
    # (COIN_MASTER, PRV_ID, 2, 1, 1, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
    # (COIN_MASTER, PRV_ID, 3, 0, 1000, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
])
def test_get_coin_with_key_positive(account, token_id, get_coin_version, offset, limit, key_type, key_value):
    CS = CoinService.CoinServiceApi(END_POINT)
    response = CS.get_coins(token_id, get_coin_version, offset, limit, **{key_type: key_value})
    response.expect_no_error()
    cs_coin_list = response.get_coin_list()
    # fn_coin_list = COIN_MASTER.list_unspent_coin()
    balance = COIN_MASTER.get_balance(token_id)
    assert sum(cs_coin_list) == balance
    # assert len(cs_coin_list) == len(fn_coin_list)
    response.expect_error()


@pytest.mark.parametrize("account, token_id, version, offset, limit, key_type, key_value", [
    (),
    ()
])
def ttest_trash_talk(account, token_id, version, offset, limit, key_type, key_value):
    pass
