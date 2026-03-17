# main.py
"""
Edu2Job - Career Prediction System
Main entry point for the application
"""

import sys
from pathlib import Path

# Add src folder to Python path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from predictor import predict_career
from config.settings import JOB_ROLE_MAPPING, FEATURE_RANGES
import pandas as pd
import json

def display_welcome():
    """Display welcome message"""
    print("="*60)
    print("🎓 EDU2JOB - CAREER PREDICTION SYSTEM")
    print("="*60)
    print(f"Available Job Roles: {len(JOB_ROLE_MAPPING)}")
    print(f"Features Used: {len(FEATURE_RANGES)}")

def get_sample_student():
    """Return a sample student profile for testing"""
    return {
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

def run_single_prediction():
    """Run prediction for a single student"""
    print("\n" + "="*60)
    print("SINGLE STUDENT PREDICTION")
    print("="*60)
    
    # Use sample student
    student_data = get_sample_student()
    
    print("\n📊 Student Profile:")
    for key, value in student_data.items():
        print(f"  {key}: {value}")
    
    # Make prediction
    print("\n🔮 Making prediction...")
    result = predict_career(student_data)
    
    # Display results
    print("\n" + "="*60)
    print("PREDICTION RESULTS")
    print("="*60)
    
    print(f"\n🎯 Primary Recommendation:")
    print(f"  Job: {result['job_name']}")
    print(f"  Code: {result['job_code']}")
    print(f"  Confidence: {result['confidence']:.1%}")
    
    if result['confidence'] > 0.5:
        print("  ✅ High Confidence Prediction")
    elif result['confidence'] > 0.3:
        print("  ⚠️  Medium Confidence Prediction")
    else:
        print("  ⚠️  Low Confidence Prediction")
    
    print(f"\n🔄 Alternative Career Paths:")
    sorted_predictions = sorted(result['all_predictions'], 
                               key=lambda x: x['confidence'], 
                               reverse=True)
    
    for i, pred in enumerate(sorted_predictions[1:4], 1):  # Skip first, get next 3
        print(f"  {i}. {pred['name']}: {pred['confidence']:.1%}")
    
    return result

def batch_prediction_demo():
    """Demo batch prediction with sample data"""
    print("\n" + "="*60)
    print("BATCH PREDICTION DEMO")
    print("="*60)
    
    # Create 3 sample students
    samples = [
        {
            'user_id': 'STU_001',
            'degree_encoded': 10,
            'specialization_encoded': 11,
            'cgpa_normalized': 8.2,
            'cgpa_category_encoded': 2,
            'certifications_count': 1,
            'coding_skills_encoded': 3,
            'internships_count': 1,
            'projects_count': 3,
            'experience_category_encoded': 1,
            'total_experience': 2,
            'has_research': 0,
            'research_level_encoded': 0,
            'extracurriculars': 5,
            'leadership_positions': 1,
            'field_courses': 4
        },
        {
            'user_id': 'STU_002',
            'degree_encoded': 4,
            'specialization_encoded': 1,
            'cgpa_normalized': 7.5,
            'cgpa_category_encoded': 1,
            'certifications_count': 0,
            'coding_skills_encoded': 1,
            'internships_count': 3,
            'projects_count': 2,
            'experience_category_encoded': 2,
            'total_experience': 4,
            'has_research': 1,
            'research_level_encoded': 1,
            'extracurriculars': 3,
            'leadership_positions': 2,
            'field_courses': 8
        },
        {
            'user_id': 'STU_003',
            'degree_encoded': 9,
            'specialization_encoded': 9,
            'cgpa_normalized': 6.8,
            'cgpa_category_encoded': 0,
            'certifications_count': 2,
            'coding_skills_encoded': 0,
            'internships_count': 0,
            'projects_count': 4,
            'experience_category_encoded': 0,
            'total_experience': 1,
            'has_research': 0,
            'research_level_encoded': 0,
            'extracurriculars': 9,
            'leadership_positions': 1,
            'field_courses': 2
        }
    ]
    
    results = []
    for student in samples:
        user_id = student.pop('user_id')
        prediction = predict_career(student)
        results.append({
            'user_id': user_id,
            'predicted_job': prediction['job_name'],
            'confidence': prediction['confidence'],
            'job_code': prediction['job_code']
        })
    
    # Display results
    print("\n📋 Batch Prediction Results:")
    print("-"*60)
    for result in results:
        print(f"\n👤 {result['user_id']}:")
        print(f"   Job: {result['predicted_job']}")
        print(f"   Confidence: {result['confidence']:.1%}")
    
    return results

def save_results_to_file(results, filename="prediction_results.json"):
    """Save prediction results to JSON file"""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to {filename}")

def main():
    """Main application flow"""
    display_welcome()
    
    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Test Single Student Prediction")
        print("2. Run Batch Prediction Demo")
        print("3. View Available Job Roles")
        print("4. View Feature Information")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            result = run_single_prediction()
            save_choice = input("\nSave results to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_results_to_file(result, "single_prediction.json")
        
        elif choice == '2':
            results = batch_prediction_demo()
            save_choice = input("\nSave batch results to file? (y/n): ").strip().lower()
            if save_choice == 'y':
                save_results_to_file(results, "batch_predictions.json")
        
        elif choice == '3':
            print("\n" + "="*60)
            print("AVAILABLE JOB ROLES")
            print("="*60)
            for code, name in sorted(JOB_ROLE_MAPPING.items()):
                print(f"{code:3d}: {name}")
        
        elif choice == '4':
            print("\n" + "="*60)
            print("FEATURE INFORMATION")
            print("="*60)
            for feature, (min_val, max_val) in FEATURE_RANGES.items():
                print(f"{feature}: Range {min_val} to {max_val}")
        
        elif choice == '5':
            print("\nThank you for using Edu2Job!")
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()