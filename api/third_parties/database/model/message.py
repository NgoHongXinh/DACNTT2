import datetime

from api.third_parties.database.model.base import BaseModel


class Message(BaseModel):

    def __init__(self, message_code=None, conversation_id=None, sender_id=None, text=None):
        super().__init__()
        self.message_code = message_code,
        self.conversation_id = conversation_id,
        self.sender_id = sender_id,
        self.text = text

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
