# # find_job_mapping.py
# import pandas as pd
# import numpy as np

# print("="*60)
# print("JOB ROLE CODE MAPPING TOOL")
# print("="*60)

# # 1. Load both datasets
# print("\n1. Loading datasets...")

# # Your encoded dataset (the one with numeric codes)
# encoded_df = pd.read_csv("data/processed_education_features.csv")
# print(f"Encoded dataset: {encoded_df.shape}")

# # Your original dataset (with actual job role names)
# # Replace "original_dataset.csv" with your actual file name
# original_df = pd.read_csv("data/preprocessed_data.csv")  # Change this to your actual file
# print(f"Original dataset: {original_df.shape}")

# # 2. Check common columns
# print("\n2. Checking common columns...")
# print(f"Encoded columns: {encoded_df.columns.tolist()}")
# print(f"Original columns: {original_df.columns.tolist()}")

# # 3. Find the job role column in original dataset
# # Look for columns that might contain job role names
# job_role_candidates = []
# for col in original_df.columns:
#     if any(keyword in col.lower() for keyword in ['job', 'role', 'career', 'target', 'position', 'title']):
#         job_role_candidates.append(col)

# print(f"\nPossible job role columns in original dataset: {job_role_candidates}")

# if not job_role_candidates:
#     print("\nCould not auto-detect job role column.")
#     print("Please specify which column contains job role names:")
#     print(f"Available columns: {original_df.columns.tolist()}")
#     job_column = input("Enter column name: ").strip()
# else:
#     job_column = job_role_candidates[0]  # Use the first candidate
#     print(f"\nUsing '{job_column}' as job role column")

# # 4. Merge datasets on user_id
# print(f"\n3. Merging datasets on 'user_id'...")

# # Ensure both have user_id column
# if 'user_id' in encoded_df.columns and 'user_id' in original_df.columns:
#     # Merge to get mapping
#     merged_df = pd.merge(
#         encoded_df[['user_id', 'target_career_encoded']],
#         original_df[['user_id', job_column]],
#         on='user_id',
#         how='inner'
#     )
    
#     print(f"Merged dataset: {merged_df.shape}")
    
#     # 5. Create the mapping
#     print("\n4. Creating mapping...")
    
#     # Group by encoded value and get unique job roles
#     mapping = {}
#     for code in sorted(merged_df['target_career_encoded'].unique()):
#         job_roles = merged_df[merged_df['target_career_encoded'] == code][job_column].unique()
#         mapping[code] = {
#             'job_roles': job_roles.tolist(),
#             'count': len(merged_df[merged_df['target_career_encoded'] == code]),
#             'example_user': merged_df[merged_df['target_career_encoded'] == code]['user_id'].iloc[0] if len(merged_df[merged_df['target_career_encoded'] == code]) > 0 else None
#         }
    
#     # 6. Display the mapping
#     print("\n" + "="*60)
#     print("JOB CODE TO JOB ROLE MAPPING")
#     print("="*60)
    
#     for code, info in mapping.items():
#         print(f"\nCode {code}:")
#         print(f"  Count: {info['count']} students")
#         print(f"  Example user: {info['example_user']}")
#         print(f"  Job role(s): {', '.join(info['job_roles'])}")
    
#     # 7. Save the mapping
#     print("\n5. Saving mapping...")
    
#     # Create a clean mapping dictionary (just code -> primary job role)
#     clean_mapping = {}
#     for code, info in mapping.items():
#         # Take the most common job role for this code
#         if len(info['job_roles']) > 0:
#             # Count frequencies
#             role_counts = merged_df[merged_df['target_career_encoded'] == code][job_column].value_counts()
#             primary_role = role_counts.index[0]
#             clean_mapping[code] = primary_role
#         else:
#             clean_mapping[code] = f"Unknown_{code}"
    
#     # Save to CSV
#     mapping_df = pd.DataFrame(list(clean_mapping.items()), columns=['code', 'job_role'])
#     mapping_df.to_csv('job_code_mapping.csv', index=False)
#     print("✓ Mapping saved to job_code_mapping.csv")
    
#     # Save to JSON (for easy use in Python)
#     import json
#     with open('job_code_mapping.json', 'w') as f:
#         json.dump(clean_mapping, f, indent=2)
#     print("✓ Mapping saved to job_code_mapping.json")
    
