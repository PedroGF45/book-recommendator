import os
import time

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class LogManager:

    def __init__(self, log_file_path: str = "logs/app.log"):
        self.log_file_path = log_file_path
        self.ensure_log_directory_exists()

    def ensure_log_directory_exists(self):
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def log(self, log_level: str = "INFO", message: str = ""):
        if log_level not in LOG_LEVELS:
            raise ValueError(f"Invalid log level: {log_level}")

        actual_time = time.strftime('%Y-%m-%d %H:%M:%S')

        with open(self.log_file_path, "a") as log_file:
            log_file.write(f"[{log_level}] {actual_time} {message}\n")