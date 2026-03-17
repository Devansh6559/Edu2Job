



const API_BASE = 'http://localhost:5000/api';

/* ============================================
   GLOBAL STATE & INITIALIZATION
============================================ */
let currentUser = null;
let predictionsCache = null;
let modelMetrics = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard initializing...');
    
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }
    
    // Load user data first
    loadUserProfile().then(() => {
        // Setup all event listeners
        setupEventListeners();
        
        // Initialize UI
        initializeUI();
        
        console.log('✅ Dashboard ready');
    }).catch(error => {
        console.error('❌ Failed to initialize dashboard:', error);
        showAlert('Failed to load dashboard. Please refresh the page.', 'danger');
    });
});

/* ============================================
   INITIALIZATION FUNCTIONS
============================================ */
function setupEventListeners() {
    // Profile form
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', updateProfile);
    }
    
    // Education form
    const educationForm = document.getElementById('educationForm');
    if (educationForm) {
        educationForm.addEventListener('submit', submitEducationForm);
    }
    
    // Password change form
    const passwordForm = document.getElementById('changePasswordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', changePassword);
        
        // Real-time password validation
        const newPasswordInput = document.getElementById('newPassword');
        const confirmPasswordInput = document.getElementById('confirmPassword');
        if (newPasswordInput) newPasswordInput.addEventListener('input', validateNewPassword);
        if (confirmPasswordInput) confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
    
    // Navigation handlers
    document.querySelectorAll('.nav-link[onclick^="showSection"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionName = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showSection(sectionName);
        });
    });
    
    // Progress update listeners for education form
    const progressFields = ['degree', 'specialization', 'cgpa', 'graduationYear', 'codingSkills', 'targetCareer'];
    progressFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', updateProgress);
            field.addEventListener('input', updateProgress);
        }
    });
    
    // Real-time validation for CGPA
    const cgpaInput = document.getElementById('cgpa');
    if (cgpaInput) {
        cgpaInput.addEventListener('change', function() {
            const value = parseFloat(this.value);
            if (value < 0 || value > 10) {
                this.classList.add('is-invalid');
                showAlert('CGPA must be between 0 and 10', 'warning');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }
}

function initializeUI() {
    // Set user name in dashboard
    if (currentUser && currentUser.name) {
        document.getElementById('userName').textContent = currentUser.name;
    }
    
    // Load initial data
    loadDashboardData();
    updateProgress();
}

/* ============================================
   USER PROFILE FUNCTIONS
============================================ */
async function loadUserProfile() {
    try {
        console.log('📡 Fetching user profile...');
        const response = await fetch(`${API_BASE}/user/profile`, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.user) {
            currentUser = data.user;
            
            // Store in localStorage for quick access
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Update UI
            updateProfileUI(data.user);
            prefillEnhancedEducationForm(data.user);
            
            return data.user;
        } else {
            throw new Error(data.message || 'Invalid user data received');
        }
    } catch (error) {
        console.error('❌ Failed to load user profile:', error);
        
        // Try to use cached data
        const cachedUser = JSON.parse(localStorage.getItem('user') || '{}');
        if (cachedUser && cachedUser.id) {
            currentUser = cachedUser;
            updateProfileUI(cachedUser);
            showAlert('Using cached profile data. Some features may be limited.', 'warning');
            return cachedUser;
        }
        
        throw error;
    }
}

function updateProfileUI(user) {
    // Update welcome message
    const userNameElement = document.getElementById('userName');
    if (userNameElement) {
        userNameElement.textContent = user.name || 'User';
    }
    
    // Update profile summary
    updateProfileSummary(user);
    
    // Prefill profile form
    prefillProfileForm(user);
}

function updateProfileSummary(user) {
    const profileSummary = document.getElementById('profileSummary');
    if (!profileSummary) return;
    
    const completionPercentage = calculateProfileCompletion(user);
    
    profileSummary.innerHTML = `
        <div class="mb-3">
            <div class="d-flex justify-content-between mb-1">
                <span>Profile Completion</span>
                <span>${completionPercentage}%</span>
            </div>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar ${completionPercentage >= 80 ? 'bg-success' : completionPercentage >= 50 ? 'bg-warning' : 'bg-danger'}" 
                     style="width: ${completionPercentage}%"></div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-6">
                <p class="mb-1"><strong>Degree:</strong></p>
                <p class="mb-1"><strong>Specialization:</strong></p>
                <p class="mb-1"><strong>CGPA:</strong></p>
                <p class="mb-1"><strong>University:</strong></p>
            </div>
            <div class="col-6 text-end">
                <p class="mb-1">${user.degree || 'Not set'}</p>
                <p class="mb-1">${user.specialization || 'Not set'}</p>
                <p class="mb-1">${user.cgpa ? user.cgpa.toFixed(2) : 'Not set'}</p>
                <p class="mb-1">${user.university || 'Not set'}</p>
            </div>
        </div>
        
        <div class="mt-3">
            <p class="mb-1"><i class="fas fa-briefcase me-2"></i>Experience: ${user.total_experience || 0} months</p>
            <p class="mb-1"><i class="fas fa-project-diagram me-2"></i>Projects: ${user.projects_count || 0}</p>
            <p class="mb-1"><i class="fas fa-certificate me-2"></i>Certifications: ${user.certifications_count || 0}</p>
            <p class="mb-0"><i class="fas fa-chart-line me-2"></i>Predictions: ${user.prediction_count || 0}</p>
        </div>
    `;
}

function prefillProfileForm(user) {
    const fields = {
        'profileName': user.name,
        'profileEmail': user.email,
        'profileDegree': user.degree,
        'profileSpecialization': user.specialization,
        'profileCgpa': user.cgpa,
        'profileGraduationYear': user.graduation_year,
        'profileUniversity': user.university,
        'profileCertifications': user.certifications || ''
    };
    
    Object.entries(fields).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.value = value || '';
        }
    });
}

async function updateProfile(e) {
    e.preventDefault();
    
    try {
        const formData = {
            name: document.getElementById('profileName').value,
            degree: document.getElementById('profileDegree').value,
            specialization: document.getElementById('profileSpecialization').value,
            cgpa: document.getElementById('profileCgpa').value || null,
            graduation_year: document.getElementById('profileGraduationYear').value || null,
            university: document.getElementById('profileUniversity').value || null,
            certifications: document.getElementById('profileCertifications').value || null
        };
        
        console.log('📤 Updating profile:', formData);
        
        const response = await fetch(`${API_BASE}/profile`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Profile updated successfully!', 'success');
            
            // Refresh user data
            await loadUserProfile();
            
            // Return to dashboard
            setTimeout(() => showSection('dashboard'), 1500);
        } else {
            throw new Error(data.message || 'Failed to update profile');
        }
    } catch (error) {
        console.error('❌ Update profile error:', error);
        showAlert(`Error updating profile: ${error.message}`, 'danger');
    }
}

