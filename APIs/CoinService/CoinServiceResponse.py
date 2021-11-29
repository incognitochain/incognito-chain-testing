from Drivers import ResponseBase


class CoinServiceResponse(ResponseBase):
    pass


class KeyInfoResponse(ResponseBase):
    @property
    def id(self):
        return self.get_result("id")

    @property
    def created_time(self):
        return self.get_result("created_at")

    @property
    def updated_time(self):
        return self.get_result("updated_at")

    @property
    def pubkey(self):
        return self.get_result("pubkey")

    @property
    def otakey(self):
        return self.get_result("otakey")
