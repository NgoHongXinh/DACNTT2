from pydantic import BaseModel,  Field
# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseFriendRequest(BaseModel):
    friendRequest_code: str = Field("", example='')
    user_receive_id: str = Field("", example='')
    # userRequest: ObjectId = Field("", example=ObjectId(''))
    user_request: str = Field("", example='')
    status: bool = Field("", example=False)
