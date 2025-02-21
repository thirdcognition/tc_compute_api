from enum import Enum
from typing import Optional


class JSONExportableEnum(Enum):
    def __str__(self):
        return self.value

    def __json__(self):
        """
        Custom method to make the Enum JSON serializable.
        """
        return self.value

    def to_json(self):
        """
        Alias for JSON serialization.
        """
        return self.value

    @staticmethod
    def from_json(value: str):
        """
        Deserialize the string value back to the Enum.
        """
        for item in list(JSONExportableEnum):
            if item.value == value:
                return item
        raise ValueError(f"{value} is not a valid {JSONExportableEnum.__name__} value")

    @classmethod
    def resolve(cls, value: Optional[str]) -> Optional["JSONExportableEnum"]:
        """
        Resolves a string or None into the Enum type or returns None if invalid.
        """
        if value is None:
            return None  # Default to None or a fallback
        try:
            return cls(value)  # Attempt to convert to Enum
        except ValueError:
            return None  # Handle invalid value with a fallback
