from pydantic import BaseModel,  Field
from typing import List


class ResponseComment(BaseModel):
    comment_code: str = Field("", example='')
    post_id: str = Field("", example='')
    post_code: str = Field("", example='')
    created_by: str = Field("", example='')
    image: str = Field("", example='')
    image_id: str = Field("", example='')
    content: str = Field("", example='')
    liked_by: List[str] = Field([], example=[''])

    # comment: List[str] = Field([], example=[''])


class ResponseCreateUpdateComment(BaseModel):
    comment_code: str = Field("", example='')
    image: str = Field("", example='')
    image_id: str = Field("", example='')
    # post_id: str = Field("", example='')
    created_by: str = Field("", example='')
    content: str = Field("", example='')


class CreateUpdateComment(BaseModel):
    content: str = Field("", example='')
    image: str = Field("", example='')

