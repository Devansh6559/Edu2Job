"""
ML Encoding/Decoding Utility Module
Provides consistent encoding and decoding for ML pipeline
"""

# ===== DEGREE MAPPINGS =====
DEGREE_MAPPING = {
    'B.Tech': 0, 
    'B.Sc': 1, 
    'M.Tech': 2, 
    'MBA': 3, 
    'BCA': 4, 
    'MCA': 5, 
    'B.E': 6, 
    'M.E': 7,
    'B.Com': 8, 
    'Diploma': 9, 
    'Ph.D': 10,
    'Unknown': -1
}

# Reverse mapping for decoding
DEGREE_REVERSE_MAPPING = {v: k for k, v in DEGREE_MAPPING.items()}

# ===== SPECIALIZATION MAPPINGS =====
SPECIALIZATION_MAPPING = {
    'CSE': 0, 
    'IT': 1, 
    'ECE': 2, 
    'Mechanical': 3,
    'Civil': 4, 
    'Electrical': 5, 
    'Electronics': 6,
    'AI/ML': 7, 
    'Data Science': 8, 
    'Cybersecurity': 9,
    'Business Administration': 10, 
    'Finance': 11, 
    'Marketing': 12,
    'Unknown': -1
}

# Reverse mapping for decoding
SPECIALIZATION_REVERSE_MAPPING = {v: k for k, v in SPECIALIZATION_MAPPING.items()}

# ===== CODING SKILLS MAPPINGS =====
CODING_SKILLS_MAPPING = {
    'beginner': 1,
    'Beginner': 1,
    'intermediate': 2,
    'Intermediate': 2,
    'advanced': 3,
    'Advanced': 3,
    'expert': 3,
    'Expert': 3
}

CODING_SKILLS_REVERSE_MAPPING = {
    1: 'Beginner',
    2: 'Intermediate',
    3: 'Advanced'
}

# ===== EXPERIENCE CATEGORY MAPPINGS =====
EXPERIENCE_CATEGORY_MAPPING = {
    'fresher': 1,
    'Fresher': 1,
    'experienced': 2,
    'Experienced': 2
}

EXPERIENCE_CATEGORY_REVERSE_MAPPING = {
    1: 'Fresher',
    2: 'Experienced'
}

# ===== PROJECT COMPLEXITY MAPPINGS =====
PROJECT_COMPLEXITY_MAPPING = {
    'simple': 1,
    'Simple': 1,
    'medium': 2,
    'Medium': 2,
    'complex': 3,
    'Complex': 3
}

PROJECT_COMPLEXITY_REVERSE_MAPPING = {
    1: 'Simple',
    2: 'Medium',
    3: 'Complex'
}

# ===== COMMUNICATION SKILLS MAPPINGS =====
COMMUNICATION_SKILLS_MAPPING = {
    'low': 1,
    'Low': 1,
    'medium': 2,
    'Medium': 2,
    'high': 3,
    'High': 3
}

COMMUNICATION_SKILLS_REVERSE_MAPPING = {
    1: 'Low',
    2: 'Medium',
    3: 'High'
}

# ===== ENCODING FUNCTIONS =====

def encode_degree(degree_str):
    """Encode degree string to integer"""
    if degree_str is None:
        return -1
    degree_str = str(degree_str).strip()
    return DEGREE_MAPPING.get(degree_str, DEGREE_MAPPING.get('Unknown', -1))

def decode_degree(degree_encoded):
    """Decode degree integer to string"""
    if degree_encoded is None:
        return 'Unknown'
    return DEGREE_REVERSE_MAPPING.get(int(degree_encoded), 'Unknown')

def encode_specialization(specialization_str):
    """Encode specialization string to integer"""
    if specialization_str is None:
        return -1
    specialization_str = str(specialization_str).strip()
    return SPECIALIZATION_MAPPING.get(specialization_str, SPECIALIZATION_MAPPING.get('Unknown', -1))

def decode_specialization(specialization_encoded):
    """Decode specialization integer to string"""
    if specialization_encoded is None:
        return 'Unknown'
    return SPECIALIZATION_REVERSE_MAPPING.get(int(specialization_encoded), 'Unknown')

