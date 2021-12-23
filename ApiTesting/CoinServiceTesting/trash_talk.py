import json
import random

import requests

from ApiTesting import END_POINT_MAINNET_V2
from Helpers import TestHelper
from Helpers.Logging import INFO, DEBUG

HEADER = {'accept-encoding': 'gzip',
          'content-type': 'application/json'}
paths = ['getcoins',
         'checkkeyimages',
         'getkeyinfo',
         'getcoinspending',
         'gettxshistory',
         'submitotakey',
         'parsetokenid',
         'sdhfslf',
         'asldhflrikd']

for p in paths:
    # data = TestHelper.make_random_str_dict()
    data = TestHelper.make_random_str_list()
    # data = TestHelper.make_random_word()
    # data = random.randrange(0, 1000000)
    INFO(f'post: {p}: {data} ')
    res_post = requests.post(END_POINT_MAINNET_V2, data=json.dumps(data), headers=HEADER)
    DEBUG(f'res post: {res_post.text}')
    INFO(f'get: {p}: {data} ')
    res__get = requests.get(END_POINT_MAINNET_V2, headers=HEADER)
    DEBUG(f'res get: {res__get.text}')
    INFO('+++++++++++++++++++')
