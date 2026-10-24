# Restaurant API

## Run locally

From this directory:

```powershell
python -m pip install -r requirements.txt
python app.py
```

The API starts on `http://127.0.0.1:5000`. The first startup creates database tables and seeds the sample menu.

## Routes

| Method | Route | Description |
| --- | --- | --- |
| GET | `/api/restaurants/source` | Fetch restaurant records from the configured restaurant API |
| GET | `/api/menu` | List available menu items; optional `?category=Starters` |
| POST | `/api/bookings` | Create a table reservation |
| POST | `/api/orders` | Place an order using menu item IDs and quantities |
| GET | `/api/restaurants` | List locally stored restaurants |
| POST | `/api/restaurants` | Create a locally stored restaurant |
| GET | `/api/restaurants/<id>` | Get a locally stored restaurant |
| PUT/PATCH | `/api/restaurants/<id>` | Update a locally stored restaurant |
| DELETE | `/api/restaurants/<id>` | Delete a locally stored restaurant |

POST routes accept JSON. Booking fields are `customer_name`, `email`, `phone`, `date` (`YYYY-MM-DD`), `time` (`HH:MM`), `guests`, and optional `notes`. Order fields are `customer_name`, `email`, `phone`, and `items`, where each item contains `menu_item_id` and `quantity`.

## Configuration

Set these values in `backend/.env` when needed:

- `DATABASE_URL`: SQLAlchemy database URL. Defaults to a local SQLite database.
- `CORS_ORIGINS`: Comma-separated allowed frontend origins. Defaults to `http://localhost:5173`.
- `RESTAURANTS_API_URL`: Restaurant data endpoint. Defaults to `https://restaurants-backend-gffy.onrender.com/api/restaurants`.
