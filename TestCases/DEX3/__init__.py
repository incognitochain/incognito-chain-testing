from Configs.Constants import coin
from Objects.IncognitoTestCase import ACCOUNTS

# declaration
TOKEN_OWNER = ACCOUNTS[0]
INIT_PAIR_IDS = []
POOL_X0 = 0
POOL_Y0 = 0
TOKEN_X = "12665208fd4b325c7936468def1ea852b7d47a6cef065d766b0a1638ef4f0f51" # AUTO-pADA
TOKEN_Y = "9db780c5a82240d38411eef30ceb49f2da68b2de0eb8dfac98aee3552e022421" # AUTO-pBTC

# ---------------------------- SET UP -------------------------------
ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()
# setup new token, un-comment to create new tokens
# tx_init_x = TOKEN_OWNER.init_custom_token_new_flow(coin(100000))
# TOKEN_X = tx_init_x.get_token_id()
# tx_init_x.get_transaction_by_hash()
# tx_init_y = TOKEN_OWNER.init_custom_token_new_flow(coin(10000000))
# TOKEN_Y = tx_init_y.get_token_id()
# tx_init_y.get_transaction_by_hash()
# TOKEN_OWNER.wait_for_balance_change(TOKEN_X, 0)
# TOKEN_OWNER.wait_for_balance_change(TOKEN_Y, 0)

TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_X)
TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_Y)
