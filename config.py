# config.py
import os

class Config:
    # 1. Base Directory Tracking
    # Gets the absolute path of the root directory where config.py lives
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # 2. Centralized Data Directory Mapping
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(DATA_DIR, 'outputs')
    
    # 3. Database & Output CSV Absolute File Targets
    DB_PATH = os.path.join(DATA_DIR, 'toolkit_v2.db')
    FINAL_OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, 'Final_Validated_Data.csv')
    
    # 4. Global API Configurations
    # Restricts incoming files to a maximum of 16 Megabytes to protect server memory
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 
    
    # Secret key for session/security protection (can be anything for local development)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-this-validation-key'