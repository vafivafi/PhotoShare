from pydantic import BaseModel, Field, EmailStr

class UserSchema(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=25,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Unique username",
        examples=["Vafitempo_is_best"],
    )
    password: str = Field(
        min_length=8,
        max_length=30,
        description="User password",
        examples=["EQWsItScVkkAa99u3VVP"],
    )