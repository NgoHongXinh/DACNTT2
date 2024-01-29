import datetime

from api.third_parties.database.model.base import BaseModel


class User(BaseModel):

    def __init__(self, user_code="", fullname="", picture="", background_picture="", picture_id="",
                 given_name="", family_name="", username="", biography="", class_name="", faculty="",
                 friends_code=[], birthday="", phone="", gender=""):
        super().__init__()
        self.user_code = user_code
        self.fullname = fullname
        self.picture = picture
        self.background_picture = background_picture
        self.picture_id = picture_id
        self.given_name = given_name
        self.family_name = family_name
        self.username = username
        self.biography = biography
        self.class_name = class_name
        self.faculty = faculty
        self.friends_code = friends_code
        self.birthday = birthday
        self.phone = phone
        self.gender = gender

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is "":
                del data[key]
        return data
