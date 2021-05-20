import Helpers.Logging as Log
import json


class ResponseBase:
    def __init__(self, response=None, more_info=None):
        self.response = response
        self.more_info = more_info
        if more_info is not None:
            Log.DEBUG(more_info, ResponseBase.__name__)
        if response is not None:
            Log.DEBUG(self.__str__(), ResponseBase.__name__)

    def __str__(self):
        return f'\n{json.dumps(self.data(), indent=3)}'

    def data(self):
        try:
            if type(self.response) is str:
                return json.loads(self.response)  # response from WebSocket
            return json.loads(self.response.text)  # response from rpc
        except Exception as e:
            print(f'+++ {self.response.text} \n {e}')

    def get_result(self, string=None):
        try:
            if string is None:
                return self.data()['Result']
            return self.data()['Result'][string]
        except(KeyError, TypeError):
            return None
