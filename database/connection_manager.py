from dotenv import load_dotenv
import os
from psycopg_pool import ConnectionPool

from logs.log_manager import LogManager

class ConnectionManager:

    def __init__(self, log_manager: LogManager):

        self.log_manager = log_manager
        self.DB_CONFIG = self.get_database_config()
        self._pool = self._initialize_connection_pool()
        
    def get_database_config(self) -> dict[str, str]:
        try:
            load_dotenv()
        except Exception as e:
            self.log_manager.log("ERROR", f"Error loading database configuration: {e}")

        DB_CONFIG = {
            'name': str(os.getenv('DB_NAME')),
            'user': str(os.getenv('DB_USER')),
            'password': str(os.getenv('DB_PASSWORD')),
            'host': str(os.getenv('DB_HOST', 'localhost')),
            'port': str(os.getenv('DB_PORT', '5432')),
        }

        self.log_manager.log("INFO", "Database configuration loaded")
        return DB_CONFIG

    def _initialize_connection_pool(self) -> ConnectionPool:
        try:
            conn_info = f"dbname={self.DB_CONFIG['name']} user={self.DB_CONFIG['user']} password={self.DB_CONFIG['password']} host={self.DB_CONFIG['host']} port={self.DB_CONFIG['port']}"
            pool = ConnectionPool(conn_info, open=True, max_size=10, max_lifetime=300)
            self.log_manager.log("INFO", "Database connection pool created successfully.")
            return pool
        except Exception as e:
            self.log_manager.log("ERROR", f"Error creating database connection pool: {e}")
            raise

    def get_connection_pool(self) -> ConnectionPool:
        return self._pool

    def close_connection_pool(self):
        try:
            self._pool.close()
            self.log_manager.log("INFO", "Database connection pool closed successfully.")
        except Exception as e:
            self.log_manager.log("ERROR", f"Error closing database connection pool: {e}")
            raise