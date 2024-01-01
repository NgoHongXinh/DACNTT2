from typing import List

from pydantic import BaseModel,  Field



class ResponsePost(BaseModel):
    post_code: str = Field("", example='')
    created_by: str = Field("", example='')
    content: str = Field("", example='')
    image: List[str] = Field([], example=[''])
    # image_id: List[str] = Field([], example=[''])
    video: str = Field("", example='')
    liked_by: List[str] = Field([], example=[''])
    comment_post: List[str] = Field([], example=[''])
    root_post: str = Field("", example='', description="bài gốc của bài được chia sẻ")
    # createdBy: ObjectId = Field("", example='')
    # likedBy: list[ObjectId] = Field("", example=[ObjectId('')])
    # commentPost: list[ObjectId] = Field("", example=[ObjectId('')])
    # rootPost: ObjectId = Field("", example='')