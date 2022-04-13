import pytest

from Helpers.Logging import INFO
from Objects.AccountObject import Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT


@pytest.mark.parametrize("setter, rate, expected", [
    (COIN_MASTER, 101, True),
    (COIN_MASTER, 200, True),
    (COIN_MASTER, 201, False),
    (COIN_MASTER, 1, True),
    (COIN_MASTER, 0, False),
    pytest.param(COIN_MASTER, -1, False, marks=pytest.mark.xfail(reason="invalid pram -1")),
    (COIN_MASTER, 30, True),
])
def test_bps_range(setter: Account, rate, expected):
    INFO(f"Get pde state before test")
    pde_b4 = SUT().pde3_get_state()
    pde_predict = pde_b4.clone()
    param_predict = pde_predict.get_pde_params()

    INFO(f"Changing default rate BPS to {rate}")
    param_predict.set_default_fee_rate_bps(rate)
    tx_modify_param = setter.pde3_modify_param(param_predict.get_configs())
    tx_modify_param.get_transaction_by_hash()

    INFO(f"Get new pde state and check")
    SUT().wait_till_next_beacon_height(2)
    pde_af_change = SUT().pde3_get_state()
    modify_status = SUT().dex_v3().get_modify_param_status(tx_modify_param.get_tx_id())
    if expected:
        assert not modify_status.get_error()
        assert pde_af_change == pde_predict
    else:
        assert modify_status.get_error()
        assert pde_af_change == pde_b4
