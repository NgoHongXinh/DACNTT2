from typing import List

from pydantic import BaseModel,  Field

from api.third_parties.database.mongodb import PyObjectId


class ResponseGroup(BaseModel):
    conversation_code: str = Field("", example='')
    name: str = Field("", example='')
    members: List[str] = Field([], example=['list_user_to_chat', 'current_user_code'])


class RequestCreateGroup(BaseModel):
    list_user_to_chat: List[str] = Field([], example=['user1', 'user2'])
    current_user_code: str = Field("", example='')  # user_code of current user
    name: str = Field("", example='')


class ResponseListGroup(BaseModel):
    list_group_info: List[ResponseGroup] = Field(...)
    last_group_id: PyObjectId = Field(default_factory=PyObjectId, alias="last_group_id")


class RequestUpdateUser(BaseModel):
    list_user_code: List[str] = Field([], example=['user1', 'user2'])
    # conversation_code: str = Field("", example='')



