from typing import List

from pydantic import BaseModel,  Field

from api.third_parties.database.mongodb import PyObjectId


class ResponseConversation(BaseModel):
    conversation_code: str = Field("", example='')
    members: List[str] = Field([], example=['user1', 'user2'])


class ResponseCreateConversation(BaseModel):
    message: str = Field("", example='')
    conversation_code: str = Field("", example='')


class RequestCreateConversation(BaseModel):
    user_code_to_chat: str = Field("", example='')  # user_code of user to chat
    current_user_code: str = Field("", example='')  # user_code of current user


class ResponseListConversation(BaseModel):
    list_conversation_info: List[ResponseConversation] = Field(...)
    last_conversation_id: PyObjectId = Field(default_factory=PyObjectId, alias="last_conversation_id")