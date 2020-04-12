from application.database import db
from application.models import User, Book, Category

book = Book(book_name='fo', latest_vol=3, user_id=1)

db.session.add(book)
db.session.commit()
db.session.close()