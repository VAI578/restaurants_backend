from sqlalchemy.exc import SQLAlchemyError

from extentions import db
from models import Resto


class RestoRepository:
    @staticmethod
    def _commit():
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def get_all():
        return Resto.query.order_by(Resto.id).all()

    @staticmethod
    def get_by_id(resto_id):
        return db.session.get(Resto, resto_id)

    @staticmethod
    def create(restaurant):
        db.session.add(restaurant)
        RestoRepository._commit()
        return restaurant

    @staticmethod
    def save(restaurant):
        RestoRepository._commit()
        return restaurant

    @staticmethod
    def delete(restaurant):
        db.session.delete(restaurant)
        RestoRepository._commit()
