class BlockChain:
    BLOCK_PER_EPOCH = 10
    RANDOM_TIME = 5
    BASIC_REWARD_PER_BLOCK = 400000000
    DAO_REWARD_PERCENT = 0.1


BURNING_ADDR = \
    "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
PRV_ID = "0000000000000000000000000000000000000000000000000000000000000004"

# old: for main net
# PBNB_ID = "b2655152784e8639fa19521a7035f331eea1f1e911b2f3200a507ebb4554387b"
# PBTC_ID = "b832e5d3b1f01a4f0623f7fe91d6673461e1f5d37d91fe78c5c2e6183ff39696"

# new: for local
PBNB_ID = "6abd698ea7ddd1f98b1ecaaddab5db0453b8363ff092f0d8d7d4c6b1155fb693"
PBTC_ID = "ef5947f70ead81a76a53c7c8b7317dd5245510c665d3a13921dc9a581188728b"

DAO_private_key = \
    "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or"
DAO_payment_key = \
    "12S5Lrs1XeQLbqN4ySyKtjAjd2d7sBP2tjFijzmp6avrrkQCNFMpkXm3FPzj2Wcu2ZNqJEmh9JriVuRErVwhuQnLmWSaggobEWsBEci"
ONE_COIN = 1000000000
MIN_FEE_PER_KB = 100000

PORTAL_COLLATERAL_PERCENT = 1.5
PORTAL_COLLATERAL_LIQUIDATE_PERCENT = 1.2
PORTAL_COLLATERAL_LIQUIDATE_TO_POOL_PERCENT = 1.05


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
    REJECTED_BY_LIQUIDATION = 4
    CANCEL_BY_LIQUIDATION_STAT = 5


class PortalPtokenReqStatus:
    ACCEPTED = 1
    REJECTED = 2


class PortalUnlockCollateralReqStatus:
    ACCEPTED = 1
    REJECTED = 2


class PortalCustodianReqMatchingStatus:
    ACCEPT = 1
    REJECTED = 2


class PortalDepositStatus:
    ACCEPT = 1
    REJECTED = 2


class PortalCustodianWithdrawStatus:
    ACCEPT = 1
    REJECTED = 2


class PortalRewardWithdrawStatus:
    ACCEPT = 1
    REJECTED = 2
