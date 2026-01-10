# # test_model.py - Quick Model Testing
# import pandas as pd
# import numpy as np
# import pickle
# from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
# import seaborn as sns
# import matplotlib.pyplot as plt

# print("="*60)
# print("MODEL TESTING SUITE")
# print("="*60)

# # 1. Load the trained model
# print("\n1. Loading model...")
# with open("models/job_role_rf_enhanced.pkl", 'rb') as f:
#     saved_data = pickle.load(f)
    
# model = saved_data['model']
# scaler = saved_data['scaler']
# feature_names = saved_data['feature_names']

# print(f"✓ Model loaded: {type(model).__name__}")
# print(f"✓ Features: {len(feature_names)}")

# # 2. Load your dataset
# print("\n2. Loading dataset...")
# df = pd.read_csv("data/processed_education_features.csv")
# print(f"✓ Dataset loaded: {df.shape}")

# # 3. Prepare test data (use last 20% as test)
# print("\n3. Preparing test data...")
# test_size = int(len(df) * 0.2)
# test_df = df.tail(test_size)  # Use last 20% as test
# train_df = df.iloc[:-test_size]  # First 80% as train

# print(f"✓ Training samples: {len(train_df)}")
# print(f"✓ Testing samples: {len(test_df)}")

# # 4. Prepare features
# X_test = test_df[feature_names] if 'user_id' not in feature_names else test_df.drop(['user_id', 'target_career_encoded'], axis=1)
# y_test = test_df['target_career_encoded']

# # Ensure correct column order
# X_test = X_test[feature_names]

# # 5. Scale and predict
# print("\n4. Making predictions...")
# X_test_scaled = scaler.transform(X_test)
# y_pred = model.predict(X_test_scaled)

# # 6. Evaluate
# print("\n5. Evaluation Results:")
# print("-"*40)

# # Basic metrics
# accuracy = accuracy_score(y_test, y_pred)
# print(f"Accuracy: {accuracy:.4f}")
# print(f"Correct predictions: {sum(y_test == y_pred)}/{len(y_test)}")

# # Detailed report
# print("\nClassification Report:")
# print(classification_report(y_test, y_pred, zero_division=0))

# # 7. Show some example predictions
# print("\n6. Example Predictions:")
# print("-"*40)
# for i in range(min(5, len(test_df))):
#     actual = y_test.iloc[i]
#     predicted = y_pred[i]
#     status = "✓" if actual == predicted else "✗"
#     print(f"{status} User {i+1}: Actual={actual}, Predicted={predicted}")

# # 8. Feature importance
# print("\n7. Feature Importance:")
# print("-"*40)
# feature_importance = pd.DataFrame({
#     'feature': feature_names,
#     'importance': model.feature_importances_
# }).sort_values('importance', ascending=False)

# print("Top 10 features:")
# print(feature_importance.head(10).to_string(index=False))

# # 9. Save test results
# print("\n8. Saving test results...")
# results_df = pd.DataFrame({
#     'actual': y_test.values,
#     'predicted': y_pred,
#     'correct': y_test.values == y_pred
# })

# # Add probabilities if needed
# if hasattr(model, 'predict_proba'):
#     proba = model.predict_proba(X_test_scaled)
#     for i, cls in enumerate(model.classes_):
#         results_df[f'prob_class_{cls}'] = proba[:, i]

# results_df.to_csv("model_test_results.csv", index=False)
# print("✓ Results saved to model_test_results.csv")

# print("\n" + "="*60)
# print("TESTING COMPLETE!")
# print("="*60)

import pickle
import pandas as pd

# Load model
with open("models/job_role_rf_enhanced.pkl", 'rb') as f:
    saved = pickle.load(f)

model = saved['model']
scaler = saved['scaler']

# Test with 5 random users from your dataset
df = pd.read_csv("data/preprocessed_data.csv")
test_samples = df.sample(5)

for i, row in test_samples.iterrows():
    # Prepare features (excluding user_id and target)
    features = row.drop(['user_id', 'target_career_encoded']).values.reshape(1, -1)
    
    # Scale and predict
    scaled = scaler.transform(features)
    pred = model.predict(scaled)[0]
    
    print(f"User: {row['user_id']}")
    print(f"Actual: {row['target_career_encoded']}, Predicted: {pred}")
    print(f"Correct: {'✓' if row['target_career_encoded'] == pred else '✗'}")
    print("-" * 40)