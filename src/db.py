import psycopg
from psycopg import Connection
from typing import List
from .models import CsvEntry


class Database:
    def __init__(self, connection_string: str):
        self.conn_string = connection_string
        self.init_db()

    def connect(self) -> Connection:
        return psycopg.connect(self.conn_string)

    def init_db(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS csv_entries (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        week_day VARCHAR(10) NOT NULL,
                        hour TIME NOT NULL,
                        ticket_number VARCHAR(50) NOT NULL,
                        waiter INTEGER NOT NULL,
                        product_name VARCHAR(200) NOT NULL,
                        quantity FLOAT NOT NULL,
                        unitary_price FLOAT NOT NULL,
                        total FLOAT NOT NULL
                    )
                """)
            conn.commit()

    def insert_entries(self, entries: List[CsvEntry]):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    """
                    INSERT INTO csv_entries (date, week_day, hour, ticket_number, waiter, product_name, quantity, unitary_price, total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [(entry.date, entry.week_day, entry.hour, entry.ticket_number, entry.waiter,
                      entry.product_name, entry.quantity, entry.unitary_price, entry.total)
                     for entry in entries]
                )
            conn.commit()

    def execute_and_stringify(self, sql_query: str) -> str:
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_query)
                    results = cur.fetchall()

                    if results is None:
                        return "No results returned."

                    stringified_results = ""
                    for row in results:
                        stringified_row = ", ".join(str(item) for item in row)
                        stringified_results += f"({stringified_row})\n"

                    return stringified_results.strip()
        except psycopg.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"An error occurred: {e}"
