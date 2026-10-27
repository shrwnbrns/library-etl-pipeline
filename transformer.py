from typing import List, Dict, Any, Set
from config import logger

class LibraryTransformer:

    REQUIRED_COLUMNS: Set[str] = {
        "loan_id", "member_id", "book_title", "category", "days_borrowed", "fine_paid"
    }

    def __init__(self, raw_data: List[Dict[str, Any]]) -> None:
        self.raw_data = raw_data

    def transform(self) -> List[Dict[str, Any]]:

        logger.info("--- Phase 2: Transformation & Validation Started --- ")
        logger.info(f"Processing {len(self.raw_data)} raw records through validation gates.")

        # Guard clause: Exit early if ingestion returned nothing.
        if not self.raw_data:
            logger.warning("Warning: Raw data dataset is empty.")
            return []

        # Step 1: System-level Validation (Hard-Fail Barrier)
        # Verify file structure before processing rows.
        self._validate_schema()

        # Step 2: Initialized State Trackers
        # - Accumulator Pattern: Gather pristine, valid row.
        # - Dedup Tracking: Set to instantly catch duplicate primary keys in memory.
        clean_accumulator: List[Dict[str, Any]] = []
        seen_loan_ids: Set[int] = set()
        dropped_count = 0

        # Step 3: Iterative Row-level Processing (Soft-Fail Loop)
        for row in self.raw_data:
            validated_row = self._validate_and_clean_row(row, seen_loan_ids)

            if validated_row:
                clean_accumulator.append(validated_row)
            else:
                dropped_count += 1

        logger.info(f"Transformation complete. Retained: {len(clean_accumulator)} rows | Dropped: {dropped_count} bad rows.")
        return clean_accumulator

    def _validate_schema(self) -> None:
        # SYSTEM-LEVEL CHECK / HARD FAIL
        # Mandatory Schema Validation

        first_row_keys = set(self.raw_data[0].keys())
        missing_columns = self.REQUIRED_COLUMNS - first_row_keys
        
        if missing_columns:
            error_msg = f"Source CSV schema mismatch. Missing required columns: {missing_columns}"
            logger.critical(error_msg)
            raise KeyError(error_msg)

        logger.info(f"Schema validation passed. All required colums present.    ")

    def _validate_and_clean_row(self, row: Dict[str, Any], seen_loan_ids: Set[int]) -> None:
        # ROW-LEVEL WORKER / SOFT-FAIL GATE
        
        try:
            # --- GATE 1: String Normalization & Strip Check ---
            # Using direct dictionary indexing (row["key"]) to catch missing keys.
            
            loan_id_raw = str(row["loan_id"]).strip()
            member_id_raw = str(row["member_id"]).strip()

            if not loan_id_raw or not member_id_raw:
                logger.warning(f"Gate 1 Failed (Empty ID): Dropping row -> {row}")
                return None

            # --- GATE 2 : Deduplication check --- 
            loan_id = int(loan_id_raw)
            if loan_id in seen_loan_ids:
                logger.warning(f"Gate 2 Failed (Duplicate Loan ID {loan_id}): Dropping duplicate row.")
                return None
            seen_loan_ids.add(loan_id)

            # --- GATE 3: Type Coercion & Data Sanitation ---
            book_title = str(row["book_title"]).strip()
            category = str(row["category"]).strip()

            # Safely coerce string to integer
            days_borrowed_raw = str(row["days_borrowed"]).strip()
            try: 
                days_borrowed = int(days_borrowed_raw)
            except ValueError:
                logger.warning(f"Gate 3 Failed (Type Error): Invalid days_borrowed '{days_borrowed_raw}' for loan {loan_id}. Dropping raw")
                return None

            # Safely coerce string float, with fallback safety
            fine_paid_raw = str(row["fine_paid_row"]).strip()
            try:
                fine_paid = float(fine_paid_raw)
            except ValueError:
                logger.warning(f"Gate 3 Failed (Type Error): Invalid fine_paid '{fine_paid}' for loan {loan_id}. Defaulting to 0.00")
                fine_paid = 0.00

            # --- GATE 4: Business Logic Sanity Check --- 
            if days_borrowed <= 0:
                logger.warning(f"Gate 4 Failed (Business Logic): Impossible days_borrowed for loan {loan_id}. Dropping row.")
                return None

            # --- SUCCESS: Build and return the clean, typed dictionary --- 
            clean_row = {
                "loan_id": loan_id,
                "member_id": member_id_raw,
                "book_title": book_title,
                "category": category, 
                "days_borrowed": days_borrowed,
                "fine_paid": fine_paid

            }
            return clean_row
        except KeyError as key_err:
            # Row-level safety net if a dictionary key is completely missing unexpectedly
            logger.error(f"Gate 1 / Schema Critical Failure: Missing expected column key {key_err} in row: {row}")
            return None
        except Exception as e:
            # Catch-all safety net for unpredictable runtine anomalies on this row
            logger.error(f"Unexpected error processing row {row}: {e}")
            return None