import datetime

from api.third_parties.database.model.base import BaseModel


class Message(BaseModel):

    def __init__(self, message_code=None, conversation_code=None, sender_code=None, text=None):
        super().__init__()
        self.message_code = message_code
        self.conversation_code = conversation_code
        self.sender_code = sender_code
        self.text = text

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
