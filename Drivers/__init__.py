import copy
import json

import deepdiff

from Helpers.Logging import config_logger

logger = config_logger(__name__)


class ResponseBase:
    def __init__(self, response=None, more_info=None):
        if isinstance(response, ResponseBase):  # for casting object
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
            logger.debug(log_str)

    def __deepcopy__(self, memo=None):
        return self.__class__(copy.deepcopy(self.response), copy.deepcopy(self.more_info))

    def __eq__(self, other):
        try:
            dd = deepdiff.DeepDiff(self.data(), other.data(), math_epsilon=1)
            if dd:
                logger.debug(dd.pretty())
                return False
        except TypeError:
            return False
        return True

    def clone(self):
        return self.__deepcopy__()

    def __str__(self):
        return f'\n{json.dumps(self.data(), indent=3)}'

    def expect_error(self, expecting_error='any error'):
        logger.warning(f"Not yet override this method in subclass: {self.expect_error.__name__}")

    def expect_no_error(self, additional_msg_if_fail=''):
        logger.warning(f"Not yet override this method in subclass: {self.expect_no_error.__name__}")

    def data(self):
        try:
            if type(self.response) is str:
                return json.loads(self.response)  # response from WebSocket
            return self.response.json()  # response from rpc
        except BaseException:
            pass

    def get_result(self, string=None, default=None):
        try:
            if string is None:
                return self.data()['Result']
            return self.data()['Result'].get(string, default)
        except(KeyError, TypeError, AttributeError):
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

    def get_node(self):
        from Objects.NodeObject import Node
        return Node(url=self.response.url)
