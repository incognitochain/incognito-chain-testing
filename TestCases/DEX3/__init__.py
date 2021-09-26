import random

from Configs.Constants import coin
from Objects.IncognitoTestCase import ACCOUNTS


ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()
# token_owner = ACCOUNTS.get_random_account()
token_owner = ACCOUNTS.find_account_by_key('1Hc7AkzLe7kHPZY3Ee7MMF6PuSGMTixqJCfki63H84QxhuWQTG')
init_x = coin(100000)
init_y = coin(100000)
pool_x0 = 0
pool_y0 = 0
tx_init_x = token_owner.init_custom_token_new_flow(init_x)
token_X = tx_init_x.get_token_id()
tx_init_x.get_transaction_by_hash()
tx_init_y = token_owner.init_custom_token_new_flow(init_y)
token_Y = tx_init_y.get_token_id()
tx_init_y.get_transaction_by_hash()
token_owner.wait_for_balance_change(token_X, 0)
token_owner.wait_for_balance_change(token_Y, 0)
