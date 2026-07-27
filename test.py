from database.connection_manager import ConnectionManager
from logs.log_manager import LogManager

log_manager = LogManager()
connection_manager = ConnectionManager(log_manager=log_manager)
connection_pool = connection_manager.get_connection_pool()

with connection_pool.connection() as conn:
    try:
        cursor = conn.execute("SELECT * FROM books;")
        for row in cursor:
            log_manager.log("INFO", f"Book: {row}")
        log_manager.log("INFO", "Query executed successfully.")
    except Exception as e:
        log_manager.log("ERROR", f"Error executing query: {e}")
