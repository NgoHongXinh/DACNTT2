from typing import List

from pydantic import BaseModel, Field

from api.endpoint.user.schema import ResponseUser


class ResponsePost(BaseModel):
    post_code: str = Field("", example='')
    created_by: str = Field("", example='')
    content: str = Field("", example='')
    image: List[str] = Field([], example=[''])
    liked_by: List[str] = Field([], example=[''])
    comment_post: List[str] = Field([], example=[''])
    root_post: str = Field("", example='', description="bài gốc của bài được chia sẻ")
    video: str = Field("", example='')
    video_ids: str = Field("", example='')


class ResponseCreateUpdatePost(BaseModel):
    post_code: str = Field("", example='')
    created_by: ResponseUser = Field(None)
    content: str = Field("", example='')
    images: List[str] = Field([], example=[''])
    liked_by: List[str] = Field([], example=[''])
    comment_post: List[str] = Field([], example=[''])
    videos: List[str] = Field([], example='')
    video_ids: List[str] = Field([], example='')


class CreateUpdatePost(BaseModel):
    content: str = Field("", example='')
    image: List[str] = Field([], example=[''])
    video: str = Field("", example='')


class ResponseLikePost(BaseModel):
    status: bool = Field(False, description="True: like bài viết, False: displike bài viết")
    like_number: int = Field(default=0, description="số lượng like")
    liked_by: List[ResponseUser] = Field(None)


class ResponseSharePost(BaseModel):
    message: str = Field("")
