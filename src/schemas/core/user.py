from pydantic import ConfigDict, BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
