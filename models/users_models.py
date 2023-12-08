from pydantic import BaseModel

class User(BaseModel):
    id: str | None = None
    username: str
    email: str
    password: str

class User_output(BaseModel):
    id: str | None = None
    username: str
    email: str