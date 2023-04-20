from sqlalchemy import create_engine, desc, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from database.models import Book, Borrow
from datetime import datetime


class DatabaseConnector:
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    DATABASE_NAME = "bot_library"
    engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@localhost:5434/{DATABASE_NAME}")
    if not database_exists(engine.url):
        create_database(engine.url)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)

    def add(self, title, author, published, date_added, date_deleted=None):
        with self.Session() as session:
            new_book = Book(title=title, author=author, published=published, date_added=date_added, date_deleted=date_deleted)
            response = False

            try:
                session.add(new_book)
                session.commit()
                response = session.query(Book).order_by(desc(Book.book_id)).first().book_id
            except:
                pass

            return response

    def delete(self, book_id):
        with self.Session() as session:
            response = True
            try:
                book = session.query(Book).filter(Book.book_id == book_id).one()
                borrows = session.query(Borrow).filter(Borrow.book_id == book_id).all()
                for borrow in borrows:
                    if borrow.date_end is None:
                        response = False
                        break
                if response:
                    book.date_deleted = datetime.now().date()
                    session.add(book)
                    session.commit()
            except:
                response = False

            return response

    def list_books(self):
        with self.Session() as session:
            books_list = []
            try:
                q = session.query(Book).all()
                for book in q:
                    temp = {"book_id": book.book_id,
                            "title": book.title,
                            "author": book.author,
                            "published": book.published,
                            "date_added": book.date_added,
                            "date_deleted": book.date_deleted}
                    books_list.append(temp)
            except:
                pass
            return books_list

    def get_book(self, title, author, published):
        with self.Session() as session:
            book_id = None
            try:
                book = session.query(Book).filter(text(f"LOWER(title) = '{title.lower()}' AND LOWER(author) = '{author.lower()}' AND LOWER(published) = '{published.lower()}'")).first()
                book_id = book.book_id
            except:
                pass

            return book_id

    def borrow(self, book_id, user_id):
        with self.Session() as session:
            response = True
            try:
                last_borrow = session.query(Borrow, Book).filter(Borrow.book_id == Book.book_id).filter(Borrow.book_id == book_id).filter(Borrow.user_id == user_id).order_by(desc(Borrow.borrow_id)).first()
                if last_borrow.Borrow.date_end is None or last_borrow.Book.date_deleted is not None:
                    response = False
            except:
                pass

            if response:
                borrow = Borrow(book_id=book_id, date_start=datetime.now().date(), date_end=None, user_id=user_id)
                session.add(borrow)
                session.commit()

            return response

    def get_borrow(self, user_id):
        with self.Session() as session:
            borrow_id = None
            try:
                borrow = session.query(Borrow).filter(text(f'user_id = {user_id} AND date_end IS NULL')).one()
                borrow_id = borrow.borrow_id
            except:
                pass

            return borrow_id

    def retrieve(self, borrow_id):
        with self.Session() as session:
            book_str = None
            try:
                borrow = session.query(Borrow).filter(Borrow.borrow_id == borrow_id).one()
                book = session.query(Book).filter(Book.book_id == borrow.book_id).one()
                book_str = f'{book.title}, {book.author}, {book.published}'
                borrow.date_end = datetime.now().date()
                session.add(borrow)
                session.commit()
            except:
                pass

            return book_str

    def statistics(self, book_id):
        with self.Session() as session:
            borrows_list = []
            try:
                borrows = session.query(Borrow).filter(Borrow.book_id == book_id).all()
                for borrow in borrows:
                    borrows_list.append({'borrow_id': borrow.borrow_id,
                                         "book_id": borrow.book_id,
                                         "date_start": str(borrow.date_start),
                                         "date_end": str(borrow.date_end),
                                         "user_id": borrow.user_id})
            except:
                pass

            return borrows_list






