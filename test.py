from logs.log_manager import LogManager
from eda.data_analyzer import DataAnalyzer

if __name__ == "__main__":
    log_manager = LogManager()
    data_analyzer = DataAnalyzer(log_manager)

    books_parquet_file_path = "F:/Code/book-recommendator/data/goodreads_books.parquet"
    users_parquet_file_path = "F:/Code/book-recommendator/data/goodreads_users.parquet"
    reviews_parquet_file_path = "F:/Code/book-recommendator/data/goodreads_reviews.parquet"

    #data_analyzer.perform_full_analysis(books_parquet_file_path, prefix="books")
    #data_analyzer.perform_full_analysis(users_parquet_file_path, prefix="users")
    data_analyzer.perform_full_analysis(reviews_parquet_file_path, prefix="reviews")
