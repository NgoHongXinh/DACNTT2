from typing import List

from pydantic import BaseModel,  Field

from api.endpoint.user.schema import ResponseUser
from api.third_parties.database.mongodb import PyObjectId


class ResponseConversation(BaseModel):
    conversation_code: str = Field("", example='')
    members: List[str] = Field([], example=['user1', 'user2'])


class ResponseCreateConversation(BaseModel):
    message: str = Field("", example='')


class RequestCreateConversation(BaseModel):
    user_code_to_chat: str = Field("", example='')  # user_code of user to chat
    # current_user_code: str = Field("", example='')  # user_code of current user


class ResponseConversationHaveMemInfo(BaseModel):
    conversation_code: str = Field("", example='')
    members_obj: List[ResponseUser] = Field([  {
                        "user_code": "123",
                        "fullname": "Nguyễn Xuân Thịnh",
                        "picture": "http://res.cloudinary.com/drxflbnoa/image/upload/v1660120955/62cbb88bf7945d8fbf3fe9b5/dtvnqsx2udzkuhgu48cn.png",
                        "background_picture": "",
                        "picture_id": "",
                        "given_name": "",
                        "family_name": "",
                        "username": "51800123@student.tdtu.edu.vn",
                        "biography": "134123123124",
                        "class_name": "",
                        "faculty": "Công nghệ thông tin",
                        "friends_code": [
                            "xinhnh"
                        ],
                        "birthday": "07/05/2000",
                        "phone": "56565656565656",
                        "gender": "Nam"
                    }])
    online: bool = Field(..., example=True)


class ResponseListConversation(BaseModel):
    list_conversation_info: List[ResponseConversationHaveMemInfo] = Field(...)
    last_conversation_id: PyObjectId = Field(default_factory=PyObjectId, alias="last_conversation_id")