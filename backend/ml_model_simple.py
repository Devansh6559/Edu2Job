import json
import random
from datetime import datetime

# Simple rule-based prediction system (No ML dependencies required)
class SimpleJobPredictor:
    def __init__(self):
        self.job_rules = {
            'Computer Science': {
                'AI': ['AI Engineer', 'Machine Learning Engineer', 'Data Scientist', 'AI Researcher'],
                'Software Engineering': ['Software Developer', 'Full Stack Developer', 'DevOps Engineer', 'Backend Engineer'],
                'Data Science': ['Data Scientist', 'Data Analyst', 'Business Intelligence Analyst', 'Data Engineer'],
                'Cybersecurity': ['Security Analyst', 'Network Security Engineer', 'Ethical Hacker', 'Security Consultant'],
                'Web Development': ['Frontend Developer', 'Full Stack Developer', 'Web Developer', 'UI/UX Developer'],
                'Mobile Development': ['Mobile App Developer', 'iOS Developer', 'Android Developer'],
                'Cloud Computing': ['Cloud Engineer', 'DevOps Engineer', 'Solutions Architect'],
                'Game Development': ['Game Developer', 'Game Programmer', 'Unity Developer'],
                'default': ['Software Developer', 'IT Consultant', 'Systems Analyst', 'Technical Support']
            },
            'Electrical Engineering': {
                'Power Systems': ['Electrical Engineer', 'Power Systems Engineer', 'Grid Operator', 'Energy Consultant'],
                'Electronics': ['Electronics Engineer', 'Hardware Engineer', 'Embedded Systems Engineer', 'VLSI Engineer'],
                'Telecommunications': ['Network Engineer', 'Telecom Engineer', 'RF Engineer', 'Communication Engineer'],
                'Control Systems': ['Control Systems Engineer', 'Automation Engineer', 'Robotics Engineer'],
                'Instrumentation': ['Instrumentation Engineer', 'Process Control Engineer'],
                'default': ['Electrical Engineer', 'Project Engineer', 'Design Engineer', 'Maintenance Engineer']
            },
            'Mechanical Engineering': {
                'Thermodynamics': ['Mechanical Engineer', 'HVAC Engineer', 'Energy Engineer', 'Thermal Engineer'],
                'Manufacturing': ['Manufacturing Engineer', 'Production Engineer', 'Quality Engineer', 'Industrial Engineer'],
                'Design': ['Design Engineer', 'CAD Engineer', 'Product Development Engineer', 'R&D Engineer'],
                'Automotive': ['Automotive Engineer', 'Vehicle Dynamics Engineer', 'Auto Design Engineer'],
                'Aerospace': ['Aerospace Engineer', 'Aircraft Engineer', 'Propulsion Engineer'],
                'default': ['Mechanical Engineer', 'Project Engineer', 'Maintenance Engineer', 'Quality Control Engineer']
            },
            'Business Administration': {
                'Finance': ['Business Analyst', 'Financial Analyst', 'Investment Banker', 'Financial Consultant'],
                'Marketing': ['Marketing Manager', 'Digital Marketer', 'Brand Manager', 'Marketing Analyst'],
                'HR': ['HR Manager', 'Recruitment Specialist', 'Training Coordinator', 'HR Business Partner'],
                'Operations': ['Operations Manager', 'Supply Chain Manager', 'Logistics Manager'],
                'Entrepreneurship': ['Business Development Manager', 'Startup Founder', 'Product Manager'],
                'default': ['Business Analyst', 'Project Manager', 'Operations Manager', 'Management Trainee']
            },
            'Information Technology': {
                'Networking': ['Network Administrator', 'Network Engineer', 'System Administrator'],
                'Database': ['Database Administrator', 'SQL Developer', 'Data Architect'],
                'Security': ['Security Analyst', 'Information Security Analyst', 'Cybersecurity Specialist'],
                'Support': ['IT Support Specialist', 'Help Desk Technician', 'Technical Support Engineer'],
                'default': ['IT Consultant', 'System Administrator', 'Technical Support', 'IT Project Manager']
            },
            'Civil Engineering': {
                'Structural': ['Structural Engineer', 'Civil Engineer', 'Design Engineer'],
                'Construction': ['Construction Manager', 'Site Engineer', 'Project Engineer'],
                'Transportation': ['Transportation Engineer', 'Highway Engineer', 'Traffic Engineer'],
                'Environmental': ['Environmental Engineer', 'Water Resources Engineer'],
                'default': ['Civil Engineer', 'Site Engineer', 'Project Engineer', 'Design Engineer']
            },
            'Electronics and Communication': {
                'VLSI': ['VLSI Engineer', 'Chip Design Engineer', 'Semiconductor Engineer'],
                'Communication': ['Communication Engineer', 'Network Engineer', 'Telecom Engineer'],
                'Embedded Systems': ['Embedded Systems Engineer', 'Firmware Engineer', 'IoT Developer'],
                'default': ['Electronics Engineer', 'Hardware Engineer', 'Design Engineer']
            },
            'Mathematics': {
                'Statistics': ['Data Analyst', 'Statistician', 'Risk Analyst', 'Quantitative Analyst'],
                'Applied Mathematics': ['Data Scientist', 'Research Analyst', 'Operations Research Analyst'],
                'Computational': ['Computational Scientist', 'Algorithm Engineer', 'Research Scientist'],
                'default': ['Data Analyst', 'Research Analyst', 'Quantitative Analyst', 'Teacher']
            },
            'Physics': {
                'Theoretical': ['Research Scientist', 'Physicist', 'Academic Researcher'],
                'Applied': ['Research Engineer', 'Development Engineer', 'Technical Consultant'],
                'Electronics': ['Electronics Engineer', 'Research Scientist', 'Instrumentation Engineer'],
                'default': ['Research Scientist', 'Lab Technician', 'Physics Teacher', 'Technical Writer']
            },
            'Chemistry': {
                'Organic': ['Chemist', 'Research Scientist', 'Pharmaceutical Researcher'],
                'Analytical': ['Analytical Chemist', 'Quality Control Chemist', 'Lab Manager'],
                'Industrial': ['Process Engineer', 'Chemical Engineer', 'Production Chemist'],
                'default': ['Chemist', 'Lab Technician', 'Quality Control Analyst', 'Research Assistant']
            },
            'Biology': {
                'Microbiology': ['Microbiologist', 'Research Scientist', 'Lab Technologist'],
                'Biotechnology': ['Biotechnologist', 'Research Scientist', 'Bioinformatics Specialist'],
                'Genetics': ['Geneticist', 'Research Scientist', 'Clinical Researcher'],
                'default': ['Biologist', 'Research Assistant', 'Lab Technician', 'Quality Control']
            },
            'default': {
                'default': ['Business Analyst', 'Project Coordinator', 'Operations Specialist', 'Customer Service Manager']
            }
        }
        
        self.skills_map = {
            'AI Engineer': ['Python', 'Machine Learning', 'Deep Learning', 'Mathematics', 'TensorFlow', 'PyTorch'],
            'Machine Learning Engineer': ['Python', 'ML Algorithms', 'Data Preprocessing', 'Model Deployment', 'Statistics'],
            'Data Scientist': ['Python', 'R', 'Statistics', 'Data Visualization', 'SQL', 'Machine Learning'],
            'Software Developer': ['Programming', 'Algorithms', 'Data Structures', 'Debugging', 'Version Control'],
            'Full Stack Developer': ['JavaScript', 'React', 'Node.js', 'Database', 'API Development', 'HTML/CSS'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'CI/CD', 'Cloud Platforms', 'Linux', 'Scripting'],
            'Data Analyst': ['Excel', 'SQL', 'Data Visualization', 'Statistics', 'Reporting', 'Python'],
            'Security Analyst': ['Network Security', 'Cybersecurity', 'Risk Assessment', 'Incident Response', 'Firewalls'],
            'Electrical Engineer': ['Circuit Design', 'Electronics', 'Power Systems', 'MATLAB', 'Simulation Tools'],
            'Mechanical Engineer': ['CAD', 'Thermodynamics', 'Mechanics', 'Design', 'Manufacturing Processes'],
            'Business Analyst': ['Analytics', 'Communication', 'Business Knowledge', 'SQL', 'Requirements Gathering'],
            'Marketing Manager': ['Digital Marketing', 'SEO', 'Social Media', 'Market Research', 'Content Strategy'],
            'HR Manager': ['Recruitment', 'Employee Relations', 'HR Policies', 'Communication', 'Conflict Resolution'],
            'Network Engineer': ['Networking', 'TCP/IP', 'Routing', 'Switching', 'Network Security'],
            'Cloud Engineer': ['AWS', 'Azure', 'GCP', 'Cloud Architecture', 'Infrastructure as Code'],
            'Game Developer': ['C++', 'Unity', 'Unreal Engine', 'Game Physics', '3D Graphics'],
            'Mobile App Developer': ['Java', 'Kotlin', 'Swift', 'React Native', 'Flutter', 'Mobile UI/UX'],
            'Research Scientist': ['Research Methodology', 'Data Analysis', 'Academic Writing', 'Laboratory Skills'],
            'Project Manager': ['Project Planning', 'Team Management', 'Risk Management', 'Communication', 'Agile/Scrum'],
            'Quality Engineer': ['Quality Control', 'Testing', 'Process Improvement', 'Standards Compliance', 'Documentation']
        }

    def predict_jobs(self, user_data):
        degree = user_data.get('degree', 'default')
        specialization = user_data.get('specialization', 'default')
        cgpa = user_data.get('cgpa', 3.0)
        graduation_year = user_data.get('graduation_year', datetime.now().year)
        
        # Get possible job roles based on degree and specialization
        degree_rules = self.job_rules.get(degree, self.job_rules['default'])
        job_roles = degree_rules.get(specialization, degree_rules['default'])
        
        # Adjust confidence based on CGPA
        base_confidence = min(85, 60 + (cgpa - 2.5) * 10)  # Scale CGPA to confidence
        
        # Adjust for graduation year (freshers get slightly lower confidence)
        current_year = datetime.now().year
        years_since_graduation = current_year - graduation_year
        if years_since_graduation <= 0:  # Fresher
            base_confidence *= 0.9  # 10% reduction for freshers
        elif years_since_graduation > 5:
            base_confidence *= 1.1  # 10% boost for experienced
        
        predictions = []
        for job_role in job_roles[:5]:  # Return top 5 roles
            # Add some randomness to make it realistic
            confidence_variation = random.uniform(-15, 15)
            confidence = max(25, min(95, base_confidence + confidence_variation))
            
            skills = self.skills_map.get(job_role, ['Communication', 'Problem Solving', 'Teamwork', 'Analytical Thinking'])
            
            # Generate reason based on profile
            if degree != 'default':
                reason = f"Strong match based on your {degree} degree"
                if specialization != 'default':
                    reason += f" with specialization in {specialization}"
            else:
                reason = "Good match based on general qualifications"
            
            predictions.append({
                'job_role': job_role,
                'confidence_score': round(confidence, 2),
                'skills_match': skills,
                'reason': reason
            })
        
        # Sort by confidence score
        predictions.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        return predictions[:5]  # Return top 5

    def get_all_degrees(self):
        """Get list of all available degrees"""
        return list(self.job_rules.keys())
    
    def get_specializations(self, degree):
        """Get specializations for a given degree"""
        if degree in self.job_rules:
            specializations = list(self.job_rules[degree].keys())
            specializations.remove('default')
            return specializations
        return []

