from Helpers import Logging
from Objects.IncognitoTestCase import ACCOUNTS


def test_gen_ota_receiver():
    Logging.INFO()
    loop = 1000
    ota_receivers = []
    acc = ACCOUNTS[0]
    for i in range(loop):
        ota = acc.portal4_gen_ota_receiver()
        assert not (ota in ota_receivers)
        ota_receivers.append(ota)

    assert len(ota_receivers) == loop
