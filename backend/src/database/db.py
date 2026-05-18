from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")


DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def repair_legacy_auth_foreign_keys() -> None:
	"""Repair old FK links to users.id and point them to auth_users.id.

	Older databases created foreign keys on user-scoped state tables against
	the legacy `users` table. Auth now uses `auth_users`, so writes can fail
	with FK violations for valid authenticated users.
	"""
	targets = {
		"chunking_requests": "id",
		"collection_state": "id",
	}

	with engine.begin() as conn:
		fk_rows = conn.execute(
			text(
				"""
				SELECT
					tc.table_name,
					tc.constraint_name,
					ccu.table_name AS referenced_table
				FROM information_schema.table_constraints tc
				JOIN information_schema.key_column_usage kcu
					ON tc.constraint_name = kcu.constraint_name
				   AND tc.table_schema = kcu.table_schema
				JOIN information_schema.constraint_column_usage ccu
					ON tc.constraint_name = ccu.constraint_name
				   AND tc.table_schema = ccu.table_schema
				WHERE tc.constraint_type = 'FOREIGN KEY'
				  AND tc.table_schema = 'public'
				  AND tc.table_name IN ('chunking_requests', 'collection_state')
				  AND kcu.column_name = 'id'
				"""
			)
		).mappings().all()

		for row in fk_rows:
			table_name = row["table_name"]
			constraint_name = row["constraint_name"]
			referenced_table = row["referenced_table"]

			if table_name not in targets:
				continue

			if referenced_table == "auth_users":
				continue

			conn.execute(
				text(f'ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS "{constraint_name}"')
			)

			id_column = targets[table_name]
			conn.execute(
				text(
					f'ALTER TABLE "{table_name}" '
					f'ADD CONSTRAINT "{constraint_name}" '
					f'FOREIGN KEY ("{id_column}") REFERENCES auth_users(id) ON DELETE CASCADE'
				)
			)