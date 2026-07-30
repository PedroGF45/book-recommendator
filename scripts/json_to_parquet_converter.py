import polars as pl
import pyarrow.parquet as pq
from tqdm import tqdm
from logs.log_manager import LogManager

class JsonToParquetConverter:
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager

    def convert_books_to_parquet(self, json_file_path: str, parquet_file_path: str, chunk_size: int = 250_000):
        self.log_manager.log("INFO", f"Starting conversion of JSON file '{json_file_path}' to Parquet file '{parquet_file_path}'.")

        try:
            with open(json_file_path, "rb") as f:
                total_lines = sum(1 for _ in f)

            # Read the JSON file into a Polars DataFrame
            df = pl.scan_ndjson(json_file_path)
            self.log_manager.log("DEBUG", f"Successfully read JSON file '{json_file_path}'.")

            cleaned_lazy = (
                df.filter(pl.col("book_id").is_not_null())
                .with_columns([
                    pl.col("book_id").cast(pl.Int64).alias("goodreads_id"),

                    pl.when((pl.col("isbn").is_not_null()) & (pl.col("isbn").str.len_chars() > 0))
                        .then(pl.col("isbn"))
                        .when((pl.col("isbn13").is_not_null()) & (pl.col("isbn13").str.len_chars() > 0))
                        .then(pl.col("isbn13"))
                        .otherwise(pl.concat_str([pl.lit("NO_ISBN_"), pl.col("book_id")]))
                        .alias("isbn"),

                    pl.col("title").fill_null("Unknown Title"),

                    pl.col("authors")
                        .list.first()
                        .struct.field("author_id")
                        .fill_null("Unknown Author")
                        .alias("author"),

                    pl.col("publisher").fill_null("Unknown Publisher"),
                    pl.col("publication_year").cast(pl.Int32, strict=False).fill_null(0),
                    pl.col("num_pages").cast(pl.Int32, strict=False).fill_null(0),
                    pl.col("ratings_count").cast(pl.Int32, strict=False).fill_null(0),
                    pl.col("average_rating").cast(pl.Float32, strict=False).fill_null(0.0),
                    pl.col("description").fill_null("No Description Available"),
                ])
                .select([
                "goodreads_id",
                "isbn",
                "title",
                "author",
                "publisher",
                "publication_year",
                "num_pages",
                "ratings_count",
                "average_rating",
                "description"
                ])
            )

            writer = None
            
            with tqdm(total=total_lines, desc="Converting JSON to Parquet", unit="lines") as pbar:
                for offset in range(0, total_lines, chunk_size):
                    chunk_df = cleaned_lazy.slice(offset, chunk_size).collect()
                    arrow_table = chunk_df.to_arrow()

                    if writer is None:
                        writer = pq.ParquetWriter(parquet_file_path, arrow_table.schema, compression="zstd")

                    writer.write_table(arrow_table)
                    pbar.update(len(chunk_df))

            if writer:
                writer.close()

            self.log_manager.log("INFO", f"Successfully wrote Parquet file '{parquet_file_path}'.")
            
        except Exception as e:
            self.log_manager.log("ERROR", f"Error during conversion: {e}")
            raise

    def convert_users_to_parquet(self, json_file_path: str, parquet_file_path: str, chunk_size: int = 250_000):
        self.log_manager.log("INFO", f"Starting conversion of JSON file '{json_file_path}' to Parquet file '{parquet_file_path}'.")

        try:
            with open(json_file_path, "rb") as f:
                total_lines = sum(1 for _ in f)

            # Read the JSON file into a Polars DataFrame
            df = pl.scan_ndjson(json_file_path)
            self.log_manager.log("DEBUG", f"Successfully read JSON file '{json_file_path}'.")

            cleaned_lazy = (
                df.filter(pl.col("user_id").is_not_null())
                .with_columns([
                    pl.col("user_id").alias("goodreads_id")
                ])
                .select([
                    "goodreads_id"
                ])
            )

            writer = None
            
            with tqdm(total=total_lines, desc="Converting JSON to Parquet", unit="lines") as pbar:
                for offset in range(0, total_lines, chunk_size):
                    chunk_df = cleaned_lazy.slice(offset, chunk_size).collect()
                    arrow_table = chunk_df.to_arrow()

                    if writer is None:
                        writer = pq.ParquetWriter(parquet_file_path, arrow_table.schema, compression="zstd")

                    writer.write_table(arrow_table)
                    pbar.update(len(chunk_df))

            if writer:
                writer.close()

            self.log_manager.log("INFO", f"Successfully wrote Parquet file '{parquet_file_path}'.")
            
        except Exception as e:
            self.log_manager.log("ERROR", f"Error during conversion: {e}")
            raise

    def convert_user_book_reviews_to_parquet(self, json_file_path: str, parquet_file_path: str, chunk_size: int = 250_000):
        self.log_manager.log("INFO", f"Starting conversion of JSON file '{json_file_path}' to Parquet file '{parquet_file_path}'.")

        try:
            with open(json_file_path, "rb") as f:
                total_lines = sum(1 for _ in f)

            # Read the JSON file into a Polars DataFrame
            df = pl.scan_ndjson(json_file_path)
            self.log_manager.log("DEBUG", f"Successfully read JSON file '{json_file_path}'.")

            cleaned_lazy = (
                df.filter(pl.col("user_id").is_not_null() & pl.col("book_id").is_not_null())
                .with_columns([
                    pl.col("user_id").alias("goodreads_id"),
                    pl.col("book_id").cast(pl.Int64).alias("book_id"),
                    pl.col("rating").cast(pl.Float32, strict=False).fill_null(0.0),
                    pl.col("review_text").fill_null("")
                ])
                .select([
                    "user_id",
                    "book_id",
                    "rating",
                    "review_text"
                ])
            )

            writer = None
            
            with tqdm(total=total_lines, desc="Converting JSON to Parquet", unit="lines") as pbar:
                for offset in range(0, total_lines, chunk_size):
                    chunk_df = cleaned_lazy.slice(offset, chunk_size).collect()
                    arrow_table = chunk_df.to_arrow()

                    if writer is None:
                        writer = pq.ParquetWriter(parquet_file_path, arrow_table.schema, compression="zstd")

                    writer.write_table(arrow_table)
                    pbar.update(len(chunk_df))

            if writer:
                writer.close()

            self.log_manager.log("INFO", f"Successfully wrote Parquet file '{parquet_file_path}'.")
            
        except Exception as e:
            self.log_manager.log("ERROR", f"Error during conversion: {e}")
            raise