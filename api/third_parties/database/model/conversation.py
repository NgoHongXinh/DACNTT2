import datetime

from api.third_parties.database.model.base import BaseModel


class Conversation(BaseModel):

    def __init__(self, stt=0, conversation_code=None, name="",  members=[]):
        super().__init__()
        self.stt = stt
        self.conversation_code = conversation_code
        self.name = name
        self.members = members

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
