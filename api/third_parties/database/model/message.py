import datetime

from api.third_parties.database.model.base import BaseModel


class Message(BaseModel):

    def __init__(self, message_code=None, conversation_code=None, sender_code=None, text=None):
        super().__init__()
        self.message_code = message_code
        self.conversation_code = conversation_code # conversation_code của cuộc trò chuyện
        self.sender_code = sender_code # user_code của người gửi
        self.text = text # nội dung tin nhắn

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
