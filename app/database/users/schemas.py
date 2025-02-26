import re

import pydantic
from pydantic import BaseModel, field_validator
from typing_extensions import Annotated


class User(BaseModel):
    id: int
    redirect_url: Annotated[str, pydantic.HttpUrl] = "https://google.com"
    address: str = ""


class TgUser(User):
    @field_validator("address", mode="before")
    def get_address(cls, address: str, info) -> str:
        values = info.data
        if address == "":
            return str(values["id"])

        assert re.fullmatch(r"^[^_]\w+[^_]$", address)
        return address

    model_config = {
        "validate_assignment": True
    }
