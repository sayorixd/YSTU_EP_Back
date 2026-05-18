import os
from alembic import context
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv

from src.core.base_model import Base
from src.activity_types.model import ActivityType
from src.competencies.model import Competency
from src.competency_groups.model import CompetencyGroup
from src.control_types.model import ControlType
from src.departments.model import Department
from src.direction_map_cors.model import DirectionMapCore
from src.directions.model import Direction
from src.discipline_block_activity_types.model import DisciplineBlockActivityType
from src.discipline_block_competencies.model import DisciplineBlockCompetency
from src.discipline_blocks.model import DisciplineBlock
from src.disciplines.model import Discipline
from src.educational_forms.model import EducationalForm
from src.educational_levels.model import EducationalLevel
from src.indicators.model import Indicator
from src.map_cors.model import MapCore
from src.study_plans.model import StudyPlan

from src.discipline_block_control_types.model import (
    DisciplineBlockControlType
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

target_metadata = Base.metadata
load_dotenv()
database_url = os.getenv('DATABASE_URL')
config.set_main_option('sqlalchemy.url', database_url)
print(database_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
