import datetime

from api.third_parties.database.model.base import BaseModel


class Conversation(BaseModel):

    def __init__(self, conversation_code=None, members=[]):
        super().__init__()
        self.conversation_code = conversation_code
        self.members = members

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
