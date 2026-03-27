from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=72)

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
