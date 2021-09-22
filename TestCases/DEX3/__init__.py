import random

from Objects.IncognitoTestCase import ACCOUNTS

token_owner = ACCOUNTS.get_random_account()
init_x = random.randint(int(10e16), int(10e17))
init_y = random.randint(int(10e16), int(10e17))
pool_x0 = 0
pool_y0 = 0
tx_init_x = token_owner.init_custom_token_new_flow(init_x)
token_X = tx_init_x.get_token_id()
tx_init_x.subscribe_transaction()
tx_init_y = token_owner.init_custom_token_new_flow(init_y)
token_Y = tx_init_y.get_token_id()
tx_init_y.subscribe_transaction()
token_owner.wait_for_balance_change(token_X, 0)
token_owner.wait_for_balance_change(token_Y, 0)
