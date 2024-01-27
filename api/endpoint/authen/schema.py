from pydantic import BaseModel,  Field



class ResponseToken(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


class RequestInfoToken(BaseModel):
    client_id: str = Field(...)
    credential: str = Field(...)
