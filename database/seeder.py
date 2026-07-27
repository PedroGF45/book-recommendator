from psycopg_pool import ConnectionPool
import os

from logs.log_manager import LogManager


class Seeder():

    def __init__(self, log_manager: LogManager, connection_pool: ConnectionPool, seed_schema_path: str = "database/seeds.sql"):
        self.log_manager = log_manager
        self.connection_pool = connection_pool
        self.seed_schema_path = seed_schema_path

        self.check_seed_schema_file_exists()

    def check_seed_schema_file_exists(self):
        if not os.path.exists(self.seed_schema_path):
            self.log_manager.log("ERROR", f"Seed schema file not found: {self.seed_schema_path}")
            raise FileNotFoundError(f"Seed schema file not found: {self.seed_schema_path}")
        else:
            self.log_manager.log("INFO", f"Seed schema file found: {self.seed_schema_path}")

    def seed_database(self):
        try:
            with open(self.seed_schema_path, "r") as seed_file:
                seed_sql = seed_file.read()

            try:
                with self.connection_pool.connection() as conn:
                    conn.execute(seed_sql)
        
                self.log_manager.log("INFO", "Database seeded successfully.")
            except Exception as e:
                self.log_manager.log("ERROR", f"Error executing seed SQL: {e}")
                raise
        except Exception as e:
            self.log_manager.log("ERROR", f"Error seeding database: {e}")
            raise


    