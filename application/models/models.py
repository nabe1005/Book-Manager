from datetime import datetime

from flask_login import UserMixin

from application.database import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    __table_args__ = (
        db.UniqueConstraint('name'),
        db.UniqueConstraint('email'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    books = db.relationship('Book', backref='owner', lazy=True)

    def __init__(self, name, display_name, email, password):
        self.name = name
        self.display_name = display_name
        self.email = email
        self.password = password


book_category = db.Table(
    'book_category',
    db.Column('series_id', db.Integer, db.ForeignKey('books.series_id'), primary_key=True, nullable=False),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id'), primary_key=True, nullable=False)
)


class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    series_id = db.Column(db.Integer, nullable=False)
    book_name = db.Column(db.String(256), nullable=False)
    vol = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)

    categories = db.relationship('Category', secondary=book_category, lazy='subquery',
                                 backref=db.backref('books', lazy=True))
    places = db.relationship('Place', backref='places', lazy=True)

    def __init__(self, series_id, book_name, vol, user_id):
        self.series_id = series_id
        self.book_name = book_name
        self.vol = vol
        self.user_id = user_id


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(256), nullable=False, unique=True)

    def __init__(self, category_name):
        self.category_name = category_name


class Place(db.Model):
    __tablename__ = 'places'

    place_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_name = db.Column(db.String(256), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    to_vol = db.Column(db.Integer, nullable=True)
    from_vol = db.Column(db.Integer, nullable=True)

    def __init__(self, place_name, book_id, to_vol, from_vol):
        self.place_name = place_name
        self.book_id = book_id
        self.to_vol = to_vol
        self.from_vol = from_vol
