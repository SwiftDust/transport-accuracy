import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


def init_database():
    """Initialize the database and create tables if they don't exist"""
    try:
        conn = psycopg2.connect(
            f"dbname=postgres user=postgres password={os.getenv('DB_PASSWORD')}"
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            ("transport_accuracy",),
        )
        db_exists = cur.fetchone()

        if not db_exists:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier("transport_accuracy")
                )
            )
            print("Created database: transport_accuracy")

        cur.close()
        conn.close()

        conn = psycopg2.connect(
            f"dbname=transport_accuracy user=postgres password={os.getenv('DB_PASSWORD')}"
        )
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS delay_snapshots (
                id SERIAL PRIMARY KEY,
                country VARCHAR(50) NOT NULL,
                realtime_avg_delay FLOAT NOT NULL,
                on_time INT NOT NULL,
                on_time_percentage FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:
        print(f"error initializing database: {e}")
        raise


def store_delay_snapshot(
    country: str, avg_delay: float, on_time: int, on_time_percentage: float
):
    conn = psycopg2.connect(
        f"dbname=transport_accuracy user=postgres password={os.getenv('DB_PASSWORD')}"
    )
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO delay_snapshots (country, realtime_avg_delay, on_time, on_time_percentage)
        VALUES (%s, %s, %s, %s)
    """,
        (country, avg_delay, on_time, on_time_percentage),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_delay_snapshots(country: str) -> dict:
    """Get aggregated historical delay statistics for a country"""
    conn = psycopg2.connect(
        f"dbname=transport_accuracy user=postgres password={os.getenv('DB_PASSWORD')}"
    )
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            AVG(realtime_avg_delay) as avg_delay,
            AVG(on_time_percentage) as avg_on_time_percentage
        FROM delay_snapshots
        WHERE country = %s
        """,
        (country,),
    )
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result and result[0] is not None:
        return {
            "avg_delay": float(result[0]),
            "on_time_percentage": float(result[1]) if result[1] else 0.0,
        }

    return {"error": "no historical data exists"}
