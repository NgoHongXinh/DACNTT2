from api.third_parties.database.model.base import BaseModel


class Group(BaseModel):

    def __init__(self, group_code=None, name=None,  members=[]):
        super().__init__()
        self.group_code = group_code
        self.name = name
        self.members = members

    def to_json(self):
        data = self.__dict__
        for key, value in list(data.items()):
            if value is None:
                del data[key]
        return data