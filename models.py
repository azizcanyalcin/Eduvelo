from pydantic import BaseModel


class SignUpRequest(BaseModel):
    email: str
    password: str