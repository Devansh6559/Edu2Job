const API_BASE = 'http://localhost:5000/api';

// Google OAuth Configuration
let googleClientId = '1019789869790-24jf1rlv594hm407c1lgfjdrr8o9m5g8.apps.googleusercontent.com'; // You'll update this later

function initializeGoogleAuth() {
    if (typeof google === 'undefined') {
        console.log('Google library not loaded yet, retrying...');
        setTimeout(initializeGoogleAuth, 1000);
        return;
    }

    try {
        google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleLogin,
            auto_select: false,
            cancel_on_tap_outside: true
        });

        // Render Google Sign-In button
        google.accounts.id.renderButton(
            document.getElementById('googleSignIn'),
            { 
                theme: 'outline', 
                size: 'large',
                width: '100%',
                text: 'continue_with',
                type: 'standard'
            }
        );

        console.log('Google OAuth initialized successfully');
    } catch (error) {
        console.error('Error initializing Google OAuth:', error);
    }
}

function handleGoogleLogin(response) {
    console.log('Google login response received');
    
    const googleToken = response.credential;
    
    showMessage('Signing in with Google...', 'info');
    
    fetch(`${API_BASE}/google-login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: googleToken })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            showMessage('Google login successful! Redirecting...', 'success');
            
            // ✅ ADMIN REDIRECT: Check user role and redirect accordingly
            if (data.user.role === 'admin') {
                setTimeout(() => {
                    window.location.href = 'admin.html';
                }, 1000);
            } else {
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            }
        } else {
            showMessage(data.message || 'Google login failed', 'danger');
        }
    })
    .catch(error => {
        console.error('Google login error:', error);
        showMessage('Google login failed. Please try email login or check console.', 'danger');
    });
}

// Form Handling
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing auth...');
    
    // Login form
    const loginForm = document.getElementById('loginFormElement');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            loginUser();
        });
    }
    
    // Signup form
    const signupForm = document.getElementById('signupFormElement');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            registerUser();
        });
    }
    
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (token) {
        // ✅ ADMIN REDIRECT: Redirect based on user role
        if (user.role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'dashboard.html';
        }
    }
    
    // Initialize Google Auth
    setTimeout(initializeGoogleAuth, 500);
});

function loginUser() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        showMessage('Please fill in all fields', 'warning');
        return;
    }
    
    showMessage('Signing in...', 'info');
    
    fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // ✅ ADMIN REDIRECT: Check user role and redirect accordingly
            if (data.user.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'dashboard.html';
            }
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Login failed. Please try again.', 'danger');
    });
}

function registerUser() {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const degree = document.getElementById('signupDegree').value;
    const specialization = document.getElementById('signupSpecialization').value;
    
    if (!name || !email || !password) {
        showMessage('Please fill in required fields', 'warning');
        return;
    }
    
    // Frontend password validation
    const strengthInfo = checkPasswordStrength(password);
    if (!strengthInfo.isValid) {
        showMessage(strengthInfo.message, 'danger');
        return;
    }
    
    showMessage('Creating account...', 'info');
    
    fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            name, 
            email, 
            password,
            degree,
            specialization 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // ✅ ADMIN REDIRECT: Check user role and redirect accordingly
            if (data.user.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'dashboard.html';
            }
        } else {
            showMessage(data.message, 'danger');
        }
    })
    .catch(error => {
        showMessage('Registration failed. Please try again.', 'danger');
    });
}

function showSignup() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupForm').style.display = 'block';
}

function showLogin() {
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Auto-dismiss success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            const alert = messageDiv.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 3000);
    }
}

// Debug function to check Google OAuth status
function checkGoogleOAuthStatus() {
    console.log('Google OAuth Status Check:');
    console.log('- Google library loaded:', typeof google !== 'undefined');
    console.log('- Client ID set:', googleClientId && googleClientId !== '1019789869790-24jf1rlv594hm407c1lgfjdrr8o9m5g8.apps.googleusercontent.com');
    console.log('- Google SignIn element:', document.getElementById('googleSignIn'));
}

// Add password strength checker
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
    
    if (!constraints.length) messages.push("at least 8 characters");
    if (!constraints.uppercase) messages.push("one uppercase letter");
    if (!constraints.lowercase) messages.push("one lowercase letter");
    if (!constraints.number) messages.push("one number");
    if (!constraints.special) messages.push("one special character");
    
    return {
        strength: strength,
        isValid: strength === 5,
        message: messages.length > 0 ? `Password must contain: ${messages.join(', ')}` : "Strong password"
    };
}

// Add real-time password validation to signup form
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('signupPassword');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strengthInfo = checkPasswordStrength(password);
            const messageDiv = document.getElementById('passwordStrength');
            
            if (!messageDiv) {
                const newDiv = document.createElement('div');
                newDiv.id = 'passwordStrength';
                newDiv.className = 'mt-2 small';
                this.parentNode.appendChild(newDiv);
            }
            
            const strengthDiv = document.getElementById('passwordStrength');
            strengthDiv.innerHTML = `
                <div class="progress mb-2" style="height: 5px;">
                    <div class="progress-bar ${strengthInfo.strength >= 4 ? 'bg-success' : strengthInfo.strength >= 3 ? 'bg-warning' : 'bg-danger'}" 
                         style="width: ${(strengthInfo.strength / 5) * 100}%">
                    </div>
                </div>
                <small class="${strengthInfo.isValid ? 'text-success' : 'text-danger'}">
                    ${strengthInfo.message}
                </small>
            `;
        });
    }
});

// this function is added for updating dashboard 
// Add this utility function to auth.js for making authenticated requests
function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showMessage('Please login first', 'danger');
        window.location.href = 'index.html';
        return Promise.reject('No token found');
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    return fetch(url, mergedOptions);
}

// Example of how to use it for profile update (you'll need to add this to your profile page)
async function updateProfile(profileData) {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE}/profile`, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Profile update failed');
        }
        
        return data;
    } catch (error) {
        console.error('Profile update error:', error);
        throw error;
    }
}