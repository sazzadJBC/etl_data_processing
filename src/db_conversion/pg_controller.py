from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
import os
Base = declarative_base()
class DatabaseController:
    def __init__(self):
        self.pg_db_url = os.environ.get("PG_DB_URL", "postgresql+psycopg2://postgres:2244@localhost/sevensix_dev_1?client_encoding=utf8")
        self.engine = create_engine( self.pg_db_url)
    



