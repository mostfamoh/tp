// Crypto Lab Frontend JavaScript

const API_BASE = '/api';

// Utility: Show alert message
function showAlert(message, type = 'info', containerId = 'alert-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.innerHTML = '';
    container.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Utility: Clear results
function clearResults(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
    }
}

// User Registration
async function registerUser(event) {
    event.preventDefault();
    
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const algorithm = document.getElementById('reg-algorithm').value;
    
    // Get key based on algorithm
    let key = {};
    
    switch(algorithm) {
        case 'caesar':
            key = { shift: parseInt(document.getElementById('caesar-shift').value) };
            break;
        case 'affine':
            key = { 
                a: parseInt(document.getElementById('affine-a').value),
                b: parseInt(document.getElementById('affine-b').value)
            };
            break;
        case 'playfair':
            key = { keyword: document.getElementById('playfair-keyword').value };
            break;
        case 'hill':
            // For Hill, we expect a 2x2 matrix as a keyword that generates the matrix
            key = { keyword: document.getElementById('hill-keyword').value };
            break;
    }
    
    const payload = {
        username: username,
        password: password,
        algorithm: algorithm,
        key: key
    };
    
    try {
        const response = await fetch(`${API_BASE}/regester/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✓ ${data.message || 'User registered successfully!'}`, 'success');
            document.getElementById('registration-form').reset();
            toggleKeyInputs(); // Reset key inputs
        } else {
            showAlert(`✗ ${data.error || 'Registration failed'}`, 'danger');
        }
    } catch (error) {
        showAlert(`✗ Error: ${error.message}`, 'danger');
    }
}

// User Login
async function loginUser(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    const payload = {
        username: username,
        password: password
    };
    
    try {
        const response = await fetch(`${API_BASE}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`✓ ${data.message || 'Login successful!'}`, 'success', 'login-alert');
        } else {
            showAlert(`✗ ${data.error || data.message || 'Login failed'}`, 'danger', 'login-alert');
        }
    } catch (error) {
        showAlert(`✗ Error: ${error.message}`, 'danger', 'login-alert');
    }
}

// Get User Info
async function getUserInfo(event) {
    event.preventDefault();
    
    const username = document.getElementById('user-lookup-username').value;
    
    try {
        const response = await fetch(`${API_BASE}/user/${username}/`);
        const data = await response.json();
        
        const resultDiv = document.getElementById('user-info-result');
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="result-card">
                    <h5>User Information</h5>
                    <p><strong>Username:</strong> ${data.username}</p>
                    <p><strong>Algorithm:</strong> ${data.algorithm}</p>
                    <p><strong>Encrypted Password:</strong> <code>${data.password_encrypted}</code></p>
                    <p><strong>Key Data:</strong> <code>${JSON.stringify(data.key_data)}</code></p>
                </div>
            `;
        } else {
            showAlert(`✗ ${data.error || 'User not found'}`, 'danger', 'user-lookup-alert');
            resultDiv.innerHTML = '';
        }
    } catch (error) {
        showAlert(`✗ Error: ${error.message}`, 'danger', 'user-lookup-alert');
    }
}

// Run Brute Force Attack
async function runBruteForce(event) {
    event.preventDefault();
    
    const username = document.getElementById('bf-username').value;
    const algorithm = document.getElementById('bf-algorithm').value || undefined;
    const limit = parseInt(document.getElementById('bf-limit').value) || 0;
    const maxSeconds = parseFloat(document.getElementById('bf-max-seconds').value) || 0;
    const keyspaceText = document.getElementById('bf-keyspace').value;
    
    let playfair_keyspace = [];
    if (keyspaceText.trim()) {
        playfair_keyspace = keyspaceText.split('\n').map(k => k.trim()).filter(k => k);
    }
    
    const payload = {
        target_username: username,
        mode: 'bruteforce',
        algorithm: algorithm,
        limit: limit,
        max_seconds: maxSeconds,
        playfair_keyspace: playfair_keyspace
    };
    
    const resultDiv = document.getElementById('bf-result');
    resultDiv.innerHTML = '<div class="spinner-container"><div class="spinner-border text-primary" role="status"></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/attack/full_bruteforce/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.error) {
            showAlert(`✗ ${data.error}`, 'danger', 'bf-alert');
            resultDiv.innerHTML = '';
            return;
        }
        
        displayAttackResults(data, resultDiv);
        showAlert('✓ Attack completed!', 'success', 'bf-alert');
        
    } catch (error) {
        showAlert(`✗ Error: ${error.message}`, 'danger', 'bf-alert');
        resultDiv.innerHTML = '';
    }
}

