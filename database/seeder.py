import polars as pl
from tqdm import tqdm
from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager
from utils.parquet_handler import ParquetHandler

class ParquetDbSeeder:
    def __init__(self, log_manager: LogManager, connection_manager: ConnectionManager, parquet_handler: ParquetHandler):
        self.log_manager = log_manager
        self.connection_manager = connection_manager
        self.parquet_handler = parquet_handler

    def seed_books(self, books_parquet_path: str, batch_size: int = 100_000):
        self.log_manager.log("INFO", f"Seeding books from {books_parquet_path}...")
        
        lazy_books = self.parquet_handler.scan_parquet(books_parquet_path)
        total_rows = lazy_books.select(pl.len()).collect().item()

        pool = self.connection_manager.get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                with tqdm(total=total_rows, desc="Seeding Books", unit="rows") as pbar:
                    for offset in range(0, total_rows, batch_size):
                        df_chunk = lazy_books.slice(offset, batch_size).collect()
                        
                        # Use .iter_rows() to yield row tuples
                        records = df_chunk.select([
                            "goodreads_id", "isbn", "title", "author", 
                            "publisher", "publication_year", "num_pages", 
                            "ratings_count", "average_rating", "description"
                        ]).iter_rows()

                        with cur.copy(
                            """
                            COPY books (
                                goodreads_id, isbn, title, author, publisher, 
                                publication_year, num_pages, ratings_count, 
                                average_rating, description
                            ) FROM STDIN
                            """
                        ) as copy:
                            for record in records:
                                copy.write_row(record)

                        conn.commit()
                        pbar.update(len(df_chunk))

        self.log_manager.log("INFO", "Books table seeded successfully.")

    def seed_users(self, users_parquet_path: str, batch_size: int = 100_000):
        self.log_manager.log("INFO", f"Seeding users from {users_parquet_path}...")
        
        lazy_users = self.parquet_handler.scan_parquet(users_parquet_path)
        total_rows = lazy_users.select(pl.len()).collect().item()

        pool = self.connection_manager.get_connection_pool()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                with tqdm(total=total_rows, desc="Seeding Users", unit="rows") as pbar:
                    for offset in range(0, total_rows, batch_size):
                        df_chunk = lazy_users.slice(offset, batch_size).collect()
                        records = df_chunk.select(["external_user_id"]).iter_rows()

                        with cur.copy("COPY users (external_user_id) FROM STDIN") as copy:
                            for record in records:
                                copy.write_row(record)

                        conn.commit()
                        pbar.update(len(df_chunk))

        self.log_manager.log("INFO", "Users table seeded successfully.")

    def seed_reviews(self, reviews_parquet_path: str, batch_size: int = 250_000):
        self.log_manager.log("INFO", f"Seeding user_book_reviews from {reviews_parquet_path}...")
        
        pool = self.connection_manager.get_connection_pool()
        
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TEMP TABLE staging_reviews (
                        external_user_id VARCHAR(64),
                        goodreads_id BIGINT,
                        rating FLOAT,
                        review_text TEXT
                    ) ON COMMIT DROP;
                """)

                lazy_reviews = self.parquet_handler.scan_parquet(reviews_parquet_path)
                total_rows = lazy_reviews.select(pl.len()).collect().item()

                with tqdm(total=total_rows, desc="Staging Reviews", unit="rows") as pbar:
                    for offset in range(0, total_rows, batch_size):
                        df_chunk = lazy_reviews.slice(offset, batch_size).collect()
                        records = df_chunk.select(["user_id", "book_id", "rating", "review_text"]).iter_rows()

                        with cur.copy("COPY staging_reviews FROM STDIN") as copy:
                            for record in records:
                                copy.write_row(record)
                        
                        pbar.update(len(df_chunk))

                self.log_manager.log("INFO", "Transferring staged reviews to user_book_reviews with FK joins...")
                
                cur.execute("""
                    INSERT INTO user_book_reviews (user_id, book_id, rating, review)
                    SELECT u.id, b.id, sr.rating, sr.review_text
                    FROM staging_reviews sr
                    JOIN users u ON u.external_user_id = sr.external_user_id
                    JOIN books b ON b.goodreads_id = sr.goodreads_id
                    ON CONFLICT (user_id, book_id) DO NOTHING;
                """)
                conn.commit()

        self.log_manager.log("INFO", "user_book_reviews seeded successfully.")