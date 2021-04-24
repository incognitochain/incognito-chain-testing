BURNING_ADDR = \
    "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
PRV_ID = "0000000000000000000000000000000000000000000000000000000000000004"

# old: for main net
# PBNB_ID = "b2655152784e8639fa19521a7035f331eea1f1e911b2f3200a507ebb4554387b"
# PBTC_ID = "b832e5d3b1f01a4f0623f7fe91d6673461e1f5d37d91fe78c5c2e6183ff39696"

# new: for local
PBNB_ID = "6abd698ea7ddd1f98b1ecaaddab5db0453b8363ff092f0d8d7d4c6b1155fb693"
PBTC_ID = "ef5947f70ead81a76a53c7c8b7317dd5245510c665d3a13921dc9a581188728b"

DAO_PRIVATE_K = \
    "112t8roafGgHL1rhAP9632Yef3sx5k8xgp8cwK4MCJsCL1UWcxXvpzg97N4dwvcD735iKf31Q2ZgrAvKfVjeSUEvnzKJyyJD3GqqSZdxN4or"


class ChainConfig:
    BLOCK_PER_EPOCH = 20
    RANDOM_TIME = 10
    BLOCK_TIME = 10
    BASIC_REWARD_PER_BLOCK = 400000000
    DAO_REWARD_PERCENT = 0.1
    ACTIVE_SHARD = 2
    BEACON_COMMITTEE_SIZE = 4
    FIX_BLOCK_VALIDATOR = 4
    SHARD_COMMITTEE_SIZE = 6
    PRIVACY_VERSION = 2
    STK_AMOUNT = 1750000000000
    STK_WAIT_TIME_OUT = 4000  # seconds
    ONE_COIN = 1000000000
    MIN_FEE_PER_KB = 100000

    class Portal:
        FEE_RATE = 0.0001
        COLLATERAL_PERCENT = 1.5
        COLLATERAL_LIQUIDATE_PERCENT = 1.2
        COLLATERAL_LIQUIDATE_TO_POOL_PERCENT = 1.05
        REQ_TIME_OUT = 15  # minutes
        # REQ_TIME_OUT = 60  # minutes, TestNet
        FEEDER_PRIVATE_K = '112t8roezimTQwKbmsoxY9h494xhMZNBe94ux6hCH4SaFYBFnFXS9J' \
                           'oNbUjmeFLQiFWHeFP9MLPcy1sEiDasdW4ZkzEDzXDLG3wmwMU551tv'

    class Dex:
        MIN_PRV_IN_POOL_FOR_TOKEN_FEE = 10000000000000

    @staticmethod
    def is_first_height_of_epoch(height):
        """
        @param height:
        @return: True if {height} is first height of epoch, else False
        """
        return height % ChainConfig.BLOCK_PER_EPOCH == 1

    @staticmethod
    def get_epoch_n_block_time(num_of_epoch=1, number_of_block=0):
        """
        @param num_of_epoch: default = 1
        @param number_of_block:
        @return: int (seconds) for {num_of_epoch} + {number_of_block} epoch to complete
        """
        num_of_epoch = max(0, num_of_epoch)  # make sure epoch and block must always >=0
        number_of_block = max(0, number_of_block)
        block_time = ChainConfig.BLOCK_TIME * number_of_block
        epoch_time = ChainConfig.BLOCK_PER_EPOCH * ChainConfig.BLOCK_TIME * num_of_epoch
        return epoch_time + block_time

    @staticmethod
    def get_running_config():
        # collecting running chain config
        from Objects.IncognitoTestCase import SUT
        bbs = SUT().get_beacon_best_state_info()
        ChainConfig.ACTIVE_SHARD = bbs.get_active_shard()
        ChainConfig.BEACON_COMMITTEE_SIZE = bbs.get_max_beacon_committee_size()
        ChainConfig.SHARD_COMMITTEE_SIZE = bbs.get_max_shard_committee_size()
        chain_info = SUT().get_block_chain_info()
        ChainConfig.BLOCK_PER_EPOCH = chain_info.get_block_per_epoch_number()
        block_3 = SUT().get_shard_block_by_height(0, 3)
        block_4 = SUT().get_shard_block_by_height(0, 4)
        ChainConfig.BLOCK_TIME = block_4.get_time() - block_3.get_time()


class TestConfig:
    KEY_VERSION = 2  # payment key version [1 or 2]
    TX_VER = 2


def coin(amount, nano=True):
    """
    :param amount:
    :param nano: if nano = true, x1000000000. else /1000000000
    :return:
    """
    if nano:
        return amount * ChainConfig.ONE_COIN
    else:
        return amount / ChainConfig.ONE_COIN


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
