import sys
from pathlib import Path
from config import logger, DATA_PATH, DB_PATH
from extractor import LibraryExtractor
from transformer import LibraryTransformer
from sqlite_loader import LibraryLoader

def run_pipeline() -> None:

    logger.info("===========================================")
    logger.info(" STARTING LIBRARY ETL PIPELINE")
    logger.info("===========================================")

    try:
        # --- PHASE 1: EXTRACTION ---
        logger.info("--- PHASE 1: Extraction Started (Source: {FILE_PATH}) ---")
        extractor = LibraryExtractor(DATA_PATH)
        raw_data = extractor.extract()
        logger.info(f"Extraction complete. Fetched {len(raw_data)} raw_rows from csv.")

        # --- PHASE 2: TRANSFORMATION --- 
        logger.info("--- PHASE 2: Transformation & Validation Started ---")
        transformer = LibraryTransformer(raw_data)
        clean_data = transformer.transform()
        logger.info(f"Transformation complete. {len(clean_data)} valid rows passed validation.")

        # --- PHASE 3: LOADING --- 
        if not clean_data:
            logger.warning("No clean data available to load. Pipeline skipping load phase.")
        else:
            loader = LibraryLoader(DB_PATH)
            loader.load(clean_data)

        logger.info("========================================")
        logger.info(" PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("========================================")

    except FileNotFoundError as fnf:
        # Catch missing file error from the extractor
        logger.critical(f"Pipeline Haldted. Missing data file --> {fnf}")
        sys.exit(1)
    except KeyError as ke:
        # Catch system-level schema hard-fails from the transfomer
        logger.critical(f"Pipeline Halted. Critical schema validation error -> {ke}")
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected system disasters
        logger.critical(f"Pipeline Halted. Unexpected fatal error -> {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()