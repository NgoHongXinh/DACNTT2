import datetime

from api.third_parties.database.model.base import BaseModel


class FriendRequest(BaseModel):

    def __init__(self, friend_request_code=None, user_receive_id=None, user_request=None, status=None):
        super().__init__()
        self.friend_request_code = friend_request_code
        self.user_receive_id = user_receive_id
        self.user_request = user_request
        self.status = status

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
