import psycopg2
from typing import List, Dict, Optional

DB_CONFIG = {
    "host": "10.10.11.25",
    "port": "5432",
    "database": "sevensix_dev_1",
    "user": "postgres",
    "password": "2244",
}

class DatabaseManager:
    def __init__(self, config: Dict):
        self.config = config

    def create_tables(self):
        person_table = """
        CREATE TABLE IF NOT EXISTS person (
            id SERIAL PRIMARY KEY,
            person_name TEXT,
            title TEXT,
            career_history TEXT,
            current_activities TEXT,
            publications TEXT
        );
        """

        organization_table = """
        CREATE TABLE IF NOT EXISTS organization (
            id SERIAL PRIMARY KEY,
            organization_name TEXT,
            company_overview TEXT,
            business_activities TEXT,
            history TEXT,
            group_companies TEXT,
            major_business_partners TEXT,
            sales_trends TEXT,
            president_message TEXT,
            interview_articles TEXT,
            past_transactions TEXT,
            person_id INTEGER REFERENCES person(id) ON DELETE SET NULL
        );
        """

        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                cur.execute(person_table)
                cur.execute(organization_table)
            conn.commit()

    def insert_data(self, data: List[Dict]):
        with psycopg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                for item in data:
                    person_id = None

                    # Insert person if available
                    person = item.get("representative_persons")
                    if person:
                        cur.execute(
                            """
                            INSERT INTO person (
                                person_name,
                                title,
                                career_history,
                                current_activities,
                                publications
                            ) VALUES (%s, %s, %s, %s, %s)
                            RETURNING id
                            """,
                            (
                                person.get("person_name"),
                                person.get("title"),
                                person.get("career_history"),
                                person.get("current_activities"),
                                person.get("publications")
                            )
                        )
                        person_id = cur.fetchone()[0]

                    # Insert organization with optional person_id
                    cur.execute(
                        """
                        INSERT INTO organization (
                            organization_name,
                            company_overview,
                            business_activities,
                            history,
                            group_companies,
                            major_business_partners,
                            sales_trends,
                            president_message,
                            interview_articles,
                            past_transactions,
                            person_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            item.get("organization_name"),
                            item.get("company_overview"),
                            item.get("business_activities"),
                            item.get("history"),
                            item.get("group_companies"),
                            item.get("major_business_partners"),
                            item.get("sales_trends"),
                            item.get("president_message"),
                            item.get("interview_articles"),
                            item.get("past_transactions"),
                            person_id
                        )
                    )
            conn.commit()
if __name__ == "__main__":
    from agentic_doc.parse import parse  # your existing parser
    db = DatabaseManager(DB_CONFIG)
    db.create_tables()

    # Example parsed structure
    data = parse("your_file_path")  # should return List[Dict]
    db.insert_data(data)
