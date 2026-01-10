
const API_BASE = 'http://localhost:5000/api';

let currentPage = 1;
const usersPerPage = 10;
let predictionsPage = 1;
const predictionsPerPage = 20;

// Fix localStorage data format on page load
function fixLocalStorageData() {
    // Check if role/user_id are missing but user object exists
    if (!localStorage.getItem('role') && localStorage.getItem('user')) {
        try {
            const userData = JSON.parse(localStorage.getItem('user'));
            if (userData) {
                // Fix the missing items
                localStorage.setItem('role', userData.role || 'user');
                localStorage.setItem('user_id', userData.id || '');
                localStorage.setItem('user_name', userData.name || '');
                localStorage.setItem('user_email', userData.email || '');
                
                console.log('Fixed localStorage format automatically');
                console.log('Role set to:', userData.role);
            }
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Fix localStorage data first
    fixLocalStorageData();
    
    // Check if user is admin
    const token = localStorage.getItem('token');
    let role = localStorage.getItem('role');
    
    if (!token) {
        alert('Authentication required! Please log in.');
        window.location.href = 'index.html';
        return;
    }
    
    if (role !== 'admin') {
        alert('Admin access required! You need administrator privileges.');
        window.location.href = 'dashboard.html';
        return;
    }

    // Display admin name
    const userName = localStorage.getItem('user_name') || 'Admin';
    document.getElementById('adminName').textContent = userName;
    
    // Load dashboard data
    loadDashboardStats();
    loadUsers();
    
    // Setup search functionality for users
    document.getElementById('userSearch').addEventListener('input', function(e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            currentPage = 1;
            loadUsers();
        }, 500);
    });
    
    // Setup search functionality for predictions
    document.getElementById('predictionSearch').addEventListener('input', function(e) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            predictionsPage = 1;
            loadPredictions();
        }, 500);
    });
    
    // Setup filter for predictions
    document.getElementById('predictionFilter').addEventListener('change', function() {
        predictionsPage = 1;
        loadPredictions();
    });
    
    // Auto-load predictions if on predictions section
    if (document.getElementById('predictionsSection').style.display !== 'none') {
        loadPredictions();
    }
});

function loadDashboardStats() {
    const token = localStorage.getItem('token');
    
    fetch(`${API_BASE}/admin/users?per_page=1000`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.users) {
            const totalUsers = data.users.length;
            const adminUsers = data.users.filter(u => u.role === 'admin').length;
            const today = new Date().toISOString().split('T')[0];
            const todayUsers = data.users.filter(u => u.created_at && u.created_at.startsWith(today)).length;
            
            document.getElementById('totalUsers').textContent = totalUsers;
            document.getElementById('activeAdmins').textContent = adminUsers;
            document.getElementById('todayUsers').textContent = todayUsers;
            
            // Load recent activity
            loadRecentActivity(data.users);
            loadModelMetrics();
            loadDatasetStats();
        }
    })
    .catch(error => {
        console.error('Error loading stats:', error);
        document.getElementById('totalUsers').textContent = '0';
        document.getElementById('activeAdmins').textContent = '0';
        document.getElementById('todayUsers').textContent = '0';
    });
}

let adminPerfChart = null;
function loadModelMetrics() {
    const token = localStorage.getItem('token');
    fetch(`${API_BASE}/admin/model-metrics`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => {
        const canvas = document.getElementById('adminModelPerformance');
        const metricsDiv = document.getElementById('adminModelMetrics');
        if (!canvas) return;
        const labels = Object.keys(data.metrics || {});
        const values = Object.values(data.metrics || {}).map(v => Math.round((v || 0) * 100));
        if (adminPerfChart) adminPerfChart.destroy();
        adminPerfChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Model Metrics (%)',
                    data: values,
                    backgroundColor: '#667eea'
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
        if (metricsDiv) {
            metricsDiv.innerHTML = `Acc: ${values[0] || 0}%, F1: ${values[1] || 0}%, Precision: ${values[2] || 0}%, Recall: ${values[3] || 0}%`;
        }
    })
    .catch(err => console.error('model metrics load error', err));
}

function loadDatasetStats() {
    const token = localStorage.getItem('token');
    fetch(`${API_BASE}/admin/dataset-stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById('adminDatasetStats');
        if (!el) return;
        if (!data.success || !data.roles) {
            el.innerHTML = '<span class="text-danger">Failed to load dataset stats</span>';
            return;
        }
        const top = data.roles.slice(0, 10).map(r => `
            <div class="d-flex justify-content-between border-bottom py-1">
                <span>${r.job_role}</span>
                <span>${r.count} (${r.percentage}%)</span>
            </div>
        `).join('');
        el.innerHTML = `
            <div class="mb-2">Total labelled roles: ${data.total}</div>
            ${top}
        `;
    })
    .catch(err => {
        console.error('dataset stats load error', err);
        const el = document.getElementById('adminDatasetStats');
        if (el) el.innerHTML = '<span class="text-danger">Error loading dataset stats</span>';
    });
}

function loadUsers() {
    const token = localStorage.getItem('token');
    const search = document.getElementById('userSearch').value;
    
    fetch(`${API_BASE}/admin/users?page=${currentPage}&per_page=${usersPerPage}&search=${encodeURIComponent(search)}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.users) {
            displayUsers(data.users);
            updatePagination(data);
        }
    })
    .catch(error => {
        console.error('Error loading users:', error);
        document.getElementById('usersTable').innerHTML = 
            '<tr><td colspan="7" class="text-center text-danger">Error loading users: ' + error.message + '</td></tr>';
    });
}

