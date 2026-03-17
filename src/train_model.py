# # ==============================
# # Edu2Job - Job Role Prediction
# # Random Forest Training Script
# # ==============================

# # ---------- 1. Imports ----------
# import pandas as pd
# import pickle

# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, f1_score, classification_report


# # ---------- 2. Task 1: Load Dataset ----------
# print("Loading dataset...")

# df = pd.read_csv("data/processed_education_features.csv")

# print("Dataset loaded successfully")
# print(df.head())
# print(df.info())
# print("Missing values:\n", df.isnull().sum())


# # ---------- 3. Task 2: Prepare X and y ----------
# print("\nPreparing features and target...")

# # Drop non-ML column
# df_model = df.drop("user_id", axis=1)

# X = df_model.drop("target_career_encoded", axis=1)
# y = df_model["target_career_encoded"]

# print("X shape:", X.shape)
# print("y shape:", y.shape)


# # ---------- 4. Train-Test Split ----------
# X_train, X_test, y_train, y_test = train_test_split(
#     X,
#     y,
#     test_size=0.2,
#     random_state=42,
#     stratify=y
# )

# print("Training set:", X_train.shape)
# print("Testing set:", X_test.shape)


# # ---------- 5. Task 3: Train Random Forest ----------
# print("\nTraining Random Forest model...")

# rf_model = RandomForestClassifier(
#     n_estimators=300,
#     random_state=42,
#     class_weight="balanced",
#     n_jobs=-1
# )

# rf_model.fit(X_train, y_train)

# print("Random Forest model trained successfully!")


# # ---------- 6. Task 4: Generate Predictions ----------
# print("\nGenerating predictions...")

# y_pred = rf_model.predict(X_test)


# # ---------- 7. Task 5: Evaluate Model ----------
# print("\nEvaluating model performance...")

# accuracy = accuracy_score(y_test, y_pred)
# f1 = f1_score(y_test, y_pred, average="weighted")

# print(f"Accuracy: {accuracy:.4f}")
# print(f"Weighted F1-Score: {f1:.4f}")

# print("\nClassification Report:")
# print(classification_report(y_test, y_pred))


# # ---------- 8. Task 6: Save Model ----------
# print("\nSaving trained model...")

# with open("models/job_role_rf.pkl", "wb") as f:
#     pickle.dump(rf_model, f)

# print("Model saved successfully at models/job_role_rf.pkl")

# print("\n Training pipeline completed successfully!")

# ==============================
# Edu2Job - Job Role Prediction
# Enhanced Random Forest Training
# ==============================

# ---------- 1. Imports ----------
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# ---------- 2. Load and Analyze Dataset ----------
print("="*60)
print("EDU2JOB - JOB ROLE PREDICTION MODEL TRAINING")
print("="*60)

print("\n1. Loading dataset...")
df = pd.read_csv("data/preprocessed_data.csv")
print(f"Dataset shape: {df.shape}")
print(f"Total samples: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# ---------- 3. Data Exploration ----------
print("\n2. Data Exploration:")
print("-"*40)

# Save user_id for reference if needed
user_ids = df['user_id'].copy() if 'user_id' in df.columns else None

# Check target distribution
print("Target Distribution:")
target_counts = df['target_career_encoded'].value_counts()
print(target_counts)

# Check if any class has too few samples
min_samples = target_counts.min()
print(f"\nMinimum samples per class: {min_samples}")
print(f"Number of classes: {len(target_counts)}")

# Create a copy without user_id for analysis
df_numeric = df.drop('user_id', axis=1) if 'user_id' in df.columns else df.copy()

print("\n3. Feature Analysis:")
print("-"*40)

# Check for non-numeric columns
non_numeric_cols = df_numeric.select_dtypes(exclude=[np.number]).columns
if len(non_numeric_cols) > 0:
    print(f"Warning: Non-numeric columns found: {list(non_numeric_cols)}")
    print("These will be excluded from correlation analysis")

# Calculate correlations only for numeric columns
numeric_cols = df_numeric.select_dtypes(include=[np.number]).columns
if 'target_career_encoded' in numeric_cols:
    correlations = df_numeric[numeric_cols].corr()['target_career_encoded'].abs().sort_values(ascending=False)
    print("\nTop 10 features correlated with target:")
    print(correlations.head(10))
else:
    print("Warning: target_career_encoded is not numeric!")

# ---------- 4. Prepare Features ----------
print("\n4. Preparing features...")

# Drop user_id and any non-numeric columns
if 'user_id' in df.columns:
    X = df.drop(["user_id", "target_career_encoded"], axis=1)
else:
    X = df.drop("target_career_encoded", axis=1)

# Ensure all columns are numeric
X = X.select_dtypes(include=[np.number])
y = df["target_career_encoded"]

# Feature names for reference
feature_names = X.columns.tolist()
print(f"Number of features: {len(feature_names)}")
print(f"Features: {feature_names}")

# Check for any NaN values
print(f"\nMissing values in X: {X.isnull().sum().sum()}")
print(f"Missing values in y: {y.isnull().sum()}")

# ---------- 5. Handle Class Imbalance ----------
print("\n5. Handling class imbalance...")

# Check if we can apply SMOTE (need at least 2 samples per class)
if min_samples >= 2:
    try:
        # Apply SMOTE for oversampling minority classes
        # Adjust k_neighbors based on smallest class size
        k_neighbors = min(5, min_samples - 1)
        smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        print(f"Original dataset size: {X.shape}")
        print(f"Resampled dataset size: {X_resampled.shape}")
        print(f"Resampled target distribution:\n{y_resampled.value_counts()}")
    except Exception as e:
        print(f"SMOTE failed: {e}")
        print("Using original data without resampling")
        X_resampled, y_resampled = X.copy(), y.copy()
else:
    print(f"Cannot apply SMOTE - minimum samples ({min_samples}) < 2")
    print("Using original data without resampling")
    X_resampled, y_resampled = X.copy(), y.copy()

# ---------- 6. Train-Test Split ----------
print("\n6. Splitting data...")

# For very small classes, we might not be able to stratify properly
if y_resampled.nunique() > len(y_resampled) * 0.2:
    print("Warning: Too many classes for stratification, using regular split")
    X_train, X_test, y_train, y_test = train_test_split(
        X_resampled, y_resampled, test_size=0.2, random_state=42
    )
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
    )

