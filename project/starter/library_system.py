"""
Module 3 Project: Library Management System
library_system.py — Database models and query functions

Your job: Implement the SQLAlchemy models and all functions marked with # TODO.
"""

from sqlalchemy import create_engine, String, Integer, Boolean, ForeignKey, Table, Column, Date, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, joinedload
from datetime import date, timedelta
from typing import Optional, List

engine = create_engine("sqlite:///library.db", echo=False)

class Base(DeclarativeBase):
    pass

# TODO: Create the association table for Book <-> Genre (many-to-many)
book_genres = Table(
    "book_genres",
    Base.metadata,
    Column("book_id",  Integer, ForeignKey("books.id"),  primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

# TODO: Implement the Author model
# Attributes: id (PK), name (required), bio (optional)
class Author(Base):
    __tablename__ = "authors"
    # TODO: define columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String(500))

    books: Mapped[List["Book"]] = relationship("Book", back_populates="author")

    def __repr__(self) -> str:
        return f"Author(id={self.id}, name={self.name!r}, bio={self.bio!r})"

# TODO: Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    # TODO: define columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    books: Mapped[List["Book"]] = relationship("Book", secondary=book_genres, back_populates="genres")

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name!r})"

# TODO: Implement the Book model
# Attributes: id (PK), title (required), isbn (unique, required),
#             published_year (optional), author_id (FK), available (bool, default True)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)
class Book(Base):
    __tablename__ = "books"
    # TODO: define columns and relationships
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id"), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    author: Mapped["Author"] = relationship("Author", back_populates="books")

    genres: Mapped[List["Genre"]] = relationship("Genre", secondary=book_genres, back_populates="books")

    checkouts: Mapped[List["Checkout"]] = relationship("Checkout", back_populates="book")

    def __repr__(self) -> str:
        return f"Book(id={self.id}, title={self.title!r}, isbn={self.isbn!r}, published_year={self.published_year!r}, author={self.author!r}, available={self.available!r}, genres={self.genres!r})"

# TODO: Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    # TODO: define columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    checkouts: Mapped[List["Checkout"]] = relationship("Checkout", back_populates="borrower")

    def __repr__(self) -> str:
        return f"Borrower(id={self.id}, name={self.name!r}, email={self.email!r}, phone={self.phone!r})"

# TODO: Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    # TODO: define columns and relationships
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False)
    borrower_id: Mapped[int] = mapped_column(Integer, ForeignKey("borrowers.id"), nullable=False)
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    book: Mapped["Book"] = relationship("Book", back_populates="checkouts")
    borrower: Mapped["Borrower"] = relationship("Borrower", back_populates="checkouts")
    
    def __repr__(self) -> str:
        return f"Checkout(id={self.id}, book={self.book!r}, borrower={self.borrower!r}, checkout_date={self.checkout_date!r}, due_date={self.due_date!r}, return_date={self.return_date!r})"


def init_db():
    """Create all database tables. Call this before using any other functions."""
    Base.metadata.create_all(engine)


def reset_db():
    """Drop all tables and recreate them. Use before seeding or demo scripts."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def drop_db():
    """Drop all tables. Use before seeding or demo scripts."""
    Base.metadata.drop_all(engine)


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================

def add_author(name: str, bio: str = None) -> Author:
    """Add a new author. Returns the created Author object."""
    # TODO: open Session, create Author, add + commit, return it
    with Session(engine) as session:
        author = session.execute(
            select(Author).where(Author.name == name)
        ).scalar_one_or_none()
        if author is None:
            author = Author(name=name, bio=bio)
            session.add(author)
            session.commit()
            session.refresh(author)
        return author

def add_book(title: str, isbn: str, author_id: int,
             published_year: int = None, genre_names: list = None) -> Book:
    """
    Add a new book. Assigns genres by name (creates genre if it doesn't exist yet).
    Returns the created Book object.
    """
    # TODO: implement
    with Session(engine) as session:
        author = session.get(Author, author_id)
        if not author:
            raise ValueError(f"Author with id {author_id} not found")
        book = Book(
            title=title,
            isbn=isbn,
            author_id=author_id,
            published_year=published_year,
        )
        session.add(book)
        session.flush()

        if genre_names:
            for genre_name in genre_names:
                genre = session.execute(select(Genre).where(Genre.name == genre_name)).scalar_one_or_none()
                if genre is None:
                    genre = Genre(name=genre_name)
                    session.add(genre)
                    session.flush()
                book.genres.append(genre)

        session.commit()
        session.refresh(book)
        return book

def add_borrower(name: str, email: str, phone: str = None) -> Borrower:
    """Register a new borrower. Returns the created Borrower object."""
    # TODO: implement
    with Session(engine) as session:
        borrower = Borrower(name=name, email=email, phone=phone)
        session.add(borrower)
        session.commit()
        session.refresh(borrower)
        return borrower

def checkout_book(book_id: int, borrower_id: int, days: int = 14) -> Checkout:
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # TODO: implement
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if not book:
            raise ValueError(f"Book with id {book_id} not found")
        if not book.available:
            raise ValueError(f"Book with id {book_id} is not available")
        borrower = session.get(Borrower, borrower_id)
        if not borrower:
            raise ValueError(f"Borrower with id {borrower_id} not found")
            
        due_date = date.today() + timedelta(days=days)
        checkout = Checkout(
            book_id=book_id,
            borrower_id=borrower_id,
            checkout_date=date.today(),
            due_date=due_date
        )
        book.available = False
        session.add(checkout)
        session.commit()
        session.refresh(checkout)
        return checkout

def return_book(checkout_id: int) -> Checkout:
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # TODO: implement
    with Session(engine) as session:
        checkout = session.get(Checkout, checkout_id)
        if not checkout:
            raise ValueError(f"Checkout with id {checkout_id} not found")
        checkout.return_date = date.today()
        checkout.book.available = True
        session.commit()
        session.refresh(checkout)
        return checkout


# ============================================================
# QUERY FUNCTIONS
# ============================================================

def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # TODO: implement — use LIKE or ilike for partial matching
    with Session(engine) as session:
        query = (
            select(Book)
            .options(joinedload(Book.author))
            .join(Author, Author.id == Book.author_id)
            .where(Author.name.ilike(f"%{author_name}%"))
            .order_by(Book.title)
        )
        return session.execute(query).scalars().unique().all()

def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # TODO: implement
    with Session(engine) as session:
        query = (
            select(Checkout)
            .options(
                joinedload(Checkout.book).joinedload(Book.author),
                joinedload(Checkout.borrower),
            )
            .where(Checkout.due_date < date.today(), Checkout.return_date.is_(None))
            .order_by(Checkout.due_date)
        )
        return session.execute(query).scalars().unique().all()

def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # TODO: implement — needs a join through Book to Checkout
    with Session(engine) as session:
        query = (
            select(Genre.name, func.count(Checkout.id).label("checkout_count"))
            .join(book_genres, Genre.id == book_genres.c.genre_id)
            .join(Book, Book.id == book_genres.c.book_id)
            .join(Checkout, Checkout.book_id == Book.id)
            .group_by(Genre.id)
            .order_by(func.count(Checkout.id).desc())
            .limit(limit)
        )
        return session.execute(query).all()

def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # TODO: implement
    with Session(engine) as session:
        query = (
            select(Book)
            .options(joinedload(Book.author))
            .where(Book.available.is_(True))
            .order_by(Book.title)
        )
        return session.execute(query).scalars().unique().all()
