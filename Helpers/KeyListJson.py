import json
from typing import Union

from Helpers.Logging import config_logger
from Objects.AccountObject import Account, AccountGroup

logger = config_logger(__name__)


class KeyListJson:
    def __init__(self, json_file_path='keylist.json'):
        with open(json_file_path, 'r') as key_list_json:
            self._data = json.load(key_list_json)

    @staticmethod
    def __raw_key_set_to_account(data, **kwargs) -> Union[Account, None]:
        """
        @param data:
        @return: Account object, if {data} does not contain "PrivateKey" return None
        """
        try:
            return Account(data['PrivateKey'], **kwargs)
        except KeyError:
            logger.error(f'Raw data block does not contain private key, only: {list(data.keys())}')

    def get_list_account(self, list_name, **kwargs):
        key_set_raw = self._data[list_name]
        if isinstance(key_set_raw, list):
            account_set = AccountGroup()
            for key_set in key_set_raw:
                acc_obj = KeyListJson.__raw_key_set_to_account(key_set, **kwargs)
                if acc_obj is not None:
                    account_set.append(acc_obj)
        elif isinstance(key_set_raw, dict):
            account_set = {}
            for shard_id, key_set_list in key_set_raw.items():
                shard_acc_list = AccountGroup()
                for key_set in key_set_list:
                    acc_obj = KeyListJson.__raw_key_set_to_account(key_set)
                    if acc_obj is not None:
                        shard_acc_list.append(acc_obj)
                account_set[shard_id] = shard_acc_list
        else:
            raise TypeError(f'Raw list "{list_name}" must be list or dict, got {type(key_set_raw)} instead')
        return account_set

    def get_beacon_accounts(self, **kwargs) -> AccountGroup:
        return self.get_list_account('Beacon', **kwargs)

    def get_shard_fix_validator_accounts(self, **kwargs):
        """
        @return: Dict of AccountGroup { shard : AccountGroup }
        """
        return self.get_list_account('Shard', **kwargs)

    def get_staker_accounts(self, **kwargs) -> AccountGroup:
        return self.get_list_account('Staker', **kwargs)
