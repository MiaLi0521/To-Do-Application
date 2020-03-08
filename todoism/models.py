from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from todoism.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    locale = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    locale = db.Column(db.String(20))

    items = db.relationship('Item', backref='author', cascade='all')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    category = db.Column(db.String(20))
    size = db.Column(db.Integer())

    def generate_pets(self):
        from faker import Faker
        import random
        fake = Faker()
        for i in range(50):
            pet = Pet(name=fake.word(), category=fake.word(), size=random.randint(20, 200))
            db.session.add(pet)
        db.session.commit()