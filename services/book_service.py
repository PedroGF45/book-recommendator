from typing import Any

from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager

import httpx

class BookService:
    def __init__(self, log_manager: LogManager, connection_manager: ConnectionManager, api_base_url: str):
        self.log_manager = log_manager
        self.connection_manager = connection_manager
        self.api_base_url = api_base_url
        self.client = httpx.Client(timeout=10)

    def get_book_by_id(self, book_id: int) -> dict[str, Any] | None:
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                cursor = conn.execute("SELECT id, isbn, title, author, genres, description FROM books WHERE id = %s", (book_id,))
                if cursor:
                    book = cursor.fetchone()
                    return book
        except Exception as e:
            self.log_manager.log("ERROR", f"Error fetching book with ID {book_id} from database: {str(e)}")
            raise

    def get_or_fetch_book_by_isbn(self, isbn: str) -> dict[str, Any] | None:

        # 1 Check if the book exists in the local database
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                cursor = conn.execute("SELECT id, title, author, description, genres FROM books WHERE isbn = %s", (isbn,))
                book = cursor.fetchone()
                if book is not None:
                    self.log_manager.log("INFO", f"Book with ISBN {isbn} found in database.")
                    return book
                
        except Exception as e:
            self.log_manager.log("ERROR", f"Error fetching book with ISBN {isbn} from database: {str(e)}")
            raise

        # 2 There is no book on the dabase with that isbn so we need to fetch it using our api
        book_url = f'{self.api_base_url}{isbn}'
        try:
            api_response = self.client.get(book_url)
            api_response.raise_for_status()
        except httpx.HTTPError as e:
            self.log_manager.log("ERROR", f"Error fetching book with ISBN {isbn} from API: {str(e)}")
            raise


    def get_all_books(self) -> list[dict[str, Any]]:
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                cursor = conn.execute("SELECT * FROM books")
                books = cursor.fetchall()
                return [
                    {"id": book[0], "isbn": book[1], "title": book[2], "author": book[3], "genres": book[4], "description": book[5]}
                    for book in books
                ]
        except Exception as e:
            self.log_manager.log("ERROR", f"Error fetching all books from database: {str(e)}")
            raise

    def create_book(self, title: str, author: str, description: str, genres: str, isbn: str) -> None:
        book_data = {
            "title": title,
            "author": author,
            "description": description,
            "genres": genres,
            "isbn": isbn
        }
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                conn.execute(
                    "INSERT INTO books (isbn, title, author, genres, description) VALUES (%s, %s, %s, %s, %s)",
                    (book_data['isbn'], book_data['title'], book_data['author'], book_data['genres'], book_data['description'])
                )
                self.log_manager.log("INFO", f"Book with ISBN {book_data['isbn']} added to database.")
        except Exception as e:
            self.log_manager.log("ERROR", f"Error adding book with ISBN {book_data['isbn']} to database: {str(e)}")
            raise

    def delete_book(self, book_id: int) -> None:
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                conn.execute("DELETE FROM books WHERE id = %s", (book_id,))
                self.log_manager.log("INFO", f"Book with ID {book_id} deleted from database.")
        except Exception as e:
            self.log_manager.log("ERROR", f"Error deleting book with ID {book_id} from database: {str(e)}")
            raise

    def update_book(self, book_id: int, title: str, author: str, description: str, genres: str, isbn: str) -> None:
        try:
            with self.connection_manager.get_connection_pool().connection() as conn:
                conn.execute(
                    "UPDATE books SET isbn = %s, title = %s, author = %s, genres = %s, description = %s WHERE id = %s",
                    (isbn, title, author, genres, description, book_id)
                )
                self.log_manager.log("INFO", f"Book with ID {book_id} updated in database.")
        except Exception as e:
            self.log_manager.log("ERROR", f"Error updating book with ID {book_id} in database: {str(e)}")
            raise