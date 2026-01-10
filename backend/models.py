
    
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import re
import bcrypt
import json

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ===== BASIC EDUCATION DETAILS (For UI Display) =====
    degree = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    certifications = db.Column(db.Text)
    university = db.Column(db.String(200))
    
    # ===== ENHANCED CAREER PROFILE FIELDS (For ML Processing) =====
    # Academic Features
    degree_encoded = db.Column(db.Integer)  # Encoded degree type
    specialization_encoded = db.Column(db.Integer)  # Encoded specialization
    cgpa_normalized = db.Column(db.Float)  # Normalized to 0-1 range
    cgpa_category_encoded = db.Column(db.Integer)  # 1=Low(<6), 2=Medium(6-8), 3=High(>8)
    graduation_year_normalized = db.Column(db.Float)  # Normalized year
    
    # Skills & Certifications
    certifications_count = db.Column(db.Integer, default=0)
    coding_skills_encoded = db.Column(db.Integer)  # 1=Beginner, 2=Intermediate, 3=Expert
    tech_stack_vector = db.Column(db.Text)  # JSON array of known technologies
    
    # Experience & Projects
    internships_count = db.Column(db.Integer, default=0)
    projects_count = db.Column(db.Integer, default=0)
    experience_category_encoded = db.Column(db.Integer)  # 1=Fresher, 2=Experienced
    total_experience = db.Column(db.Integer, default=0)  # Months
    project_complexity = db.Column(db.Integer)  # 1=Simple, 2=Medium, 3=Complex
    
    # Research & Academics
    has_research = db.Column(db.Boolean, default=False)
    research_level_encoded = db.Column(db.Integer)  # 0=None, 1=Basic, 2=Advanced
    publications_count = db.Column(db.Integer, default=0)
    field_courses = db.Column(db.Integer, default=0)
    
    # Extracurricular & Soft Skills
    extracurriculars = db.Column(db.Text)  # Comma-separated activities
    extracurriculars_count = db.Column(db.Integer, default=0)
    leadership_positions = db.Column(db.Integer, default=0)
    communication_skills = db.Column(db.Integer)  # 1=Low, 2=Medium, 3=High
    
    # Career Goals
    target_career_encoded = db.Column(db.Integer)
    career_tier = db.Column(db.Integer)  # 1=Entry, 2=Mid, 3=Senior, 4=Lead
    preferred_location_encoded = db.Column(db.Integer)
    salary_expectation_normalized = db.Column(db.Float)  # 0-1 range
    
    # Profile Completion & Status
    profile_completion = db.Column(db.Integer, default=0)  # 0-100%
    last_profile_update = db.Column(db.DateTime)
    is_profile_complete = db.Column(db.Boolean, default=False)
    
    # ===== RELATIONSHIPS =====
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    processed_education = db.relationship('ProcessedEducation', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    def set_password(self, password):
        """Hash and set password using bcrypt"""
        is_valid, message = self.validate_password(password)
        if not is_valid:
            raise ValueError(message)
        
        # Generate salt and hash password with bcrypt
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash using bcrypt"""
        if not self.password_hash or not password:
            return False
        
        try:
            # Verify password against the stored hash
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                self.password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def to_dict(self):
        """Convert user object to dictionary with all fields"""
        base_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            
            # Basic education (for UI)
            'degree': self.degree,
            'specialization': self.specialization,
            'cgpa': self.cgpa,
            'graduation_year': self.graduation_year,
            'certifications': self.certifications,
            'university': self.university,
            
            # Enhanced profile (for ML)
            'degree_encoded': self.degree_encoded,
            'specialization_encoded': self.specialization_encoded,
            'cgpa_normalized': self.cgpa_normalized,
            'cgpa_category_encoded': self.cgpa_category_encoded,
            'graduation_year_normalized': self.graduation_year_normalized,
            'certifications_count': self.certifications_count,
            'coding_skills_encoded': self.coding_skills_encoded,
            'tech_stack_vector': json.loads(self.tech_stack_vector) if self.tech_stack_vector else [],
            'internships_count': self.internships_count,
            'projects_count': self.projects_count,
            'experience_category_encoded': self.experience_category_encoded,
            'total_experience': self.total_experience,
            'project_complexity': self.project_complexity,
            'has_research': self.has_research,
            'research_level_encoded': self.research_level_encoded,
            'publications_count': self.publications_count,
            'field_courses': self.field_courses,
            'extracurriculars': self.extracurriculars,
            'extracurriculars_count': self.extracurriculars_count,
            'leadership_positions': self.leadership_positions,
            'communication_skills': self.communication_skills,
            'target_career_encoded': self.target_career_encoded,
            'career_tier': self.career_tier,
            'preferred_location_encoded': self.preferred_location_encoded,
            'salary_expectation_normalized': self.salary_expectation_normalized,
            'profile_completion': self.profile_completion,
            'last_profile_update': self.last_profile_update.isoformat() if self.last_profile_update else None,
            'is_profile_complete': self.is_profile_complete
        }
        
        # Add prediction count
        if hasattr(self, 'predictions'):
            base_dict['prediction_count'] = len(self.predictions)
        
        # Add processed education data if exists
        if self.processed_education:
            base_dict['processed_education'] = self.processed_education.to_dict()
        
        return base_dict
    
    def get_feature_vector(self):
        """Get complete feature vector for ML model"""
        features = [
            self.degree_encoded or 0,
            self.specialization_encoded or 0,
            self.cgpa_normalized or 0,
            self.cgpa_category_encoded or 0,
            self.certifications_count or 0,
            self.coding_skills_encoded or 0,
            self.internships_count or 0,
            self.projects_count or 0,
            self.experience_category_encoded or 0,
            (self.total_experience or 0) / 60.0,  # Normalize to years
            self.project_complexity or 0,
            1 if self.has_research else 0,
            self.research_level_encoded or 0,
            self.publications_count or 0,
            self.field_courses or 0,
            self.extracurriculars_count or 0,
            self.leadership_positions or 0,
            self.communication_skills or 0,
            self.career_tier or 0
        ]
        
        # Add tech stack vector if available
        if self.tech_stack_vector:
            try:
                tech_stack = json.loads(self.tech_stack_vector)
                features.extend(tech_stack[:10])  # Add first 10 technologies
            except:
                features.extend([0] * 10)
        else:
            features.extend([0] * 10)
        
        return features
    
    def calculate_profile_completion(self):
        """Calculate how complete the user's profile is"""
        total_fields = 25  # Total fields we consider important
        completed_fields = 0
        
        # Check essential fields
        if self.name: completed_fields += 1
        if self.degree_encoded: completed_fields += 1
        if self.specialization_encoded: completed_fields += 1
        if self.cgpa_normalized: completed_fields += 1
        if self.coding_skills_encoded: completed_fields += 1
        if self.target_career_encoded: completed_fields += 1
        
        # Check experience fields
        if self.internships_count is not None: completed_fields += 1
        if self.projects_count is not None: completed_fields += 1
        if self.total_experience is not None: completed_fields += 1
        
        # Calculate percentage
        completion = int((completed_fields / total_fields) * 100)
        self.profile_completion = completion
        self.is_profile_complete = completion >= 70  # 70% = complete
        
        return completion


class ProcessedEducation(db.Model):
    __tablename__ = 'processed_education'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # ===== FEATURE VECTORS =====
    academic_vector = db.Column(db.Text)  # JSON: [degree, specialization, cgpa, etc]
    skills_vector = db.Column(db.Text)  # JSON: [coding_skills, tech_stack, etc]
    experience_vector = db.Column(db.Text)  # JSON: [internships, projects, experience]
    extras_vector = db.Column(db.Text)  # JSON: [research, publications, leadership]
    
    # Complete processed vector (all features concatenated)
    processed_vector = db.Column(db.Text)  # JSON array - all features for ML
    
    # ===== NORMALIZED VALUES =====
    cgpa_normalized = db.Column(db.Float)
    experience_normalized = db.Column(db.Float)
    skills_normalized = db.Column(db.Float)
    
    # ===== ENCODED LABELS =====
    target_career_encoded = db.Column(db.Integer)
    career_cluster = db.Column(db.Integer)  # Group similar careers
    
    # ===== METADATA =====
    version = db.Column(db.String(20), default='1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'academic_vector': json.loads(self.academic_vector) if self.academic_vector else [],
            'skills_vector': json.loads(self.skills_vector) if self.skills_vector else [],
            'experience_vector': json.loads(self.experience_vector) if self.experience_vector else [],
            'extras_vector': json.loads(self.extras_vector) if self.extras_vector else [],
            'processed_vector': json.loads(self.processed_vector) if self.processed_vector else [],
            'cgpa_normalized': self.cgpa_normalized,
            'experience_normalized': self.experience_normalized,
            'skills_normalized': self.skills_normalized,
            'target_career_encoded': self.target_career_encoded,
            'career_cluster': self.career_cluster,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_vectors(self, user):
        """Update all vectors based on user data"""
        try:
            # ✅ Save normalized values
            self.cgpa_normalized = user.cgpa_normalized if user.cgpa_normalized else 0.0
            
            # Calculate other normalized values
            if user.total_experience:
                self.experience_normalized = min(user.total_experience / 60.0, 1.0)
            else:
                self.experience_normalized = 0.0
            
            if user.coding_skills_encoded:
                self.skills_normalized = user.coding_skills_encoded / 3.0
            else:
                self.skills_normalized = 0.0
            
            # Academic vector
            self.academic_vector = json.dumps([
                user.degree_encoded if user.degree_encoded is not None else 0,
                user.specialization_encoded if user.specialization_encoded is not None else 0,
                user.cgpa_normalized if user.cgpa_normalized is not None else 0,
                user.cgpa_category_encoded if user.cgpa_category_encoded is not None else 0,
                user.graduation_year_normalized if user.graduation_year_normalized is not None else 0,
                user.field_courses if user.field_courses is not None else 0
            ])
            
            # Skills vector
            self.skills_vector = json.dumps([
                user.coding_skills_encoded if user.coding_skills_encoded is not None else 0,
                user.certifications_count if user.certifications_count is not None else 0,
                user.communication_skills if user.communication_skills is not None else 0
            ])
            
            # Experience vector
            self.experience_vector = json.dumps([
                user.internships_count if user.internships_count is not None else 0,
                user.projects_count if user.projects_count is not None else 0,
                user.total_experience if user.total_experience is not None else 0,
                user.experience_category_encoded if user.experience_category_encoded is not None else 0,
                user.project_complexity if user.project_complexity is not None else 0
            ])
            
            # Extras vector
            self.extras_vector = json.dumps([
                1 if user.has_research else 0,
                user.research_level_encoded if user.research_level_encoded is not None else 0,
                user.publications_count if user.publications_count is not None else 0,
                user.extracurriculars_count if user.extracurriculars_count is not None else 0,
                user.leadership_positions if user.leadership_positions is not None else 0
            ])
            
            # Combine all vectors
            try:
                academic = json.loads(self.academic_vector)
                skills = json.loads(self.skills_vector)
                experience = json.loads(self.experience_vector)
                extras = json.loads(self.extras_vector)
                self.processed_vector = json.dumps(academic + skills + experience + extras)
            except:
                self.processed_vector = json.dumps([])
            
            # Store target
            self.target_career_encoded = user.target_career_encoded if user.target_career_encoded is not None else 0
            self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
        except Exception as e:
            print(f"Error in update_vectors: {e}")
            # Don't fail, just log

class Prediction(db.Model):
    __tablename__ = 'predictions'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Prediction details
    job_role = db.Column(db.String(100), nullable=False)
    job_role_encoded = db.Column(db.Integer)  # Encoded job role
    confidence_score = db.Column(db.Float, nullable=False)  # 0-1 range
    confidence_percentage = db.Column(db.Float)  # 0-100%
    
    # Features used for this prediction
    feature_vector = db.Column(db.Text)  # JSON array of features used
    model_version = db.Column(db.String(20), default='1.0')
    
    # Matching details
    skills_match = db.Column(db.Text)  # JSON array of matching skills
    matching_score = db.Column(db.Float)  # How well user matches this role (0-1)
    gap_analysis = db.Column(db.Text)  # JSON: skills user needs to develop
    
    # Career path details
    career_level = db.Column(db.String(50))  # Entry, Mid, Senior
    expected_salary_range = db.Column(db.Text)  # JSON: [min, max]
    growth_potential = db.Column(db.Float)  # 0-1
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_role': self.job_role,
            'job_role_encoded': self.job_role_encoded,
            'confidence_score': self.confidence_score,
            'confidence_percentage': self.confidence_percentage or (self.confidence_score * 100),
            'feature_vector': json.loads(self.feature_vector) if self.feature_vector else [],
            'model_version': self.model_version,
            'skills_match': json.loads(self.skills_match) if self.skills_match else [],
            'matching_score': self.matching_score,
            'gap_analysis': json.loads(self.gap_analysis) if self.gap_analysis else [],
            'career_level': self.career_level,
            'expected_salary_range': json.loads(self.expected_salary_range) if self.expected_salary_range else [],
            'growth_potential': self.growth_potential,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ===== LOGGING & FEEDBACK =====

class PredictionLog(db.Model):
    __tablename__ = 'prediction_logs'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    job_role = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    features_used = db.Column(db.Text)  # JSON blob of input features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'user_id': self.user_id,
            'job_role': self.job_role,
            'confidence': self.confidence,
            'features_used': json.loads(self.features_used) if self.features_used else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# class UserFeedback(db.Model):
#     __tablename__ = 'user_feedback'
#     __table_args__ = {'extend_existing': True}

#     id = db.Column(db.Integer, primary_key=True)
#     prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id', ondelete='CASCADE'))
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
#     rating = db.Column(db.Integer)  # 1-5
#     comment = db.Column(db.Text)
#     was_correct = db.Column(db.Boolean)
#     improvement_suggestions = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'prediction_id': self.prediction_id,
#             'user_id': self.user_id,
#             'rating': self.rating,
#             'comment': self.comment,
#             'was_correct': self.was_correct,
#             'improvement_suggestions': self.improvement_suggestions,
#             'created_at': self.created_at.isoformat() if self.created_at else None
#         }
class UserFeedback(db.Model):
    __tablename__ = 'user_feedback'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text)
    was_correct = db.Column(db.Boolean)
    improvement_suggestions = db.Column(db.Text)
    feedback_type = db.Column(db.String(20), default='prediction')  # 'prediction', 'system', 'general'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'was_correct': self.was_correct,
            'improvement_suggestions': self.improvement_suggestions,
            'feedback_type': self.feedback_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
# ===== ADDITIONAL MODELS FOR FUTURE ENHANCEMENTS =====

class CareerPath(db.Model):
    """Career paths and progression"""
    __tablename__ = 'career_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100), nullable=False)
    job_role_encoded = db.Column(db.Integer, unique=True)
    
    # Career details
    category = db.Column(db.String(50))  # Tech, Business, Research, etc.
    tier = db.Column(db.Integer)  # 1=Entry, 2=Mid, 3=Senior, 4=Lead
    
    # Required skills
    required_skills = db.Column(db.Text)  # JSON array
    required_degree = db.Column(db.Text)  # JSON array of acceptable degrees
    experience_required = db.Column(db.Integer)  # Months
    
    # Salary ranges
    entry_salary = db.Column(db.Float)
    mid_salary = db.Column(db.Float)
    senior_salary = db.Column(db.Float)
    
    # Growth metrics
    demand_score = db.Column(db.Float)  # 0-1
    future_growth = db.Column(db.Float)  # 0-1
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_role': self.job_role,
            'job_role_encoded': self.job_role_encoded,
            'category': self.category,
            'tier': self.tier,
            'required_skills': json.loads(self.required_skills) if self.required_skills else [],
            'required_degree': json.loads(self.required_degree) if self.required_degree else [],
            'experience_required': self.experience_required,
            'entry_salary': self.entry_salary,
            'mid_salary': self.mid_salary,
            'senior_salary': self.senior_salary,
            'demand_score': self.demand_score,
            'future_growth': self.future_growth
        }


