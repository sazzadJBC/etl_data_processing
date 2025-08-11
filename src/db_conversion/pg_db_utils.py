# crud_manager.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Union
from src.db_conversion.models_organization import Organization
from src.db_conversion.models_person import Person
from src.db_conversion.database import Base
import os

class DatabaseManager:
    def __init__(self):
        self.pg_db_url = os.environ.get("PG_DB_URL", "postgresql+psycopg2://postgres:2244@localhost/sevensix_dev_1?client_encoding=utf8")
        self.engine = create_engine( self.pg_db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def _to_dict(self, data: Union[dict, object]) -> dict:
        """Convert Pydantic or object with dict/model_dump to plain dict."""
        if isinstance(data, dict):
            return data
        if hasattr(data, "model_dump"):
            return data.model_dump()
        if hasattr(data, "dict"):
            return data.dict()
        raise TypeError("Data must be a dict or have dict()/model_dump() method")

    def insert(self, model, data: Union[dict, object]):
        """Generic insert method."""
        data = self._to_dict(data)
        with self.SessionLocal() as session:
            obj = model(**data)
            session.add(obj)
            session.commit()
            session.refresh(obj)  # get auto-generated ID
            return obj.id

    def insert_organization_with_person(self, data: Union[dict, object]) -> int:
        data = self._to_dict(data)
        person_data = data.pop("representative_persons", None)

        with self.SessionLocal() as session:
            # Create organization first
            org = Organization(**data)
            session.add(org)
            session.flush()  # This assigns the ID to org
            
            if person_data:
                person_data = self._to_dict(person_data)
                person_data.pop("organization", None)
                
                # Set the foreign key to link person to organization
                person_data['organization_id'] = org.id
                
                person = Person(**person_data)
                session.add(person)

            session.commit()
            return org.id


    def insert_person(self, data: Union[dict, object]) -> int:
        """Insert person only."""
        return self.insert(Person, data)

    def insert_organization_only(self, data: Union[dict, object]) -> int:
        """Insert organization without person."""
        return self.insert(Organization, data)
