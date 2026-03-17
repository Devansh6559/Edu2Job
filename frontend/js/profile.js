// profile.js
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        window.location.href = 'index.html';
        return;
    }
    
    // Load current profile data
    loadProfile();
    
    // Setup form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            updateProfile();
        });
    }
    
    // Setup logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        });
    }
});

async function loadProfile() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load profile');
        }
        
        const data = await response.json();
        
        // Populate form fields with current data
        document.getElementById('name').value = data.user.name || '';
        document.getElementById('degree').value = data.user.degree || '';
        document.getElementById('specialization').value = data.user.specialization || '';
        document.getElementById('cgpa').value = data.user.cgpa || '';
        document.getElementById('university').value = data.user.university || '';
        document.getElementById('graduation_year').value = data.user.graduation_year || '';
        document.getElementById('certifications').value = data.user.certifications || '';
        
    } catch (error) {
        console.error('Error loading profile:', error);
        showMessage('Failed to load profile data', 'danger');
    }
}

async function updateProfile() {
    const profileData = {
        name: document.getElementById('name').value,
        degree: document.getElementById('degree').value,
        specialization: document.getElementById('specialization').value,
        cgpa: document.getElementById('cgpa').value,
        university: document.getElementById('university').value,
        graduation_year: document.getElementById('graduation_year').value,
        certifications: document.getElementById('certifications').value
    };
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Profile update failed');
        }
        
        // Update local storage with new user data
        localStorage.setItem('user', JSON.stringify(data.user));
        
        showMessage('Profile updated successfully!', 'success');
        
    } catch (error) {
        console.error('Profile update error:', error);
        showMessage(error.message, 'danger');
    }
}

function showMessage(message, type) {
    // Create or use existing message container
    let messageDiv = document.getElementById('message');
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = 'message';
        document.body.prepend(messageDiv);
    }
    
    messageDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (type === 'success') {
        setTimeout(() => {
            const alert = messageDiv.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 3000);
    }
}