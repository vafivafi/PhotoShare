from typing import Optional
from pydantic import BaseModel, Field
from fastapi import Form

class ImageAddSchema(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=25,
        description="Image name",
        examples=["Cloud"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=250,
        description="Image description",
        examples=["This cloud is very wonderful"]
    )

    @classmethod
    def as_form(
        cls,
        name: str = Form(..., description="Image name"),
        description: Optional[str] = Form(default=None, description="Image description"),
    ) -> "ImageAddSchema":
        return cls(name=name, description=description)

class ImageUpdateNameSchema(BaseModel):
    new_name: str = Field(
        min_length=3,
        max_length=25,
        description="Image name",
        examples=["Cloud"]
    )

class ImageUpdateDescriptionSchema(BaseModel):
    new_description: str = Field(
        max_length=250,
        description="Image description",
        examples=["This cloud is very wonderful"]
    )
