from pydantic import BaseModel,  Field



class ResponseToken(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
