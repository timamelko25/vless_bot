from alembic.config import Config
from alembic import command
import os


def run_migrations():
    os.environ["ALEMBIC_DATABASE_URL"] = (
        "postgresql+asyncpg://test:test@localhost:5430/test_db"
    )

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "app/migration")

    command.upgrade(alembic_cfg, "head")
