import sqlite3

import pytest
from sqlalchemy import create_engine, inspect

import app.migrate as migrate
from app.database import Base


def _versions(path):
    con = sqlite3.connect(path)
    try:
        return con.execute("select version_num from alembic_version").fetchall()
    finally:
        con.close()


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "m.db"
    monkeypatch.setattr(migrate.settings, "DATABASE_URL", f"sqlite+aiosqlite:///{path}")
    return path


async def test_fresh_database_is_stamped_at_head(db_path):
    assert await migrate.database_state() == "empty"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    engine.dispose()
    assert await migrate.database_state() == "legacy"
    await migrate.run_migrations("empty")
    assert _versions(db_path) == [("0001",)]
    assert await migrate.database_state() == "versioned"


async def test_baseline_upgrade_from_nothing_builds_full_schema(db_path):
    await migrate.asyncio.to_thread(migrate.command.upgrade, migrate._config(), "head")
    tables = set(inspect(create_engine(f"sqlite:///{db_path}")).get_table_names())
    assert set(Base.metadata.tables) <= tables


async def test_legacy_database_is_stamped_then_upgraded(db_path):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    engine.dispose()
    await migrate.run_migrations("legacy")
    assert _versions(db_path) == [("0001",)]


async def test_baseline_matches_models_no_drift(db_path):
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    await migrate.asyncio.to_thread(migrate.command.upgrade, migrate._config(), "head")
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), Base.metadata)
    assert diff == [], f"models drifted from migrations: {diff[:3]}"
