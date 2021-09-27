import random

from Configs.Constants import coin
from Objects.IncognitoTestCase import ACCOUNTS


ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()
TOKEN_OWNER = ACCOUNTS[0]
init_x = coin(100000)
init_y = coin(100000)
pool_x0 = 0
pool_y0 = 0
tx_init_x = TOKEN_OWNER.init_custom_token_new_flow(init_x)
TOKEN_X = tx_init_x.get_token_id()
tx_init_x.get_transaction_by_hash()
tx_init_y = TOKEN_OWNER.init_custom_token_new_flow(init_y)
TOKEN_Y = tx_init_y.get_token_id()
tx_init_y.get_transaction_by_hash()
TOKEN_OWNER.wait_for_balance_change(TOKEN_X, 0)
TOKEN_OWNER.wait_for_balance_change(TOKEN_Y, 0)
