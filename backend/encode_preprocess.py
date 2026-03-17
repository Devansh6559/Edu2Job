# """
# encode_preprocess.py
# Standalone preprocessing + encoding script for Edu2Job.

# This script:
# - Connects to the database using SQLAlchemy models
# - Reads user education data
# - Applies Label Encoding / One-Hot Encoding
# - Prints ML-ready encoded vectors
# """

# import json
# import numpy as np
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sklearn.preprocessing import LabelEncoder

# # Import your SQLAlchemy models
# from models import User, db
# from config import Config


# # ------------------------------------------------------
# # Database Setup
# # ------------------------------------------------------
# def create_session():
#     engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
#     Session = sessionmaker(bind=engine)
#     return Session()


# # ------------------------------------------------------
# # Define Master Categories
# # (Update this list according to your project)
# # ------------------------------------------------------
# # Add "Unknown" category to avoid errors
# DEGREE_LIST = ["Unknown", "B.Tech", "B.Sc", "M.Tech", "MBA","CSE", "IT", "ECE", "Mechanical", "Civil Engineering", "Electrical", "Management", "Finance", "Marketing","Computer Science","AI"]
# SPECIALIZATION_LIST = ["Unknown", "CSE", "IT", "ECE", "Mechanical", "Civil", "Electrical", "Management", "Finance", "Marketing","Computer Science","AI","Designing"]


# CERTIFICATION_MASTER = [
#     "Python",
#     "Java",
#     "C++",
#     "Machine Learning",
#     "Data Science",
#     "AWS",
#     "DevOps",
#     "Cyber Security",
# ]


# # ------------------------------------------------------
# # Prepare Label Encoders
# # ------------------------------------------------------
# degree_encoder = LabelEncoder()
# specialization_encoder = LabelEncoder()

# degree_encoder.fit(DEGREE_LIST)
# specialization_encoder.fit(SPECIALIZATION_LIST)


# # Encoding Function

# def encode_user(degree, specialization, certifications_json, cgpa):

#     degree = degree.strip() if degree else "Unknown"
#     specialization = specialization.strip() if specialization else "Unknown"
#     if degree not in degree_encoder.classes_:
#         print(f"[WARN] Unknown degree found: {degree} -> using 'Unknown'")
#         degree = "Unknown"

#     degree_enc = int(degree_encoder.transform([degree])[0])
#     if specialization not in specialization_encoder.classes_:
#         print(f"[WARN] Unknown specialization found: {specialization} -> using 'Unknown'")
#         specialization = "Unknown"

#     specialization_enc = int(specialization_encoder.transform([specialization])[0])

#     certifications = json.loads(certifications_json) if certifications_json else []
#     cert_vector = [1 if cert in certifications else 0 for cert in CERTIFICATION_MASTER]

#     try:
#         cgpa = float(cgpa)
#         normalized_cgpa = cgpa / 10   
#     except:
#         print(f"[WARN] Invalid CGPA value: {cgpa} -> using 0")
#         normalized_cgpa = 0

#     return [degree_enc, specialization_enc, normalized_cgpa] + cert_vector
# # for milstone 2
# # for milstone 2


# # end m2
# # ------------------------------------------------------
# # Main Execution
# # ------------------------------------------------------
# if __name__ == "__main__":
#     print("\nConnecting to database...")

#     session = create_session()

#     print("Fetching user education records\n")

#     users = session.query(User).all()

#     if not users:
#         print("No users found in database.")
#         exit()

#     print("ENCODED OUTPUT\n")

#     for user in users:
#         vector = encode_user(
#     user.degree,
#     user.specialization,
#     user.certifications,
#     user.cgpa
#     )


#         print(f"User: {user.email}")
#         print(f"Encoded Vector: {vector}\n")

#     print("Encoding Completed Successfully!")


"""# # for milstone 2"""
"""
encode_preprocess.py - ML Preprocessing Module
DEPRECATED: Use ml_encoding.py for consistent encoding/decoding
This file is kept for backward compatibility
"""

import json
from ml_encoding import (
    encode_degree, encode_specialization, normalize_cgpa,
    DEGREE_MAPPING, SPECIALIZATION_MAPPING
)

# Keep mappings for backward compatibility
# But use functions from ml_encoding.py for actual encoding

def preprocess_single_user(user_data):
    """
    Preprocess a single user's education data for ML model
    
    Args:
        user_data: dict with keys: degree, specialization, cgpa, 
                   graduation_year, certifications
                   
    Returns:
        processed_vector: list of numerical values ready for ML model
    """
    try:
        # Get raw values with defaults
        degree = user_data.get('degree', '').strip() or 'Unknown'
        specialization = user_data.get('specialization', '').strip() or 'Unknown'
        cgpa = user_data.get('cgpa', 0)
        graduation_year = user_data.get('graduation_year', 0)
        certifications = user_data.get('certifications', '')
        
        # Encode degree using unified encoding utility
        degree_encoded = encode_degree(degree)
        
        # Encode specialization using unified encoding utility
        specialization_encoded = encode_specialization(specialization)
        
        # Normalize CGPA using unified encoding utility
        cgpa_normalized = normalize_cgpa(cgpa)
        
        # Process certifications (count)
        cert_count = 0
        if certifications:
            cert_list = [cert.strip() for cert in certifications.split(',') if cert.strip()]
            cert_count = len(cert_list)
        
        # Create processed vector
        processed_vector = [
            degree_encoded,
            specialization_encoded,
            cgpa_normalized,
            int(graduation_year),
            cert_count
        ]
        
        print(f"[Preprocessing] Raw: {user_data}")
        print(f"[Preprocessing] Processed: {processed_vector}")
        
        return processed_vector
        
    except Exception as e:
        print(f"[Preprocessing Error] {e}")
        return None

# For batch processing
if __name__ == "__main__":
    # Example usage
    test_data = {
        'degree': 'B.Tech',
        'specialization': 'CSE',
        'cgpa': 8.5,
        'graduation_year': 2024,
        'certifications': 'Python, Machine Learning'
    }
    
    result = preprocess_single_user(test_data)
    print(f"Test Result: {result}")
