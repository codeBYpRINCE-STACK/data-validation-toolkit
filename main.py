# main.py
import os
import sqlite3
from config import Config
from toolkit import SQLDataToolkit, get_transformation_query

def run_advanced_toolkit():
    print("--- Starting 5-Layer Data Validation Toolkit (CLI Mode) ---")
    
    # 1. Pull dynamic path targets from centralized config
    csv_source = '/Users/princekumar/Downloads/Financial data analysis /venv/data/Transactions.csv'
    db_path = Config.DB_PATH
    output_csv = Config.FINAL_OUTPUT_CSV
    
    # 2. Ensure targeted storage directories exist seamlessly
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
    
    # 3. Instantiate and run toolkit engine
    toolkit = SQLDataToolkit(db_path)
    toolkit.ingest_data(csv_source, 'transactions')

    print("Layer 1: Data Cleansing & Normalization")
    toolkit.execute_logic(get_transformation_query('transactions', 'standardize_names'))

    print("Layer 2: Structural Integrity Checks")
    toolkit.run_sql_validation('transactions', 'newbalanceOrig', 'balance_integrity')
    toolkit.run_sql_validation('transactions', 'step', 'impossible_step')

    print("Layer 3: Logical Value Validation")
    toolkit.run_sql_validation('transactions', 'amount', 'negative_check')
    toolkit.run_sql_validation('transactions', 'nameOrig', 'identity_completeness')

    print("Layer 4: Statistical Outlier Detection")
    toolkit.run_sql_validation('transactions', 'amount', 'outlier_detection')

    print("Layer 5: Business Intelligence Transformation")
    # Wrap in a try-except block to gracefully handle repeated local CLI runs
    try:
        toolkit.execute_logic("ALTER TABLE transactions ADD COLUMN risk_score TEXT;")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            pass  # The column already exists from a prior run, bypass safely
        else:
            raise e  # If it's a different database issue, raise it
            
    toolkit.execute_logic(get_transformation_query('transactions', 'flag_high_risk'))
    toolkit.execute_logic(get_transformation_query('transactions', 'default_low_risk'))

    # 4. Save result output to the designated 'data/outputs' folder
    toolkit.export_table_to_csv('transactions', output_csv)
    toolkit.close_toolkit()
    
    print(f"--- Toolkit Execution Successful ---")
    print(f"Validated file saved to: {output_csv}")

if __name__ == "__main__":
    run_advanced_toolkit()