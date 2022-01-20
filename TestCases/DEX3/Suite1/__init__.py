from Configs.Constants import coin, PRV_ID
from Helpers.Logging import config_logger
from Objects.IncognitoTestCase import ACCOUNTS

logger = config_logger(__name__)
# declaration
TOKEN_OWNER = ACCOUNTS[0]
TOKEN_X = "00000000000000000000000000000000000000000000000000000000000000aa"
TOKEN_Y = "00000000000000000000000000000000000000000000000000000000000000bb"

INIT_PAIR_IDS = []
BEACON_HEIGHT_START = 0
COLLECTED_FEE = {}
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
