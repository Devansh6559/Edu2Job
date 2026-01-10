"""
Validators for model training and data validation
"""
import pandas as pd
import numpy as np
from datetime import datetime

class ModelTrainingValidator:
    @staticmethod
    def validate_training_data(X, y, min_samples=50):
        """Validate training data before training"""
        errors = []
        
        # Check if data exists
        if X is None or y is None:
            errors.append("No training data provided")
            return False, errors
        
        # Check minimum samples
        if len(X) < min_samples:
            errors.append(f"Insufficient training data: {len(X)} samples (minimum {min_samples} required)")
        
        # Check feature consistency
        if len(X.shape) != 2:
            errors.append(f"Invalid feature shape: {X.shape}")
        
        # Check target consistency
        if len(y.shape) != 1:
            errors.append(f"Invalid target shape: {y.shape}")
        
        # Check for missing values
        if pd.isnull(X).any().any():
            errors.append("Training data contains missing values")
        
        if pd.isnull(y).any():
            errors.append("Target data contains missing values")
        
        # Check for sufficient classes
        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            errors.append(f"Insufficient number of classes: {len(unique_classes)} (minimum 2 required)")
        
        success = len(errors) == 0
        return success, errors
    
    @staticmethod
    def validate_model_parameters(parameters):
        """Validate model training parameters"""
        errors = []
        
        if 'n_estimators' in parameters:
            if not (10 <= parameters['n_estimators'] <= 500):
                errors.append(f"n_estimators must be between 10 and 500, got {parameters['n_estimators']}")
        
        if 'max_depth' in parameters:
            if not (3 <= parameters['max_depth'] <= 50):
                errors.append(f"max_depth must be between 3 and 50, got {parameters['max_depth']}")
        
        if 'test_size' in parameters:
            if not (0.1 <= parameters['test_size'] <= 0.5):
                errors.append(f"test_size must be between 0.1 and 0.5, got {parameters['test_size']}")
        
        success = len(errors) == 0
        return success, errors

class DataValidator:
    @staticmethod
    def validate_user_data(user_data):
        """Validate user data for prediction"""
        errors = []
        required_fields = [
            'degree_encoded',
            'specialization_encoded',
            'cgpa_normalized',
            'coding_skills_encoded'
        ]
        
        for field in required_fields:
            if field not in user_data or user_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        return True, []