function displayUsers(users) {
    const tbody = document.getElementById('usersTable');
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No users found</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>
                <strong>${user.name || 'Unknown'}</strong>
                ${user.role === 'admin' ? '<i class="fas fa-crown text-warning ms-1" title="Admin"></i>' : ''}
            </td>
            <td>${user.email || 'No email'}</td>
            <td>
                <span class="badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}">
                    ${user.role || 'user'}
                </span>
            </td>
            <td>${user.degree || 'Not set'}</td>
            <td>${user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewUserDetails(${user.id})" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning" onclick="editUserRole(${user.id})" title="Edit Role">
                    <i class="fas fa-edit"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function updatePagination(data) {
    const pagination = document.getElementById('pagination');
    const info = document.getElementById('paginationInfo');
    
    if (!data || !data.users) {
        info.textContent = 'Showing 0 users';
        pagination.innerHTML = '';
        return;
    }
    
    info.textContent = `Showing ${data.users.length} of ${data.total || 0} users`;
    
    let paginationHTML = '';
    const totalPages = data.pages || 1;
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Previous</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        paginationHTML += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Next</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHTML;
}

function changePage(page) {
    if (page < 1) return;
    currentPage = page;
    loadUsers();
}

function viewUserDetails(userId) {
    const token = localStorage.getItem('token');
    
    fetch(`${API_BASE}/admin/users/${userId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.user) {
            const user = data.user;
            const modalContent = document.getElementById('userDetailContent');
            
            modalContent.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Personal Information</h6>
                        <p><strong>Name:</strong> ${user.name}</p>
                        <p><strong>Email:</strong> ${user.email}</p>
                        <p><strong>Role:</strong> <span class="badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}">${user.role}</span></p>
                        <p><strong>Joined:</strong> ${new Date(user.created_at).toLocaleString()}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Education Details</h6>
                        <p><strong>Degree:</strong> ${user.degree || 'Not set'}</p>
                        <p><strong>Specialization:</strong> ${user.specialization || 'Not set'}</p>
                        <p><strong>CGPA:</strong> ${user.cgpa || 'Not set'}</p>
                        <p><strong>University:</strong> ${user.university || 'Not set'}</p>
                    </div>
                </div>
                
                <div class="mt-4">
                    <h6>Prediction History (${user.prediction_count || 0} predictions)</h6>
                    ${user.predictions && user.predictions.length > 0 ? 
                        user.predictions.map(pred => `
                            <div class="card mb-2">
                                <div class="card-body py-2">
                                    <div class="d-flex justify-content-between">
                                        <strong>${pred.job_role}</strong>
                                        <span class="badge bg-primary">${pred.confidence_score}%</span>
                                    </div>
                                    <small class="text-muted">${new Date(pred.created_at).toLocaleString()}</small>
                                </div>
                            </div>
                        `).join('') : 
                        '<p class="text-muted">No predictions yet</p>'
                    }
                </div>
            `;
            
            new bootstrap.Modal(document.getElementById('userDetailModal')).show();
        }
    })
    .catch(error => {
        alert('Error loading user details: ' + error.message);
    });
}

function editUserRole(userId) {
    const newRole = prompt('Enter new role (user/admin):');
    if (newRole && ['user', 'admin'].includes(newRole)) {
        const token = localStorage.getItem('token');
        
        fetch(`${API_BASE}/admin/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ role: newRole })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert('User role updated successfully!');
                loadUsers();
                loadDashboardStats();
            } else {
                alert(data.message || 'Error updating role');
            }
        })
        .catch(error => {
            alert('Error updating user role: ' + error.message);
        });
    }
}

function loadRecentActivity(users) {
    const activityDiv = document.getElementById('recentActivity');
    
    if (!users || users.length === 0) {
        activityDiv.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
        return;
    }
    
    // Sort users by creation date (newest first) and take top 5
    const recentUsers = users
        .filter(u => u.created_at)
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    
    activityDiv.innerHTML = recentUsers.map(user => `
        <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-2">
            <div>
                <strong>${user.name || 'Unknown User'}</strong> 
                <span class="text-muted">joined</span>
                <small class="text-muted">${new Date(user.created_at).toLocaleDateString()}</small>
            </div>
            <span class="badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}">
                ${user.role || 'user'}
            </span>
        </div>
    `).join('');
}

// Load predictions
function loadPredictions() {
    console.log('Loading predictions...');
    
    const token = localStorage.getItem('token');
    const search = document.getElementById('predictionSearch').value;
    const filter = document.getElementById('predictionFilter').value;
    
    // Check if user is admin
    const role = localStorage.getItem('role');
    if (role !== 'admin') {
        console.error('Non-admin trying to access predictions');
        document.getElementById('predictionsTable').innerHTML = 
            '<tr><td colspan="7" class="text-center text-danger">Admin access required</td></tr>';
        return;
    }
    
    console.log('Fetching from:', `${API_BASE}/admin/predictions?page=${predictionsPage}&per_page=${predictionsPerPage}&search=${encodeURIComponent(search)}&date_filter=${filter}`);
    
    fetch(`${API_BASE}/admin/predictions?page=${predictionsPage}&per_page=${predictionsPerPage}&search=${encodeURIComponent(search)}&date_filter=${filter}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} - ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        
        if (data.predictions) {
            displayPredictions(data.predictions);
            updatePredictionsPagination(data.pagination);
            updatePredictionStats(data.statistics);
            updatePredictionChart(data.statistics?.job_role_distribution);
        } else if (data.message) {
            console.error('API error:', data.message);
            document.getElementById('predictionsTable').innerHTML = 
                `<tr><td colspan="7" class="text-center text-warning">${data.message}</td></tr>`;
        } else {
            console.error('Unexpected response format:', data);
            document.getElementById('predictionsTable').innerHTML = 
                '<tr><td colspan="7" class="text-center text-danger">Unexpected response format</td></tr>';
        }
    })
    .catch(error => {
        console.error('Error loading predictions:', error);
        document.getElementById('predictionsTable').innerHTML = 
            `<tr><td colspan="7" class="text-center text-danger">Error loading predictions: ${error.message}</td></tr>`;
    });
}

