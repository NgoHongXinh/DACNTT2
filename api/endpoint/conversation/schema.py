from typing import List

from pydantic import BaseModel,  Field
# from bson import ObjectId

# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseConversation(BaseModel):
    conversation_code: str = Field("", example='')
    members: List[str] = Field([], example=['user1', 'user2'])


class ResponseCreateConversation(BaseModel):
    message: str = Field("", example='')
    conversation_code: str = Field("", example='')


class RequestCreateConversation(BaseModel):
    user_code_to_chat: str = Field("", example='')  # user_code of user to chat
    current_user_code: str = Field("", example='')  # user_code of current user
