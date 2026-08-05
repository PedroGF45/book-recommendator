from logs.log_manager import LogManager
import polars as pl
import os
import datetime

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

    def write_parquet(self, df: pl.DataFrame | pl.LazyFrame, path: str = "data", parquet_name: str = "output.parquet") -> bool:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        parquet_path = os.path.join(path, f"{date_str}_{parquet_name}")

        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
                self.log_manager.log("INFO", f"Created directory for Parquet file: {os.path.dirname(path)}")
            except Exception as e:
                self.log_manager.log("ERROR", f"Error creating directory for Parquet file: {os.path.dirname(path)}. Error: {str(e)}")
                return False

        try:
            if isinstance(df, pl.LazyFrame):
                df.sink_parquet(parquet_path)
            else:
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
