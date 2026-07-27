from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager

import httpx

class BookService:
    def __init__(self, log_manager: LogManager, connection_manager: ConnectionManager, api_base_url: str):
        self.log_manager = log_manager
        self.connection_manager = connection_manager
        self.api_base_url = api_base_url
        self.client = httpx.Client(timeout=10)


    def get_book_by_isbn(self, isbn: str):

        # 1 Check if the book exists in the local database
        with self.connection_manager.get_connection() as conn:
            book = conn.execute("SELECT id, title, author, description, genres FROM books WHERE isbn = %s", (isbn,))

            if book:
                return book


        # 2 There is no book on the dabase with that isbn so we need to fetch it using our api
        book_url = f'{self.api_base_url}{isbn}'
        api_response = self.client.get(book_url)
        book_data = api_response.json()

        print(book_data)