burning_address = \
    "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
prv_token_id = "0000000000000000000000000000000000000000000000000000000000000004"
pbnb_id = "b2655152784e8639fa19521a7035f331eea1f1e911b2f3200a507ebb4554387b"
pbtc_id = "b832e5d3b1f01a4f0623f7fe91d6673461e1f5d37d91fe78c5c2e6183ff39696"

master_address_private_key = \
    "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or"
master_address_payment_key = \
    "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci"
ONE_COIN = 1000000000
min_fee_per_kb = 100000


def coin(amount, nano=True):
    """
    :param amount:
    :param nano: if nano = true, x1000000000. else /1000000000
    :return:
    """
    if nano:
        return amount * ONE_COIN
    else:
        return amount / ONE_COIN


class PortalPortingStatusByPortingId:
    SUCCESS = 1
    WAITING = 2
    EXPIRED = 3
    LIQUIDATED = 4


class PortalPortingStatusByTxId:
    ACCEPTED = 1
    REJECTED = 3


class PortalRedeemStatus:
    SUCCESS = 1
    WAITING = 2
    LIQUIDATED = 3


class PortalPtokenReqStatus:
    ACCEPTED = 1
    REJECTED = 2


class PortalUnloclCollateralReqStatus:
    ACCEPTED = 1
    REJECTED = 2


class PortalCustodianReqMatchingStatus:
    ACCEPT = 1
