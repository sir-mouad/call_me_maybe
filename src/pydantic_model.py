from typing import Any
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    field_validator
)


SUPPORTED_TYPES: set[str] = {"number", "string", "boolean", "integer", "float"}


class RequestInput(BaseModel):
    """Pydantic model for validating a single input prompt."""

    prompt: str = Field(min_length=1)


class FunctionDefinition(BaseModel):
    """Pydantic model for validating a function definition."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, str]
    returns: str

    @field_validator("parameters")
    @classmethod
    def check_types(cls, params: dict[str, str]) -> dict[str, str]:
        """Validate that all parameter types are supported.

        Args:
            params: Dict of parameter names to their types.

        Returns:
            The validated parameters dict.

        Raises:
            ValueError: If an unsupported type is found.
        """
        for name, t in params.items():
            if t not in SUPPORTED_TYPES:
                raise ValueError(
                    f"unsupported type '{t}' for parameter '{name}'")
        return params

    @model_validator(mode="before")
    @classmethod
    def normalize(cls, data: Any) -> Any:
        """normalize nested type dicts into plain strings.

        Args:
            data: Raw input data before validation.

        Returns:
            normalizeed data with string types.
        """
        if isinstance(data.get("parameters"), dict):
            parameters = {}
            for k, v in data["parameters"].items():
                parameters[k] = v["type"]

            data["parameters"] = parameters
        if isinstance(data.get("returns"), dict):
            data["returns"] = data["returns"]["type"]

        return data
