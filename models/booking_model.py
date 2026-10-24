from extentions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="confirmed")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.booking_date.isoformat(),
            "time": self.booking_time.strftime("%H:%M"),
            "guests": self.guests,
            "status": self.status,
        }