function calculateProfileCompletion(user) {
    const requiredFields = [
        user.name, user.email, user.degree, user.specialization,
        user.cgpa, user.graduation_year, user.university
    ];
    
    const completedFields = requiredFields.filter(field => 
        field !== null && field !== undefined && field !== ''
    ).length;
    
    return Math.round((completedFields / requiredFields.length) * 100);
}

/* ============================================
   EDUCATION FORM FUNCTIONS
============================================ */
function prefillEnhancedEducationForm(user) {
    if (!user) return;

    // Convert ML encoded values back to form select values so the correct
    // options (especially MBA, Ph.D, Diploma) are shown in the UI.
    const degreeMlToForm = {
        // ML:Form mapping (inverse of FORM_DEGREE_TO_ML_MAPPING in ml_encoding.py)
        0: 1,   // B.Tech/B.E
        2: 2,   // M.Tech/M.E
        4: 3,   // BCA
        5: 4,   // MCA
        1: 5,   // B.Sc
        3: 7,   // MBA
        10: 8,  // Ph.D
        9: 9    // Diploma
    };

    const specializationMlToForm = {
        // ML:Form mapping (inverse of FORM_SPECIALIZATION_TO_ML_MAPPING)
        0: 1,   // CSE -> Computer Science
        1: 2,   // IT -> Information Technology
        6: 3,   // Electronics
        3: 4,   // Mechanical
        4: 5,   // Civil
        5: 6,   // Electrical
        7: 7,   // AI/ML
        8: 8,   // Data Science
        9: 9,   // Cybersecurity
        10: 10, // Business Administration -> Business
        11: 11  // Finance
    };

    const degreeValue = (user.degree_encoded !== undefined && user.degree_encoded !== null)
        ? (degreeMlToForm[user.degree_encoded] || '')
        : '';

    const specializationValue = (user.specialization_encoded !== undefined && user.specialization_encoded !== null)
        ? (specializationMlToForm[user.specialization_encoded] || '')
        : '';

    const fieldMappings = {
        // Academic
        'degree': degreeValue,
        'specialization': specializationValue,
        'cgpa': user.cgpa || '',
        'graduationYear': user.graduation_year || '',
        'university': user.university || '',
        'fieldCourses': user.field_courses || 0,
        
        // Skills
        'codingSkills': user.coding_skills_encoded || '',
        'certificationsCount': user.certifications_count || 0,
        'techStack': user.tech_stack ? JSON.parse(user.tech_stack).join(', ') : '',
        
        // Experience
        'internshipsCount': user.internships_count || 0,
        'projectsCount': user.projects_count || 0,
        'totalExperience': user.total_experience || 0,
        'projectComplexity': user.project_complexity || 1,
        
        // Research
        'researchLevel': user.research_level_encoded || 0,
        'publicationsCount': user.publications_count || 0,
        'leadershipPositions': user.leadership_positions || 0,
        'communicationSkills': user.communication_skills || 2,
        'extracurriculars': user.extracurriculars || '',
        
        // Career Goals
        'targetCareer': user.target_career_encoded || '',
        'careerTier': user.career_tier || 1,
        'salaryExpectation': user.salary_expectation ? (user.salary_expectation * 100) : '',
        'preferredLocation': user.preferred_location_encoded || 1
    };
    
    Object.entries(fieldMappings).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value !== undefined && value !== null) {
            element.value = value;
        }
    });
}

function updateProgress() {
    const requiredFields = [
        'degree', 'specialization', 'cgpa', 'graduationYear', 
        'codingSkills', 'targetCareer'
    ];
    
    let completed = 0;
    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && field.value && field.value.toString().trim() !== '') {
            completed++;
        }
    });
    
    const progress = Math.round((completed / requiredFields.length) * 100);
    
    // Update progress bar
    const progressBar = document.getElementById('profileProgress');
    const completionText = document.getElementById('profileCompletion');
    
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
        progressBar.className = progress < 50 ? 'progress-bar bg-danger' :
                                progress < 80 ? 'progress-bar bg-warning' :
                                'progress-bar bg-success';
    }
    
    if (completionText) {
        completionText.textContent = `${progress}%`;
    }
    
    return progress;
}

