from dotenv import load_dotenv
import os

from logs.log_manager import LogManager

class ConnectionManager:

    def __init__(self, log_manager: LogManager):

        self.log_manager = log_manager
        self.DB_CONFIG = self.get_database_config()
        
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

        self.log_manager.log("INFO", f"Database configuration loaded: {DB_CONFIG}")
        return DB_CONFIG