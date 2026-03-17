"""
Test script for Milestone 3 enhanced ML integration
"""
import sys
import os

# Add backend to path
sys.path.append('backend')

from enhanced_ml_model import predict_job_roles_enhanced

def test_predictions():
    """Test the enhanced prediction system"""
    
    print(" Testing Enhanced ML Integration for Milestone 3")
    print("=" * 60)
    
    # Test user profile
    test_profile = {
        'degree_encoded': 8,  # B.Com
        'specialization_encoded': 10,  # Business
        'cgpa_normalized': 9.5 / 10.0,  # 9.5 CGPA normalized
        'cgpa_category_encoded': 3,  # High
        'certifications_count': 2,
        'coding_skills_encoded': 2,  # Intermediate
        'internships_count': 1,
        'projects_count': 3,
        'experience_category_encoded': 2,  # Has experience
        'total_experience': 6,  # 6 months
        'has_research': 0,
        'research_level_encoded': 0,
        'extracurriculars_count': 2,
        'leadership_positions': 1,
        'field_courses': 4
    }
    
    print("\nTest User Profile:")
    for key, value in test_profile.items():
        print(f"  {key}: {value}")
    
    print("\n Getting Predictions...")
    
    try:
        predictions = predict_job_roles_enhanced(test_profile)
        
        print(f"\n Successfully generated {len(predictions)} predictions")
        print("\n Top Job Recommendations:")
        
        for i, pred in enumerate(predictions, 1):
            print(f"\n  {i}. {pred['job_role']}")
            print(f"     Confidence: {pred['confidence_percentage']:.1f}%")
            print(f"     Skills: {', '.join(pred.get('skills_match', []))}")
        
        print("\n" + "=" * 60)
        print(" Milestone 3 ML Integration Test Complete!")
        
    except Exception as e:
        print(f"\n Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_predictions()
