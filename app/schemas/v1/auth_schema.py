from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    password: str


class UserPatchRequest(BaseModel):
    username: str | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str


class UserCreateResponse(BaseModel):
    message: str = "User created successfully"
    created_item: UserResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
