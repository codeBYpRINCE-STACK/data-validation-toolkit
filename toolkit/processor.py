import sqlite3
import pandas as pd

class SQLDataToolkit:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def ingest_data(self, csv_path, table_name):
        data_frame = pd.read_csv(csv_path)
        data_frame.to_sql(table_name, self.connection, if_exists='replace', index=False)
        return True

    def run_sql_validation(self, table_name, column, rule_type):
        from toolkit.validator_sql import get_validation_query
        query = get_validation_query(table_name, column, rule_type)
        invalid_records = pd.read_sql_query(query, self.connection)
        print(f"Validation [{rule_type}]: {len(invalid_records)} issues found.")
        return invalid_records

    def execute_logic(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    def export_table_to_csv(self, table_name, output_path):
        query = f"SELECT * FROM {table_name};"
        processed_data = pd.read_sql_query(query, self.connection)
        processed_data.to_csv(output_path, index=False)
        print(f"Exported clean data to {output_path}")

    def close_toolkit(self):
        self.connection.close()