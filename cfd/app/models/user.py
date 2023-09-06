from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import datetime


SCAN_LIMITS = {
    'free': 10,
    'professional': 50,
    'enterprise': 1000,
}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Adding the user tiers.
    # 'free', 'professional', 'enterprise'
    tier = db.Column(db.String(20), nullable=False, default='free')
    last_reset = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    scans = db.relationship('Scan', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return True
    
    def get_id(self):
        return str(self.id)
    
    def record_scan(self):
        today = datetime.date.today()
        scan_record = Scan(user_id=self.id, date=today)
        db.session.add(scan_record)
        db.session.commit()
    
    def remaining_scans(self):
        # Check if a day has passed since the last reset
        time_since_reset = datetime.datetime.utcnow() - self.last_reset
        if time_since_reset.days >= 1:
            # Reset the scan count and update the reset timestamp
            self.last_reset = datetime.datetime.utcnow()
            db.session.commit()
            return SCAN_LIMITS.get(self.tier, 0)
        else:
            # Calculate remaining scans for today.
            today = datetime.date.today()
            scans_done_today = self.scans.filter_by(date=today).count()
            remaining = SCAN_LIMITS.get(self.tier, 0) - scans_done_today
            # Ensure the remaining value does not drop below zero
            return max(0, remaining) 
    
class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today) 
    def __repr__(self):
        return f"<Scan(user_id={self.user_id}, date={self.date})>"