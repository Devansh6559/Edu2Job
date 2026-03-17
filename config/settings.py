# config/settings.py
import os
from pathlib import Path
import json

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Paths
MODEL_PATH = BASE_DIR / "models" / "job_role_rf_enhanced.pkl"
DATA_PATH = BASE_DIR / "data" / "processed_education_features.csv"
MAPPING_PATH = BASE_DIR / "config" / "job_mapping.json"

# Load job mapping
with open(MAPPING_PATH, 'r') as f:
    JOB_ROLE_MAPPING = json.load(f)
    JOB_ROLE_MAPPING = {int(k): v for k, v in JOB_ROLE_MAPPING.items()}

# Feature information
FEATURE_NAMES = [
    'degree_encoded',
    'specialization_encoded', 
    'cgpa_normalized',
    'cgpa_category_encoded',
    'certifications_count',
    'coding_skills_encoded',
    'internships_count',
    'projects_count',
    'experience_category_encoded',
    'total_experience',
    'has_research',
    'research_level_encoded',
    'extracurriculars',
    'leadership_positions',
    'field_courses'
]

FEATURE_RANGES = {
    'degree_encoded': (0, 10),
    'specialization_encoded': (0, 14),
    'cgpa_normalized': (0.0, 10.0),
    'cgpa_category_encoded': (0, 4),
    'certifications_count': (0, 5),
    'coding_skills_encoded': (0, 4),
    'internships_count': (0, 4),
    'projects_count': (0, 5),
    'experience_category_encoded': (0, 3),
    'total_experience': (0, 7),
    'has_research': (0, 1),
    'research_level_encoded': (0, 2),
    'extracurriculars': (0, 9),
    'leadership_positions': (0, 3),
    'field_courses': (0, 9)
}

# Model info
MODEL_INFO = {
    'name': 'Random Forest Classifier',
    'accuracy': 0.32,
    'num_classes': 15,
    'num_features': 15
}