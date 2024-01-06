import datetime
import datetime
import uuid
from api.third_parties.database.model.base import BaseModel


class Comment(BaseModel):

    def __init__(self, comment_code=str(uuid.uuid4()), created_by=None,
                 content=None, liked_by=[], post_code=None, user_code=None, comment=None):
        super().__init__()
        self.comment_code = comment_code
        self.post_code = post_code
        # self.user_code = user_code,
        self.created_by = created_by
        self.content = content
        self.liked_by = liked_by
        # self.comment = comment

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
