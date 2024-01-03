from pydantic import BaseModel,  Field
from typing import List


# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseComment(BaseModel):
    comment_code: str = Field("", example='')
    post_id: str = Field("", example='')
    # createdBy: ObjectId = Field("", example=ObjectId(''))
    created_by: str = Field("", example='')
    content: str = Field("", example='')
    # likedBy: list[ObjectId] = Field("",example=[ObjectId('')])
    liked_by: List[str] = Field([], example=[''])
    comment: List[str] = Field([], example=[''])

