from pydantic import BaseModel,  Field
# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseMessage(BaseModel):
    message_code: str = Field("", example='')
    # conversationId: ObjectId = Field("", example=ObjectId(''))
    # senderId: ObjectId = Field("", example=ObjectId(''))
    conversation_id: str = Field("", example='')
    sender_id: str = Field("", example='')
    text: str = Field("", example='')

