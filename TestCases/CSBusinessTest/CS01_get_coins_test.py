import pytest

from APIs.BackEnd.CoinService import CoinService
from Configs.Constants import PRV_ID
from Objects.AccountObject import COIN_MASTER

END_POINT = 'http://51.161.119.66:9009'


@pytest.mark.parametrize("account, token_id, get_coin_version, offset, limit, key_type, key_value", [
    (COIN_MASTER, PRV_ID, 1, 0, 1000, CoinService.K_TYPE_PAYMENT, COIN_MASTER.payment_key),
    (COIN_MASTER, PRV_ID, 2, 0, 1000, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
    (COIN_MASTER, PRV_ID, 2, 1, 1, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
    (COIN_MASTER, PRV_ID, 3, 0, 1000, CoinService.K_TYPE_OTA, COIN_MASTER.ota_k),
])
def test_get_coin_with_key_positive(account, token_id, get_coin_version, offset, limit, key_type, key_value):
    CS = CoinService.CoinServiceApi(END_POINT)
    response = CS.get_coins(token_id, get_coin_version, offset, limit, **{key_type: key_value})
    response.expect_no_error()
    cs_coin_list = response.get_coin_list()
    balance = COIN_MASTER.get_balance(token_id)
    assert sum(cs_coin_list) == balance
    response.expect_error()


@pytest.mark.parametrize("account, token_id, version, offset, limit, key_type, key_value", [
])
def test_trash_talk(account, token_id, version, offset, limit, key_type, key_value):
    pass
