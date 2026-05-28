# Data Processing and Validation Toolkit

A modular Python and SQL framework designed to handle structured datasets with high efficiency. This toolkit implements a 5-layer validation architecture to ensure data integrity and reliability for large-scale financial records.

## Key Features
- **Layer 1: Normalization** - Standardizes string data using SQL UPPER and TRIM functions.
- **Layer 2: Structural Integrity** - Mathematically verifies account balance consistency across millions of rows.
- **Layer 3: Logical Validation** - Scans for negative values, nulls, and impossible time steps.
- **Layer 4: Anomaly Detection** - Identifies high-value outliers using statistical thresholding.
- **Layer 5: Feature Engineering** - Programmatically injects risk-level labeling based on transaction behavior.

## Tech Stack
- **Python:** Modular Object-Oriented programming for the toolkit engine.
- **SQL (SQLite):** Set-based logic for high-performance data transformation.
- **Pandas:** Efficient data ingestion and CSV exporting.

## Usage
The toolkit is designed to be imported into any data pipeline:
```python
from toolkit.processor import SQLDataToolkit
toolkit = SQLDataToolkit('database.db')
toolkit.ingest_data('source.csv', 'table_name')
toolkit.run_sql_validation('table_name', 'column', 'balance_integrity')
