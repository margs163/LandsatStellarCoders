from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    full_name: str = Field()
    email: EmailStr = Field()

class UserInDB(User):
    hashed_password: str = Field(description="hash of the password")