from Configs.Constants import PRV_ID
from Configs.TokenIds import pUSDC, pWETH, pUSDT, pETH, pDAI
from Helpers.Logging import config_logger
from Objects.IncognitoTestCase import SUT

logger = config_logger(__name__)
pde = SUT().pde3_get_state()
PATH1 = [pde.get_pool_pair(tokens=[PRV_ID, pUSDC])[0].get_pool_pair_id()]
trace5 = [PRV_ID, pDAI, pUSDT, pETH, pWETH]
trace6 = [pUSDT, pDAI, PRV_ID, pUSDC, pUSDT, pETH]
PATH4 = []
PATH5 = []
logger.info("Making path 5")
for i in range(len(trace5) - 1):
    token1, token2 = trace5[i], trace5[i + 1]
    PATH4.append(pde.get_pool_pair(tokens=[token1, token2])[0].get_pool_pair_id())

logger.info("Making path 6")
for i in range(len(trace6) - 1):
    token1, token2 = trace6[i], trace6[i + 1]
    PATH5.append(pde.get_pool_pair(tokens=[token1, token2])[0].get_pool_pair_id())
