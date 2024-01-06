import datetime
import uuid

from api.third_parties.database.model.base import BaseModel


class Post(BaseModel):

    def __init__(self, post_code=None, created_by=None, content=None, images=[],
                 image_ids=[], videos=None, video_ids=None, liked_by=[],
                 comment_post=[], root_post=None):
        super().__init__()
        self.post_code = post_code
        self.created_by = created_by
        self.content = content
<<<<<<< HEAD
        self.image = image
        self.image_id = image_id
        self.video = video
=======
        self.images = images
        self.image_ids = image_ids
        self.videos = videos
>>>>>>> origin
        self.video_ids = video_ids
        self.liked_by = liked_by
        self.comment_post = comment_post
        self.root_post = root_post
        self.post_code = post_code

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data
