# test_crud_manager.py
from src.db_conversion.pg_db_utils import DatabaseManager
from src.db_conversion.models_organization import Organization
from src.db_conversion.models_person import Person

# Sample input data
input_data = {
    "organization_name": "株式会社ハナムラオプティクス",
    "company_overview": "",
    "business_activities": "光学写真機械器具卸",
    "history": "設立：平成7年6月13日",
    "group_companies": "",
    "major_business_partners": "",
    "sales_trends": "",
    "president_message": "",
    "interview_articles": "",
    "past_transactions": "",
    "representative_persons": {
        "person_name": "花村 和伸",
        "organization": "株式会社ハナムラオプティクス",
        "title": "取締役社長（代表）",
        "career_history": "",
        "current_activities": "全般",
        "publications": ""
    }
}

def test_insert_organization_with_person():
    # Use an in-memory SQLite DB for testing
    db = DatabaseManager("postgresql+psycopg2://postgres:2244@localhost/sevensix_dev_1?client_encoding=utf8")
    db.create_tables()

    # Insert data
    org_id = db.insert_organization_with_person(input_data)
    print(f"Inserted Organization ID: {org_id}")

    # Verify inserted data
    with db.SessionLocal() as session:
        org = session.query(Organization).filter_by(id=org_id).first()
        person = session.query(Person).filter_by(id=org.person_id).first()

        print(f"Organization: {org.organization_name}")
        print(f"Person: {person.person_name} - {person.title}")

if __name__ == "__main__":
    test_insert_organization_with_person()
