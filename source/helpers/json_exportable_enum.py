from enum import Enum


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
