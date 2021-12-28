from Configs.Constants import coin
from Helpers.Logging import config_logger
from Objects.IncognitoTestCase import ACCOUNTS

logger = config_logger(__name__)
# declaration
TOKEN_OWNER = ACCOUNTS[0]
INIT_PAIR_IDS = []
TOKEN_X = "405195f60daa7faf11c06c74ccff0df70a327a25663887e8d67b09da734f7837."
TOKEN_Y = "5698d6ce531b053677b03ac25c1b073339ad50d013728af1ba34dd8737992105."

# ---------------------------- SET UP -------------------------------
ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()

# Mint new ptoken if needed
__token_amount = coin(10000000)  # 10 mil
__token_list = [TOKEN_X, TOKEN_Y]
for token in __token_list:
    if TOKEN_OWNER.get_balance(token) < __token_amount / 100:
        tx_init = TOKEN_OWNER.init_custom_token_new_flow(__token_amount)
        __token_list[__token_list.index(token)] = tx_init.get_token_id()
        tx_init.get_transaction_by_hash()
        TOKEN_OWNER.wait_for_balance_change(token, 0)

TOKEN_X, TOKEN_Y = __token_list
logger.info(f"""   !!! Using tokens: 
    {TOKEN_X}
    {TOKEN_Y}""")

TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_X)
TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_Y)
