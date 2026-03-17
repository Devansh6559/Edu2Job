"""
Test script for encoding fixes
Tests form value to ML encoding conversion
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_encoding import (
    convert_form_degree_to_ml,
    convert_form_specialization_to_ml,
    prepare_ml_features,
    encode_degree,
    encode_specialization,
    decode_degree,
    decode_specialization
)

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_test_result(test_name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")

def test_form_degree_conversion():
    """Test form degree values to ML encoding conversion"""
    print_header("Testing Form Degree Value Conversion")
    
    test_cases = [
        (1, 0, "B.Tech/B.E -> B.Tech"),
        (2, 2, "M.Tech/M.E -> M.Tech"),
        (3, 4, "BCA -> BCA"),
        (4, 5, "MCA -> MCA"),
        (5, 1, "B.Sc -> B.Sc"),
        (6, -1, "M.Sc -> Unknown"),
        (7, 3, "MBA -> MBA"),
        (8, 10, "Ph.D -> Ph.D"),
        (9, 9, "Diploma -> Diploma"),
    ]
    
    all_passed = True
    for form_val, expected_ml, description in test_cases:
        result = convert_form_degree_to_ml(form_val)
        passed = result == expected_ml
        all_passed = all_passed and passed
        print_test_result(
            f"Form degree {form_val} ({description})",
            passed,
            f"Expected: {expected_ml}, Got: {result}"
        )
    
    return all_passed

def test_form_specialization_conversion():
    """Test form specialization values to ML encoding conversion"""
    print_header("Testing Form Specialization Value Conversion")
    
    test_cases = [
        (1, 0, "Computer Science -> CSE"),
        (2, 1, "Information Technology -> IT"),
        (3, 6, "Electronics -> Electronics"),
        (4, 3, "Mechanical -> Mechanical"),
        (5, 4, "Civil -> Civil"),  # This is the critical fix!
        (6, 5, "Electrical -> Electrical"),
        (7, 7, "AI/ML -> AI/ML"),
        (8, 8, "Data Science -> Data Science"),
        (9, 9, "Cybersecurity -> Cybersecurity"),
        (10, 10, "Business -> Business Administration"),
        (11, 11, "Finance -> Finance"),
    ]
    
    all_passed = True
    for form_val, expected_ml, description in test_cases:
        result = convert_form_specialization_to_ml(form_val)
        passed = result == expected_ml
        all_passed = all_passed and passed
        print_test_result(
            f"Form specialization {form_val} ({description})",
            passed,
            f"Expected: {expected_ml}, Got: {result}"
        )
    
    return all_passed

def test_prepare_ml_features_with_form_values():
    """Test prepare_ml_features with form values (the actual use case)"""
    print_header("Testing prepare_ml_features with Form Values")
    
    # Test case: Civil Engineer profile
    print("\n[TEST CASE 1] Civil Engineer Profile")
    print("-" * 60)
    civil_engineer_data = {
        'degree_encoded': 1,  # Form value for B.Tech/B.E
        'specialization_encoded': 5,  # Form value for Civil (THIS WAS THE BUG!)
        'cgpa': 8.5,
        'total_experience': 12,
        'projects_count': 3,
        'internships_count': 2,
        'coding_skills_encoded': 2,
        'certifications_count': 1,
        'research_level_encoded': 0,
        'extracurriculars_count': 2,
        'leadership_positions': 1,
        'field_courses': 8
    }
    
    features = prepare_ml_features(civil_engineer_data)
    
    print(f"Input - degree_encoded (form): {civil_engineer_data['degree_encoded']}")
    print(f"Input - specialization_encoded (form): {civil_engineer_data['specialization_encoded']}")
    print(f"\nOutput - degree_encoded (ML): {features['degree_encoded']}")
    print(f"Output - specialization_encoded (ML): {features['specialization_encoded']}")
    
    # Verify conversions
    degree_ok = features['degree_encoded'] == 0  # B.Tech
    spec_ok = features['specialization_encoded'] == 4  # Civil (CRITICAL!)
    
    print_test_result(
        "Civil Engineer - Degree conversion",
        degree_ok,
        f"Expected: 0 (B.Tech), Got: {features['degree_encoded']}"
    )
    print_test_result(
        "Civil Engineer - Specialization conversion",
        spec_ok,
        f"Expected: 4 (Civil), Got: {features['specialization_encoded']}"
    )
    
    # Test case: Computer Science profile
    print("\n[TEST CASE 2] Computer Science Profile")
    print("-" * 60)
    cs_data = {
        'degree_encoded': 1,  # Form value for B.Tech/B.E
        'specialization_encoded': 1,  # Form value for Computer Science
        'cgpa': 9.0,
        'total_experience': 6,
        'projects_count': 5,
        'internships_count': 2,
        'coding_skills_encoded': 3,
        'certifications_count': 3,
        'research_level_encoded': 1,
        'extracurriculars_count': 3,
        'leadership_positions': 2,
        'field_courses': 10
    }
    
    features_cs = prepare_ml_features(cs_data)
    
    print(f"Input - degree_encoded (form): {cs_data['degree_encoded']}")
    print(f"Input - specialization_encoded (form): {cs_data['specialization_encoded']}")
    print(f"\nOutput - degree_encoded (ML): {features_cs['degree_encoded']}")
    print(f"Output - specialization_encoded (ML): {features_cs['specialization_encoded']}")
    
    cs_degree_ok = features_cs['degree_encoded'] == 0  # B.Tech
    cs_spec_ok = features_cs['specialization_encoded'] == 0  # CSE
    
    print_test_result(
        "Computer Science - Degree conversion",
        cs_degree_ok,
        f"Expected: 0 (B.Tech), Got: {features_cs['degree_encoded']}"
    )
    print_test_result(
        "Computer Science - Specialization conversion",
        cs_spec_ok,
        f"Expected: 0 (CSE), Got: {features_cs['specialization_encoded']}"
    )
    
    # Test case: Already ML-encoded values (should not convert)
    # Note: Value 0 is unambiguous (ML format only, form doesn't use 0)
    # Value 4 is ambiguous (could be form value 4 -> ML 3, or ML value 4)
    # For unambiguous values, we preserve them. For ambiguous values, conversion may occur.
    print("\n[TEST CASE 3] Already ML-Encoded Values (Unambiguous)")
    print("-" * 60)
    ml_encoded_data = {
        'degree_encoded': 0,  # Already ML format (B.Tech) - unambiguous
        'specialization_encoded': 0,  # Already ML format (CSE) - unambiguous (form uses 1-11)
        'cgpa': 8.0,
    }
    
    features_ml = prepare_ml_features(ml_encoded_data)
    
    print(f"Input - degree_encoded (ML): {ml_encoded_data['degree_encoded']}")
    print(f"Input - specialization_encoded (ML): {ml_encoded_data['specialization_encoded']}")
    print(f"\nOutput - degree_encoded (ML): {features_ml['degree_encoded']}")
    print(f"Output - specialization_encoded (ML): {features_ml['specialization_encoded']}")
    
    ml_degree_ok = features_ml['degree_encoded'] == 0
    ml_spec_ok = features_ml['specialization_encoded'] == 0
    
    print_test_result(
        "ML-Encoded values (unambiguous) - No conversion",
        ml_degree_ok and ml_spec_ok,
        f"Expected: degree=0, spec=0, Got: degree={features_ml['degree_encoded']}, spec={features_ml['specialization_encoded']}"
    )
    
    # Test case: String values (should encode)
    print("\n[TEST CASE 4] String Values (Encoding)")
    print("-" * 60)
    string_data = {
        'degree': 'B.Tech',
        'specialization': 'Civil',
        'cgpa': 7.5,
    }
    
    features_str = prepare_ml_features(string_data)
    
    print(f"Input - degree (string): '{string_data['degree']}'")
    print(f"Input - specialization (string): '{string_data['specialization']}'")
    print(f"\nOutput - degree_encoded (ML): {features_str['degree_encoded']}")
    print(f"Output - specialization_encoded (ML): {features_str['specialization_encoded']}")
    
    str_degree_ok = features_str['degree_encoded'] == 0  # B.Tech
    str_spec_ok = features_str['specialization_encoded'] == 4  # Civil
    
    print_test_result(
        "String values - Encoding",
        str_degree_ok and str_spec_ok,
        f"Expected: degree=0, spec=4, Got: degree={features_str['degree_encoded']}, spec={features_str['specialization_encoded']}"
    )
    
    return degree_ok and spec_ok and cs_degree_ok and cs_spec_ok and ml_degree_ok and ml_spec_ok and str_degree_ok and str_spec_ok

def test_edge_cases():
    """Test edge cases"""
    print_header("Testing Edge Cases")
    
    all_passed = True
    
    # Test invalid form values
    invalid_degree = convert_form_degree_to_ml(99)
    passed = invalid_degree == -1
    all_passed = all_passed and passed
    print_test_result(
        "Invalid degree form value",
        passed,
        f"Expected: -1, Got: {invalid_degree}"
    )
    
    invalid_spec = convert_form_specialization_to_ml(99)
    passed = invalid_spec == -1
    all_passed = all_passed and passed
    print_test_result(
        "Invalid specialization form value",
        passed,
        f"Expected: -1, Got: {invalid_spec}"
    )
    
    # Test None values
    none_data = {
        'degree_encoded': None,
        'specialization_encoded': None,
    }
    features_none = prepare_ml_features(none_data)
    passed = features_none['degree_encoded'] == -1 and features_none['specialization_encoded'] == -1
    all_passed = all_passed and passed
    print_test_result(
        "None values handling",
        passed,
        f"Expected: degree=-1, spec=-1, Got: degree={features_none['degree_encoded']}, spec={features_none['specialization_encoded']}"
    )
    
    # Test missing keys
    empty_data = {}
    features_empty = prepare_ml_features(empty_data)
    passed = features_empty['degree_encoded'] == -1 and features_empty['specialization_encoded'] == -1
    all_passed = all_passed and passed
    print_test_result(
        "Missing keys handling",
        passed,
        f"Expected: degree=-1, spec=-1, Got: degree={features_empty['degree_encoded']}, spec={features_empty['specialization_encoded']}"
    )
    
    return all_passed

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  ENCODING FIX TEST SUITE")
    print("="*60)
    print("\nTesting form value to ML encoding conversion fixes...")
    
    results = []
    
    # Run all test suites
    results.append(("Form Degree Conversion", test_form_degree_conversion()))
    results.append(("Form Specialization Conversion", test_form_specialization_conversion()))
    results.append(("prepare_ml_features with Form Values", test_prepare_ml_features_with_form_values()))
    results.append(("Edge Cases", test_edge_cases()))
    
    # Print summary
    print_header("Test Summary")
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
        all_passed = all_passed and passed
    
    print("\n" + "="*60)
    if all_passed:
        print("  [SUCCESS] ALL TESTS PASSED!")
        print("  The encoding fix is working correctly.")
    else:
        print("  [ERROR] SOME TESTS FAILED")
        print("  Please review the test output above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

