from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Book(Base):

    __tablename__ = "books"

    book_id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    published = Column(String(4), nullable=False)
    date_added = Column(Date, nullable=False)
    date_deleted = Column(Date, nullable=True)


class Borrow(Base):

    __tablename__ = "borrows"

    borrow_id = Column(Integer, nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.book_id), nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=True)
    user_id = Column(Integer, nullable=False)



