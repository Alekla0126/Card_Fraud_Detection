from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import datetime


SCAN_LIMITS = {
    'free': 10,
    'professional': 50,
    'enterprise': 1000,
}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Adding the user tiers.
    # 'free', 'professional', 'enterprise'
    tier = db.Column(db.String(20), nullable=False, default='free')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)
    
    def remaining_scans(self):
        time_since_reset = datetime.datetime.utcnow() - self.last_reset
        if time_since_reset.days >= 1:
            self.last_reset = datetime.datetime.utcnow()
            db.session.commit()
            return SCAN_LIMITS.get(self.tier, 0)
        else:
            today = datetime.date.today()
            return SCAN_LIMITS.get(self.tier, 0) - self.scans.filter_by(date=today).count() 

    def is_authenticated(self):
        # Assuming you have a boolean field 'authenticated' in your User model
        return self.authenticated

    def is_active(self):
        # Implement logic for active/inactive users here
        return True
    
    def is_anonymous(self):
        return False
    
class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    
    def __repr__(self):
        return f"<Scan(user_id={self.user_id}, date={self.date})>"