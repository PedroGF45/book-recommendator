from logs.log_manager import LogManager
from utils.parquet_handler import ParquetHandler

from datetime import date
import polars as pl


class DataCleaner:
    def __init__(self, log_manager: LogManager, parquet_handler: ParquetHandler):
        self.log_manager = log_manager
        self.parquet_handler = parquet_handler

    def perform_full_cleaning(
        self, 
        books_parquet_path: str, 
        users_parquet_path: str, 
        reviews_parquet_path: str,
        min_book_ratings: int = 5,
        min_user_reviews: int = 5,
        output_path: str = "data/cleaned"
    ):
        self.log_manager.log("INFO", "Starting dataset cleaning pipeline...")

        # 1. Clean books first
        cleaned_books_df = self.clean_book_data(books_parquet_path, min_book_ratings=min_book_ratings)
        if cleaned_books_df is None:
            self.log_manager.log("ERROR", "Book cleaning failed. Aborting pipeline.")
            return

        self.parquet_handler.write_parquet(cleaned_books_df, output_path, "cleaned_goodreads_books.parquet")
        self.log_manager.log("INFO", f"Saved cleaned books: {cleaned_books_df.select(pl.len()).collect().item()} rows.")

        # 2. Filter reviews against valid books & compute active users
        raw_users_df = self.parquet_handler.scan_parquet(users_parquet_path)
        raw_reviews_df = self.parquet_handler.scan_parquet(reviews_parquet_path)

        if raw_users_df is None or raw_reviews_df is None:
            self.log_manager.log("ERROR", "Failed to load users or reviews data. Aborting pipeline.")
            return

        cleaned_users_df, cleaned_reviews_df = self.clean_users_and_reviews(
            raw_reviews_df=raw_reviews_df,
            valid_books_df=cleaned_books_df,
            min_user_reviews=min_user_reviews
        )

        self.parquet_handler.write_parquet(cleaned_users_df, output_path, "cleaned_goodreads_users.parquet")
        self.log_manager.log("INFO", f"Saved cleaned users: {cleaned_users_df.select(pl.len()).collect().item()} rows.")

        self.parquet_handler.write_parquet(cleaned_reviews_df, output_path, "cleaned_goodreads_reviews.parquet")
        self.log_manager.log("INFO", f"Saved cleaned reviews: {cleaned_reviews_df.select(pl.len()).collect().item()} rows.")

    def clean_book_data(self, books_parquet_path: str, min_book_ratings: int = 5) -> pl.LazyFrame | None:
        books_df = self.parquet_handler.scan_parquet(books_parquet_path)
        current_year = date.today().year

        try:
            cleaned_books_df = (
                books_df
                # Filter publication years
                .filter(
                    (pl.col("publication_year") >= 1700) &
                    (pl.col("publication_year") <= current_year)
                )
                # Filter books with positive page counts
                .filter(pl.col("num_pages") > 0)
                # Filter books with meaningful rating count
                .filter(pl.col("ratings_count") >= min_book_ratings)
                .with_columns([
                    pl.col("title").str.strip_chars(),
                    pl.col("author").str.strip_chars(),
                    pl.col("publisher").str.strip_chars(),
                    pl.col("description").str.strip_chars(),
                ])
            )
            return cleaned_books_df
        except Exception as e:
            self.log_manager.log("ERROR", f"Error cleaning book data: {str(e)}")
            return None

    def clean_users_and_reviews(
        self, 
        raw_reviews_df: pl.LazyFrame,
        valid_books_df: pl.LazyFrame,
        min_user_reviews: int = 5
    ) -> tuple[pl.LazyFrame, pl.LazyFrame]:
        try:
            self.log_manager.log("INFO", "Filtering reviews against valid books...")
            
            reviews_valid_books = raw_reviews_df.join(
                valid_books_df.select(["goodreads_id"]),
                left_on="book_id",
                right_on="goodreads_id",
                how="inner"
            )

            # 3. Filter users with >= min_user_reviews and select column matching DB schema: `goodreads_id`
            active_users_df = (
                reviews_valid_books
                .group_by("user_id")
                .agg(pl.len().alias("total_reviews"))
                .filter(pl.col("total_reviews") >= min_user_reviews)
                .select([
                    pl.col("user_id").alias("goodreads_id")
                ])
            )

            # 4. Filter and select cleaned reviews schema matching staging table requirements
            cleaned_reviews_df = (
                reviews_valid_books.join(
                    active_users_df,
                    left_on="user_id",
                    right_on="goodreads_id",
                    how="inner"
                )
                .select([
                    pl.col("user_id"),                          # Maps to users.goodreads_id
                    pl.col("book_id"),                          # Maps to books.goodreads_id
                    pl.col("rating").cast(pl.Float64),
                    pl.col("review_text").fill_null("")
                ])
            )

            return active_users_df, cleaned_reviews_df

        except Exception as e:
            self.log_manager.log("ERROR", f"Error filtering users and reviews: {str(e)}")
            raise