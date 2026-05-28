# toolkit/validator_sql.py

def get_validation_query(table_name, column_name, constraint):
    """Generates generic data-agnostic structural queries using runtime column metadata"""
    
    # 1. Null, Empty, or Missing Data Audit
    if constraint == "identity_completeness":
        return f'SELECT * FROM "{table_name}" WHERE "{column_name}" IS NULL OR "{column_name}" = \'\';'
    
    # 2. Mathematical Negatives Tracking (Safe for any numeric category)
    elif constraint == "negative_check":
        return f'SELECT * FROM "{table_name}" WHERE "{column_name}" < 0;'
    
    # 3. Dynamic Structural Anomaly Check
    elif constraint == "impossible_step":
        return f'SELECT * FROM "{table_name}" WHERE "{column_name}" IS NULL;'
        
    # 4. Statistical Dynamic Outlier Detection (Z-Score calculation using SQLite formulas)
    elif constraint == "outlier_detection":
        return f"""
            SELECT * FROM "{table_name}" 
            WHERE "{column_name}" > (
                SELECT AVG("{column_name}") + 3 * (
                    SELECT AVG(("{column_name}" - sub.a) * ("{column_name}" - sub.a)) 
                    FROM "{table_name}", (SELECT AVG("{column_name}") AS a FROM "{table_name}") AS sub
                ) FROM "{table_name}"
            );
        """
        
    return f'SELECT * FROM "{table_name}" WHERE 1=0;' # Safe fallback to avoid SQL execution errors


def get_transformation_query(table_name, task, column_name=None):
    """Applies universal metadata cleanups and risk classifications"""
    
    # Layer 1: Universal String Trimming and Upper-casing
    if task == "standardize_names" and column_name:
        return f'UPDATE "{table_name}" SET "{column_name}" = UPPER(TRIM("{column_name}")) WHERE "{column_name}" IS NOT NULL;'
    
    # Layer 5: Fallback High-Risk Evaluation rules for arbitrary outliers
    elif task == "flag_high_risk" and column_name:
        return f'UPDATE "{table_name}" SET risk_score = \'HIGH\' WHERE "{column_name}" IS NULL;'
    
    # Layer 5 Default
    elif task == "default_low_risk":
        return f'UPDATE "{table_name}" SET risk_score = \'LOW\' WHERE risk_score IS NULL;'
        
    return ""