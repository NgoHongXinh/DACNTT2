import datetime

from api.third_parties.database.model.base import BaseModel


class UserOnline(BaseModel):

    def __init__(self, user_online_code=None, user_id=None, socket_id=None, status=None):
        super().__init__()
        self.user_online_code = user_online_code
        self.user_id = user_id
        self.socket_id = socket_id
        self.status = status

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
