BURNING_ADDR = \
    "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
PRV_ID = "0000000000000000000000000000000000000000000000000000000000000004"

# old: for main net
# PBNB_ID = "b2655152784e8639fa19521a7035f331eea1f1e911b2f3200a507ebb4554387b"
# PBTC_ID = "b832e5d3b1f01a4f0623f7fe91d6673461e1f5d37d91fe78c5c2e6183ff39696"
# PBAT_ID = "1fe75e9afa01b85126370a1583c7af9f1a5731625ef076ece396fcc6584c2b44"
# PUSDT_ID = "716fd1009e2a1669caacc36891e707bfdf02590f96ebd897548e8963c95ebac0"
# PUSDC_ID = "1ff2da446abfebea3ba30385e2ca99b0f0bbeda5c6371f4c23c939672b429a42"

# new: for local
PBNB_ID = "6abd698ea7ddd1f98b1ecaaddab5db0453b8363ff092f0d8d7d4c6b1155fb693"
PBTC_ID = "ef5947f70ead81a76a53c7c8b7317dd5245510c665d3a13921dc9a581188728b"
PETH_ID = "ffd8d42dc40a8d166ea4848baf8b5f6e9fe0e9c30d60062eb7d44a8df9e00854"

DAO_PRIVATE_K = \
    "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or"
ADDR_10MIL = \
    '112t8rnX6L6keA9b4WeM1Ay3BjVkaeib2zv1fw3sLnrmbLSgXwNbBdhnhXiKT28ZhAgoa4RByXhzY5uLe8WxQXpLjR4LmqLz61VKz6mh5PfX'


def coin(amount, nano=True):
    """
    :param amount:
    :param nano: if nano = true, x1000000000. else /1000000000
    :return:
    """
    if nano:
        return int(amount * 1e9)
    else:
        return amount / 1e9


class Status:
    class Portal:
        # more portal status @ common/constants.go
        class PortingStatusByPortingId:
            SUCCESS = 1
            WAITING = 2
            EXPIRED = 3
            LIQUIDATED = 4

        class PortingStatusByTxId:
            ACCEPTED = 1
            REJECTED = 3

        class RedeemStatus:
            SUCCESS = 1
            WAITING = 2
            MATCHED = 3
            LIQUIDATED = 4
            CANCEL_BY_LIQUIDATION_STATUS = 5

        class PtokenReqStatus:
            ACCEPTED = 1
            REJECTED = 2

        class UnlockCollateralReqStatus:
            ACCEPTED = 1
            REJECTED = 2

        class CustodianReqMatchingStatus:
            ACCEPT = 1
            REJECTED = 2

        class DepositStatus:
            ACCEPT = 1
            REJECTED = 2

        class CustodianWithdrawStatus:
            ACCEPT = 1
            REJECTED = 2

        class RewardWithdrawStatus:
            ACCEPT = 1
            REJECTED = 2

        class RedeemMatchingStatus:
            ACCEPT = 1
            REJECTED = 2

    class Dex:
        NOT_FOUND = 0

        class Contribution:
            WAITING = 1
            ACCEPTED = 2
            REFUND = 3  # contrib same token twice with same pair id
            MATCHED_RETURNED = 4  # success with return.....

        class Trading:
            ACCEPTED = 1
            REFUND = 2

        class CrossTrade:
            ACCEPTED = 1
            REFUND = 2

        class WithdrawContribution:
            ACCEPTED = 1
            REJECTED = 2

        class WithdrawFee:
            ACCEPTED = 1
            REJECTED = 2

    class DexV3:
        class Order:
            ACCEPT = 1
            REFUND = 0

        class ShareWithdraw:
            SUCCESS = 1
