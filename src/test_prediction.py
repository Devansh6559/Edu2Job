# test_predictions.py
from predictor import predict_career

# Initialize
predictor = predict_career()

# Test with different student profiles
test_cases = [
    {
        'name': "Tech Student",
        'features': {
            'degree_encoded': 10,
            'specialization_encoded': 11,
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
    },
    {
        'name': "Engineering Student", 
        'features': {
            'degree_encoded': 4,
            'specialization_encoded': 1,
            'cgpa_normalized': 8.2,
            'cgpa_category_encoded': 3,
            'certifications_count': 1,
            'coding_skills_encoded': 2,
            'internships_count': 3,
            'projects_count': 3,
            'experience_category_encoded': 1,
            'total_experience': 2,
            'has_research': 0,
            'research_level_encoded': 0,
            'extracurriculars': 4,
            'leadership_positions': 2,
            'field_courses': 8
        }
    },
    {
        'name': "Design Student",
        'features': {
            'degree_encoded': 9,
            'specialization_encoded': 9,
            'cgpa_normalized': 7.8,
            'cgpa_category_encoded': 2,
            'certifications_count': 2,
            'coding_skills_encoded': 1,
            'internships_count': 1,
            'projects_count': 4,
            'experience_category_encoded': 0,
            'total_experience': 1,
            'has_research': 0,
            'research_level_encoded': 0,
            'extracurriculars': 9,
            'leadership_positions': 1,
            'field_courses': 3
        }
    }
]

print("Testing Career Predictions for Different Student Profiles")
print("="*70)

for test in test_cases:
    print(f"\n🎓 Student: {test['name']}")
    print("-"*40)
    
    result = predictor.predict_job(test['features'], return_details=True)
    
    print(f"Predicted Career: {result['primary_prediction']['job_name']}")
    print(f"Confidence: {result['primary_prediction']['confidence']:.1%}")
    print(f"Category: {result['primary_prediction']['category']}")
    
    print("Top Alternatives:")
    for alt in result['alternative_predictions'][:2]:
        print(f"  • {alt['job_name']} ({alt['confidence']:.1%})")
    
    print("-"*40)