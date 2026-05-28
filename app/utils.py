
import os

def allowed_file(filename, allowed_extensions={'csv'}):
    """
    Utility check to see if an incoming file extension matches system expectations
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions