import copy

from Objects.IncognitoTestCase import ACCOUNTS

CHECKPOINT_HEIGHT = 12345
ACCOUNTS.convert_payment_address_to_version(1)  # just to make sure that the accounts is at version 1 
ACCOUNT_V2 = copy.deepcopy(ACCOUNTS).convert_payment_address_to_version(2)
