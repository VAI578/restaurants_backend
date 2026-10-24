import json
import re
from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import date, datetime

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from extentions import db
from models import Booking, MenuItem, Order


DEFAULT_MENU = [
    {
        "name": "Burrata & Heirloom Tomato",
        "description": "Creamy burrata, ripe tomatoes, basil oil, toasted sourdough.",
        "category": "Starters",
        "price": 14,
        "image_url": "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Crispy Calamari",
        "description": "Golden calamari, lemon, garden herbs and smoked paprika aioli.",
        "category": "Starters",
        "price": 16,
        "image_url": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Wild Mushroom Risotto",
        "description": "Arborio rice, wild mushrooms, parmesan and a little truffle.",
        "category": "Mains",
        "price": 26,
        "image_url": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Roasted Salmon",
        "description": "Line-caught salmon, lemon beurre blanc and seasonal greens.",
        "category": "Mains",
        "price": 29,
        "image_url": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Herb-Roasted Chicken",
        "description": "Free-range chicken, creamy polenta and pan jus.",
        "category": "Mains",
        "price": 27,
        "image_url": "https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Chocolate Olive Oil Cake",
        "description": "Rich dark chocolate cake, sea salt and vanilla cream.",
        "category": "Desserts",
        "price": 12,
        "image_url": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "Seasonal Berry Panna Cotta",
        "description": "Silky vanilla panna cotta with fresh berries.",
        "category": "Desserts",
        "price": 11,
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "name": "House Lemonade",
        "description": "Fresh lemons, mint and a touch of wildflower honey.",
        "category": "Drinks",
        "price": 7,
        "image_url": "https://images.unsplash.com/photo-1513558161293-cafs3fdfd8e4?auto=format&fit=crop&w=1000&q=85",
    },
]


class HospitalityService:
    @staticmethod
    def get_external_restaurants():
        request = Request(
            current_app.config["RESTAURANTS_API_URL"],
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=15) as response:
                restaurants = json.load(response)
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            current_app.logger.exception("Could not load restaurants from the configured API")
            raise RuntimeError("Restaurant data source is temporarily unavailable") from exc

        if not isinstance(restaurants, list):
            current_app.logger.error("Configured restaurant API returned an unexpected response")
            raise RuntimeError("Restaurant data source returned an invalid response")
        return restaurants

    @staticmethod
    def seed_menu():
        if MenuItem.query.first() is None:
            db.session.add_all(MenuItem(**item) for item in DEFAULT_MENU)
            _commit()

    @staticmethod
    def list_menu(category=None):
        query = MenuItem.query.filter_by(is_available=True)
        if category and category.lower() != "all":
            query = query.filter(db.func.lower(MenuItem.category) == category.lower())
        return query.order_by(MenuItem.category, MenuItem.name).all()

    @staticmethod
    def create_booking(data):
        required = ("customer_name", "email", "phone", "date", "time", "guests")
        _require_fields(data, required)
        name = _text(data["customer_name"], "customer_name", 120)
        email = _email(data["email"])
        phone = _text(data["phone"], "phone", 40)
        try:
            booking_date = date.fromisoformat(data["date"])
            booking_time = datetime.strptime(data["time"], "%H:%M").time()
            guests = int(data["guests"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Date, time, or guest count is invalid") from exc
        if booking_date < date.today():
            raise ValueError("Booking date must be today or later")
        if guests < 1 or guests > 20:
            raise ValueError("Guest count must be between 1 and 20")

        booking = Booking(
            customer_name=name,
            email=email,
            phone=phone,
            booking_date=booking_date,
            booking_time=booking_time,
            guests=guests,
            notes=_text(data.get("notes", ""), "notes", 500, allow_empty=True),
        )
        db.session.add(booking)
        _commit()
        return booking

    @staticmethod
    def create_order(data):
        _require_fields(data, ("customer_name", "email", "phone", "items"))
        name = _text(data["customer_name"], "customer_name", 120)
        email = _email(data["email"])
        phone = _text(data["phone"], "phone", 40)
        requested_items = data["items"]
        if not isinstance(requested_items, list) or not requested_items:
            raise ValueError("Order must contain at least one item")

        normalized = []
        total = 0
        for requested in requested_items:
            if not isinstance(requested, dict):
                raise ValueError("Each order item must be an object")
            try:
                item_id = int(requested["menu_item_id"])
                quantity = int(requested["quantity"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("Each item needs a valid menu_item_id and quantity") from exc
            if quantity < 1 or quantity > 50:
                raise ValueError("Item quantity must be between 1 and 50")
            menu_item = db.session.get(MenuItem, item_id)
            if menu_item is None or not menu_item.is_available:
                raise ValueError(f"Menu item {item_id} is not available")
            line_total = round(menu_item.price * quantity, 2)
            total += line_total
            normalized.append(
                {
                    "menu_item_id": menu_item.id,
                    "name": menu_item.name,
                    "quantity": quantity,
                    "unit_price": menu_item.price,
                    "line_total": line_total,
                }
            )

        order = Order(
            customer_name=name,
            email=email,
            phone=phone,
            items=normalized,
            total=round(total, 2),
        )
        db.session.add(order)
        _commit()
        return order


def _require_fields(data, fields):
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def _text(value, field, max_length, allow_empty=False):
    if not isinstance(value, str):
        raise ValueError(f"Field '{field}' must be text")
    cleaned = value.strip()
    if not cleaned and not allow_empty:
        raise ValueError(f"Field '{field}' cannot be empty")
    if len(cleaned) > max_length:
        raise ValueError(f"Field '{field}' must be at most {max_length} characters")
    return cleaned


def _email(value):
    email = _text(value, "email", 254)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Field 'email' must be a valid email address")
    return email


def _commit():
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
