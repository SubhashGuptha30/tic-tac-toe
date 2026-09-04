from sqlalchemy import (
    inspect,
    text,
)

from app.database.database import engine


MIGRATIONS: dict[str, str] = {
    "best_future_q": (
        "ALTER TABLE learning_updates "
        "ADD COLUMN best_future_q "
        "FLOAT NOT NULL DEFAULT 0.0"
    ),
    "td_target": (
        "ALTER TABLE learning_updates "
        "ADD COLUMN td_target "
        "FLOAT NOT NULL DEFAULT 0.0"
    ),
    "delta_q": (
        "ALTER TABLE learning_updates "
        "ADD COLUMN delta_q "
        "FLOAT NOT NULL DEFAULT 0.0"
    ),
    "alpha": (
        "ALTER TABLE learning_updates "
        "ADD COLUMN alpha "
        "FLOAT NOT NULL DEFAULT 0.20"
    ),
    "gamma": (
        "ALTER TABLE learning_updates "
        "ADD COLUMN gamma "
        "FLOAT NOT NULL DEFAULT 0.95"
    ),
}


TRAINING_RUN_MIGRATIONS: dict[str, str] = {
    "tactical_probability": (
        "ALTER TABLE training_runs "
        "ADD COLUMN tactical_probability "
        "FLOAT NULL"
    ),
}


def run_database_migrations() -> None:
    """
    Safely upgrades an existing database without deleting learned
    Q-values or experiment history.
    """

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    added_columns: list[str] = []

    with engine.begin() as connection:
        if "learning_updates" in table_names:
            existing_columns = {
                column["name"]
                for column in inspector.get_columns(
                    "learning_updates"
                )
            }

            for (
                column_name,
                migration_sql,
            ) in MIGRATIONS.items():
                if column_name in existing_columns:
                    continue

                connection.execute(
                    text(migration_sql)
                )
                added_columns.append(column_name)

                print(
                    "[DB MIGRATION] Added column: "
                    f"learning_updates.{column_name}"
                )

        if "training_runs" in table_names:
            existing_training_columns = {
                column["name"]
                for column in inspector.get_columns(
                    "training_runs"
                )
            }

            for (
                column_name,
                migration_sql,
            ) in TRAINING_RUN_MIGRATIONS.items():
                if column_name in existing_training_columns:
                    continue

                connection.execute(
                    text(migration_sql)
                )

                print(
                    "[DB MIGRATION] Added column: "
                    f"training_runs.{column_name}"
                )

        if "delta_q" in added_columns:
            connection.execute(
                text(
                    """
                    UPDATE learning_updates
                    SET delta_q = new_q - old_q
                    """
                )
            )

            print(
                "[DB MIGRATION] Backfilled delta_q"
            )

        if "td_target" in added_columns:
            connection.execute(
                text(
                    """
                    UPDATE learning_updates
                    SET td_target = td_error + old_q
                    """
                )
            )

            print(
                "[DB MIGRATION] Backfilled td_target"
            )
