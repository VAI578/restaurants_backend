from models import Resto
from repositories import RestoRepository


class RestoService:
    _fields = {"name", "address", "cuisine"}
    _optional_fields = {"address", "cuisine"}

    @staticmethod
    def list_restaurants():
        return RestoRepository.get_all()

    @classmethod
    def get_restaurant(cls, resto_id):
        return RestoRepository.get_by_id(resto_id)

    @classmethod
    def create_restaurant(cls, data):
        cls._validate(data, partial=False)
        restaurant = Resto(
            name=data["name"].strip(),
            address=cls._clean_optional(data.get("address")),
            cuisine=cls._clean_optional(data.get("cuisine")),
        )
        return RestoRepository.create(restaurant)

    @classmethod
    def update_restaurant(cls, resto_id, data, partial=True):
        cls._validate(data, partial=partial)
        restaurant = RestoRepository.get_by_id(resto_id)
        if restaurant is None:
            return None

        if not partial:
            for field in cls._optional_fields:
                if field not in data:
                    setattr(restaurant, field, None)

        for field, value in data.items():
            cleaned_value = value.strip() if isinstance(value, str) else value
            setattr(restaurant, field, cleaned_value)
        return RestoRepository.save(restaurant)

    @classmethod
    def delete_restaurant(cls, resto_id):
        restaurant = RestoRepository.get_by_id(resto_id)
        if restaurant is None:
            return False
        RestoRepository.delete(restaurant)
        return True

    @classmethod
    def _validate(cls, data, partial):
        unknown_fields = set(data) - cls._fields
        if unknown_fields:
            raise ValueError(f"Unknown field(s): {', '.join(sorted(unknown_fields))}")

        if not partial and "name" not in data:
            raise ValueError("Field 'name' is required")
        if partial and not data:
            raise ValueError("At least one field is required")

        if "name" in data and (
            not isinstance(data["name"], str) or not data["name"].strip()
        ):
            raise ValueError("Field 'name' must be a non-empty string")

        for field in cls._optional_fields.intersection(data):
            value = data[field]
            if value is not None and not isinstance(value, str):
                raise ValueError(f"Field '{field}' must be a string or null")

    @staticmethod
    def _clean_optional(value):
        return value.strip() if isinstance(value, str) else value
