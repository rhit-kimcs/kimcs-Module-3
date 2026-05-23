"""
Module 3 Project: Library Management System
cli.py — Command-line interface

Your job: Implement each menu handler function below.
The main menu loop is already provided — just fill in the handlers.
"""

from library_system import (
    init_db, add_author, add_book, add_borrower,
    checkout_book, return_book, find_books_by_author,
    get_overdue_books, get_popular_genres, get_available_books
)


def menu_add_book():
    """Prompt for book details and add to the database."""
    title = input("Enter the title of the book: ")
    isbn = input("Enter the ISBN of the book: ")
    author_name = input("Enter the name of the author: ")
    year_str = input("Enter the year of publication: ")
    genres_str = input("Enter the genres of the book (comma separated): ")

    author = add_author(author_name)
    year = int(year_str) if year_str.strip() else None
    genre_names = [g.strip() for g in genres_str.split(",") if g.strip()] or None

    book = add_book(title, isbn, author.id, year, genre_names)
    print(f"Book '{book.title}' added successfully (id={book.id}).")


def menu_add_borrower():
    """Prompt for borrower details and register in the database."""
    name = input("Enter the name of the borrower: ")
    email = input("Enter the email of the borrower: ")
    phone = input("Enter the phone number of the borrower (optional): ").strip() or None
    borrower = add_borrower(name, email, phone)
    print(f"Borrower '{borrower.name}' added successfully (id={borrower.id}).")


def menu_checkout():
    """Prompt for book ID and borrower ID, then check out the book."""
    available_books = get_available_books()
    if not available_books:
        print("No books are currently available.")
        return

    print("Available books:")
    for book in available_books:
        print(f"  [{book.id}] {book.title} by {book.author.name}")

    book_id = input("Enter the ID of the book to checkout: ")
    borrower_id = input("Enter the ID of the borrower: ")
    try:
        checkout = checkout_book(int(book_id), int(borrower_id))
        print(f"Checkout #{checkout.id} created successfully (due {checkout.due_date}).")
    except ValueError as exc:
        print(f"Error: {exc}")


def menu_return():
    """Prompt for checkout ID and return the book."""
    checkout_id = input("Enter the ID of the checkout to return: ")
    try:
        checkout = return_book(int(checkout_id))
        print(f"Checkout #{checkout.id} returned successfully on {checkout.return_date}.")
    except ValueError as exc:
        print(f"Error: {exc}")


def menu_search_by_author():
    """Prompt for author name and display matching books."""
    author_name = input("Enter the name of the author: ")
    books = find_books_by_author(author_name)
    print(f"Books by '{author_name}':")
    if not books:
        print("  No books found.")
        return
    for book in books:
        status = "available" if book.available else "checked out"
        print(f"  [{book.id}] {book.title} by {book.author.name} ({book.published_year}) [{status}]")


def menu_overdue():
    """Display all overdue checkouts."""
    overdue_checkouts = get_overdue_books()
    print("Overdue checkouts:")
    if not overdue_checkouts:
        print("  None.")
        return
    for checkout in overdue_checkouts:
        print(
            f"  Checkout #{checkout.id}: '{checkout.book.title}' by "
            f"{checkout.book.author.name} -> {checkout.borrower.name} "
            f"(due {checkout.due_date})"
        )


def menu_popular_genres():
    """Display the most popular genres by checkout count."""
    popular_genres = get_popular_genres()
    print("Popular genres:")
    if not popular_genres:
        print("  No checkout data yet.")
        return
    for genre_name, count in popular_genres:
        print(f"  {genre_name}: {count} checkout(s)")


def main():
    init_db()

    while True:
        print("\n=== Library Management System ===")
        print("1. Add a book")
        print("2. Register a borrower")
        print("3. Check out a book")
        print("4. Return a book")
        print("5. Search by author")
        print("6. View overdue books")
        print("7. View popular genres")
        print("8. Quit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            menu_add_book()
        elif choice == "2":
            menu_add_borrower()
        elif choice == "3":
            menu_checkout()
        elif choice == "4":
            menu_return()
        elif choice == "5":
            menu_search_by_author()
        elif choice == "6":
            menu_overdue()
        elif choice == "7":
            menu_popular_genres()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()
