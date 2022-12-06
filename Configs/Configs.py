class TestConfig:
    KEY_VERSION = 2  # payment key version [1 or 2]
    TX_VER = 2
    TEST_BED = 'TestNet'
    TEST_DATA = 'account_sample'


class ChainConfig:
    ACCESS_TOKEN = '0ec910a54ffbf2a0bdfc0c8b05e8b5445e51a2ae54f659a35ac7ad9980e4fd2c'
    # ACCESS_TOKEN = '0c3d46946bbf99c8213dd7f6c640ed6433bdc056a5b68e7e80f5525311b0ca11'
    BLOCK_PER_EPOCH = 20
    RANDOM_TIME = 10  # the n(th) height in epoch to call random function, usually = BLOCK_PER_EPOCH/2 not BLOCK_TIME/2
    BLOCK_TIME = 10
    BASIC_REWARD_PER_BLOCK = 400000000
    DAO_REWARD_PERCENT = 0.1
    ACTIVE_SHARD = 2
    BEACON_COMMITTEE_SIZE = 4
    FIX_BLOCK_VALIDATOR = 4
    SHARD_COMMITTEE_SIZE = 6
    PRIVACY_VERSION = 2
    STK_AMOUNT = 1750000000000
    STK_WAIT_TIME_OUT = 80000  # seconds
    FEE_MIN_PER_KB = 1e6
    FEE_MIN = 1e8

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

    class Dex3:
        DECIMAL = 10000
        TRADE_PATH_MAX_LEN = 3
        NFT_MINT_REQ = 100

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
        return ChainConfig.BLOCK_TIME * (number_of_block + num_of_epoch * ChainConfig.BLOCK_PER_EPOCH)

    @staticmethod
    def get_running_config(from_node=None, from_height=None):
        # collecting running chain config
        if not from_node:
            from Objects.IncognitoTestCase import SUT
            from_node = SUT()
        bbs = from_node.get_beacon_best_state_info()
        if from_height is None:
            from_height = bbs.get_beacon_height() - 1
        chain_info = from_node.get_block_chain_info()
        ChainConfig.BEACON_COMMITTEE_SIZE = bbs.get_max_beacon_committee_size()
        ChainConfig.ACTIVE_SHARD = bbs.get_active_shard()
        ChainConfig.SHARD_COMMITTEE_SIZE = bbs.get_max_shard_committee_size()
        ChainConfig.FIX_BLOCK_VALIDATOR = bbs.get_min_shard_committee_size()
        ChainConfig.BLOCK_PER_EPOCH = chain_info.get_block_per_epoch_number()
        ChainConfig.BLOCK_TIME = from_node.cal_current_block_time()
        ChainConfig.RANDOM_TIME = ChainConfig.BLOCK_PER_EPOCH / 2


class CoinServiceConfig:
    PROD_ENDPOINT = "https://api-coinservice.incognito.org"
    BETA_ENDPOINT = "http://51.83.36.184:9005"
