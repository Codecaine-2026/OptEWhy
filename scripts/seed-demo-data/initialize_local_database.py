"""Apply local database migrations and seed the reference causal graph."""

import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from psycopg import connect
from psycopg import sql

from seed_graph import main as seed_graph


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIRECTORY = REPOSITORY_ROOT / "infra" / "migrations"


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to initialize the local database")

    parsed_url = urlsplit(database_url)
    database_name = parsed_url.path.lstrip("/") or "optewhy"
    if not database_name.replace("_", "").isalnum():
        raise RuntimeError("DATABASE_URL must use an alphanumeric database name")

    admin_url = urlunsplit(parsed_url._replace(path="/postgres"))
    with connect(admin_url, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
        if not exists:
            connection.execute(
                sql.SQL("CREATE DATABASE {} ").format(sql.Identifier(database_name))
            )

    migration_paths = sorted(MIGRATIONS_DIRECTORY.glob("*.sql"))
    with connect(database_url) as connection:
        for migration_path in migration_paths:
            connection.execute(migration_path.read_text(encoding="utf-8"))

    seed_graph()
    print("Local PostgreSQL schema and reference graph are ready.")


if __name__ == "__main__":
    main()