// Run Dictionary Attack
async function runDictionaryAttack(event) {
    event.preventDefault();
    
    const username = document.getElementById('dict-username').value;
    const algorithm = document.getElementById('dict-algorithm').value || undefined;
    const limit = parseInt(document.getElementById('dict-limit').value) || 0;
    const maxSeconds = parseFloat(document.getElementById('dict-max-seconds').value) || 0;
    const dictionaryText = document.getElementById('dict-dictionary').value;
    
    let dictionary = [];
    if (dictionaryText.trim()) {
        dictionary = dictionaryText.split('\n').map(w => w.trim()).filter(w => w);
    }
    
    const payload = {
        target_username: username,
        mode: 'dictionary',
        algorithm: algorithm,
        limit: limit,
        max_seconds: maxSeconds,
        dictionary: dictionary
    };
    
    const resultDiv = document.getElementById('dict-result');
    resultDiv.innerHTML = '<div class="spinner-container"><div class="spinner-border text-primary" role="status"></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/attack/full_dictionary/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.error) {
            showAlert(`✗ ${data.error}`, 'danger', 'dict-alert');
            resultDiv.innerHTML = '';
            return;
        }
        
        displayAttackResults(data, resultDiv);
        showAlert('✓ Attack completed!', 'success', 'dict-alert');
        
    } catch (error) {
        showAlert(`✗ Error: ${error.message}`, 'danger', 'dict-alert');
        resultDiv.innerHTML = '';
    }
}

// Display attack results
function displayAttackResults(data, container) {
    let html = `
        <div class="row mb-3">
            <div class="col-md-3">
                <div class="stats-box">
                    <h3>${data.attempts}</h3>
                    <p>Attempts</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-box">
                    <h3>${data.matches_count}</h3>
                    <p>Matches</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-box">
                    <h3>${data.time_sec}s</h3>
                    <p>Time</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stats-box">
                    <h3>${data.algorithm}</h3>
                    <p>Algorithm</p>
                </div>
            </div>
        </div>
    `;
    
    if (data.limit_reached) {
        html += '<div class="alert alert-warning">⚠ Limit reached</div>';
    }
    if (data.timeout_reached) {
        html += '<div class="alert alert-warning">⚠ Timeout reached</div>';
    }
    
    if (data.matches && data.matches.length > 0) {
        html += '<h5 class="mt-4 mb-3">Matches Found:</h5>';
        
        data.matches.forEach((match, idx) => {
            const confidenceClass = `badge-confidence-${match.confidence}`;
            html += `
                <div class="match-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-2">Match #${idx + 1}</h6>
                            <p class="mb-1"><strong>Plaintext:</strong> <code class="text-success">${match.candidate_plaintext}</code></p>
                            <p class="mb-1"><strong>Key:</strong> <code>${JSON.stringify(match.candidate_key)}</code></p>
                            <p class="mb-0"><small class="text-muted">${match.notes}</small></p>
                        </div>
                        <span class="badge ${confidenceClass}">${match.confidence.toUpperCase()}</span>
                    </div>
                </div>
            `;
        });
    } else {
        html += '<div class="alert alert-info">No matches found.</div>';
    }
    
    if (data.notes) {
        html += `<div class="alert alert-secondary mt-3"><small>${data.notes}</small></div>`;
    }
    
    container.innerHTML = html;
}

// Toggle key input fields based on selected algorithm
function toggleKeyInputs() {
    const algorithm = document.getElementById('reg-algorithm').value;
    
    // Hide all key input groups
    document.querySelectorAll('.key-input-group').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the relevant key input
    const selectedGroup = document.getElementById(`${algorithm}-key-group`);
    if (selectedGroup) {
        selectedGroup.style.display = 'block';
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Registration form
    const regForm = document.getElementById('registration-form');
    if (regForm) {
        regForm.addEventListener('submit', registerUser);
        document.getElementById('reg-algorithm').addEventListener('change', toggleKeyInputs);
        toggleKeyInputs(); // Initial state
    }
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', loginUser);
    }
    
    // User lookup form
    const userLookupForm = document.getElementById('user-lookup-form');
    if (userLookupForm) {
        userLookupForm.addEventListener('submit', getUserInfo);
    }
    
    // Brute force form
    const bfForm = document.getElementById('bruteforce-form');
    if (bfForm) {
        bfForm.addEventListener('submit', runBruteForce);
    }
    
    // Dictionary attack form
    const dictForm = document.getElementById('dictionary-form');
    if (dictForm) {
        dictForm.addEventListener('submit', runDictionaryAttack);
    }
});