def encode_coding_skills(coding_skills_str):
    """Encode coding skills string to integer"""
    if coding_skills_str is None:
        return 1  # Default to Beginner
    coding_skills_str = str(coding_skills_str).strip().lower()
    return CODING_SKILLS_MAPPING.get(coding_skills_str, CODING_SKILLS_MAPPING.get('beginner', 1))

def decode_coding_skills(coding_skills_encoded):
    """Decode coding skills integer to string"""
    if coding_skills_encoded is None:
        return 'Beginner'
    return CODING_SKILLS_REVERSE_MAPPING.get(int(coding_skills_encoded), 'Beginner')

def encode_experience_category(experience_str):
    """Encode experience category string to integer"""
    if experience_str is None:
        return 1  # Default to Fresher
    experience_str = str(experience_str).strip().lower()
    return EXPERIENCE_CATEGORY_MAPPING.get(experience_str, 1)

def encode_project_complexity(complexity_str):
    """Encode project complexity string to integer"""
    if complexity_str is None:
        return 1  # Default to Simple
    complexity_str = str(complexity_str).strip().lower()
    return PROJECT_COMPLEXITY_MAPPING.get(complexity_str, 1)

def encode_communication_skills(skills_str):
    """Encode communication skills string to integer"""
    if skills_str is None:
        return 2  # Default to Medium
    skills_str = str(skills_str).strip().lower()
    return COMMUNICATION_SKILLS_MAPPING.get(skills_str, 2)

def normalize_cgpa(cgpa):
    """Normalize CGPA from 0-10 scale to 0-1"""
    try:
        cgpa_float = float(cgpa) if cgpa else 0.0
        normalized = cgpa_float / 10.0
        return max(0.0, min(1.0, normalized))
    except (ValueError, TypeError):
        return 0.0

def categorize_cgpa(cgpa):
    """Categorize CGPA: 1=Low(<6), 2=Medium(6-8), 3=High(>8)"""
    try:
        cgpa_float = float(cgpa) if cgpa else 0.0
        if cgpa_float < 6:
            return 1
        elif cgpa_float <= 8:
            return 2
        else:
            return 3
    except (ValueError, TypeError):
        return 1

def count_extracurriculars(extracurriculars_str):
    """Count extracurricular activities from comma-separated string"""
    if not extracurriculars_str:
        return 0
    try:
        items = [item.strip() for item in str(extracurriculars_str).split(',') if item.strip()]
        return len(items)
    except:
        return 0

# ===== FORM VALUE TO ML ENCODING MAPPINGS =====
# These mappings convert HTML form values to ML model encoding values

# Form degree values (from HTML) → ML encoding values
FORM_DEGREE_TO_ML_MAPPING = {
    1: 0,   # Form: "B.Tech/B.E" (value=1) → ML: B.Tech=0
    2: 2,   # Form: "M.Tech/M.E" (value=2) → ML: M.Tech=2
    3: 4,   # Form: "BCA" (value=3) → ML: BCA=4
    4: 5,   # Form: "MCA" (value=4) → ML: MCA=5
    5: 1,   # Form: "B.Sc" (value=5) → ML: B.Sc=1
    6: -1,  # Form: "M.Sc" (value=6) → ML: Not in mapping, use Unknown
    7: 3,   # Form: "MBA" (value=7) → ML: MBA=3
    8: 10,  # Form: "Ph.D" (value=8) → ML: Ph.D=10
    9: 9,   # Form: "Diploma" (value=9) → ML: Diploma=9
}

# Form specialization values (from HTML) → ML encoding values
FORM_SPECIALIZATION_TO_ML_MAPPING = {
    1: 0,   # Form: "Computer Science" (value=1) → ML: CSE=0
    2: 1,   # Form: "Information Technology" (value=2) → ML: IT=1
    3: 6,   # Form: "Electronics" (value=3) → ML: Electronics=6
    4: 3,   # Form: "Mechanical" (value=4) → ML: Mechanical=3
    5: 4,   # Form: "Civil" (value=5) → ML: Civil=4
    6: 5,   # Form: "Electrical" (value=6) → ML: Electrical=5
    7: 7,   # Form: "AI/ML" (value=7) → ML: AI/ML=7
    8: 8,   # Form: "Data Science" (value=8) → ML: Data Science=8
    9: 9,   # Form: "Cybersecurity" (value=9) → ML: Cybersecurity=9
    10: 10, # Form: "Business" (value=10) → ML: Business Administration=10
    11: 11, # Form: "Finance" (value=11) → ML: Finance=11
}

def convert_form_degree_to_ml(form_value):
    """Convert HTML form degree value to ML encoding value"""
    try:
        form_int = int(form_value)
        return FORM_DEGREE_TO_ML_MAPPING.get(form_int, -1)
    except (ValueError, TypeError):
        return -1

def convert_form_specialization_to_ml(form_value):
    """Convert HTML form specialization value to ML encoding value"""
    try:
        form_int = int(form_value)
        return FORM_SPECIALIZATION_TO_ML_MAPPING.get(form_int, -1)
    except (ValueError, TypeError):
        return -1

def prepare_ml_features(user_data):
    """
    Prepare user data for ML model prediction
    Converts raw user data to properly encoded ML features
    
    Args:
        user_data: dict with user data (can have mixed raw/encoded values)
    
    Returns:
        dict: Properly encoded features ready for ML model
    """
    features = {}
    
    # Academic features
    # Handle degree encoding - check if it's a form value that needs conversion
    if 'degree_encoded' in user_data and user_data['degree_encoded'] is not None:
        degree_val = user_data['degree_encoded']
        # Form values are 1-9, ML values are 0-10
        # If value is 0, it's definitely ML format (B.Tech)
        # If value is 1-9, check if it matches form mapping - if conversion result is different, it was a form value
        if isinstance(degree_val, (int, float)) and 1 <= int(degree_val) <= 9:
            original_val = int(degree_val)
            converted_val = convert_form_degree_to_ml(original_val)
            # Only convert if the conversion changes the value (form value) or if result is valid
            # If conversion gives -1 or same value, might already be ML format
            if converted_val != -1 and converted_val != original_val:
                features['degree_encoded'] = converted_val
                print(f"[CONVERT] Form degree value {original_val} -> ML encoding {converted_val}")
            else:
                # Value might already be in ML format, use as-is
                features['degree_encoded'] = int(degree_val)
                print(f"[OK] Using degree_encoded value as-is: {features['degree_encoded']}")
        elif isinstance(degree_val, (int, float)) and int(degree_val) == 0:
            # Value 0 is definitely ML format (B.Tech)
            features['degree_encoded'] = 0
            print(f"[OK] Using ML degree_encoded value: 0 (B.Tech)")
        else:
            features['degree_encoded'] = int(degree_val)
            print(f"[OK] Using direct degree_encoded value: {features['degree_encoded']}")
    elif 'degree' in user_data:
        # Try to encode from string
        features['degree_encoded'] = encode_degree(user_data['degree'])
        print(f"[ENCODE] Degree string '{user_data['degree']}' -> {features['degree_encoded']}")
    else:
        features['degree_encoded'] = -1
        print("[WARN] No degree data found, using -1 (Unknown)")
    
    # Handle specialization encoding - check if it's a form value that needs conversion
    if 'specialization_encoded' in user_data and user_data['specialization_encoded'] is not None:
        spec_val = user_data['specialization_encoded']
        # Form values are 1-11, ML values are 0-11
        # If value is 0, it's definitely ML format (CSE)
        # If value is 1-11, check conversion - if result differs, it was a form value
        if isinstance(spec_val, (int, float)) and 1 <= int(spec_val) <= 11:
            original_val = int(spec_val)
            converted_val = convert_form_specialization_to_ml(original_val)
            # Only convert if the conversion changes the value (form value)
            # Check if conversion makes sense - form value 5 -> ML 4, form value 4 -> ML 3, etc.
            # If the converted value is different from original, it was a form value
            if converted_val != -1 and converted_val != original_val:
                features['specialization_encoded'] = converted_val
                print(f"[CONVERT] Form specialization value {original_val} -> ML encoding {converted_val}")
            else:
                # Value might already be in ML format, use as-is
                features['specialization_encoded'] = int(spec_val)
                print(f"[OK] Using specialization_encoded value as-is: {features['specialization_encoded']}")
        elif isinstance(spec_val, (int, float)) and int(spec_val) == 0:
            # Value 0 is definitely ML format (CSE)
            features['specialization_encoded'] = 0
            print(f"[OK] Using ML specialization_encoded value: 0 (CSE)")
        else:
            features['specialization_encoded'] = int(spec_val)
            print(f"[OK] Using direct specialization_encoded value: {features['specialization_encoded']}")
    elif 'specialization' in user_data:
        # Try to encode from string
        features['specialization_encoded'] = encode_specialization(user_data['specialization'])
        print(f"[ENCODE] Specialization string '{user_data['specialization']}' -> {features['specialization_encoded']}")
    else:
        features['specialization_encoded'] = -1
        print("[WARN] No specialization data found, using -1 (Unknown)")
    
    # CGPA handling
    if 'cgpa_normalized' in user_data and user_data['cgpa_normalized'] is not None:
        features['cgpa_normalized'] = float(user_data['cgpa_normalized'])
    elif 'cgpa' in user_data:
        features['cgpa_normalized'] = normalize_cgpa(user_data['cgpa'])
    else:
        features['cgpa_normalized'] = 0.0
    
    if 'cgpa_category_encoded' in user_data and user_data['cgpa_category_encoded'] is not None:
        features['cgpa_category_encoded'] = int(user_data['cgpa_category_encoded'])
    elif 'cgpa' in user_data:
        features['cgpa_category_encoded'] = categorize_cgpa(user_data['cgpa'])
    else:
        features['cgpa_category_encoded'] = 1
    
    # Skills features
    if 'coding_skills_encoded' in user_data and user_data['coding_skills_encoded'] is not None:
        features['coding_skills_encoded'] = int(user_data['coding_skills_encoded'])
    elif 'coding_skills' in user_data:
        features['coding_skills_encoded'] = encode_coding_skills(user_data['coding_skills'])
    else:
        features['coding_skills_encoded'] = 1
    
    features['certifications_count'] = int(user_data.get('certifications_count', 0) or 0)
    
    # Experience features
    features['internships_count'] = int(user_data.get('internships_count', 0) or 0)
    features['projects_count'] = int(user_data.get('projects_count', 0) or 0)
    features['total_experience'] = int(user_data.get('total_experience', 0) or 0)
    
    if 'experience_category_encoded' in user_data and user_data['experience_category_encoded'] is not None:
        features['experience_category_encoded'] = int(user_data['experience_category_encoded'])
    elif features['total_experience'] > 0:
        features['experience_category_encoded'] = 2  # Experienced
    else:
        features['experience_category_encoded'] = 1  # Fresher
    
    if 'project_complexity' in user_data:
        if isinstance(user_data['project_complexity'], (int, float)):
            features['project_complexity'] = int(user_data['project_complexity'])
        else:
            features['project_complexity'] = encode_project_complexity(user_data['project_complexity'])
    else:
        features['project_complexity'] = 1
    
    # Research features
    if 'has_research' in user_data:
        features['has_research'] = 1 if (user_data['has_research'] or 
                                        user_data.get('research_level_encoded', 0) > 0) else 0
    else:
        features['has_research'] = 0
    
    features['research_level_encoded'] = int(user_data.get('research_level_encoded', 0) or 0)
    features['publications_count'] = int(user_data.get('publications_count', 0) or 0)
    
    # Extracurriculars - handle both string and count
    if 'extracurriculars_count' in user_data and user_data['extracurriculars_count'] is not None:
        features['extracurriculars'] = int(user_data['extracurriculars_count'])
    elif 'extracurriculars' in user_data:
        if isinstance(user_data['extracurriculars'], (int, float)):
            features['extracurriculars'] = int(user_data['extracurriculars'])
        else:
            features['extracurriculars'] = count_extracurriculars(user_data['extracurriculars'])
    else:
        features['extracurriculars'] = 0
    
    features['leadership_positions'] = int(user_data.get('leadership_positions', 0) or 0)
    features['field_courses'] = int(user_data.get('field_courses', 0) or 0)
    
    return features

