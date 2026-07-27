from database.connection_manager import ConnectionManager
from database.seeder import Seeder
from logs.log_manager import LogManager

log_manager = LogManager()
connection_manager = ConnectionManager(log_manager=log_manager)
connection_pool = connection_manager.get_connection_pool()

seeder = Seeder(log_manager=log_manager, connection_pool=connection_pool)
seeder.seed_database()