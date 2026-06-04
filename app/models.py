from app import db
from datetime import datetime

class Credit(db.Model):
    __tablename__ = "credits"   # TABLA CREDITS

    id          = db.Column(db.Integer, primary_key=True)

    client_id   = db.Column(db.String(50), nullable=False, unique=True) # CAMPO NO PUEDE QUEDAR SIN LLENAR NI REPETIRSE
    client_name = db.Column(db.String(120), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    interest    = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)

    # "ACTIVO" automáticamente
    status      = db.Column(db.String(20), default="ACTIVO")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
