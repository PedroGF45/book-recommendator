from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager

log_manager = LogManager()
connection_manager = ConnectionManager(log_manager=log_manager)