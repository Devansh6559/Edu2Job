"""
Test CSE input to see what predictions we get
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_encoding import prepare_ml_features
from enhanced_ml_model import get_predictor

def test_cse_prediction():
    """Test CSE specialization prediction"""
    print("="*60)
    print("Testing CSE (Computer Science) Input")
    print("="*60)
    
    # CSE profile - form values
    cse_data = {
        'degree_encoded': 1,  # Form value for B.Tech/B.E
        'specialization_encoded': 1,  # Form value for Computer Science
        'cgpa': 9.0,
        'total_experience': 6,
        'projects_count': 5,
        'internships_count': 2,
        'coding_skills_encoded': 3,  # Advanced
        'certifications_count': 3,
        'research_level_encoded': 1,
        'extracurriculars_count': 3,
        'leadership_positions': 2,
        'field_courses': 10
    }
    
    print("\nInput Data (Form Values):")
    print(f"  degree_encoded: {cse_data['degree_encoded']} (form)")
    print(f"  specialization_encoded: {cse_data['specialization_encoded']} (form)")
    print(f"  coding_skills_encoded: {cse_data['coding_skills_encoded']}")
    print(f"  cgpa: {cse_data['cgpa']}")
    
    # Prepare ML features
    ml_features = prepare_ml_features(cse_data)
    
    print("\nPrepared ML Features:")
    print(f"  degree_encoded: {ml_features['degree_encoded']} (ML)")
    print(f"  specialization_encoded: {ml_features['specialization_encoded']} (ML)")
    print(f"  coding_skills_encoded: {ml_features['coding_skills_encoded']}")
    print(f"  cgpa_normalized: {ml_features['cgpa_normalized']:.3f}")
    
    # Get predictions
    predictor = get_predictor()
    if not predictor:
        print("\n[ERROR] Could not load predictor")
        return
    
    predictions = predictor.predict_top_jobs(ml_features, top_n=5)
    
    print("\nPredictions:")
    print("-" * 60)
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. {pred['job_role']}")
        print(f"   Confidence: {pred['confidence_percentage']:.2f}%")
        print(f"   Job Code: {pred['job_role_encoded']}")
    
    # Check if predictions make sense
    print("\n" + "="*60)
    print("Analysis:")
    print("="*60)
    
    top_prediction = predictions[0]['job_role'] if predictions else None
    top_code = predictions[0]['job_role_encoded'] if predictions else None
    
    # Expected jobs for CSE: Software Developer (13), Web Developer (14), Data Scientist (6), etc.
    expected_jobs = [13, 14, 6, 5, 9]  # Software Dev, Web Dev, Data Scientist, Cybersecurity, Game Dev
    unexpected_jobs = [4, 11, 7, 3]  # Civil Engineer, Mechanical Engineer, Electrical Engineer, Chemical Engineer
    
    if top_code in unexpected_jobs:
        print(f"[PROBLEM] Top prediction is {top_prediction} (code {top_code})")
        print("This is NOT appropriate for CSE specialization!")
        print(f"Expected jobs for CSE: Software Developer, Web Developer, Data Scientist, etc.")
        return False
    elif top_code in expected_jobs:
        print(f"[OK] Top prediction is {top_prediction} (code {top_code})")
        print("This is appropriate for CSE specialization!")
        return True
    else:
        print(f"[WARNING] Top prediction is {top_prediction} (code {top_code})")
        print("Not in expected list, but might be valid")
        return True

if __name__ == "__main__":
    test_cse_prediction()