async function submitEducationForm(e) {
    e.preventDefault();
    
    const responseDiv = document.getElementById('educationResponse');
    responseDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-3"></div>
                <strong>Building your career profile...</strong>
            </div>
        </div>
    `;
    
    // Collect form data
    const educationData = {
        // Academic
        degree_encoded: parseInt(document.getElementById('degree').value) || 0,
        specialization_encoded: parseInt(document.getElementById('specialization').value) || 0,
        cgpa: parseFloat(document.getElementById('cgpa').value) || 0,
        graduation_year: parseInt(document.getElementById('graduationYear').value) || 0,
        university: document.getElementById('university').value.trim(),
        field_courses: parseInt(document.getElementById('fieldCourses').value) || 0,
        
        // Skills
        coding_skills_encoded: parseInt(document.getElementById('codingSkills').value) || 0,
        certifications_count: parseInt(document.getElementById('certificationsCount').value) || 0,
        tech_stack_vector: document.getElementById('techStack').value
            .split(',')
            .map(skill => skill.trim())
            .filter(skill => skill.length > 0),
        
        // Experience
        internships_count: parseInt(document.getElementById('internshipsCount').value) || 0,
        projects_count: parseInt(document.getElementById('projectsCount').value) || 0,
        total_experience: parseInt(document.getElementById('totalExperience').value) || 0,
        project_complexity: parseInt(document.getElementById('projectComplexity').value) || 1,
        
        // Research
        research_level_encoded: parseInt(document.getElementById('researchLevel').value) || 0,
        publications_count: parseInt(document.getElementById('publicationsCount').value) || 0,
        leadership_positions: parseInt(document.getElementById('leadershipPositions').value) || 0,
        communication_skills: parseInt(document.getElementById('communicationSkills').value) || 2,
        extracurriculars: document.getElementById('extracurriculars').value.trim(),
        extracurriculars_count: document.getElementById('extracurriculars').value.trim() ? 
            document.getElementById('extracurriculars').value.split(',').length : 0,
        
        // Career Goals
        target_career_encoded: parseInt(document.getElementById('targetCareer').value) || 0,
        career_tier: parseInt(document.getElementById('careerTier').value) || 1,
        salary_expectation_normalized: parseFloat(document.getElementById('salaryExpectation').value) / 100 || 0.1,
        preferred_location_encoded: parseInt(document.getElementById('preferredLocation').value) || 1,
        
        // For backward compatibility
        degree: document.getElementById('degree').selectedOptions[0]?.text.split(' ')[0] || '',
        specialization: document.getElementById('specialization').selectedOptions[0]?.text || ''
    };
    
    // Validation
    const errors = [];
    if (!educationData.degree_encoded) errors.push('Degree is required');
    if (!educationData.specialization_encoded) errors.push('Specialization is required');
    if (!educationData.cgpa || educationData.cgpa < 0 || educationData.cgpa > 10) {
        errors.push('CGPA must be between 0 and 10');
    }
    if (!educationData.graduation_year || educationData.graduation_year < 2000 || educationData.graduation_year > 2030) {
        errors.push('Graduation year must be between 2000 and 2030');
    }
    if (!educationData.coding_skills_encoded) errors.push('Coding skill level is required');
    if (!educationData.target_career_encoded) errors.push('Target career is required');
    
    if (errors.length > 0) {
        responseDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>Validation Errors</h5>
                ${errors.join('<br>')}
            </div>
        `;
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/education/add`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(educationData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            responseDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-check-circle me-2"></i>Career Profile Built Successfully!</h5>
                    
                    <div class="row mt-3">
                        <div class="col-md-6">
                            <strong>Academic Profile:</strong><br>
                            • ${data.profile.degree || 'Not set'} in ${data.profile.specialization || 'Not set'}<br>
                            • CGPA: ${data.profile.cgpa || 'Not set'}/10<br>
                            • Graduation: ${data.profile.graduation_year || 'Not set'}
                        </div>
                        <div class="col-md-6">
                            <strong>Skills & Experience:</strong><br>
                            • Internships: ${data.profile.internships_count || 0}<br>
                            • Projects: ${data.profile.projects_count || 0}<br>
                            • Coding Level: ${getSkillLevelText(data.profile.coding_skills_encoded)}
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <button onclick="showSection('predict')" class="btn btn-success">
                            <i class="fas fa-brain me-1"></i>Get Job Predictions Now
                        </button>
                        <button onclick="showSection('dashboard')" class="btn btn-outline-secondary ms-2">
                            Return to Dashboard
                        </button>
                    </div>
                </div>
            `;
            
            // Update local user data
            localStorage.setItem('user', JSON.stringify(data.profile));
            currentUser = data.profile;
            
            // Update dashboard
            await loadUserProfile();
            
        } else {
            throw new Error(data.message || 'Failed to save education data');
        }
    } catch (error) {
        console.error('❌ Education submission error:', error);
        responseDiv.innerHTML = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle me-2"></i>Profile Creation Failed</h5>
                ${error.message}
            </div>
        `;
    }
}

function getSkillLevelText(encoded) {
    switch(encoded) {
        case 1: return 'Beginner';
        case 2: return 'Intermediate';
        case 3: return 'Advanced';
        default: return 'Not specified';
    }
}

/* ============================================
   PREDICTION FUNCTIONS
============================================ */
async function getPrediction() {
    console.log('📊 Starting prediction process...');
    
    if (!currentUser) {
        await loadUserProfile();
    }
    
    // Check if user has completed education profile
    if (!currentUser.degree || !currentUser.specialization) {
        showAlert('Please complete your education profile first! Go to the Education section and fill out the form.', 'warning');
        showSection('education');
        return;
    }
    
    // Show loading
    const resultsDiv = document.getElementById('predictionResults');
    resultsDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h4>Analyzing Your Profile</h4>
            <p class="text-muted">Our AI is matching your skills with the best job opportunities...</p>
        </div>
    `;
    
    try {
        // Prepare data for ML model - Use encoded values from user profile
        // The backend will handle encoding if needed, but prefer encoded values
        const predictionData = {
            // Academic - Prefer encoded values, fallback to raw for encoding
            degree_encoded: currentUser.degree_encoded !== undefined ? currentUser.degree_encoded : null,
            specialization_encoded: currentUser.specialization_encoded !== undefined ? currentUser.specialization_encoded : null,
            degree: currentUser.degree || '',  // For encoding fallback
            specialization: currentUser.specialization || '',  // For encoding fallback
            cgpa: currentUser.cgpa || 0,
            cgpa_normalized: currentUser.cgpa_normalized !== undefined ? currentUser.cgpa_normalized : null,
            cgpa_category_encoded: currentUser.cgpa_category_encoded !== undefined ? currentUser.cgpa_category_encoded : null,
            graduation_year: currentUser.graduation_year || 2024,
            
            // Skills & Experience - Prefer encoded values
            coding_skills_encoded: currentUser.coding_skills_encoded !== undefined ? currentUser.coding_skills_encoded : null,
            coding_skills: currentUser.coding_skills || '',  // For encoding fallback
            total_experience: currentUser.total_experience || 0,
            projects_count: currentUser.projects_count || 0,
            internships_count: currentUser.internships_count || 0,
            certifications_count: currentUser.certifications_count || 0,
            experience_category_encoded: currentUser.experience_category_encoded !== undefined ? currentUser.experience_category_encoded : null,
            
            // Research
            research_level_encoded: currentUser.research_level_encoded !== undefined ? currentUser.research_level_encoded : 0,
            has_research: currentUser.has_research || false,
            publications_count: currentUser.publications_count || 0,
            
            // Extracurriculars - Send both count and string for flexibility
            extracurriculars_count: currentUser.extracurriculars_count !== undefined ? currentUser.extracurriculars_count : null,
            extracurriculars: currentUser.extracurriculars || '',  // For counting fallback
            leadership_positions: currentUser.leadership_positions || 0,
            
            // Project complexity - Prefer encoded
            project_complexity: currentUser.project_complexity !== undefined ? currentUser.project_complexity : 1,
            
            // Field courses
            field_courses: currentUser.field_courses || 0
        };
        
        console.log('📤 Sending to ML model:', predictionData);
        
        // Make prediction request
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(predictionData)
        });
        
        if (!response.ok) {
            throw new Error(`Prediction failed: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('📥 ML Response:', result);
        
        // Display results
        if (result.success && result.predictions && result.predictions.length > 0) {
            modelMetrics = result.model_metrics || null;
            displayPredictions(result.predictions, modelMetrics);
            predictionsCache = result.predictions;
            
            // Save to history
            savePredictionToHistory(result.predictions);
        } else {
            resultsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No predictions generated. Try adding more details to your education profile.
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Prediction error:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-times-circle me-2"></i>
                Failed to generate predictions: ${error.message}
            </div>
        `;
    }
}