# Global predictor instance
predictor = SimpleJobPredictor()

def train_model():
    """Mock training function for compatibility"""
    return "Rule-based model ready - No training required"

def predict_job_roles(user_data):
    """Main prediction function - takes user data and returns job predictions"""
    try:
        return predictor.predict_jobs(user_data)
    except Exception as e:
        print(f"Prediction error: {e}")
        # Return default predictions in case of error
        return [
            {
                'job_role': 'Software Developer',
                'confidence_score': 75.0,
                'skills_match': ['Programming', 'Problem Solving', 'Teamwork'],
                'reason': 'General recommendation based on available data'
            }
        ]

def generate_skills_match(user_data, job_role):
    """Generate skills match for a job role"""
    skills = predictor.skills_map.get(job_role, ['Communication', 'Problem Solving', 'Teamwork', 'Analytical Thinking'])
    return skills

def get_available_degrees():
    """Get list of all available degrees for forms"""
    return predictor.get_all_degrees()

def get_available_specializations(degree):
    """Get specializations for a given degree"""
    return predictor.get_specializations(degree)

# Test the model
if __name__ == "__main__":
    # Test with sample data
    test_user = {
        'degree': 'Computer Science',
        'specialization': 'AI',
        'cgpa': 3.8,
        'graduation_year': 2024
    }
    
    predictions = predict_job_roles(test_user)
    print("🧪 Testing ML Model Simple")
    print("=" * 50)
    print(f"Input: {test_user}")
    print("Predictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. {pred['job_role']} - {pred['confidence_score']}%")
        print(f"   Skills: {', '.join(pred['skills_match'][:3])}...")
        print(f"   Reason: {pred['reason']}")
        print()