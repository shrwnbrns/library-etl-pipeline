import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from config import logger, DB_PATH

class LibraryLoader:

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = Path(db_path)

    def load(self, clean_data: List[Dict[str, Any]]) -> None:

        if not clean_data:
            logger.warning("Loader received empty dataset. Nothing to load.")
            return 

        logger.info("--- Phase 3: Loading into SQLite {self.db_path} Started ---")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Step 1: Create target table if missing
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS library_loans (
                        loan_id INTEGER PRIMARY KEY,
                        member_id TEXT NOT NULL,
                        book_title TEXT NOT NULL,
                        category TEXT NOT NULL,
                        days_borrowed INTEGER NOT NULL,
                        fine_paid REAL NOT NULL
                    )
                """)

                # Step 2: Format rows for batch insertion
                rows_to_insert = [
                    (
                        row["loan_id"],
                        row["member_id"],
                        row["book_title"],
                        row["category"],
                        row["days_borrowed"],
                        row["fine_paid"]
                    )
                    for row in clean_data
                ]

                # Step 3: Batch upsert using executemany
                cursor.executemany("""
                    INSERT OR REPLACE INTO library_loans
                    (loan_id, member_id, book_title, category, days_borrowed, fine_paid)
                    VALUES (?,?,?,?,?,?)
                """, rows_to_insert
                )

                conn.commit()
                logger.info(f"Successfully committed {len(rows_to_insert)} rows to SQLite database.")
        
        except sqlite3.Error as e:
            logger.error(f"Database error during loading phase: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in loader: {e}")
            raise