print(f"Training set: {X_train.shape}")
print(f"Testing set: {X_test.shape}")

# ---------- 7. Feature Scaling ----------
print("\n7. Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------- 8. Train Model ----------
print("\n8. Training Random Forest...")

# Optimized parameters for small dataset
rf_model = RandomForestClassifier(
    n_estimators=150,           # Reduced for faster training
    max_depth=8,                # Limit depth to prevent overfitting
    min_samples_split=5,        # Require minimum samples to split
    min_samples_leaf=2,         # Minimum samples in leaf nodes
    max_features='sqrt',        # Use sqrt of features for each tree
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=0
)

# Cross-validation
print("Performing cross-validation...")
try:
    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
except Exception as e:
    print(f"Cross-validation failed: {e}")
    print("Proceeding with training...")
    cv_scores = np.array([0])

# Train final model
rf_model.fit(X_train_scaled, y_train)
print("Model training completed!")

# ---------- 9. Evaluate Model ----------
print("\n9. Evaluating model...")

# Predictions
y_pred = rf_model.predict(X_test_scaled)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
f1_weighted = f1_score(y_test, y_pred, average='weighted')
f1_macro = f1_score(y_test, y_pred, average='macro')

print(f"Accuracy: {accuracy:.4f}")
print(f"Weighted F1-Score: {f1_weighted:.4f}")
print(f"Macro F1-Score: {f1_macro:.4f}")

# Classification report
print("\nDetailed Classification Report:")
try:
    print(classification_report(y_test, y_pred, zero_division=0))
except Exception as e:
    print(f"Classification report error: {e}")

# Confusion matrix summary
print("Confusion Matrix Summary:")
try:
    cm = confusion_matrix(y_test, y_pred)
    print(f"Correct predictions: {np.diag(cm).sum()}/{cm.sum()}")
    print(f"Error rate: {(cm.sum() - np.diag(cm).sum()) / cm.sum():.4f}")
except Exception as e:
    print(f"Confusion matrix error: {e}")

# ---------- 10. Feature Importance ----------
print("\n10. Feature Importance Analysis:")
try:
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    print("Top 15 Most Important Features:")
    print(feature_importance.head(15))

    # Visualize top features
    top_features = feature_importance.head(10)
    print("\nTop 10 Features:")
    for idx, row in top_features.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
except Exception as e:
    print(f"Feature importance error: {e}")

# ---------- 11. Test on Original Data ----------
print("\n11. Testing on original (unbalanced) data...")

try:
    # Create a small validation set from original data
    X_orig_train, X_orig_val, y_orig_train, y_orig_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() < len(y)*0.2 else None
    )

    # Scale validation data
    X_orig_val_scaled = scaler.transform(X_orig_val)

    # Predict
    y_orig_pred = rf_model.predict(X_orig_val_scaled)
    orig_accuracy = accuracy_score(y_orig_val, y_orig_pred)
    print(f"Accuracy on original validation set: {orig_accuracy:.4f}")
except Exception as e:
    print(f"Original data test failed: {e}")

# ---------- 12. Save Model and Artifacts ----------
print("\n12. Saving model and artifacts...")

# Create directories
os.makedirs("models", exist_ok=True)
os.makedirs("artifacts", exist_ok=True)

# Save model
model_path = "models/job_role_rf_enhanced.pkl"
try:
    with open(model_path, "wb") as f:
        pickle.dump({
            'model': rf_model,
            'scaler': scaler,
            'feature_names': feature_names,
            'classes': sorted(y.unique())
        }, f)
    print(f"Model saved to: {model_path}")
except Exception as e:
    print(f"Error saving model: {e}")

# Save feature importance
try:
    if 'feature_importance' in locals():
        feature_importance.to_csv("artifacts/feature_importance_detailed.csv", index=False)
        print("Feature importance saved to artifacts/feature_importance_detailed.csv")
except Exception as e:
    print(f"Error saving feature importance: {e}")

# Save performance metrics
try:
    metrics = {
        'accuracy': accuracy,
        'f1_weighted': f1_weighted,
        'f1_macro': f1_macro,
        'cv_mean': cv_scores.mean() if len(cv_scores) > 0 else 0,
        'cv_std': cv_scores.std() if len(cv_scores) > 0 else 0
    }
    
    if 'orig_accuracy' in locals():
        metrics['orig_accuracy'] = orig_accuracy
    
    pd.DataFrame([metrics]).to_csv("artifacts/model_metrics.csv", index=False)
    print("Model metrics saved to artifacts/model_metrics.csv")
except Exception as e:
    print(f"Error saving metrics: {e}")

# ---------- 13. Final Summary ----------
print("\n" + "="*60)
print("MODEL TRAINING SUMMARY")
print("="*60)
print(f"Dataset size: {len(df)} samples")
print(f"Features used: {len(feature_names)}")
print(f"Target classes: {len(target_counts)}")
print(f"Final Accuracy: {accuracy:.4f}")
print(f"Final Weighted F1: {f1_weighted:.4f}")

print("\n" + "="*60)
print("TRAINING COMPLETED!")
print("="*60)