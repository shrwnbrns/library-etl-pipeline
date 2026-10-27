import csv
from pathlib import Path
from typing import List, Dict, Any
from config import logger

class LibraryExtractor:
    """
    Responsible for extracting raw library loan data from a source CSV file 
    using standard Python file I/O and the built-in csv module.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def extract(self) -> List[Dict[str, Any]]:
        """
        Safely open and reads the CSV file, transforming each row into a dictionary.
        Returns: 
            List[Dict[str, Any]]: A list containing all extracted records.
        """
        
        logger.info("--- Phase 1: Extraction Started ---")
        logger.info(f"Target extraction path: {self.file_path}")

        # Definesive check: Ensure file exist before attempting to read

        if not self.file_path.exists():
            logger.error(f"Critical Error: File not found at {self.file_path}")
            raise FileNotFoundError(f"Source data file missing: {self.file_path}")

        raw_rows: List[Dict[str, Any]] = []

        try:
            # Using Python's built=in context manager (with open) for safe resource handling
            with open(self.file_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    raw_rows.append(row)
            
            logger.info(f"Extraction successful. Pulled {len(raw_rows)} raw rows.")
            return raw_rows
        
        except Exception as e:
            logger.error(f"Failed to read raw CSV data: {e}")
            raise