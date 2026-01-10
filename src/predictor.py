# simple_predictor.py
import pandas as pd
import numpy as np
import pickle

# Load model
with open("models/job_role_rf_enhanced.pkl", 'rb') as f:
    saved_data = pickle.load(f)

model = saved_data['model']
scaler = saved_data['scaler']
feature_names = saved_data['feature_names']

# Use the classes from the model itself
model_classes = model.classes_

# Create a simple mapping - you can customize this
JOB_NAMES = {
    0: "AI Researcher",                
  1: "Aerospace Engineer",             
  2: "Business Analyst",               
  3: "Chemical Engineer",             
  4: "Civil Engineer",                 
  5: "Cybersecurity Analyst",          
  6: "Data Scientist",                 
  7: "Electrical Engineer",            
  8: "Financial Analyst",              
  9: "Game Developer",                 
 10: "Graphic Designer",               
 11: "Mechanical Engineer",            
 12: "Product Manager",                
 13: "Software Developer",             
 14: "Web Developer"                                  
}

def predict_career(student_data):
    """Simple prediction function"""
    # Prepare input
    X = pd.DataFrame([student_data])
    
    # Add missing features
    for feature in feature_names:
        if feature not in X.columns:
            X[feature] = 0
    
    X = X[feature_names]
    
    # Scale and predict
    X_scaled = scaler.transform(X)
    pred_class = int(model.predict(X_scaled)[0])
    probabilities = model.predict_proba(X_scaled)[0]
    
    # Find index in model classes
    pred_index = np.where(model_classes == pred_class)[0][0]
    confidence = probabilities[pred_index]
    
    # Get job name
    job_name = JOB_NAMES.get(pred_class, f"Career Code {pred_class}")
    
    return {
        'job_code': pred_class,
        'job_name': job_name,
        'confidence': float(confidence),
        'all_predictions': [
            {
                'code': int(model_classes[i]),
                'name': JOB_NAMES.get(int(model_classes[i]), f"Code {int(model_classes[i])}"),
                'confidence': float(prob)
            }
            for i, prob in enumerate(probabilities) if prob > 0.01
        ]
    }

# Test
print("Testing prediction system...")

test_student = {
    'degree_encoded': 8,
    'specialization_encoded': 10,
    'cgpa_normalized': 9.5,
    'cgpa_category_encoded': 3,
    'certifications_count': 3,
    'coding_skills_encoded': 4,
    'internships_count': 2,
    'projects_count': 5,
    'experience_category_encoded': 2,
    'total_experience': 3,
    'has_research': 1,
    'research_level_encoded': 2,
    'extracurriculars': 7,
    'leadership_positions': 3,
    'field_courses': 6
}

result = predict_career(test_student)
print(f"\nPrediction: {result['job_name']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Code: {result['job_code']}")

print("\nTop alternatives:")
for pred in sorted(result['all_predictions'], key=lambda x: x['confidence'], reverse=True)[:3]:
    print(f"  • {pred['name']}: {pred['confidence']:.1%}")