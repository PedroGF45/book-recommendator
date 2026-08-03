from scripts.json_to_parquet_converter import JsonToParquetConverter
from logs.log_manager import LogManager

log_manager = LogManager()
converter = JsonToParquetConverter(log_manager)

input_json_file_path = 'C:\\Users\\pedro\\Downloads\\goodreads_reviews_dedup.json\\goodreads_reviews_dedup.json'
output_users_parquet_file_path = 'F:\\Code\\book-recommendator\\data\\goodreads_users.parquet'
output_reviews_parquet_file_path = 'F:\\Code\\book-recommendator\\data\\goodreads_reviews.parquet'

#converter.convert_users_to_parquet(input_json_file_path, output_users_parquet_file_path)
converter.convert_user_book_reviews_to_parquet(input_json_file_path, output_reviews_parquet_file_path)
