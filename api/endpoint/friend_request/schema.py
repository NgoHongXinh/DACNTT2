from pydantic import BaseModel,  Field
# from bson import ObjectId
# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseFriendRequest(BaseModel):
    message: str = Field("")