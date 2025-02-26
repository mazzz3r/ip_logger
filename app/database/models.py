import datetime
from app.database import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    redirect_url = db.Column(db.String(255), nullable=False, default="https://google.com")
    address = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "redirect_url": self.redirect_url,
            "address": self.address
        }

class Log(db.Model):
    __tablename__ = "logs"
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    data = db.Column(db.JSON, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    
    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "user_id": self.user_id,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
