from sqlalchemy import text
from app.db.database import engine


def test_database():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM cutoffs"))
            count = result.scalar()

            print("✅ Successfully connected to Supabase!")
            print(f"Total rows in cutoffs table: {count}")

    except Exception as e:
        print("❌ Database connection failed!")
        print(e)


if __name__ == "__main__":
    test_database()