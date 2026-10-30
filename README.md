📚 Modular Object-Oriented ETL Data Pipeline

A production-grade, object-oriented Extract, Transform, Load (ETL) pipeline built from scratch in Python. This system ingests raw library loan data, executes a 4-gate validation and data-cleaning engine, and securely persists clean records into an SQLite relational database.

The project demonstrates software engineering best practices, emphasizing OOP encapsulation, defensive programming, fail-fast schema enforcement, and centralized logging.

🚀 Key Architectural Features

Object-Oriented Design & Encapsulation: Modular architecture with dedicated single-responsibility classes (LibraryExtractor, LibraryTransformer, LibraryLoader). Complex transformation logic is encapsulated into specialized private methods (_validate_schema, _check_duplicates, _coerce_types, _apply_business_logic).

Fail-Fast Schema Enforcement: Uses direct indexing (row["column"]) during initial extraction and validation gates to immediately trigger KeyError boundaries on unexpected or missing schema keys, avoiding silent data corruption.

Defensive Boundary Handling: Targeted try...except exception boundaries isolate runtime file I/O locks, non-numeric type conversions, and corrupt records without collapsing the entire pipeline execution.

Modern Python Infrastructure: Cross-platform path handling via pathlib.Path and centralized execution lifecycle tracking using standard logging.

⚙️ Pipeline Lifecycle & Data Architecture

┌─────────────────┐      ┌─────────────────────┐      ┌─────────────────┐
│   Raw CSV Data  │ ───► │  LibraryTransformer │ ───► │   SQLite Database│
└─────────────────┘      └─────────────────────┘      └─────────────────┘
                                    │
                       ┌────────────┴────────────┐
                       │  4-Gate Validation Engine│
                       ├─────────────────────────┤
                       │ Gate 1: Schema Checks   │
                       │ Gate 2: De-duplication  │
                       │ Gate 3: Type Coercion   │
                       │ Gate 4: Business Rules  │
                       └─────────────────────────┘


Extract (extractor.py): Ingests raw loan files with pre-flight existence checks and structured exception boundaries.

Transform (transformer.py): Passes incoming records through four specialized validation gates:

Gate 1 (Schema & Missing Values): Direct indexing checks to confirm key presence and string validity.

Gate 2 (Duplicate Prevention): Stateful Set lookup tracking unique loan_id occurrences.

Gate 3 (Type Coercion): Defensive integer and float conversion with targeted logging defaults.

Gate 4 (Business Rules): Verification of domain constraints (e.g., days_borrowed > 0).

Load (sqlite_loader.py): Manages SQLite connections, handles schema creation, and executes transactional batch insertions via executemany.

Orchestrate (main.py): Central entry point coordinating end-to-end execution, lifecycle error bubbling, and system exit status codes.

📁 Repository Structure

.
├── config.py           # Centralized configuration & logging setup
├── extractor.py        # Data ingestion class
├── transformer.py      # Encapsulated 4-gate data transformation logic
├── sqlite_loader.py    # Database connection & persistence management
├── main.py             # Pipeline orchestrator
├── data/               # Source data directory
├── .gitignore          # Environment and database exclusion rules
└── README.md           # Project documentation


🛠️ Getting Started

Prerequisites

Python 3.10+ installed on your system.

Setup Instructions

Clone the repository:

git clone https://github.com/shrwnbrns/library-etl-pipeline.git
cd library-etl-pipeline


Set up a virtual environment (Optional but recommended):

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate


Run the ETL Pipeline:

python main.py


📋 Logging Output Example

When executed, the pipeline logs structured operational telemetry to the console: