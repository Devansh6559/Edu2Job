import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

# Sample training data (In practice, you'd load from a CSV/database)
def create_sample_data():
    data = {
        'degree': ['Computer Science', 'Computer Science', 'Electrical Engineering', 
                  'Mechanical Engineering', 'Business Administration', 'Computer Science',
                  'Electrical Engineering', 'Mechanical Engineering', 'Mathematics',
                  'Physics', 'Chemistry', 'Biology', 'Computer Science'],
        'specialization': ['AI', 'Software Engineering', 'Power Systems', 'Thermodynamics',
                          'Finance', 'Data Science', 'Electronics', 'Manufacturing',
                          'Statistics', 'Quantum', 'Organic', 'Genetics', 'Cybersecurity'],
        'cgpa': [3.8, 3.5, 3.6, 3.4, 3.7, 3.9, 3.3, 3.5, 3.8, 3.6, 3.4, 3.5, 3.7],
        'graduation_year': [2023, 2022, 2023, 2022, 2023, 2024, 2022, 2023, 2023, 2022, 2023, 2022, 2024],
        'job_role': ['AI Engineer', 'Software Developer', 'Electrical Engineer', 
                    'Mechanical Engineer', 'Business Analyst', 'Data Scientist',
                    'Electronics Engineer', 'Manufacturing Engineer', 'Data Analyst',
                    'Research Scientist', 'Chemist', 'Biotechnologist', 'Security Analyst']
    }
    return pd.DataFrame(data)

model = None
label_encoders = {}
feature_columns = ['degree', 'specialization', 'cgpa', 'graduation_year']

def train_model():
    global model, label_encoders
    
    # Load or create sample data
    df = create_sample_data()
    
    # Prepare features
    X = df[feature_columns].copy()
    y = df['job_role']
    
    # Encode categorical variables
    label_encoders = {}
    for column in ['degree', 'specialization']:
        le = LabelEncoder()
        X[column] = le.fit_transform(X[column])
        label_encoders[column] = le
    
    # Encode target
    le_job = LabelEncoder()
    y_encoded = le_job.fit_transform(y)
    label_encoders['job_role'] = le_job
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y_encoded)
    
    # Calculate accuracy
    from sklearn.metrics import accuracy_score
    y_pred = model.predict(X)
    accuracy = accuracy_score(y_encoded, y_pred)
    
    # Save model
    joblib.dump((model, label_encoders), 'job_predictor_model.pkl')
    
    return accuracy

def predict_job_roles(user_data):
    global model, label_encoders
    
    if model is None:
        # Load model if not loaded
        try:
            model, label_encoders = joblib.load('job_predictor_model.pkl')
        except:
            train_model()
    
    # Prepare input data
    input_data = pd.DataFrame([{
        'degree': user_data['degree'],
        'specialization': user_data['specialization'],
        'cgpa': user_data['cgpa'],
        'graduation_year': user_data['graduation_year']
    }])
    
    # Encode categorical features
    for column in ['degree', 'specialization']:
        if column in label_encoders:
            try:
                input_data[column] = label_encoders[column].transform([user_data[column]])[0]
            except:
                # If unknown category, use most frequent
                input_data[column] = 0
    
    # Get predictions with probabilities
    probabilities = model.predict_proba(input_data)[0]
    job_classes = label_encoders['job_role'].classes_
    
    # Get top 5 predictions
    top_5_indices = probabilities.argsort()[-5:][::-1]
    predictions = []
    
    for idx in top_5_indices:
        job_role = job_classes[idx]
        confidence = probabilities[idx]
        
        # Generate skills match explanation
        skills_match = generate_skills_match(user_data, job_role)
        
        predictions.append({
            'job_role': job_role,
            'confidence_score': round(confidence * 100, 2),
            'skills_match': skills_match
        })
    
    return predictions

def generate_skills_match(user_data, job_role):
    # Simple rule-based skills matching
    skills_map = {
        'AI Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'Mathematics'],
        'Software Developer': ['Programming', 'Algorithms', 'Software Engineering', 'Problem Solving'],
        'Data Scientist': ['Statistics', 'Python', 'Machine Learning', 'Data Analysis'],
        'Electrical Engineer': ['Circuit Design', 'Electronics', 'Power Systems', 'Mathematics'],
        'Mechanical Engineer': ['CAD', 'Thermodynamics', 'Mechanics', 'Design'],
        'Business Analyst': ['Analytics', 'Communication', 'Business Knowledge', 'SQL']
    }
    
    default_skills = ['Communication', 'Problem Solving', 'Teamwork', 'Analytical Thinking']
    
    return skills_map.get(job_role, default_skills)