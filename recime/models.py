from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from probe import reel_url


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ImportRequest(Model):
    url: str = Field(max_length=2048)
    demo_scenario: Literal["success", "fail_once"] = "success"

    @field_validator("url")
    @classmethod
    def validate_url(cls, value):
        value = value.strip()
        if any(ord(char) < 32 for char in value):
            raise ValueError("A URL contém caracteres inválidos.")
        reel_url(value)
        return value


class IngredientEdit(Model):
    id: int | None = Field(default=None, ge=0)
    name: str | None = Field(default=None, max_length=500)
    quantity_text: str | None = Field(default=None, max_length=200)


class StepEdit(Model):
    id: int | None = Field(default=None, ge=0)
    instruction: str | None = Field(default=None, max_length=4000)


class DraftEdit(Model):
    version: int = Field(ge=1)
    title: str | None = Field(default=None, max_length=300)
    ingredients: list[IngredientEdit] = Field(max_length=100)
    steps: list[StepEdit] = Field(max_length=100)


class Version(Model):
    version: int = Field(ge=1)
