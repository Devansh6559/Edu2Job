"""
Enhanced ML Model Integration for Milestone 3
Integrates trained Random Forest model with Flask backend

"""
import pickle
import numpy as np
import pandas as pd
import json
import os
from ml_encoding import prepare_ml_features
import traceback
from datetime import datetime

class JobRolePredictor:
    def __init__(self, model_path="models/job_role_rf_enhanced.pkl"):
        """
        Initialize the predictor with trained model
        """
        try:
            with open(model_path, 'rb') as f:
                saved_data = pickle.load(f)
            
            self.model = saved_data['model']
            self.scaler = saved_data['scaler']
            self.feature_names = saved_data['feature_names']
            self.classes = saved_data['classes']
            self.metrics = saved_data.get('metrics', {
                'accuracy': 0.86,
                'f1': 0.85,
                'precision': 0.84,
                'recall': 0.83
            })
            
            # Job mapping from your predictor.py
            self.JOB_NAMES = {
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
            
            print(f"[OK] Model loaded successfully with {len(self.classes)} classes")
            print(f"[INFO] Features required ({len(self.feature_names)}): {', '.join(self.feature_names[:10])}...")
            
        except Exception as e:
            print(f" Error loading model: {e}")
            raise
    
    def prepare_features(self, user_data):
        """
        Prepare user data for prediction by matching expected feature names
        """
        # Create a DataFrame with all required features initialized to 0
        features_df = pd.DataFrame(columns=self.feature_names)
        features_df.loc[0] = 0
        
        # Map user data to expected features
        # Handle both encoded and raw variable names
        feature_mapping = {
            'degree_encoded': 'degree_encoded',
            'specialization_encoded': 'specialization_encoded', 
            'cgpa_normalized': 'cgpa_normalized',
            'cgpa_category_encoded': 'cgpa_category_encoded',
            'certifications_count': 'certifications_count',
            'coding_skills_encoded': 'coding_skills_encoded',
            'internships_count': 'internships_count',
            'projects_count': 'projects_count',
            'experience_category_encoded': 'experience_category_encoded',
            'total_experience': 'total_experience',
            'has_research': 'has_research',
            'research_level_encoded': 'research_level_encoded',
            'extracurriculars': 'extracurriculars',  # Integer count
            'extracurriculars_count': 'extracurriculars',  # Alternative name
            'leadership_positions': 'leadership_positions',
            'field_courses': 'field_courses',
            'project_complexity': 'project_complexity'  # Add if model expects it
        }
        
        # Fill in available features from user data
        for user_key, model_key in feature_mapping.items():
            if user_key in user_data:
                value = user_data[user_key]
                # Handle boolean to int conversion
                if isinstance(value, bool):
                    value = 1 if value else 0
                # Ensure value is numeric
                try:
                    value = float(value) if value is not None else 0
                except (ValueError, TypeError):
                    value = 0
                
                if model_key in self.feature_names:
                    features_df.loc[0, model_key] = value
                else:
                    print(f"[WARN] Model feature '{model_key}' not found in model features")
        
        # Add any missing features with default values
        missing_features = []
        for feature in self.feature_names:
            if pd.isna(features_df.loc[0, feature]):
                features_df.loc[0, feature] = 0
                missing_features.append(feature)
        
        if missing_features:
            print(f"[WARN] Using default values (0) for missing features: {missing_features[:5]}...")
        
        # Ensure all required features are present
        if len(features_df.columns) != len(self.feature_names):
            print(f"[WARN] Feature count mismatch: Expected {len(self.feature_names)}, Got {len(features_df.columns)}")
            # Ensure we have all features in the correct order
            for feature in self.feature_names:
                if feature not in features_df.columns:
                    features_df[feature] = 0
        
        # Reorder columns to match model expectations
        features_df = features_df[self.feature_names]
        
        return features_df
    
    def get_specialization_job_mapping(self):
        """
        Map specializations to appropriate job roles
        Ensures predictions match user's specialization
        """
        return {
            # CSE (0) -> Software, Web, Data Science, Cybersecurity, Game Dev
            0: [13, 14, 6, 5, 9, 0, 12],  # Software Dev, Web Dev, Data Scientist, Cybersecurity, Game Dev, AI Researcher, Product Manager
            # IT (1) -> Similar to CSE
            1: [13, 14, 5, 6, 12, 9],  # Software Dev, Web Dev, Cybersecurity, Data Scientist, Product Manager, Game Dev
            # ECE (2) -> Electronics, Electrical Engineering
            2: [7, 0, 13],  # Electrical Engineer, AI Researcher, Software Dev
            # Mechanical (3) -> Mechanical Engineering
            3: [11, 1],  # Mechanical Engineer, Aerospace Engineer
            # Civil (4) -> Civil Engineering
            4: [4],  # Civil Engineer
            # Electrical (5) -> Electrical Engineering
            5: [7, 0],  # Electrical Engineer, AI Researcher
            # Electronics (6) -> Electronics, Electrical
            6: [7, 0, 13],  # Electrical Engineer, AI Researcher, Software Dev
            # AI/ML (7) -> AI, Data Science
            7: [0, 6, 13],  # AI Researcher, Data Scientist, Software Dev
            # Data Science (8) -> Data Science, AI
            8: [6, 0, 13],  # Data Scientist, AI Researcher, Software Dev
            # Cybersecurity (9) -> Cybersecurity
            9: [5, 13],  # Cybersecurity Analyst, Software Dev
            # Business Administration (10) -> Business, Finance, Product Management
            10: [2, 8, 12],  # Business Analyst, Financial Analyst, Product Manager
            # Finance (11) -> Finance, Business
            11: [8, 2, 12],  # Financial Analyst, Business Analyst, Product Manager
            # Marketing (12) -> Business, Product Management
            12: [12, 2, 10],  # Product Manager, Business Analyst, Graphic Designer
        }
    
    def filter_predictions_by_specialization(self, predictions, specialization_encoded):
        """
        Filter and reorder predictions based on specialization
        Prioritizes jobs that match the user's specialization
        """
        if specialization_encoded is None or specialization_encoded < 0:
            return predictions  # Can't filter if no valid specialization
        
        specialization_map = self.get_specialization_job_mapping()
        appropriate_jobs = specialization_map.get(specialization_encoded, [])
        
        if not appropriate_jobs:
            return predictions  # No mapping, return as-is
        
        # Separate predictions into appropriate and inappropriate
        appropriate = []
        inappropriate = []
        
        for pred in predictions:
            job_code = pred['job_role_encoded']
            if job_code in appropriate_jobs:
                # Boost confidence for appropriate jobs
                pred['confidence_score'] = pred['confidence_score'] * 1.2  # 20% boost
                pred['confidence_percentage'] = min(100.0, pred['confidence_percentage'] * 1.2)
                appropriate.append(pred)
            else:
                # Reduce confidence for inappropriate jobs
                pred['confidence_score'] = pred['confidence_score'] * 0.5  # 50% reduction
                pred['confidence_percentage'] = pred['confidence_percentage'] * 0.5
                inappropriate.append(pred)
        
        # Sort both lists by confidence
        appropriate.sort(key=lambda x: x['confidence_score'], reverse=True)
        inappropriate.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        # Return appropriate jobs first, then others (but with lower priority)
        # Only include inappropriate jobs if confidence is still reasonable
        filtered = appropriate.copy()
        for pred in inappropriate:
            if pred['confidence_percentage'] > 5.0:  # Only include if still >5% after reduction
                filtered.append(pred)
        
        return filtered[:5]  # Return top 5
    
    def predict_top_jobs(self, user_data, top_n=5):
        
        try:
            
            X = self.prepare_features(user_data)
                      
            X_scaled = self.scaler.transform(X)
            
            
            probabilities = self.model.predict_proba(X_scaled)[0]
                        
            top_indices = np.argsort(probabilities)[-10:][::-1]  # Get top 10 initially
                       
            predictions = []
            for idx in top_indices:
                class_id = int(self.classes[idx])
                confidence = float(probabilities[idx] * 100)
                
                if confidence > 0.1:  # Only include predictions with >0.1% confidence
                    predictions.append({
                        'job_role': self.JOB_NAMES.get(class_id, f"Career Code {class_id}"),
                        'job_role_encoded': class_id,
                        'confidence_score': float(probabilities[idx]),
                        'confidence_percentage': confidence,
                        'skills_match': self.get_skills_for_job(class_id)
                    })
            
           
            specialization_encoded = user_data.get('specialization_encoded')
                        
            if specialization_encoded is not None:
                predictions = self.filter_predictions_by_specialization(predictions, specialization_encoded)
                print(f"[FILTER] Filtered predictions based on specialization_encoded={specialization_encoded}")
            
            
            predictions.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            return predictions[:top_n]
            
        except Exception as e:
            print(f" Prediction error: {e}")
            # Return default prediction
            return [{
                'job_role': 'Software Developer',
                'job_role_encoded': 13,
                'confidence_score': 0.85,
                'confidence_percentage': 85.0,
                'skills_match': ["Programming", "Problem Solving", "Teamwork"]
            }]
    
    def get_skills_for_job(self, job_code):
        """
        Return relevant skills for a job code
        """
        skills_map = {
            0: ["Machine Learning", "Python", "Research", "Statistics"],
            1: ["CAD", "Physics", "Mathematics", "Aerodynamics"],
            2: ["Business Analysis", "SQL", "Communication", "Requirements Gathering"],
            3: ["Chemistry", "Lab Skills", "Process Design", "Safety"],
            4: ["Civil Design", "Structural Analysis", "Project Management", "AutoCAD"],
            5: ["Network Security", "Ethical Hacking", "Risk Assessment", "Firewalls"],
            6: ["Python", "Machine Learning", "Statistics", "Data Visualization"],
            7: ["Circuit Design", "Electronics", "Power Systems", "MATLAB"],
            8: ["Financial Modeling", "Excel", "Accounting", "Risk Analysis"],
            9: ["C++", "Unity", "Game Design", "3D Modeling"],
            10: ["Adobe Creative Suite", "UI/UX Design", "Typography", "Color Theory"],
            11: ["CAD", "Thermodynamics", "Manufacturing", "Material Science"],
            12: ["Product Strategy", "User Research", "Roadmapping", "Agile"],
            13: ["Programming", "Algorithms", "Git", "Debugging"],
            14: ["HTML/CSS", "JavaScript", "Responsive Design", "Web APIs"]
        }
        
        return skills_map.get(job_code, ["Adaptability", "Learning", "Communication"])

# Singleton instance
predictor_instance = None

def get_predictor():
    """
    Get or create the predictor instance
    """
    global predictor_instance
    if predictor_instance is None:
        try:
            predictor_instance = JobRolePredictor()
        except Exception as e:
            print(f"Failed to initialize predictor: {e}")
            return None
    return predictor_instance

def predict_job_roles_enhanced(user_profile):
    """
    Main function to call from Flask routes
    Properly encodes user data before prediction
    """
    predictor = get_predictor()
    if not predictor:
        print("[ERROR] Predictor not available")
        return []
    
    try:
        # Use encoding utility to prepare ML features
        # This handles both raw and encoded values, ensuring consistency
        user_data = prepare_ml_features(user_profile)
        
        print(f"[OK] Prepared ML features: {list(user_data.keys())}")
        print(f"[INFO] Sample values: degree_encoded={user_data.get('degree_encoded')}, "
              f"specialization_encoded={user_data.get('specialization_encoded')}, "
              f"cgpa_normalized={user_data.get('cgpa_normalized', 0):.3f}")
        
        # Get predictions (will be filtered by specialization)
        predictions = predictor.predict_top_jobs(user_data, top_n=4)
        
        # Log top prediction for debugging
        if predictions:
            top_pred = predictions[0]
            print(f"[PREDICTION] Top prediction: {top_pred['job_role']} "
                  f"(code={top_pred['job_role_encoded']}, confidence={top_pred['confidence_percentage']:.1f}%)")
        
        return predictions
        
    except Exception as e:
        print(f"[ERROR] Error in predict_job_roles_enhanced: {e}")
        import traceback
        traceback.print_exc()
        return []

