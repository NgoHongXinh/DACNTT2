from pydantic import BaseModel,  Field

from api.third_parties.database.mongodb import PyObjectId


# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseCreateFriendRequest(BaseModel):
    message: str = Field("")


class ResponseFriendRequest(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    friend_request_code: str = Field("")
    user_code_receive: str = Field("")
    user_code_request: str = Field("")
    status: bool = Field("")


