from typing import List

from pydantic import BaseModel,  Field
# from bson import ObjectId

# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseConversation(BaseModel):
    conversation_code: str = Field("", example='')
    # members: list[ObjectId] = Field("",example=[ObjectId('')])
    members: List[str] = Field([], example=[''])
