import datetime

from api.third_parties.database.model.base import BaseModel


class Comment(BaseModel):

    def __init__(self, comment_code=None, post_id=None, created_by=None,
                 content=None, liked_by=[], comment=None):
        super().__init__()
        self.comment_code = comment_code,
        self.post_id = post_id,
        self.created_by = created_by,
        self.content = content,
        self.liked_by = liked_by,
        self.comment = comment

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
