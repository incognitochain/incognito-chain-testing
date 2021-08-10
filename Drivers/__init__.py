import copy
import json
from abc import abstractmethod

import Helpers.Logging as Log


class ResponseBase:
    def __init__(self, response=None, more_info=None):
        if isinstance(response, ResponseBase):  # for cloning object
            self.response = response.response
            self.more_info = response.more_info
        else:
            self.response = response
            self.more_info = more_info
            log_str = ''
            try:
                log_str += f'[{self.response.status_code}] '
            except AttributeError:
                pass
            try:
                log_str += f'{self.response.url}'
            except AttributeError:
                log_str += f'{more_info}'
            log_str += f'{self.__str__()}' if response else ''
            Log.DEBUG(log_str, ResponseBase.__name__)

    def __deepcopy__(self, memodict={}):
        r = ResponseBase()
        r.response = copy.deepcopy(self.response)
        r.more_info = copy.deepcopy(self.more_info)
        return r

    def __str__(self):
        return f'\n{json.dumps(self.data(), indent=3)}'

    @abstractmethod
    def expect_error(self, expecting_error='any error'):
        pass

    @abstractmethod
    def expect_no_error(self, additional_msg_if_fail=''):
        pass

    def data(self):
        try:
            if type(self.response) is str:
                return json.loads(self.response)  # response from WebSocket
            return json.loads(self.response.text)  # response from rpc
        except Exception as e:
            pass

    def get_result(self, string=None, default=None):
        try:
            if string is None:
                return self.data()['Result']
            return self.data()['Result'].get(string, default)
        except(KeyError, TypeError):
            return None

    def get_error_msg(self):
        try:
            return self.data()['Error']['Message']
        except (KeyError, TypeError):
            pass
        try:
            return self.data()['Error']
        except KeyError:
            pass