class Skill(db.Model):
    """Skills database for matching"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50))  # Programming, Database, Cloud, Soft Skills
    weight = db.Column(db.Float)  # Importance weight for matching
    description = db.Column(db.Text)
    
    # Which careers require this skill
    required_for_careers = db.Column(db.Text)  # JSON array of career IDs
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'weight': self.weight,
            'description': self.description,
            'required_for_careers': json.loads(self.required_for_careers) if self.required_for_careers else []
        }


# ===== HELPER FUNCTIONS =====

def init_default_data():
    """Initialize default career paths and skills"""
    with db.session.no_autoflush:
        # Create default career paths if they don't exist
        default_careers = [
            CareerPath(
                job_role="Software Developer",
                job_role_encoded=1,
                category="Technology",
                tier=1,
                required_skills='["Python", "JavaScript", "SQL", "Git"]',
                required_degree='["B.Tech", "B.E", "BCA", "M.Tech"]',
                experience_required=0,
                entry_salary=600000,
                mid_salary=1200000,
                senior_salary=2500000,
                demand_score=0.9,
                future_growth=0.8
            ),
            CareerPath(
                job_role="Data Scientist",
                job_role_encoded=2,
                category="Technology",
                tier=2,
                required_skills='["Python", "Machine Learning", "Statistics", "SQL"]',
                required_degree='["B.Tech", "M.Tech", "M.Sc"]',
                experience_required=12,
                entry_salary=800000,
                mid_salary=1500000,
                senior_salary=3000000,
                demand_score=0.85,
                future_growth=0.9
            ),
            CareerPath(
                job_role="ML Engineer",
                job_role_encoded=3,
                category="Technology",
                tier=2,
                required_skills='["Python", "TensorFlow", "PyTorch", "MLOps"]',
                required_degree='["B.Tech", "M.Tech"]',
                experience_required=18,
                entry_salary=900000,
                mid_salary=1800000,
                senior_salary=3500000,
                demand_score=0.8,
                future_growth=0.85
            )
        ]
        
        for career in default_careers:
            if not CareerPath.query.filter_by(job_role_encoded=career.job_role_encoded).first():
                db.session.add(career)
        
        db.session.commit()
        print("✅ Default career paths initialized")
# Add this to your User class in models.py
def get_ml_features(self):
    """Get properly formatted features for ML model"""
    return {
        'degree_encoded': self.degree_encoded or 0,
        'specialization_encoded': self.specialization_encoded or 0,
        'cgpa_normalized': float(self.cgpa_normalized or 0),
        'cgpa_category_encoded': self.cgpa_category_encoded or 0,
        'certifications_count': int(self.certifications_count or 0),
        'coding_skills': int(self.coding_skills_encoded or 0),  # Map coding_skills_encoded to coding_skills
        'internships_count': int(self.internships_count or 0),
        'projects_count': int(self.projects_count or 0),
        'experience_category_encoded': self.experience_category_encoded or 0,
        'total_experience': int(self.total_experience or 0),
        'has_research': bool(self.has_research or False),
        'research_level_encoded': self.research_level_encoded or 0,
        'extracurriculars': int(self.extracurriculars_count or 0),  # Map extracurriculars_count to extracurriculars
        'leadership_positions': int(self.leadership_positions or 0),
        'field_courses': int(self.field_courses or 0),
        # Add any other features your ML model expects
    }
