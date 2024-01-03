import datetime

from api.third_parties.database.model.base import BaseModel


class Notification(BaseModel):

    def __init__(self, notification_code=None, user_id=None, user_id_guest=None, content=None,
                 is_checked=None, deleted_flag=None):
        super().__init__()
        self.notification_code = notification_code,
        self.user_id = user_id,
        self.user_id_guest = user_id_guest,
        self.content = content,
        self.is_checked = is_checked,
        self.deleted_flag = deleted_flag

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
