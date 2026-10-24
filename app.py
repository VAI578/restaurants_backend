from flask import Flask
from config import Config
from extentions import db, cors
from controllers import api
from models import Booking, MenuItem, Order, Resto
from services.hospitality_service import HospitalityService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app, origins=Config.CORS_ORIGINS.split(","))

    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.create_all()
        HospitalityService.seed_menu()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)