# app/routes.py
import os
import sqlite3
import pandas as pd
from flask import Blueprint, request, jsonify, send_file, render_template
from flask import current_app as app
from toolkit import SQLDataToolkit, get_transformation_query

api_bp = Blueprint('api', __name__)

def execute_dynamic_clean_and_validate(csv_path, table_name):
    """Dynamically parses, cleans, and standardizes any CSV for inconsistencies"""
    # Load data dynamically
    df = pd.read_csv(csv_path)
    
    # 1. PRE-CLEANING WITH PANDAS (Fix basic structural breaks before SQL ingestion)
    # Strip whitespaces from column headers themselves
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]
    
    # Identify dynamic column data types
    text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    all_cols = df.columns.tolist()

    # Fill structural NaN values with clear placeholders to clean inconsistencies
    for col in text_cols:
        df[col] = df[col].fillna('UNKNOWN').astype(str).str.strip()
    for col in numeric_cols:
        df[col] = df[col].fillna(0)

    # Boot up SQL engine with the pre-cleaned structure
    toolkit = SQLDataToolkit(app.config['DB_PATH'])
    
    # Re-ingest the cleaned memory frame into SQLite
    df.to_sql(table_name, toolkit.connection, if_exists='replace', index=False)

    # 2. SQL INCONSISTENCY REPAIR WORKFLOW
    # Append master tracking columns for metadata visibility
    try:
        toolkit.execute_logic(f'ALTER TABLE "{table_name}" ADD COLUMN validation_notes TEXT;')
        toolkit.execute_logic(f'ALTER TABLE "{table_name}" ADD COLUMN risk_score TEXT;')
    except sqlite3.OperationalError:
        pass  # Columns already exist

    # Initialize tracking defaults
    toolkit.execute_logic(f'UPDATE "{table_name}" SET validation_notes = "CLEANED", risk_score = "LOW";')

    # Tier A: Clean Text Inconsistencies (Standardize to Upper Case)
    for col in text_cols:
        query = get_transformation_query(table_name, "standardize_names", col)
        if query:
            toolkit.execute_logic(query)
            
        # Flag structural fields left as 'UNKNOWN'
        toolkit.execute_logic(f"""
            UPDATE "{table_name}" 
            SET validation_notes = validation_notes || ' | Missing Value in [{col}]', risk_score = 'MEDIUM'
            WHERE "{col}" = 'UNKNOWN';
        """)

    # Tier B: Flag Numerical Anomalies and Inconsistencies
    for col in numeric_cols:
        # Check for negative value inconsistencies (e.g., negative prices/quantities)
        toolkit.execute_logic(f"""
            UPDATE "{table_name}" 
            SET validation_notes = validation_notes || ' | Negative Value in [{col}]', risk_score = 'HIGH'
            WHERE "{col}" < 0;
        """)

        # Statistical Outlier Detection Inconsistencies
        if df[col].nunique() > 1:
            mean = df[col].mean()
            std = df[col].std()
            outlier_boundary = mean + (3 * std)
            
            toolkit.execute_logic(f"""
                UPDATE "{table_name}" 
                SET validation_notes = validation_notes || ' | Statistical Outlier in [{col}]', risk_score = 'HIGH'
                WHERE "{col}" > {outlier_boundary};
            """)

    # Export out the fully corrected dataset tracking file
    toolkit.export_table_to_csv(table_name, app.config['FINAL_OUTPUT_CSV'])
    toolkit.close_toolkit()


@api_bp.route('/', methods=['GET'])
def home_portal():
    return render_template('upload.html')


@api_bp.route('/validate', methods=['POST'])
def validate_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file field found"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    if file and file.filename.endswith('.csv'):
        filename = file.filename
        table_name = os.path.splitext(filename)[0].lower().replace(" ", "_").replace("-", "_")
        
        uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incoming_data.csv')
        file.save(uploaded_path)
        
        try:
            # Execute the auto-cleaning pipeline loop
            execute_dynamic_clean_and_validate(uploaded_path, table_name)
            
            if request.referrer:
                return f'''
                <div style="font-family:-apple-system,BlinkMacSystemFont,sans-serif; text-align:center; padding-top:100px; background:#f4f6f9; height:100vh; margin:0;">
                    <div style="background:white; display:inline-block; padding:40px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.05); width:450px;">
                        <h2 style="color:#16a34a; margin-bottom:10px;">Data Cleaned & Validated!</h2>
                        <p style="color:#4b5563; font-size:14px; margin-bottom:20px;">
                            Processed <strong>{filename}</strong>. Standardized text cases, fixed missing entries, and appended an anomaly audit summary log.
                        </p>
                        <a href="/download" style="background:#2563eb; color:white; padding:12px 24px; text-decoration:none; border-radius:6px; display:block; font-weight:600; transition:0.2s;">Download Cleaned CSV File</a>
                        <br>
                        <a href="/" style="color:#64748b; font-size:13px; text-decoration:none;">← Upload another dataset</a>
                    </div>
                </div>
                '''
            return jsonify({"status": "success", "message": "Inconsistency processing finalized successfully."}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": f"Pipeline execution failure: {str(e)}"}), 500
    return jsonify({"error": "Invalid format."}), 400


@api_bp.route('/download', methods=['GET'])
def download_file():
    target_file = app.config['FINAL_OUTPUT_CSV']
    if os.path.exists(target_file):
        return send_file(target_file, as_attachment=True, download_name="Cleaned_And_Validated_Dataset.csv")
    return jsonify({"error": "No validation file available."}), 404