#     # 8. Verify mapping quality
#     print("\n6. Verifying mapping quality...")
    
#     # Check for codes with multiple job roles
#     ambiguous_codes = []
#     for code, info in mapping.items():
#         if len(info['job_roles']) > 1:
#             ambiguous_codes.append((code, info['job_roles']))
    
#     if ambiguous_codes:
#         print(f"\n⚠️  Warning: {len(ambiguous_codes)} codes have multiple job roles:")
#         for code, roles in ambiguous_codes:
#             print(f"  Code {code}: {roles}")
#     else:
#         print("✓ All codes map to a single job role")
    
#     # 9. Create a complete analysis report
#     print("\n7. Generating complete report...")
    
#     report_data = []
#     for code, info in mapping.items():
#         subset = merged_df[merged_df['target_career_encoded'] == code]
        
#         report_data.append({
#             'code': code,
#             'job_role': clean_mapping[code],
#             'student_count': info['count'],
#             'unique_roles': len(info['job_roles']),
#             'example_users': ', '.join(subset['user_id'].head(3).tolist()),
#             'role_distribution': dict(subset[job_column].value_counts().head(3))
#         })
    
#     report_df = pd.DataFrame(report_data)
#     report_df.to_csv('job_mapping_report.csv', index=False)
#     print("✓ Report saved to job_mapping_report.csv")
    
#     # 10. Quick validation
#     print("\n8. Quick validation:")
#     sample_codes = list(clean_mapping.keys())[:5]  # First 5 codes
#     for code in sample_codes:
#         sample_user = merged_df[merged_df['target_career_encoded'] == code]['user_id'].iloc[0]
#         actual_role = merged_df[merged_df['user_id'] == sample_user][job_column].iloc[0]
#         print(f"  Code {code}: {clean_mapping[code]} (example: {sample_user} = {actual_role})")
    
# else:
#     print("\n❌ Error: 'user_id' column not found in both datasets!")
#     print(f"Encoded dataset columns: {encoded_df.columns.tolist()}")
#     print(f"Original dataset columns: {original_df.columns.tolist()}")

# print("\n" + "="*60)
# print("MAPPING COMPLETE!")
# print("="*60)

# quick_mapping_fixed.py
import pandas as pd

# Load datasets
encoded_df = pd.read_csv("data/preprocessed_data.csv")
original_df = pd.read_csv("data/original_dataset.csv")  # Your file with job names

# Find job column (simplified)
job_column = "target_career"
# for col in original_df.columns:
#     if col.lower() in ['job', 'role', 'career', 'target', 'position']:
#         job_column = col
#         break

# if not job_column:
#     # Try to find any string column with reasonable number of unique values
#     for col in original_df.columns:
#         if original_df[col].dtype == 'object' and 1 < original_df[col].nunique() < 50:
#             job_column = col
#             break

# if not job_column:
#     job_column = original_df.columns[1]  # Use second column as fallback

# print(f"Using column: {job_column}")

# Merge and create mapping
merged = pd.merge(
    encoded_df[['user_id', 'target_career_encoded']],
    original_df[['user_id', job_column]],
    on='user_id'
)

# Convert all job values to strings
merged[job_column] = merged[job_column].astype(str)

# Create mapping
mapping = {}
for code in sorted(merged['target_career_encoded'].unique()):
    # Get unique non-empty job roles
    roles = merged[merged['target_career_encoded'] == code][job_column].unique()
    roles = [r for r in roles if r and r.lower() != 'nan']
    
    if roles:
        # Take most common role
        most_common = merged[merged['target_career_encoded'] == code][job_column].mode()
        if len(most_common) > 0:
            mapping[code] = most_common[0]
        else:
            mapping[code] = roles[0]
    else:
        mapping[code] = f"Unknown_{code}"

# Display results
print("\nJob Code Mapping:")
for code, role in sorted(mapping.items()):
    count = len(merged[merged['target_career_encoded'] == code])
    print(f"{code:3d}: {role:30s} ({count} students)")

# # Save to file
# import json
# with open('mapping.json', 'w') as f:
#     json.dump(mapping, f, indent=2)

# print(f"\n✓ Mapping saved to mapping.json")