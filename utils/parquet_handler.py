from logs.log_manager import LogManager
import polars as pl

class ParquetHandler:
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager

    def read_parquet(self, parquet_path: str) -> pl.DataFrame | None:
        try:
            df = pl.read_parquet(parquet_path)
            self.log_manager.log("INFO", f"Successfully loaded Parquet file: {parquet_path}")
            return df
        except Exception as e:
            self.log_manager.log("ERROR", f"Error loading Parquet file: {parquet_path}. Error: {str(e)}")
            return None

    def write_parquet(self, df: pl.DataFrame, parquet_path: str) -> bool:
        try:
            df.write_parquet(parquet_path)
            self.log_manager.log("INFO", f"Successfully wrote Parquet file: {parquet_path}")
            return True
        except Exception as e:
            self.log_manager.log("ERROR", f"Error writing Parquet file: {parquet_path}. Error: {str(e)}")
            return False

    def scan_parquet(self, parquet_path: str) -> pl.LazyFrame | None:
        try:
            lazy_df = pl.scan_parquet(parquet_path)
            self.log_manager.log("INFO", f"Successfully scanned Parquet file: {parquet_path}")
            return lazy_df
        except Exception as e:
            self.log_manager.log("ERROR", f"Error scanning Parquet file: {parquet_path}. Error: {str(e)}")
            return None