from extentions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    items = db.Column(db.JSON, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="received")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
