"""
Model Manager for Edu2Job - Handles model training, saving, loading, and retraining
"""
import pickle
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import json
from datetime import datetime
import traceback
from sqlalchemy import create_engine, text
from config import Config

class ModelManager:
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.model = None
        self.label_encoder = None
        self.metrics = None
        self.model_version = 'enhanced_rf_1.0'
        self.model_path = 'models/job_role_rf_enhanced.pkl'
        self.label_encoder_path = 'models/label_encoder.pkl'
        self.training_log_path = 'models/training_log.json'
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
    def load_model(self):
        """Load trained model and label encoder from disk"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.label_encoder_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print(f"✅ Model loaded from {self.model_path}")
                return True
            else:
                print("⚠️ No trained model found")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def save_model(self):
        """Save model and label encoder to disk"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.label_encoder_path, 'wb') as f:
                pickle.dump(self.label_encoder, f)
            print(f"✅ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def get_training_data_from_db(self):
        """Extract training data from database"""
        try:
            if not self.db_session:
                # Create direct database connection
                engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
                connection = engine.connect()
            else:
                connection = self.db_session.connection()
            
            # Query for training data
            query = text("""
                SELECT 
                    u.degree_encoded,
                    u.specialization_encoded,
                    u.cgpa_normalized,
                    u.cgpa_category_encoded,
                    u.graduation_year_normalized,
                    u.coding_skills_encoded,
                    u.certifications_count,
                    u.internships_count,
                    u.projects_count,
                    u.total_experience,
                    u.experience_category_encoded,
                    u.research_level_encoded,
                    u.publications_count,
                    u.extracurriculars_count,
                    u.leadership_positions,
                    u.communication_skills,
                    u.target_career_encoded,
                    u.career_tier,
                    u.preferred_location_encoded,
                    u.salary_expectation_normalized,
                    p.job_role_encoded
                FROM users u
                JOIN predictions p ON u.id = p.user_id
                WHERE u.degree_encoded IS NOT NULL 
                    AND u.specialization_encoded IS NOT NULL
                    AND p.job_role_encoded IS NOT NULL
                ORDER BY p.created_at DESC
                LIMIT 1000
            """)
            
            result = connection.execute(query)
            data = result.fetchall()
            
            if not self.db_session:
                connection.close()
            
            if not data:
                print("⚠️ No training data found in database")
                return None, None
            
            # Convert to DataFrame
            columns = [
                'degree_encoded', 'specialization_encoded', 'cgpa_normalized',
                'cgpa_category_encoded', 'graduation_year_normalized', 'coding_skills_encoded',
                'certifications_count', 'internships_count', 'projects_count',
                'total_experience', 'experience_category_encoded', 'research_level_encoded',
                'publications_count', 'extracurriculars_count', 'leadership_positions',
                'communication_skills', 'target_career_encoded', 'career_tier',
                'preferred_location_encoded', 'salary_expectation_normalized', 'job_role_encoded'
            ]
            
            df = pd.DataFrame(data, columns=columns)
            
            # Handle missing values
            df = df.fillna(0)
            
            # Separate features and target
            X = df.drop('job_role_encoded', axis=1)
            y = df['job_role_encoded']
            
            print(f"✅ Loaded {len(df)} training samples")
            return X, y
            
        except Exception as e:
            print(f"❌ Error getting training data: {e}")
            traceback.print_exc()
            return None, None
    
    def train_model(self, force_retrain=False):
        """Train or retrain the model"""
        try:
            print("🔄 Starting model training...")
            
            # Get training data
            X, y = self.get_training_data_from_db()
            
            if X is None or y is None or len(X) < 50:
                print("⚠️ Insufficient training data. Need at least 50 samples.")
                if not force_retrain:
                    return self.load_model()  # Try to load existing model
                else:
                    return False, "Insufficient training data (minimum 50 samples required)"
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            print(f"📊 Training samples: {len(X_train)}, Test samples: {len(X_test)}")
            
            # Initialize and train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            
            self.metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred, average='weighted'),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'unique_classes': len(np.unique(y)),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Model trained successfully!")
            print(f"   Accuracy: {self.metrics['accuracy']:.4f}")
            print(f"   F1 Score: {self.metrics['f1']:.4f}")
            print(f"   Precision: {self.metrics['precision']:.4f}")
            print(f"   Recall: {self.metrics['recall']:.4f}")
            
            # Save model
            self.save_model()
            
            # Log training session
            self.log_training_session()
            
            return True, "Model trained successfully"
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            traceback.print_exc()
            return False, str(e)
    
    def log_training_session(self):
        """Log training session details"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'model_version': self.model_version,
                'metrics': self.metrics,
                'model_path': self.model_path
            }
            
            # Load existing log
            log_data = []
            if os.path.exists(self.training_log_path):
                try:
                    with open(self.training_log_path, 'r') as f:
                        log_data = json.load(f)
                except:
                    pass
            
            # Add new entry
            log_data.append(log_entry)
            
            # Keep only last 10 entries
            if len(log_data) > 10:
                log_data = log_data[-10:]
            
            # Save log
            with open(self.training_log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f"✅ Training session logged to {self.training_log_path}")
            
        except Exception as e:
            print(f"⚠️ Could not log training session: {e}")
    
    # def get_model_info(self):
    #     """Get information about the current model"""
    #     info = {
    #         'loaded': self.model is not None,
    #         'version': self.model_version,
    #         'last_trained': None,
    #         'metrics': self.metrics or {},
    #         'features': None,
    #         'classes': None
    #     }
        
    #     if self.model is not None:
    #         info['features'] = len(self.model.feature_importances_) if hasattr(self.model, 'feature_importances_') else None
    #         info['classes'] = len(self.model.classes_) if hasattr(self.model, 'classes_') else None
        
    #     # Get last training timestamp from log
    #     if os.path.exists(self.training_log_path):
    #         try:
    #             with open(self.training_log_path, 'r') as f:
    #                 log_data = json.load(f)
    #                 if log_data:
    #                     last_entry = log_data[-1]
    #                     info['last_trained'] = last_entry.get('timestamp')
    #                     if not info['metrics']:
    #                         info['metrics'] = last_entry.get('metrics', {})
    #         except:
    #             pass
        
    #     return info
    def get_model_info(self):
        """Get information about the current model (SAFE for bundled pickle)"""

        info = {
            'loaded': False,
            'version': self.model_version,
            'last_trained': None,
            'metrics': self.metrics or {},
            'features': None,
            'classes': None
        }

        try:
            # Case 1: Model not loaded yet
            if self.model is None:
                return info

            # Case 2: Bundled pickle (dict)
            if isinstance(self.model, dict):
                model_obj = self.model.get("model")
                feature_names = self.model.get("feature_names", [])
                classes = self.model.get("classes", [])

                info['loaded'] = model_obj is not None
                info['features'] = len(feature_names)
                info['classes'] = len(classes)

            # Case 3: Legacy direct model (fallback)
            else:
                info['loaded'] = True
                if hasattr(self.model, "feature_importances_"):
                    info['features'] = len(self.model.feature_importances_)
                if hasattr(self.model, "classes_"):
                    info['classes'] = len(self.model.classes_)

            # Load last training timestamp from log
            if os.path.exists(self.training_log_path):
                try:
                    with open(self.training_log_path, 'r') as f:
                        log_data = json.load(f)
                        if log_data:
                            last_entry = log_data[-1]
                            info['last_trained'] = last_entry.get('timestamp')
                            if not info['metrics']:
                                info['metrics'] = last_entry.get('metrics', {})
                except Exception:
                    pass

            return info

        except Exception as e:
            print("❌ get_model_info error:", e)
            return info
    
    def predict(self, features):
        """Make prediction using the trained model"""
        if self.model is None:
            raise ValueError("Model not loaded or trained")
        
        # Convert features to numpy array
        features_array = np.array([features])
        
        # Make prediction
        prediction_encoded = self.model.predict(features_array)[0]
        probabilities = self.model.predict_proba(features_array)[0]
        
        # Decode prediction if label encoder is available
        prediction = prediction_encoded
        if self.label_encoder:
            try:
                prediction = self.label_encoder.inverse_transform([prediction_encoded])[0]
            except:
                pass
        
        confidence = float(probabilities[prediction_encoded])
        
        return {
            'prediction': prediction,
            'prediction_encoded': int(prediction_encoded),
            'confidence': confidence,
            'probabilities': probabilities.tolist()
        }

# Global model manager instance
model_manager_instance = None

def get_model_manager(db_session=None):
    """Get or create the global model manager instance"""
    global model_manager_instance
    if model_manager_instance is None:
        model_manager_instance = ModelManager(db_session)
        model_manager_instance.load_model()
    return model_manager_instance