// Display predictions in table
function displayPredictions(predictions) {
    const tbody = document.getElementById('predictionsTable');
    
    if (!predictions || predictions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No predictions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = predictions.map(pred => {
        const confidencePercentage = pred.confidence_percentage || (pred.confidence_score * 100) || 0;
        const confidenceScore = pred.confidence_score || 0;
        
        return `
        <tr>
            <td>${pred.id || 'N/A'}</td>
            <td>
                <div>
                    <strong>${pred.user_name || 'Unknown'}</strong><br>
                    <small class="text-muted">${pred.user_email || 'No email'}</small>
                </div>
            </td>
            <td>
                <strong>${pred.job_role || 'No role'}</strong>
                ${pred.job_role_encoded ? `<br><small class="text-muted">Code: ${pred.job_role_encoded}</small>` : ''}
                ${pred.model_metrics ? `<div class="mt-1 small text-muted">
                    Acc ${(pred.model_metrics.accuracy * 100).toFixed(1)}% ·
                    F1 ${(pred.model_metrics.f1 * 100).toFixed(1)}% ·
                    Prec ${(pred.model_metrics.precision * 100).toFixed(1)}% ·
                    Rec ${(pred.model_metrics.recall * 100).toFixed(1)}%
                </div>` : ''}
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-2" style="height: 10px;">
                        <div class="progress-bar ${getConfidenceClass(confidenceScore)}" 
                             style="width: ${confidencePercentage}%">
                        </div>
                    </div>
                    <span class="badge ${getConfidenceClass(confidenceScore)}">
                        ${confidencePercentage.toFixed(1)}%
                    </span>
                </div>
            </td>
            <td>
                ${pred.skills_match && pred.skills_match.length > 0 ? 
                    `<div class="d-flex flex-wrap">
                        ${pred.skills_match.slice(0, 2).map(skill => 
                            `<span class="badge bg-secondary skill-badge">${skill}</span>`
                        ).join('')}
                        ${pred.skills_match.length > 2 ? 
                            `<span class="badge bg-light text-dark skill-badge">+${pred.skills_match.length - 2}</span>` : ''}
                    </div>` : 
                    '<span class="text-muted small">No skills</span>'
                }
            </td>
            <td>
                ${pred.created_at ? new Date(pred.created_at).toLocaleDateString() : 'N/A'}<br>
                ${pred.created_at ? `<small class="text-muted">${new Date(pred.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</small>` : ''}
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewPredictionDetails(${pred.id})" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deletePrediction(${pred.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
        `;
    }).join('');
}

// Update predictions pagination
function updatePredictionsPagination(pagination) {
    const paginationEl = document.getElementById('predictionsPagination');
    const infoEl = document.getElementById('predictionsInfo');
    
    if (!pagination) {
        paginationEl.innerHTML = '';
        infoEl.textContent = 'Showing 0 predictions';
        return;
    }
    
    const showingFrom = ((predictionsPage - 1) * predictionsPerPage) + 1;
    const showingTo = Math.min(predictionsPage * predictionsPerPage, pagination.total);
    
    infoEl.textContent = `Showing ${showingFrom}-${showingTo} of ${pagination.total} predictions`;
    
    let paginationHTML = '';
    
    // Previous button
    paginationHTML += `
        <li class="page-item ${predictionsPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePredictionsPage(${predictionsPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </a>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, predictionsPage - 2);
    const endPage = Math.min(pagination.pages, predictionsPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${predictionsPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePredictionsPage(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHTML += `
        <li class="page-item ${predictionsPage === pagination.pages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePredictionsPage(${predictionsPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </a>
        </li>
    `;
    
    paginationEl.innerHTML = paginationHTML;
}

// Change predictions page
function changePredictionsPage(page) {
    if (page < 1) return;
    predictionsPage = page;
    loadPredictions();
}

// Update prediction statistics
function updatePredictionStats(stats) {
    if (!stats) {
        document.getElementById('totalPredictionsCount').textContent = '0';
        document.getElementById('avgConfidence').textContent = '0%';
        document.getElementById('todayPredictions').textContent = '0';
        document.getElementById('topRole').textContent = '-';
        return;
    }
    
    document.getElementById('totalPredictionsCount').textContent = stats.total_predictions || 0;
    document.getElementById('avgConfidence').textContent = stats.avg_confidence ? `${stats.avg_confidence.toFixed(1)}%` : '0%';
    document.getElementById('todayPredictions').textContent = stats.today_predictions || 0;
    document.getElementById('topRole').textContent = stats.top_job_role || '-';
    
    // Update dashboard stats too if element exists
    const totalPredEl = document.getElementById('totalPredictions');
    if (totalPredEl) {
        totalPredEl.textContent = stats.total_predictions || 0;
    }
}

// Update prediction chart
function updatePredictionChart(distribution) {
    const chartDiv = document.getElementById('predictionChart');
    
    if (!distribution || distribution.length === 0) {
        chartDiv.innerHTML = '<p class="text-muted text-center py-4">No prediction data available</p>';
        return;
    }
    
    // Create a simple bar chart using HTML/CSS
    const maxCount = Math.max(...distribution.map(d => d.count));
    
    chartDiv.innerHTML = `
        <div style="max-height: 300px; overflow-y: auto;">
            ${distribution.map(item => `
                <div class="mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="small">${item.job_role}</span>
                        <span class="small">${item.count}</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-primary" 
                             style="width: ${maxCount > 0 ? (item.count / maxCount) * 100 : 0}%">
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Get confidence class
function getConfidenceClass(score) {
    if (score >= 0.8) return 'bg-success';
    if (score >= 0.6) return 'bg-warning';
    return 'bg-danger';
}

// View prediction details
function viewPredictionDetails(predictionId) {
    const token = localStorage.getItem('token');
    
    fetch(`${API_BASE}/predictions/${predictionId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.prediction) {
            const pred = data.prediction;
            const confidencePercentage = pred.confidence_percentage || (pred.confidence_score * 100) || 0;
            
            const modalContent = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Prediction Details</h6>
                        <p><strong>ID:</strong> ${pred.id}</p>
                        <p><strong>User:</strong> ${pred.user_name || 'Unknown'} (${pred.user_email || 'No email'})</p>
                        <p><strong>Job Role:</strong> ${pred.job_role || 'Not specified'}</p>
                        <p><strong>Confidence:</strong> ${confidencePercentage.toFixed(1)}%</p>
                        <p><strong>Model:</strong> ${pred.model_version || 'v1.0'}</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Skills Match</h6>
                        ${pred.skills_match && pred.skills_match.length > 0 ? 
                            `<div class="d-flex flex-wrap gap-2">
                                ${pred.skills_match.map(skill => 
                                    `<span class="badge bg-primary">${skill}</span>`
                                ).join('')}
                            </div>` : 
                            '<p class="text-muted">No skills recorded</p>'
                        }
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Timestamps</h6>
                        <p><strong>Created:</strong> ${pred.created_at ? new Date(pred.created_at).toLocaleString() : 'Unknown'}</p>
                    </div>
                </div>
            `;
            
            // Create a modal to show details
            const modal = new bootstrap.Modal(document.createElement('div'));
            modal._element.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Prediction Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${modalContent}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal._element);
            modal.show();
        }
    })
    .catch(error => {
        alert('Error loading prediction details: ' + error.message);
    });
}

// Delete prediction
function deletePrediction(predictionId) {
    if (!confirm('Are you sure you want to delete this prediction?')) {
        return;
    }
    
    const token = localStorage.getItem('token');
    
    fetch(`${API_BASE}/admin/predictions/${predictionId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert('Prediction deleted successfully!');
            loadPredictions();
            loadDashboardStats();
        } else {
            alert(data.message || 'Error deleting prediction');
        }
    })
    .catch(error => {
        alert('Error deleting prediction: ' + error.message);
    });
}

function showSection(sectionName) {
    // List of all possible sections
    const sections = ['dashboard', 'users', 'predictions', 'analytics'];
    
    // Hide all existing sections
    sections.forEach(section => {
        const sectionElement = document.getElementById(section + 'Section');
        if (sectionElement) {
            sectionElement.style.display = 'none';
        }
    });
    
    // Show selected section if it exists
    const selectedSection = document.getElementById(sectionName + 'Section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    } else {
        console.warn(`Section "${sectionName}Section" not found in HTML`);
        // Fallback to dashboard if section doesn't exist
        const dashboardSection = document.getElementById('dashboardSection');
        if (dashboardSection) {
            dashboardSection.style.display = 'block';
            sectionName = 'dashboard';
        }
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick')?.includes(sectionName)) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    if (sectionName === 'dashboard') {
        loadDashboardStats();
    } else if (sectionName === 'users') {
        currentPage = 1;
        loadUsers();
    } else if (sectionName === 'predictions') {
        predictionsPage = 1;
        loadPredictions();
    } else if (sectionName === 'analytics') {
        console.log('Analytics section selected - implement analytics loading here');
        // You can add analytics loading function here when you create it
    }
    // Refresh charts when dashboard is shown
    if (sectionName === 'dashboard') {
        loadModelMetrics();
        loadDatasetStats();
    }
}
/* ============================================
   ADMIN FEEDBACK FUNCTIONS
============================================ */
let feedbackPage = 1;
let feedbackPerPage = 20;
let feedbackChart = null;

async function loadFeedbackData() {
    try {
        const token = localStorage.getItem('token');
        
        // Build query parameters
        const params = new URLSearchParams({
            page: feedbackPage,
            per_page: feedbackPerPage,
            rating: document.getElementById('feedbackRatingFilter').value || '',
            type: document.getElementById('feedbackTypeFilter').value || '',
            date_from: document.getElementById('feedbackDateFrom').value || '',
            date_to: document.getElementById('feedbackDateTo').value || ''
        });
        
        const search = document.getElementById('feedbackSearch').value;
        if (search) {
            params.append('search', search);
        }
        
        const response = await fetch(`${API_BASE}/admin/feedback/all?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayFeedbackTable(data.feedback);
            updateFeedbackPagination(data.pagination);
            updateFeedbackStats(data.statistics);
            updateFeedbackAnalytics();
            createFeedbackChart(data.statistics?.rating_distribution);
        }
        
    } catch (error) {
        console.error('Error loading feedback data:', error);
        document.getElementById('feedbackTable').innerHTML = 
            `<tr><td colspan="9" class="text-center text-danger">Error: ${error.message}</td></tr>`;
    }
}

function displayFeedbackTable(feedbackList) {
    const tbody = document.getElementById('feedbackTable');
    
    if (!feedbackList || feedbackList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">No feedback found</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = feedbackList.map(fb => {
        const stars = '★'.repeat(fb.rating) + '☆'.repeat(5 - fb.rating);
        const date = new Date(fb.created_at).toLocaleDateString();
        
        return `
            <tr>
                <td>${fb.id}</td>
                <td>
                    <strong>${fb.user_name || 'Unknown'}</strong><br>
                    <small class="text-muted">${fb.user_email || 'No email'}</small>
                </td>
                <td>
                    <span class="${getRatingColorClass(fb.rating)}">${stars}</span>
                    <br><small>(${fb.rating}/5)</small>
                </td>
                <td>
                    <span class="badge ${fb.feedback_type === 'prediction' ? 'bg-primary' : 'bg-success'}">
                        ${fb.feedback_type || 'general'}
                    </span>
                </td>
                <td>
                    ${fb.comment ? 
                        `<small title="${fb.comment}">${fb.comment.substring(0, 50)}${fb.comment.length > 50 ? '...' : ''}</small>` : 
                        '<span class="text-muted">No comment</span>'
                    }
                </td>
                <td>
                    ${fb.prediction_info ? 
                        `<span class="badge bg-info">${fb.prediction_info.job_role || 'Unknown'}</span>` : 
                        '<span class="text-muted">-</span>'
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
                <td>${date}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewAdminFeedbackDetail(${fb.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAdminFeedback(${fb.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateFeedbackPagination(pagination) {
    const infoEl = document.getElementById('feedbackPaginationInfo');
    
    if (!pagination) {
        infoEl.textContent = 'Page 1 of 1';
        return;
    }
    
    infoEl.textContent = `Page ${pagination.page} of ${pagination.pages}`;
}

function updateFeedbackStats(stats) {
    if (!stats) return;
    
    document.getElementById('totalFeedbackCount').textContent = stats.total_feedback || 0;
    document.getElementById('avgFeedbackRating').textContent = stats.avg_rating ? stats.avg_rating.toFixed(1) : '0.0';
    document.getElementById('recentFeedback').textContent = stats.recent_feedback_count || 0;
    
    // Calculate feedback with comments
    if (stats.total_feedback > 0 && stats.rating_distribution) {
        const withComments = Math.round((stats.total_feedback * 0.3)); // This is an estimate
        document.getElementById('feedbackWithComments').textContent = withComments;
    }
}

async function updateFeedbackAnalytics() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/feedback/analytics`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                // Update analytics cards if needed
                const analytics = data.analytics;
                if (analytics) {
                    document.getElementById('feedbackWithComments').textContent = 
                        analytics.feedback_with_comments || 0;
                }
            }
        }
    } catch (error) {
        console.error('Error loading feedback analytics:', error);
    }
}

function createFeedbackChart(ratingDistribution) {
    const canvas = document.getElementById('feedbackRatingChart');
    if (!canvas) return;
    
    if (feedbackChart) {
        feedbackChart.destroy();
    }
    
    if (!ratingDistribution || ratingDistribution.length === 0) {
        canvas.innerHTML = '<p class="text-muted text-center py-4">No rating data available</p>';
        return;
    }
    
    const labels = ratingDistribution.map(r => `${r.rating} Star${r.rating > 1 ? 's' : ''}`);
    const data = ratingDistribution.map(r => r.count);
    const colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997'];
    
    feedbackChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Ratings',
                data: data,
                backgroundColor: colors.slice(0, data.length),
                borderColor: colors.slice(0, data.length).map(c => c.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function changeFeedbackPage(delta) {
    const newPage = feedbackPage + delta;
    if (newPage < 1) return;
    
    feedbackPage = newPage;
    loadFeedbackData();
}

async function viewAdminFeedbackDetail(feedbackId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/feedback/${feedbackId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.feedback) {
            showAdminFeedbackDetailModal(data.feedback);
        }
        
    } catch (error) {
        console.error('Error viewing feedback detail:', error);
        alert('Error loading feedback details: ' + error.message);
    }
}

function showAdminFeedbackDetailModal(feedback) {
    const stars = '★'.repeat(feedback.rating) + '☆'.repeat(5 - feedback.rating);
    const date = new Date(feedback.created_at).toLocaleString();
    
    const modalContent = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Feedback Details - ID: ${feedback.id}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>User Information</h6>
                            <p><strong>Name:</strong> ${feedback.user_info?.name || 'Unknown'}</p>
                            <p><strong>Email:</strong> ${feedback.user_info?.email || 'No email'}</p>
                            <p><strong>Role:</strong> 
                                <span class="badge ${feedback.user_info?.role === 'admin' ? 'badge-admin' : 'badge-user'}">
                                    ${feedback.user_info?.role || 'user'}
                                </span>
                            </p>
                            <p><strong>Profile Completion:</strong> ${feedback.user_info?.profile_completion || 0}%</p>
                        </div>
                        
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
                    </div>
                    
                    <div class="row mt-3">
                        ${feedback.comment ? `
                            <div class="col-md-6">
                                <h6>Comments</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p class="mb-0">${feedback.comment}</p>
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${feedback.improvement_suggestions ? `
                            <div class="col-md-6">
                                <h6>Improvement Suggestions</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p class="mb-0">${feedback.improvement_suggestions}</p>
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${feedback.prediction_details ? `
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6>Prediction Details</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <p><strong>Job Role:</strong> ${feedback.prediction_details.job_role}</p>
                                        <p><strong>Confidence Score:</strong> ${feedback.prediction_details.confidence_score}</p>
                                        <p><strong>Created:</strong> ${new Date(feedback.prediction_details.created_at).toLocaleString()}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-danger" onclick="deleteAdminFeedback(${feedback.id}) && this.closest('.modal').querySelector('.btn-close').click()">
                        Delete Feedback
                    </button>
                </div>
            </div>
        </div>
    `;
    
    showAdminModal('Feedback Details', modalContent);
}

async function deleteAdminFeedback(feedbackId) {
    if (!confirm('Are you sure you want to delete this feedback? This action cannot be undone.')) {
        return false;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/feedback/${feedbackId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Feedback deleted successfully!');
            loadFeedbackData();
            return true;
        } else {
            throw new Error(data.message || 'Failed to delete feedback');
        }
        
    } catch (error) {
        console.error('Error deleting feedback:', error);
        alert('Error deleting feedback: ' + error.message);
        return false;
    }
}

async function exportFeedback() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/feedback/export`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.csv_data) {
            // Create download link
            const blob = new Blob([data.csv_data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename || 'feedback_export.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            alert('Feedback exported successfully!');
        } else {
            throw new Error(data.message || 'Failed to export feedback');
        }
        
    } catch (error) {
        console.error('Error exporting feedback:', error);
        alert('Error exporting feedback: ' + error.message);
    }
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

function showAdminModal(title, content) {
    // Remove existing modal
    const existingModal = document.getElementById('adminDynamicModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal
    const modalDiv = document.createElement('div');
    modalDiv.id = 'adminDynamicModal';
    modalDiv.className = 'modal fade';
    modalDiv.innerHTML = content;
    
    document.body.appendChild(modalDiv);
    
    // Show modal
    const modal = new bootstrap.Modal(modalDiv);
    modal.show();
    
    // Cleanup on hide
    modalDiv.addEventListener('hidden.bs.modal', function() {
        modalDiv.remove();
    });
}

// Update showSection function in admin.js to include feedback
function showSection(sectionName) {
    // List of all possible sections
    const sections = ['dashboard', 'users', 'predictions', 'analytics', 'feedback'];
    
    // Hide all existing sections
    sections.forEach(section => {
        const sectionElement = document.getElementById(section + 'Section');
        if (sectionElement) {
            sectionElement.style.display = 'none';
        }
    });
    
    // Show selected section if it exists
    const selectedSection = document.getElementById(sectionName + 'Section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    } else {
        console.warn(`Section "${sectionName}Section" not found in HTML`);
        // Fallback to dashboard if section doesn't exist
        const dashboardSection = document.getElementById('dashboardSection');
        if (dashboardSection) {
            dashboardSection.style.display = 'block';
            sectionName = 'dashboard';
        }
    }
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick')?.includes(sectionName)) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    if (sectionName === 'dashboard') {
        loadDashboardStats();
    } else if (sectionName === 'users') {
        currentPage = 1;
        loadUsers();
    } else if (sectionName === 'predictions') {
        predictionsPage = 1;
        loadPredictions();
    } else if (sectionName === 'analytics') {
        console.log('Analytics section selected');
    } else if (sectionName === 'feedback') {
        feedbackPage = 1;
        loadFeedbackData();
        updateFeedbackAnalytics();
    }
}
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    window.location.href = 'index.html';
}

/* ============================================
   MODEL RETRAINING FUNCTIONS
============================================ */

let trainingInProgress = false;

// Update showSection function to include modelRetrain
function showSection(sectionName) {
    const sections = ['dashboard', 'users', 'predictions', 'analytics', 'feedback', 'modelRetrain'];
    
    sections.forEach(section => {
        const sectionElement = document.getElementById(section + 'Section');
        if (sectionElement) {
            sectionElement.style.display = 'none';
        }
    });
    
    const selectedSection = document.getElementById(sectionName + 'Section');
    if (selectedSection) {
        selectedSection.style.display = 'block';
    } else {
        const dashboardSection = document.getElementById('dashboardSection');
        if (dashboardSection) {
            dashboardSection.style.display = 'block';
            sectionName = 'dashboard';
        }
    }
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick')?.includes(sectionName)) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    if (sectionName === 'dashboard') {
        loadDashboardStats();
    } else if (sectionName === 'users') {
        currentPage = 1;
        loadUsers();
    } else if (sectionName === 'predictions') {
        predictionsPage = 1;
        loadPredictions();
    } else if (sectionName === 'feedback') {
        feedbackPage = 1;
        loadFeedbackData();
    } else if (sectionName === 'modelRetrain') {
        loadModelInfo();
        validateTrainingData();
    }
}

// Load model information
async function loadModelInfo() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/model/info`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        if (data.success) {
            displayModelInfo(data);
        }
        
    } catch (error) {
        console.error('Error loading model info:', error);
        document.getElementById('modelInfoContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading model information: ${error.message}
            </div>
        `;
    }
}

// Display model information
function displayModelInfo(data) {
    const info = data.model_info;
    const stats = data.dataset_stats;
    const requirements = data.requirements;
    
    const metrics = info.metrics || {};
    const lastTrained = info.last_trained ? new Date(info.last_trained).toLocaleString() : 'Never';
    
    // Calculate data sufficiency
    const hasEnoughData = stats.total_predictions >= requirements.min_training_samples;
    const dataStatus = hasEnoughData ? 
        '<span class="badge bg-success">Sufficient</span>' : 
        '<span class="badge bg-warning">Insufficient</span>';
    
    document.getElementById('modelInfoContent').innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Model Status</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Loaded:</strong></td>
                        <td>
                            ${info.loaded ? 
                                '<span class="badge bg-success">Yes</span>' : 
                                '<span class="badge bg-danger">No</span>'
                            }
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Version:</strong></td>
                        <td>${info.version || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Last Trained:</strong></td>
                        <td>${lastTrained}</td>
                    </tr>
                    <tr>
                        <td><strong>Features:</strong></td>
                        <td>${info.features || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Classes:</strong></td>
                        <td>${info.classes || 'N/A'}</td>
                    </tr>
                </table>
            </div>
            
            <div class="col-md-6">
                <h6>Performance Metrics</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Accuracy:</strong></td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                                    <div class="progress-bar bg-success" style="width: ${(metrics.accuracy || 0) * 100}%"></div>
                                </div>
                                <span>${((metrics.accuracy || 0) * 100).toFixed(1)}%</span>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>F1 Score:</strong></td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                                    <div class="progress-bar bg-info" style="width: ${(metrics.f1 || 0) * 100}%"></div>
                                </div>
                                <span>${((metrics.f1 || 0) * 100).toFixed(1)}%</span>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Precision:</strong></td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                                    <div class="progress-bar bg-primary" style="width: ${(metrics.precision || 0) * 100}%"></div>
                                </div>
                                <span>${((metrics.precision || 0) * 100).toFixed(1)}%</span>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Recall:</strong></td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress flex-grow-1 me-2" style="height: 10px;">
                                    <div class="progress-bar bg-warning" style="width: ${(metrics.recall || 0) * 100}%"></div>
                                </div>
                                <span>${((metrics.recall || 0) * 100).toFixed(1)}%</span>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="row mt-3">
            <div class="col-12">
                <h6>Dataset Statistics</h6>
                <div class="row">
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-primary">${stats.total_predictions || 0}</h3>
                                <p class="text-muted mb-0">Total Predictions</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-success">${stats.unique_job_roles || 0}</h3>
                                <p class="text-muted mb-0">Unique Job Roles</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="text-info">${stats.avg_confidence ? stats.avg_confidence.toFixed(1) : '0.0'}%</h3>
                                <p class="text-muted mb-0">Avg Confidence</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center">
                            <div class="card-body">
                                <h3 class="${hasEnoughData ? 'text-success' : 'text-warning'}">
                                    ${stats.total_predictions || 0}/${requirements.min_training_samples}
                                </h3>
                                <p class="text-muted mb-0">Training Samples ${dataStatus}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Validate training data
async function validateTrainingData() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/model/validate-data`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        displayValidationResults(data);
        
    } catch (error) {
        console.error('Error validating data:', error);
        document.getElementById('dataValidationContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error validating training data: ${error.message}
            </div>
        `;
    }
}

// Display validation results
function displayValidationResults(data) {
    const stats = data.stats || {};
    const errors = data.errors || [];
    const canRetrain = data.can_retrain;
    
    let validationHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Data Statistics</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Total Samples:</strong></td>
                        <td>
                            ${stats.total_samples}
                            ${stats.total_samples >= 50 ? 
                                '<span class="badge bg-success ms-2">✓</span>' : 
                                '<span class="badge bg-danger ms-2">✗</span>'
                            }
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Features:</strong></td>
                        <td>${stats.features}</td>
                    </tr>
                    <tr>
                        <td><strong>Unique Classes:</strong></td>
                        <td>
                            ${stats.unique_classes}
                            ${stats.unique_classes >= 2 ? 
                                '<span class="badge bg-success ms-2">✓</span>' : 
                                '<span class="badge bg-danger ms-2">✗</span>'
                            }
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Has Data:</strong></td>
                        <td>
                            ${stats.has_data ? 
                                '<span class="badge bg-success">Yes</span>' : 
                                '<span class="badge bg-danger">No</span>'
                            }
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="col-md-6">
                <h6>Validation Status</h6>
                <div class="alert ${data.is_valid ? 'alert-success' : 'alert-warning'}">
                    <h6>
                        ${data.is_valid ? 
                            '<i class="fas fa-check-circle me-2"></i> Data is Valid' : 
                            '<i class="fas fa-exclamation-triangle me-2"></i> Data Validation Issues'
                        }
                    </h6>
                    <p class="mb-0">
                        ${canRetrain ? 
                            'Ready for retraining' : 
                            'Not ready for retraining'
                        }
                    </p>
                </div>
            </div>
        </div>
    `;
    
    if (errors.length > 0) {
        validationHTML += `
            <div class="mt-3">
                <h6>Validation Errors</h6>
                <div class="alert alert-danger">
                    <ul class="mb-0">
                        ${errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    validationHTML += `
        <div class="mt-3">
            <h6>Requirements</h6>
            <table class="table table-sm">
                <tr>
                    <td>Minimum Training Samples:</td>
                    <td>50</td>
                    <td>
                        ${stats.total_samples >= 50 ? 
                            '<span class="badge bg-success">Met</span>' : 
                            '<span class="badge bg-danger">Not Met</span>'
                        }
                    </td>
                </tr>
                <tr>
                    <td>Minimum Unique Classes:</td>
                    <td>2</td>
                    <td>
                        ${stats.unique_classes >= 2 ? 
                            '<span class="badge bg-success">Met</span>' : 
                            '<span class="badge bg-danger">Not Met</span>'
                        }
                    </td>
                </tr>
            </table>
        </div>
    `;
    
    document.getElementById('dataValidationContent').innerHTML = validationHTML;
    
    // Update button states
    document.getElementById('retrainBtn').disabled = !canRetrain;
    document.getElementById('forceRetrainBtn').disabled = false;
}

// Retrain model
async function retrainModel() {
    if (trainingInProgress) return;
    
    if (!confirm('Are you sure you want to retrain the model? This may take a few minutes.')) {
        return;
    }
    
    await performRetrain(false);
}

// Force retrain model
async function forceRetrainModel() {
    if (trainingInProgress) return;
    
    if (!confirm('WARNING: Force retraining will train the model even with insufficient data.\nThis may result in poor model performance.\n\nAre you sure you want to continue?')) {
        return;
    }
    
    await performRetrain(true);
}

// Perform the actual retraining
async function performRetrain(force = false) {
    trainingInProgress = true;
    
    // Show progress modal
    const progressModal = new bootstrap.Modal(document.getElementById('trainingProgressModal'));
    progressModal.show();
    
    // Update progress
    updateTrainingProgress(0, 'Starting model training...');
    
    try {
        const token = localStorage.getItem('token');
        
        // Get custom parameters if enabled
        const useCustomParams = document.getElementById('useCustomParams').checked;
        let params = { force: force };
        
        if (useCustomParams) {
            params.n_estimators = parseInt(document.getElementById('nEstimators').value);
            params.max_depth = parseInt(document.getElementById('maxDepth').value);
        }
        
        // Start training
        const response = await fetch(`${API_BASE}/admin/model/retrain`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(params)
        });
        
        updateTrainingProgress(50, 'Training in progress...');
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.message || 'Training failed');
        }
        
        updateTrainingProgress(100, 'Training completed successfully!');
        
        // Wait a moment to show completion
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        progressModal.hide();
        
        if (data.success) {
            // Show success message
            showTrainingResult('success', 'Model Retrained Successfully!', data);
            
            // Reload model info
            loadModelInfo();
            validateTrainingData();
        } else {
            throw new Error(data.details || data.message || 'Training failed');
        }
        
    } catch (error) {
        console.error('Error retraining model:', error);
        progressModal.hide();
        showTrainingResult('error', 'Model Training Failed', {
            message: error.message,
            details: 'Check console for more details'
        });
    } finally {
        trainingInProgress = false;
    }
}

// Update training progress
function updateTrainingProgress(percent, message) {
    const progressBar = document.getElementById('trainingProgressBar');
    const status = document.getElementById('trainingStatus');
    const details = document.getElementById('trainingDetails');
    
    if (progressBar) progressBar.style.width = `${percent}%`;
    if (status) status.textContent = message;
    
    // Update details based on progress
    if (details) {
        if (percent < 25) details.textContent = 'Loading training data...';
        else if (percent < 50) details.textContent = 'Preprocessing data...';
        else if (percent < 75) details.textContent = 'Training model...';
        else if (percent < 100) details.textContent = 'Evaluating model...';
        else details.textContent = 'Saving model...';
    }
}

// Show training result
function showTrainingResult(type, title, data) {
    let icon, color, content;
    
    if (type === 'success') {
        icon = 'fas fa-check-circle';
        color = 'success';
        content = `
            <h5><i class="${icon} me-2"></i> ${title}</h5>
            <p>${data.message}</p>
            
            <div class="mt-4">
                <h6>Training Results:</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Accuracy:</strong></td>
                        <td>${(data.metrics?.accuracy * 100 || 0).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td><strong>F1 Score:</strong></td>
                        <td>${(data.metrics?.f1 * 100 || 0).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td><strong>Precision:</strong></td>
                        <td>${(data.metrics?.precision * 100 || 0).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td><strong>Recall:</strong></td>
                        <td>${(data.metrics?.recall * 100 || 0).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td><strong>Training Samples:</strong></td>
                        <td>${data.metrics?.training_samples || 0}</td>
                    </tr>
                    <tr>
                        <td><strong>Test Samples:</strong></td>
                        <td>${data.metrics?.test_samples || 0}</td>
                    </tr>
                </table>
            </div>
            
            <p class="text-muted small mt-3">
                <i class="fas fa-info-circle me-1"></i>
                Model saved and ready for predictions. The new model will be used immediately.
            </p>
        `;
    } else {
        icon = 'fas fa-exclamation-triangle';
        color = 'danger';
        content = `
            <h5><i class="${icon} me-2"></i> ${title}</h5>
            <p>${data.message || 'Unknown error occurred'}</p>
            
            ${data.details ? `
                <div class="alert alert-warning mt-3">
                    <strong>Details:</strong> ${data.details}
                </div>
            ` : ''}
            
            <p class="text-muted small mt-3">
                <i class="fas fa-lightbulb me-1"></i>
                Please check if you have sufficient training data (minimum 50 samples) and try again.
            </p>
        `;
    }
    
    const modalContent = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-${color} text-white">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-${color}" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    showAdminModal('Training Result', modalContent);
}

// Show training history
async function showTrainingHistory() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/admin/model/info`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        
        if (data.success) {
            displayTrainingHistory(data.training_log || []);
        }
        
    } catch (error) {
        console.error('Error loading training history:', error);
        document.getElementById('trainingHistoryContent').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading training history: ${error.message}
            </div>
        `;
    }
    
    new bootstrap.Modal(document.getElementById('trainingHistoryModal')).show();
}

// Display training history
function displayTrainingHistory(history) {
    if (!history || history.length === 0) {
        document.getElementById('trainingHistoryContent').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No training history found.
            </div>
        `;
        return;
    }
    
    // Sort by timestamp (newest first)
    history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    const historyHTML = history.map((session, index) => {
        const metrics = session.metrics || {};
        const date = new Date(session.timestamp).toLocaleString();
        
        return `
            <div class="card mb-3 ${index === 0 ? 'border-primary' : ''}">
                <div class="card-header ${index === 0 ? 'bg-primary text-white' : 'bg-light'}">
                    <h6 class="mb-0">
                        <i class="fas fa-calendar-alt me-2"></i>
                        Training Session ${history.length - index} - ${date}
                        ${index === 0 ? '<span class="badge bg-success ms-2">Current</span>' : ''}
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Accuracy:</strong></td>
                                    <td>${(metrics.accuracy * 100 || 0).toFixed(2)}%</td>
                                </tr>
                                <tr>
                                    <td><strong>F1 Score:</strong></td>
                                    <td>${(metrics.f1 * 100 || 0).toFixed(2)}%</td>
                                </tr>
                                <tr>
                                    <td><strong>Precision:</strong></td>
                                    <td>${(metrics.precision * 100 || 0).toFixed(2)}%</td>
                                </tr>
                                <tr>
                                    <td><strong>Recall:</strong></td>
                                    <td>${(metrics.recall * 100 || 0).toFixed(2)}%</td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <table class="table table-sm">
                                <tr>
                                    <td><strong>Version:</strong></td>
                                    <td>${session.model_version || 'N/A'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Training Samples:</strong></td>
                                    <td>${metrics.training_samples || 0}</td>
                                </tr>
                                <tr>
                                    <td><strong>Test Samples:</strong></td>
                                    <td>${metrics.test_samples || 0}</td>
                                </tr>
                                <tr>
                                    <td><strong>Unique Classes:</strong></td>
                                    <td>${metrics.unique_classes || 0}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('trainingHistoryContent').innerHTML = historyHTML;
}

// Toggle custom parameters
document.addEventListener('DOMContentLoaded', function() {
    const useCustomParams = document.getElementById('useCustomParams');
    const customParams = document.getElementById('customParams');
    
    if (useCustomParams && customParams) {
        useCustomParams.addEventListener('change', function() {
            customParams.style.display = this.checked ? 'block' : 'none';
        });
    }
});