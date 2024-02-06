from pydantic import BaseModel,  Field
# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseMessage(BaseModel):
    message_code: str = Field("", example='')
    conversation_code: str = Field("", example='')
    sender_code: str = Field("", example='')
    text: str = Field("", example='')


class RequestCreateMessage(BaseModel):
    conversation_code: str = Field("", example='')
    text: str = Field("", example='')

