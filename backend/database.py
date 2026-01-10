"""
Database utilities for model training
"""
from sqlalchemy import create_engine, text
from config import Config

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    def get_training_samples(self, limit=1000):
        """Get training samples from database"""
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
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {'limit': limit})
            return result.fetchall()
    
    def get_dataset_stats(self):
        """Get dataset statistics"""
        stats_query = text("""
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(p.id) as total_predictions,
                COUNT(DISTINCT p.job_role) as unique_job_roles,
                AVG(p.confidence_score) as avg_confidence
            FROM users u
            LEFT JOIN predictions p ON u.id = p.user_id
            WHERE u.degree_encoded IS NOT NULL
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(stats_query)
            stats = result.fetchone()
            return {
                'total_users': stats[0] or 0,
                'total_predictions': stats[1] or 0,
                'unique_job_roles': stats[2] or 0,
                'avg_confidence': float(stats[3] or 0) * 100
            }
    
    def get_recent_feedback(self, days=7):
        """Get recent feedback for model improvement"""
        query = text("""
            SELECT 
                f.rating,
                f.comment,
                f.improvement_suggestions,
                p.job_role,
                p.confidence_score
            FROM user_feedback f
            LEFT JOIN predictions p ON f.prediction_id = p.id
            WHERE f.created_at >= NOW() - INTERVAL :days DAY
            ORDER BY f.created_at DESC
            LIMIT 100
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {'days': days})
            return result.fetchall()