function displayPredictions(predictions, metrics) {
    const resultsDiv = document.getElementById('predictionResults');
    
    let html = `
        <div class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Success!</strong> Found ${predictions.length} job roles matching your profile.
        </div>
        
        <div class="row">
    `;
    
    predictions.forEach((pred, index) => {
        const confidence = pred.confidence_percentage || (pred.confidence_score * 100) || 0;
        const confidenceClass = confidence >= 70 ? 'high' : confidence >= 50 ? 'medium' : 'low';
        
        html += `
            <div class="col-md-6 mb-4">
                <div class="card h-100 ${index === 0 ? 'border-primary border-3' : ''}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title mb-0">
                                ${index === 0 ? '🏆 ' : '🎯 '}${pred.job_role}
                                ${index === 0 ? '<span class="badge bg-success ms-2">Best Match</span>' : ''}
                            </h5>
                            <span class="badge bg-primary">#${index + 1}</span>
                        </div>
                        
                        <div class="mb-3">
                            <div class="d-flex justify-content-between mb-1">
                                <small>Suitability Score</small>
                                <small class="text-${confidenceClass}"><strong>${confidence.toFixed(1)}%</strong></small>
                            </div>
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar bg-${confidenceClass}" 
                                     style="width: ${confidence}%"></div>
                            </div>
                        </div>
                        
                        ${pred.required_skills && pred.required_skills.length > 0 ? `
                            <div class="mb-3">
                                <small class="text-muted">Key Skills Required:</small>
                                <div class="d-flex flex-wrap gap-1 mt-1">
                                    ${pred.required_skills.slice(0, 4).map(skill => 
                                        `<span class="badge bg-secondary">${skill}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${pred.salary_range ? `
                            <div class="mb-2">
                                <small class="text-muted">Expected Salary:</small>
                                <p class="mb-0"><strong>${pred.salary_range}</strong></p>
                            </div>
                        ` : ''}
                        
                        ${pred.growth_projection ? `
                            <div class="mb-2">
                                <small class="text-muted">Growth Potential:</small>
                                <div class="progress" style="height: 6px;">
                                    <div class="progress-bar bg-info" style="width: ${pred.growth_projection * 10}%"></div>
                                </div>
                                <small>${pred.growth_projection.toFixed(1)}/10</small>
                            </div>
                        ` : ''}
                        
                        ${metrics ? `
                            <div class="mb-2">
                                <small class="text-muted">Model Performance</small>
                                <div class="d-flex flex-wrap gap-2 mt-1">
                                    <span class="badge bg-light text-dark">Acc: ${(metrics.accuracy * 100).toFixed(1)}%</span>
                                    <span class="badge bg-light text-dark">F1: ${(metrics.f1 * 100).toFixed(1)}%</span>
                                    <span class="badge bg-light text-dark">Precision: ${(metrics.precision * 100).toFixed(1)}%</span>
                                    <span class="badge bg-light text-dark">Recall: ${(metrics.recall * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                        ` : ''}
                        
                        <div class="mt-3">
                            <button class="btn btn-outline-primary btn-sm" onclick="showPredictionDetails(${index})">
                                <i class="fas fa-info-circle me-1"></i> View Details
                            </button>
                            <button class="btn btn-outline-success btn-sm ms-2" onclick="savePrediction(${index})">
                                <i class="fas fa-bookmark me-1"></i> Save
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
        </div>
        
        <div class="mt-4 text-center">
            <button class="btn btn-primary" onclick="getPrediction()">
                <i class="fas fa-sync-alt me-1"></i> Regenerate Predictions
            </button>
            <button class="btn btn-outline-secondary ms-2" onclick="showSection('history')">
                <i class="fas fa-history me-1"></i> View History
            </button>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function showPredictionDetails(index) {
    if (!predictionsCache || !predictionsCache[index]) return;
    
    const pred = predictionsCache[index];
    const confidence = pred.confidence_percentage || (pred.confidence_score * 100) || 0;
    
    const modalContent = `
        <div class="modal-header">
            <h5 class="modal-title">${pred.job_role} - Detailed Analysis</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <div class="row">
                <div class="col-md-6">
                    <h6>Match Details</h6>
                    <p><strong>Suitability Score:</strong> ${confidence.toFixed(1)}%</p>
                    <p><strong>Rank:</strong> #${index + 1}</p>
                    <p><strong>Model Version:</strong> ${pred.model_version || 'v2.0'}</p>
                </div>
                <div class="col-md-6">
                    <h6>Career Information</h6>
                    ${pred.salary_range ? `<p><strong>Salary Range:</strong> ${pred.salary_range}</p>` : ''}
                    ${pred.growth_projection ? `<p><strong>Growth Projection:</strong> ${pred.growth_projection.toFixed(1)}/10</p>` : ''}
                </div>
            </div>
            
            ${pred.required_skills && pred.required_skills.length > 0 ? `
                <div class="mt-3">
                    <h6>Required Skills</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${pred.required_skills.map(skill => 
                            `<span class="badge bg-primary">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${pred.companies && pred.companies.length > 0 ? `
                <div class="mt-3">
                    <h6>Top Hiring Companies</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${pred.companies.map(company => 
                            `<span class="badge bg-success">${company}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${pred.learning_path && pred.learning_path.length > 0 ? `
                <div class="mt-3">
                    <h6>Recommended Learning Path</h6>
                    <ul class="list-group">
                        ${pred.learning_path.map(item => 
                            `<li class="list-group-item">${item}</li>`
                        ).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary" onclick="savePrediction(${index})">
                <i class="fas fa-bookmark me-1"></i> Save Recommendation
            </button>
        </div>
    `;
    
    showModal('Prediction Details', modalContent);
}

function savePrediction(index) {
    if (!predictionsCache || !predictionsCache[index]) return;
    
    const pred = predictionsCache[index];
    
    // Get saved predictions from localStorage
    let savedPredictions = JSON.parse(localStorage.getItem('savedPredictions') || '[]');
    
    // Check if already saved
    const alreadySaved = savedPredictions.some(saved => 
        saved.job_role === pred.job_role && 
        saved.timestamp === new Date().toISOString().split('T')[0]
    );
    
    if (!alreadySaved) {
        savedPredictions.push({
            job_role: pred.job_role,
            confidence: pred.confidence_percentage || (pred.confidence_score * 100),
            timestamp: new Date().toISOString().split('T')[0],
            date_saved: new Date().toISOString()
        });
        
        localStorage.setItem('savedPredictions', JSON.stringify(savedPredictions));
        showAlert('Prediction saved to your favorites!', 'success');
    } else {
        showAlert('This prediction is already saved.', 'info');
    }
}

function savePredictionToHistory(predictions) {
    if (!predictions || predictions.length === 0) return;
    
    // Get prediction history from localStorage
    let predictionHistory = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
    
    // Add new prediction
    predictionHistory.unshift({
        date: new Date().toISOString(),
        predictions: predictions.map(p => ({
            job_role: p.job_role,
            confidence: p.confidence_percentage || (p.confidence_score * 100)
        })),
        top_prediction: predictions[0].job_role,
        top_confidence: predictions[0].confidence_percentage || (predictions[0].confidence_score * 100)
    });
    
    // Keep only last 20 predictions
    if (predictionHistory.length > 20) {
        predictionHistory = predictionHistory.slice(0, 20);
    }
    
    localStorage.setItem('predictionHistory', JSON.stringify(predictionHistory));
    
    // Update user's prediction count
    if (currentUser) {
        currentUser.prediction_count = (currentUser.prediction_count || 0) + 1;
        localStorage.setItem('user', JSON.stringify(currentUser));
    }
}

/* ============================================
   HISTORY & DASHBOARD FUNCTIONS
============================================ */
function loadDashboardData() {
    loadRecentPredictions();
    loadRecentActivity();
    loadInsights(); // new Milestone 4 insights
}

async function loadInsights() {
    try {
        // Degree -> top roles
        const degreeRes = await fetch(`${API_BASE}/insights/degree-jobs`, { headers: getAuthHeaders() });
        if (degreeRes.ok) {
            const data = await degreeRes.json();
            renderDegreeInsights(data.top_roles || []);
        }
        
        // Domain distribution
        const domainRes = await fetch(`${API_BASE}/insights/job-domains`, { headers: getAuthHeaders() });
        if (domainRes.ok) {
            const data = await domainRes.json();
            renderDomainInsights(data.distribution || []);
        }
        
        // User context
        const ctxRes = await fetch(`${API_BASE}/insights/user-context`, { headers: getAuthHeaders() });
        if (ctxRes.ok) {
            const data = await ctxRes.json();
            renderContextInsights(data);
        }
    } catch (err) {
        console.error('Insights load error', err);
    }
}

function renderDegreeInsights(items) {
    const el = document.getElementById('insightDegreeRoles');
    const canvas = document.getElementById('insightDegreeRolesChart');
    if (!el) return;
    if (!items.length) {
        el.innerHTML = '<p class="text-muted small mb-0">Not enough data yet.</p>';
        if (canvas) canvas.replaceChildren();
        return;
    }
    if (canvas) {
        if (window.degreeRolesChart) {
            window.degreeRolesChart.destroy();
        }
        const labels = items.map(i => i.job_role);
        const counts = items.map(i => i.count);
        window.degreeRolesChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Roles',
                    data: counts,
                    backgroundColor: '#667eea'
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }
    el.innerHTML = items.map(item => `
        <div class="d-flex justify-content-between small py-1 border-bottom">
            <span>${item.job_role}</span>
            <strong>${item.count}</strong>
        </div>
    `).join('');
}

function renderDomainInsights(items) {
    const el = document.getElementById('insightDomains');
    const canvas = document.getElementById('insightDomainsChart');
    if (!el) return;
    if (!items.length) {
        el.innerHTML = '<p class="text-muted small mb-0">No domain data yet.</p>';
        if (canvas) canvas.replaceChildren();
        return;
    }
    if (canvas) {
        if (window.domainChart) {
            window.domainChart.destroy();
        }
        const labels = items.map(i => i.domain);
        const counts = items.map(i => i.count);
        const colors = ['#667eea','#4bc0c0','#ffcd56','#ff6384','#36a2eb','#2ecc71'];
        window.domainChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data: counts,
                    backgroundColor: colors.slice(0, counts.length)
                }]
            },
            options: { responsive: true }
        });
    }
    el.innerHTML = items.map(item => `
        <div class="d-flex justify-content-between align-items-center small py-1 border-bottom">
            <span>${item.domain}</span>
            <span class="badge bg-primary-subtle text-primary">${item.percentage}%</span>
        </div>
    `).join('');
}

function renderContextInsights(data) {
    const el = document.getElementById('insightContext');
    if (!el) return;
    if (!data || !data.similar_users_outcomes || !data.similar_users_outcomes.length) {
        el.innerHTML = '<p class="text-muted small mb-0">Not enough similar profiles yet.</p>';
        return;
    }
    const outcomes = data.similar_users_outcomes.map(item => `
        <div class="d-flex justify-content-between small py-1 border-bottom">
            <span>${item.role}</span>
            <strong>${item.percentage}%</strong>
        </div>
    `).join('');
    const reasons = (data.why_suggested || []).map(r => `<li class="small">${r}</li>`).join('');
    el.innerHTML = `
        <div class="mb-2">${outcomes}</div>
        ${reasons ? `<ul class="mb-0">${reasons}</ul>` : ''}
    `;
}

async function loadRecentPredictions() {
    try {
        const response = await fetch(`${API_BASE}/predictions`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.predictions && data.predictions.length > 0) {
                displayRecentPredictions(data.predictions.slice(0, 3));
                return;
            }
        }
        
        // Fallback to localStorage
        const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
        if (history.length > 0) {
            displayRecentPredictions(history[0].predictions || []);
        } else {
            document.getElementById('recentPredictions').innerHTML = `
                <p class="text-muted">No predictions yet. <a href="#" onclick="showSection('predict')">Get your first prediction!</a></p>
            `;
        }
    } catch (error) {
        console.error('❌ Failed to load recent predictions:', error);
    }
}

function displayRecentPredictions(predictions) {
    const container = document.getElementById('recentPredictions');
    if (!container) return;
    
    if (!predictions || predictions.length === 0) {
        container.innerHTML = `
            <p class="text-muted">No recent predictions. <a href="#" onclick="showSection('predict')">Generate one now!</a></p>
        `;
        return;
    }
    
    container.innerHTML = predictions.map(pred => `
        <div class="card mb-2">
            <div class="card-body py-2">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${pred.job_role}</strong>
                        <div class="text-muted small">
                            ${new Date(pred.created_at || new Date()).toLocaleDateString()}
                        </div>
                    </div>
                    <span class="badge ${getConfidenceBadgeClass(pred.confidence_score || (pred.confidence / 100))}">
                        ${(pred.confidence_score ? (pred.confidence_score * 100) : pred.confidence || 0).toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `).join('');
}

function loadRecentActivity() {
    // This would normally fetch from API
    const activity = [
        { action: 'Updated education profile', time: '2 hours ago' },
        { action: 'Generated job predictions', time: 'Yesterday' },
        { action: 'Completed profile setup', time: '2 days ago' }
    ];
    
    // Display activity
    const activityElement = document.getElementById('recentActivity');
    if (activityElement) {
        activityElement.innerHTML = activity.map(item => `
            <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
                <div>
                    <i class="fas fa-circle text-success me-2" style="font-size: 8px;"></i>
                    ${item.action}
                </div>
                <small class="text-muted">${item.time}</small>
            </div>
        `).join('');
    }
}

function loadPredictionHistory() {
    const container = document.getElementById('predictionHistory');
    if (!container) return;
    
    const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
    
    if (history.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No prediction history found. Generate your first prediction to get started!
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-history me-2"></i>Prediction History</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Top Prediction</th>
                                <th>Confidence</th>
                                <th>Total Predictions</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${history.map((item, index) => `
                                <tr>
                                    <td>${new Date(item.date).toLocaleDateString()}</td>
                                    <td><strong>${item.top_prediction}</strong></td>
                                    <td>
                                        <span class="badge ${getConfidenceBadgeClass(item.top_confidence / 100)}">
                                            ${item.top_confidence.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td>${item.predictions.length}</td>
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" 
                                                onclick="viewHistoryDetails(${index})">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function viewHistoryDetails(index) {
    const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
    if (!history[index]) return;
    
    const item = history[index];
    
    const modalContent = `
        <div class="modal-header">
            <h5 class="modal-title">Prediction from ${new Date(item.date).toLocaleDateString()}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
            <h6>Top ${item.predictions.length} Recommendations:</h6>
            ${item.predictions.map((pred, i) => `
                <div class="card mb-2">
                    <div class="card-body py-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>#${i + 1} ${pred.job_role}</strong>
                            </div>
                            <span class="badge ${getConfidenceBadgeClass(pred.confidence / 100)}">
                                ${pred.confidence.toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
    `;
    
    showModal('Prediction History Details', modalContent);
}

/* ============================================
   SECTION MANAGEMENT
============================================ */
function showSection(sectionName) {
    // Hide all sections
    const sections = ['dashboard', 'education', 'profile', 'predict', 'history'];
    sections.forEach(section => {
        const element = document.getElementById(`${section}Section`);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Show selected section
    const targetSection = document.getElementById(`${sectionName}Section`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(sectionName)) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'history':
            loadPredictionHistory();
            break;
        case 'education':
            prefillEnhancedEducationForm(currentUser);
            updateProgress();
            break;
        case 'predict':
            // Clear previous results when entering prediction section
            document.getElementById('predictionResults').innerHTML = '';
            break;
    }
}

/* ============================================
   PASSWORD MANAGEMENT
============================================ */
function validateNewPassword() {
    const password = document.getElementById('newPassword').value;
    const strength = checkPasswordStrength(password);
    const output = document.getElementById('newPasswordStrength');
    
    if (output) {
        output.innerHTML = `
            <div class="progress mb-2" style="height: 5px;">
                <div class="progress-bar ${strength.strength >= 4 ? 'bg-success' : strength.strength >= 3 ? 'bg-warning' : 'bg-danger'}" 
                     style="width: ${(strength.strength / 5) * 100}%"></div>
            </div>
            <small class="${strength.isValid ? 'text-success' : 'text-danger'}">${strength.message}</small>
        `;
    }
}

function validatePasswordMatch() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const output = document.getElementById('passwordMatch');
    
    if (!output) return;
    
    if (!confirmPassword) {
        output.innerHTML = '';
        return;
    }
    
    output.innerHTML = newPassword === confirmPassword 
        ? '<small class="text-success">✓ Passwords match</small>' 
        : '<small class="text-danger">✗ Passwords do not match</small>';
}

function checkPasswordStrength(password) {
    const constraints = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    const strength = Object.values(constraints).filter(Boolean).length;
    const messages = [];
    
    if (!constraints.length) messages.push('at least 8 characters');
    if (!constraints.uppercase) messages.push('one uppercase letter');
    if (!constraints.lowercase) messages.push('one lowercase letter');
    if (!constraints.number) messages.push('one number');
    if (!constraints.special) messages.push('one special character');
    
    return {
        strength,
        isValid: strength === 5,
        message: messages.length ? `Needs: ${messages.join(', ')}` : 'Strong password'
    };
}

async function changePassword(e) {
    e.preventDefault();
    
    try {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // Validation
        if (newPassword !== confirmPassword) {
            showAlert('Passwords do not match!', 'danger');
            return;
        }
        
        const strength = checkPasswordStrength(newPassword);
        if (!strength.isValid) {
            showAlert(strength.message, 'danger');
            return;
        }
        
        const response = await fetch(`${API_BASE}/change-password`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Password changed successfully!', 'success');
            document.getElementById('changePasswordForm').reset();
            document.getElementById('newPasswordStrength').innerHTML = '';
            document.getElementById('passwordMatch').innerHTML = '';
        } else {
            throw new Error(data.message || 'Failed to change password');
        }
    } catch (error) {
        console.error('❌ Change password error:', error);
        showAlert(`Error changing password: ${error.message}`, 'danger');
    }
}

/* ============================================
   UTILITY FUNCTIONS
============================================ */
function getAuthHeaders(contentType = 'application/json') {
    const token = localStorage.getItem('token');
    const headers = {};
    
    if (contentType) {
        headers['Content-Type'] = contentType;
    }
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    document.querySelectorAll('.alert-fixed').forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-fixed`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    const icons = {
        'success': '✅',
        'danger': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    alertDiv.innerHTML = `
        <strong>${icons[type] || ''}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showModal(title, content) {
    // Remove existing modal
    const existingModal = document.getElementById('dynamicModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal
    const modalDiv = document.createElement('div');
    modalDiv.id = 'dynamicModal';
    modalDiv.className = 'modal fade';
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                ${content}
            </div>
        </div>
    `;
    
    document.body.appendChild(modalDiv);
    
    // Show modal
    const modal = new bootstrap.Modal(modalDiv);
    modal.show();
    
    // Cleanup on hide
    modalDiv.addEventListener('hidden.bs.modal', function() {
        modalDiv.remove();
    });
}

function getConfidenceBadgeClass(score) {
    if (score >= 0.8) return 'bg-success';
    if (score >= 0.6) return 'bg-info';
    if (score >= 0.4) return 'bg-warning';
    return 'bg-secondary';
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('savedPredictions');
        localStorage.removeItem('predictionHistory');
        window.location.href = 'index.html';
    }
}

/* ============================================
   DEBUG HELPER (optional)
============================================ */
function debugDashboard() {
    console.log('=== DASHBOARD DEBUG INFO ===');
    console.log('Current User:', currentUser);
    console.log('Token exists:', !!localStorage.getItem('token'));
    console.log('Predictions Cache:', predictionsCache);
    console.log('Saved Predictions:', JSON.parse(localStorage.getItem('savedPredictions') || '[]'));
    console.log('Prediction History:', JSON.parse(localStorage.getItem('predictionHistory') || '[]'));
}
/* ============================================
   FEEDBACK FUNCTIONS
============================================ */
let feedbackType = 'prediction';

async function loadFeedbackData() {
    try {
        // Load user feedback stats
        const response = await fetch(`${API_BASE}/feedback/user/stats`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                updateFeedbackStats(data.stats);
            }
        }
        
        // Load user's predictions for feedback
        await loadUserPredictionsForFeedback();
        
        // Load feedback history
        await loadUserFeedbackHistory();
        
    } catch (error) {
        console.error('Error loading feedback data:', error);
    }
}

function updateFeedbackStats(stats) {
    document.getElementById('feedbackCount').textContent = stats.feedback_count || 0;
    document.getElementById('avgRating').textContent = stats.avg_rating_given || '0.0';
    
    // Calculate prediction feedback count
    const predictionFeedback = stats.prediction_feedback_distribution?.reduce((sum, item) => sum + item.count, 0) || 0;
    document.getElementById('predictionFeedback').textContent = predictionFeedback;
    
    // Calculate system feedback (total - prediction)
    const systemFeedback = (stats.feedback_count || 0) - predictionFeedback;
    document.getElementById('systemFeedback').textContent = systemFeedback > 0 ? systemFeedback : 0;
}

async function loadUserPredictionsForFeedback() {
    try {
        const response = await fetch(`${API_BASE}/predictions`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.predictions) {
                populatePredictionDropdown(data.predictions);
            }
        }
    } catch (error) {
        console.error('Error loading predictions for feedback:', error);
    }
}

function populatePredictionDropdown(predictions) {
    const select = document.getElementById('feedbackPredictionSelect');
    if (!select) return;
    
    // Clear existing options except the first one
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Add prediction options
    predictions.slice(0, 10).forEach(pred => {
        const option = document.createElement('option');
        option.value = pred.id;
        option.textContent = `${pred.job_role} (${new Date(pred.created_at).toLocaleDateString()})`;
        select.appendChild(option);
    });
    
    if (predictions.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No predictions available';
        option.disabled = true;
        select.appendChild(option);
    }
}

async function loadUserFeedbackHistory() {
    try {
        const response = await fetch(`${API_BASE}/feedback/mine`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.feedback) {
                displayFeedbackHistory(data.feedback);
                populateFeedbackTable(data.feedback);
            }
        }
    } catch (error) {
        console.error('Error loading feedback history:', error);
    }
}

function displayFeedbackHistory(feedbackList) {
    const container = document.getElementById('feedbackHistory');
    if (!container) return;
    
    if (!feedbackList || feedbackList.length === 0) {
        container.innerHTML = '<p class="text-muted">No feedback submitted yet.</p>';
        return;
    }
    
    // Show only last 5 feedback items
    const recentFeedback = feedbackList.slice(0, 5);
    
    container.innerHTML = recentFeedback.map(fb => {
        const stars = '★'.repeat(fb.rating) + '☆'.repeat(5 - fb.rating);
        const date = new Date(fb.created_at).toLocaleDateString();
        
        return `
            <div class="border-bottom pb-2 mb-2">
                <div class="d-flex justify-content-between">
                    <strong class="${getRatingColorClass(fb.rating)}">${stars}</strong>
                    <small class="text-muted">${date}</small>
                </div>
                <div class="small">
                    ${fb.feedback_type === 'prediction' ? 
                        `<span class="badge bg-primary">Prediction</span>` : 
                        `<span class="badge bg-success">System</span>`}
                    ${fb.comment ? `<p class="mt-1 mb-0">${fb.comment.substring(0, 100)}${fb.comment.length > 100 ? '...' : ''}</p>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function populateFeedbackTable(feedbackList) {
    const tbody = document.getElementById('feedbackTableBody');
    if (!tbody) return;
    
    if (!feedbackList || feedbackList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">No feedback submitted yet</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = feedbackList.map(fb => {
        const stars = '★'.repeat(fb.rating) + '☆'.repeat(5 - fb.rating);
        const date = new Date(fb.created_at).toLocaleDateString();
        
        return `
            <tr>
                <td>${date}</td>
                <td>
                    <span class="badge ${fb.feedback_type === 'prediction' ? 'bg-primary' : 'bg-success'}">
                        ${fb.feedback_type || 'general'}
                    </span>
                </td>
                <td>
                    <span class="${getRatingColorClass(fb.rating)}">${stars}</span>
                    <br><small>(${fb.rating}/5)</small>
                </td>
                <td>
                    ${fb.prediction_id ? 
                        `<span class="badge bg-info">ID: ${fb.prediction_id}</span>` : 
                        '<span class="text-muted">-</span>'
                    }
                </td>
                <td>
                    ${fb.comment ? 
                        `<small>${fb.comment.substring(0, 50)}${fb.comment.length > 50 ? '...' : ''}</small>` : 
                        '<span class="text-muted">No comment</span>'
                    }
                </td>
                <td>
                    ${fb.was_correct !== null && fb.was_correct !== undefined ?
                        (fb.was_correct ? 
                            '<span class="badge bg-success">Yes</span>' : 
                            '<span class="badge bg-danger">No</span>') :
                        '<span class="text-muted">-</span>'
                    }
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewFeedbackDetail(${fb.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function getRatingColorClass(rating) {
    switch(rating) {
        case 1: return 'text-danger';
        case 2: return 'text-warning';
        case 3: return 'text-info';
        case 4: return 'text-primary';
        case 5: return 'text-success';
        default: return 'text-muted';
    }
}

function showFeedbackType(type) {
    feedbackType = type;
    
    // Update button states
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    if (type === 'prediction') {
        document.querySelector('.btn-outline-primary').classList.add('active');
        document.getElementById('predictionFeedbackCard').style.display = 'block';
        document.getElementById('systemFeedbackCard').style.display = 'none';
    } else {
        document.querySelector('.btn-outline-success').classList.add('active');
        document.getElementById('predictionFeedbackCard').style.display = 'none';
        document.getElementById('systemFeedbackCard').style.display = 'block';
    }
}

// Initialize star rating system
function initStarRating() {
    // Setup star rating for prediction feedback
    const predictionStars = document.querySelectorAll('#predictionFeedbackCard .star');
    predictionStars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));
            document.getElementById('predictionRating').value = value;
            
            // Update star display
            predictionStars.forEach(s => {
                s.classList.remove('active');
                if (parseInt(s.getAttribute('data-value')) <= value) {
                    s.classList.add('active');
                }
            });
            
            // Update rating text
            const ratingText = document.getElementById('ratingText');
            ratingText.textContent = `${value} star${value > 1 ? 's' : ''}`;
            ratingText.className = getRatingColorClass(value);
        });
    });
    
    // Setup star rating for system feedback
    const systemStars = document.querySelectorAll('#systemFeedbackCard .star');
    systemStars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));
            document.getElementById('systemRating').value = value;
            
            // Update star display
            systemStars.forEach(s => {
                s.classList.remove('active');
                if (parseInt(s.getAttribute('data-value')) <= value) {
                    s.classList.add('active');
                }
            });
            
            // Update rating text
            const ratingText = document.getElementById('systemRatingText');
            ratingText.textContent = `${value} star${value > 1 ? 's' : ''}`;
            ratingText.className = getRatingColorClass(value);
        });
    });
}

// Handle prediction feedback submission
document.getElementById('predictionFeedbackForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const predictionId = document.getElementById('feedbackPredictionSelect').value;
    const rating = parseInt(document.getElementById('predictionRating').value);
    const comment = document.getElementById('predictionComment').value;
    const wasCorrect = document.querySelector('input[name="wasCorrect"]:checked')?.value;
    const improvements = document.getElementById('predictionImprovements').value;
    
    if (!predictionId || rating < 1 || rating > 5) {
        showAlert('Please select a prediction and provide a rating (1-5 stars)', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/feedback/prediction`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                prediction_id: parseInt(predictionId),
                rating: rating,
                comment: comment,
                was_correct: wasCorrect === 'true',
                improvement_suggestions: improvements
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Prediction feedback submitted successfully!', 'success');
            
            // Reset form
            this.reset();
            document.querySelectorAll('#predictionFeedbackCard .star').forEach(star => {
                star.classList.remove('active');
            });
            document.getElementById('ratingText').textContent = 'Not rated';
            document.getElementById('ratingText').className = '';
            
            // Reload feedback data
            await loadFeedbackData();
        } else {
            throw new Error(data.message || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error submitting prediction feedback:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    }
});

// Handle system feedback submission
document.getElementById('systemFeedbackForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const rating = parseInt(document.getElementById('systemRating').value);
    const comment = document.getElementById('systemComment').value;
    const improvements = document.getElementById('systemImprovements').value;
    
    if (rating < 1 || rating > 5) {
        showAlert('Please provide a rating (1-5 stars)', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/feedback/system`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                rating: rating,
                comment: comment,
                improvement_suggestions: improvements
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('System feedback submitted successfully! Thank you!', 'success');
            
            // Reset form
            this.reset();
            document.querySelectorAll('#systemFeedbackCard .star').forEach(star => {
                star.classList.remove('active');
            });
            document.getElementById('systemRatingText').textContent = 'Not rated';
            document.getElementById('systemRatingText').className = '';
            
            // Reload feedback data
            await loadFeedbackData();
        } else {
            throw new Error(data.message || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error submitting system feedback:', error);
        showAlert(`Error: ${error.message}`, 'danger');
    }
});

async function viewFeedbackDetail(feedbackId) {
    try {
        const response = await fetch(`${API_BASE}/feedback/mine`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.feedback) {
                const feedback = data.feedback.find(f => f.id === feedbackId);
                if (feedback) {
                    showFeedbackDetailModal(feedback);
                }
            }
        }
    } catch (error) {
        console.error('Error viewing feedback detail:', error);
        showAlert('Error loading feedback details', 'danger');
    }
}

function showFeedbackDetailModal(feedback) {
    const stars = '★'.repeat(feedback.rating) + '☆'.repeat(5 - feedback.rating);
    const date = new Date(feedback.created_at).toLocaleString();
    
    const modalContent = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Feedback Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Feedback Information</h6>
                            <p><strong>Type:</strong> 
                                <span class="badge ${feedback.feedback_type === 'prediction' ? 'bg-primary' : 'bg-success'}">
                                    ${feedback.feedback_type || 'general'}
                                </span>
                            </p>
                            <p><strong>Rating:</strong> 
                                <span class="${getRatingColorClass(feedback.rating)}">
                                    ${stars} (${feedback.rating}/5)
                                </span>
                            </p>
                            <p><strong>Submitted:</strong> ${date}</p>
                            ${feedback.prediction_id ? 
                                `<p><strong>Prediction ID:</strong> ${feedback.prediction_id}</p>` : 
                                ''
                            }
                            ${feedback.was_correct !== null && feedback.was_correct !== undefined ?
                                `<p><strong>Was Prediction Correct:</strong> 
                                    ${feedback.was_correct ? 
                                        '<span class="badge bg-success">Yes</span>' : 
                                        '<span class="badge bg-danger">No</span>'
                                    }
                                </p>` : 
                                ''
                            }
                        </div>
                        
                        <div class="col-md-6">
                            ${feedback.comment ? `
                                <h6>Comments</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p class="mb-0">${feedback.comment}</p>
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${feedback.improvement_suggestions ? `
                                <h6 class="mt-3">Improvement Suggestions</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p class="mb-0">${feedback.improvement_suggestions}</p>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    showModal('Feedback Details', modalContent);
}

// Update the showSection function to include feedback section
function showSection(sectionName) {
    // Hide all sections
    const sections = ['dashboard', 'education', 'profile', 'predict', 'history', 'feedback'];
    sections.forEach(section => {
        const element = document.getElementById(`${section}Section`);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Show selected section
    const targetSection = document.getElementById(`${sectionName}Section`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick') && link.getAttribute('onclick').includes(sectionName)) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'history':
            loadPredictionHistory();
            break;
        case 'education':
            prefillEnhancedEducationForm(currentUser);
            updateProgress();
            break;
        case 'predict':
            document.getElementById('predictionResults').innerHTML = '';
            break;
        case 'feedback':
            loadFeedbackData();
            initStarRating();
            showFeedbackType('prediction');
            break;
    }
}

// Initialize feedback when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add this to your existing initialization
    setTimeout(() => {
        initStarRating();
    }, 1000);
});

// """new code ends here"""

// Make debug function available globally
window.debugDashboard = debugDashboard;

// Export logout for use in HTML
window.logout = logout;
window.showSection = showSection;
window.getPrediction = getPrediction;