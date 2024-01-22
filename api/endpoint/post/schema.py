from typing import List

from pydantic import BaseModel, Field

from api.endpoint.user.schema import ResponseUser


class ResponsePost(BaseModel):
    post_code: str = Field("", example='')
    created_by: str = Field("", example='')
    content: str = Field("", example='')
    images: List[str] = Field([], example=[''])
    image_ids: List[str] = Field([], example=[''])
    liked_by: List[str] = Field([], example=[''])
    comment_post: List[str] = Field([], example=[''])
    root_post: str = Field("", example='', description="bài gốc của bài được chia sẻ")
    video: str = Field("", example='')
    video_id: str = Field("", example='')


class ResponseCreateUpdatePost(BaseModel):
    post_code: str = Field("", example='')
    created_by: ResponseUser = Field(None)
    content: str = Field("", example='')
    images: List[str] = Field([], example=[''])
    image_ids: List[str] = Field([], example=[''])
    liked_by: List[str] = Field([], example=[''])
    comment_post: List[str] = Field([], example=[''])
    video: str = Field("", example='')
    video_id: str = Field("", example='')


class CreateUpdatePost(BaseModel):
    content: str = Field("", example='')
    images: List[str] = Field([], example=[''])
    video: str = Field("", example='')



