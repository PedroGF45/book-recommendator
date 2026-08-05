from logs.log_manager import LogManager
from utils.parquet_handler import ParquetHandler

from datetime import date
import polars as pl


class DataCleaner:
    def __init__(self, log_manager: LogManager, parquet_handler: ParquetHandler):
        self.log_manager = log_manager
        self.parquet_handler = parquet_handler

    def clean_book_data(self, books_parquet_path: str) -> pl.DataFrame | None:
        books_df = self.parquet_handler.read_parquet(books_parquet_path)

        current_year = date.today().year

        try:
            cleaned_books_df = (
                books_df

                # filter publication years between 1700 and current year
                .filter(
                    (pl.col("publication_year") >= 1700) &
                    (pl.col("publication_year") <= current_year)
                )

                # filter books with more than 0 pages
                .filter(pl.col("num_pages") > 0)

                # filter books with more than 0 ratings
                .filter(pl.col("ratings_count") > 0)

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
