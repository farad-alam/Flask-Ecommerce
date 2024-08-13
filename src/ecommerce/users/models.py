from ecommerce import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(130), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False )
    profile_pic = db.Column(db.String(30), nullable=True, default='default_profile.png')
    created_at = db.Column(db.DateTime, default=datetime.now())
    role = db.Column(db.Integer, nullable=False, default=0)  

    def is_superadmin(self):
        return self.role == 1

    def is_user(self):
        return self.role == 0

    def get_reset_token(self):
        print("SECRET_KEY type:", type(app.config['SECRET_KEY']))
        print("SECRET_KEY value:", app.config['SECRET_KEY'])

        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': str(self.id)}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, max_age=expires_sec)['user_id']
            return User.query.get(user_id)
        except:
            return None




    def __repr__(self):
        return f"{self.username} - {self.email} - {self.created_at}"
    

