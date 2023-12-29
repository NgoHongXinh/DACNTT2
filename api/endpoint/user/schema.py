from pydantic import BaseModel,  Field

# from api.base.schema import CommonModel
# from api.third_parties.database.model.base import BaseModel


class ResponseUser(BaseModel):
    user_code: str = Field("", example='')
    fullname: str = Field("", example='')
    picture: str = Field("", example='')
    background_picture: str = Field("", example='')
    picture_id: str = Field("", example='')
    given_name: str = Field("", example='')
    family_name: str = Field("", example='')
    user_name: str = Field("", example='')
    biography: str = Field("", example='')
    class_name: str = Field("", example='')
    faculty: str = Field("", example='')
    friend_ids: str = Field("", example='')
    birthday: str = Field("", example='')
    phone: str = Field("", example='')
    gender: str = Field("", example='')
