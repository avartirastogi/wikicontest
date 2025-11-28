/**
 * WikiContest Frontend JavaScript
 * 
 * This module handles all client-side functionality for the WikiContest platform,
 * including API communication, UI interactions, authentication, and data management.
 * 
 * Architecture:
 * - Modular function organization by feature
 * - Centralized API communication with error handling
 * - JWT-based authentication with CSRF protection
 * - Responsive UI with Bootstrap components
 * - Real-time data updates and state management
 * 
 * Key Features:
 * - User authentication (login/logout/register)
 * - Contest management (create/view/submit)
 * - Dashboard with user statistics
 * - Responsive design with modern UI components
 * 
 * Author: WikiContest Development Team
 * Version: 1.0.0
 */

// =============================================================================
// GLOBAL CONFIGURATION AND STATE
// =============================================================================

// API Configuration
const API_BASE_URL = '/api';  // Base URL for all API endpoints

// Global application state
let currentUser = null;  // Currently logged-in user information
let currentContests = {  // Cached contest data organized by status
    current: [],    // Active contests
    upcoming: [],   // Future contests
    past: []        // Completed contests
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Display alert messages to the user with Bootstrap styling.
 * 
 * This function creates temporary alert notifications that automatically
 * disappear after 5 seconds. It supports different alert types (success,
 * error, warning, info) with appropriate Bootstrap CSS classes.
 * 
 * @param {string} message - The message to display
 * @param {string} type - Alert type: 'success', 'error', 'warning', 'info'
 * 
 * Example:
 * showAlert('Login successful!', 'success');
 * showAlert('Invalid credentials', 'error');
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = 'alert-' + Date.now();

    // Create alert HTML with Bootstrap classes
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Insert alert at the end of the container
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Set loading state for UI elements.
 * 
 * This function manages the loading state of buttons and other interactive
 * elements by adding/removing CSS classes and disabling pointer events.
 * 
 * @param {HTMLElement} element - The element to set loading state for
 * @param {boolean} loading - Whether to show loading state (default: true)
 * 
 * Example:
 * setLoading(submitButton, true);  // Show loading
 * setLoading(submitButton, false); // Hide loading
 */
function setLoading(element, loading = true) {
    if (loading) {
        element.classList.add('loading');
        element.style.pointerEvents = 'none';
    } else {
        element.classList.remove('loading');
        element.style.pointerEvents = 'auto';
    }
}

/**
 * Get cookie value by name.
 * 
 * This utility function retrieves cookie values from the browser's
 * cookie storage. It's primarily used for CSRF token management
 * in API requests.
 * 
 * @param {string} name - Cookie name to retrieve
 * @returns {string|null} Cookie value or null if not found
 * 
 * Example:
 * const csrfToken = getCookie('csrf_access_token');
 */
function getCookie(name) {
    // Split all cookies into individual entries
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);

    // Return cookie value if found, null otherwise
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return null;
}

/**
 * Format date string for display in the UI.
 * 
 * Converts ISO date strings to user-friendly format for display
 * in contest cards and other UI elements.
 * 
 * @param {string} dateString - ISO date string (YYYY-MM-DD)
 * @returns {string} Formatted date string
 * 
 * Example:
 * formatDate('2025-10-29') returns 'October 29, 2025'
 */
function formatDate(dateString) {
    if (!dateString) return 'No date';

    try {
        // Parse the date and format it for display
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid date';
    }
}

/**
 * Check if a date is in the past.
 * 
 * Utility function to determine if a given date has already passed.
 * Used for contest status determination and UI state management.
 * 
 * @param {string} dateString - ISO date string to check
 * @returns {boolean} True if date is in the past, false otherwise
 */
function isDatePast(dateString) {
    if (!dateString) return false;

    try {
        const date = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);  // Reset time to start of day
        return date < today;
    } catch (error) {
        console.error('Error checking date:', error);
        return false;
    }
}

// =============================================================================
// API COMMUNICATION FUNCTIONS
// =============================================================================

/**
 * Centralized API request function with error handling and CSRF protection.
 * 
 * This function handles all API communication with the backend, including:
 * - Automatic CSRF token inclusion for security
 * - JWT cookie management for authentication
 * - Consistent error handling and response parsing
 * - Request/response logging for debugging
 * 
 * @param {string} endpoint - API endpoint path (e.g., '/user/login')
 * @param {Object} options - Fetch API options (method, body, headers, etc.)
 * @returns {Promise<Object>} Parsed JSON response data
 * @throws {Error} If request fails or returns error status
 * 
 * Example:
 * const userData = await apiRequest('/user/dashboard');
 * const result = await apiRequest('/contest/create', {
 *     method: 'POST',
 *     body: JSON.stringify(contestData)
 * });
 */
async function apiRequest(endpoint, options = {}) {
    // Construct full URL
    const url = `${API_BASE_URL}${endpoint}`;

    // Default request options
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for JWT authentication
    };

    // Add CSRF token if available for security
    const csrfToken = getCookie('csrf_access_token');
    if (csrfToken) {
        defaultOptions.headers['X-CSRF-TOKEN'] = csrfToken;
    }

    // Merge default options with provided options
    const finalOptions = { ...defaultOptions, ...options };

    try {
        // Make the API request
        const response = await fetch(url, finalOptions);
        const data = await response.json();

        // Check if response indicates an error
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        // Log error for debugging
        console.error('API Error:', error);
        throw error;
    }
}


// =============================================================================
// AUTHENTICATION FUNCTIONS
// =============================================================================

/**
 * Authenticate user with email and password.
 * 
 * This function handles user login by sending credentials to the backend
 * and managing the authentication state. On successful login, it updates
 * the global currentUser variable and redirects to the dashboard.
 * 
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Login response data
 * 
 * Example:
 * await login('user@example.com', 'password123');
 */
async function login(email, password) {
    try {
        // Send login request to backend
        const response = await apiRequest('/user/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });

        // Update global user state with response data
        currentUser = {
            id: response.userId,
            username: response.username,
            email: email
        };

        // Update UI to reflect authenticated state
        updateAuthUI();
        showAlert('Login successful!', 'success');
        showSection('dashboard');

        return response;
    } catch (error) {
        // Show error message to user
        showAlert(error.message, 'danger');
        throw error;
    }
}

/**
 * Register a new user account.
 * 
 * This function creates a new user account with the provided information.
 * After successful registration, it prompts the user to login with their
 * new credentials.
 * 
 * @param {string} username - Desired username
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Registration response data
 * 
 * Example:
 * await register('newuser', 'user@example.com', 'password123');
 */
async function register(username, email, password) {
    try {
        // Send registration request to backend
        const response = await apiRequest('/user/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password }),
        });

        // Show success message and redirect to login
        showAlert('Registration successful! Please login.', 'success');
        showSection('login');

        return response;
    } catch (error) {
        // Show error message to user
        showAlert(error.message, 'danger');
        throw error;
    }
}

/**
 * Logout the current user.
 * 
 * This function handles user logout by invalidating the session on the
 * backend and clearing the local authentication state. It then redirects
 * the user to the home page.
 * 
 * @returns {Promise<void>}
 * 
 * Example:
 * await logout();
 */
async function logout() {
    try {
        // Send logout request to backend
        await apiRequest('/user/logout', {
            method: 'POST',
        });

        // Clear local user state
        currentUser = null;

        // Update UI to reflect logged-out state
        updateAuthUI();
        showAlert('Logged out successfully!', 'info');
        showSection('home');

    } catch (error) {
        // Show error message to user
        showAlert(error.message, 'danger');
    }
}

/**
 * Check if user is currently authenticated.
 * 
 * This function verifies the user's authentication status by checking
 * the JWT cookie with the backend. It's used during app initialization
 * to determine if the user should see the dashboard or login form.
 * 
 * @returns {Promise<boolean>} True if user is authenticated, false otherwise
 * 
 * Example:
 * const isAuthenticated = await checkAuth();
 */
async function checkAuth() {
    try {
        // Check authentication status with backend
        const response = await apiRequest('/cookie');

        // Update global user state if authenticated
        currentUser = {
            id: response.userId,
            username: response.username,
            email: response.email
        };

        // Update UI to reflect authenticated state
        updateAuthUI();
        return true;
    } catch (error) {
        // User is not authenticated
        currentUser = null;
        updateAuthUI();
        return false;
    }
}

// Contest Functions
/**
 * Load all contests from the backend.
 * 
 * This function fetches contests without requiring authentication,
 * allowing non-logged-in users to view contests.
 * 
 * @returns {Promise<void>}
 */
async function loadContests() {
    try {
        // Load contests without authentication requirement
        // This allows non-logged-in users to view contests
        const response = await apiRequest('/contest');
        currentContests = response;
        displayContests();
    } catch (error) {
        // Show error but don't block the UI for non-logged-in users
        console.error('Failed to load contests:', error);
        showAlert('Failed to load contests: ' + error.message, 'danger');
    }
}

async function createContest(contestData) {
    // Check authentication before creating contest
    if (!currentUser) {
        showAlert('Please login to create a contest', 'warning');
        showSectionInternal('login');
        return;
    }
    
    try {
        const response = await apiRequest('/contest', {
            method: 'POST',
            body: JSON.stringify(contestData),
        });

        showAlert('Contest created successfully!', 'success');
        loadContests(); // Refresh contests list
        return response;
    } catch (error) {
        showAlert('Failed to create contest: ' + error.message, 'danger');
        throw error;
    }
}


/**
 * Display Autocomplete Results
 * 
 * @param {Array} users - Array of user objects with username
 * @param {HTMLElement} container - Container element for results
 * @param {Function} onSelect - Callback when user is selected
 */
function displayAutocompleteResults(users, container, onSelect) {
    if (users.length === 0) {
        container.innerHTML = `
            <div style="padding: 10px; text-align: center; color: #6c757d;">
                <i class="fas fa-search"></i> No users found
            </div>
        `;
        container.style.display = 'block';
        return;
    }

    // Clear previous content
    container.innerHTML = '';

    // Create and append each result item
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.style.cssText = `
            padding: 10px; 
            cursor: pointer; 
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s;
        `;

        item.innerHTML = `
            <i class="fas fa-user me-2 text-primary"></i>
            <strong>${user.username}</strong>
        `;

        // Add hover effects
        item.addEventListener('mouseenter', () => {
            item.style.backgroundColor = '#f8f9fa';
        });

        item.addEventListener('mouseleave', () => {
            item.style.backgroundColor = 'white';
        });

        // Add click handler
        item.addEventListener('click', () => {
            onSelect(user.username);
        });

        container.appendChild(item);
    });

    container.style.display = 'block';
}

/**
 * Enhanced Submit Create Contest
 * 
 * Yeh function existing submitCreateContest() function ko replace karega
 * Is me jury members hidden input se read honge
 */
async function submitCreateContest() {
    const form = document.getElementById('createContestForm');

    // Get form values
    const codeLinkElement = document.getElementById('codeLink');
    const codeLinkValue = codeLinkElement ? codeLinkElement.value.trim() : '';
    
    const contestData = {
        name: document.getElementById('contestName').value.trim(),
        project_name: document.getElementById('projectName').value.trim(),
        description: document.getElementById('contestDescription').value.trim(),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        // Get jury members from hidden input (comma-separated)
        jury_members: document.getElementById('juryMembers').value
            .split(',')
            .map(name => name.trim())
            .filter(name => name),
        marks_setting_accepted: parseInt(document.getElementById('marksAccepted').value) || 0,
        marks_setting_rejected: parseInt(document.getElementById('marksRejected').value) || 0,
        // Send null if code_link is empty (optional field)
        code_link: codeLinkValue || null
    };

    // Validate required fields
    if (!contestData.name) {
        showAlert('Contest name is required', 'warning');
        return;
    }

    if (!contestData.project_name) {
        showAlert('Project name is required', 'warning');
        return;
    }

    if (!contestData.start_date) {
        showAlert('Start date is required', 'warning');
        return;
    }

    if (!contestData.end_date) {
        showAlert('End date is required', 'warning');
        return;
    }

    if (contestData.jury_members.length === 0) {
        showAlert('At least one jury member is required', 'warning');
        return;
    }

    // Validate date logic
    if (new Date(contestData.start_date) >= new Date(contestData.end_date)) {
        showAlert('End date must be after start date', 'warning');
        return;
    }

    try {
        await createContest(contestData);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createContestModal'));
        modal.hide();

        // Clear form
        form.reset();

    } catch (error) {
        // Error already handled in createContest function
    }
}
// ============================================================================
// JURY AUTOCOMPLETE - COMPLETE WORKING VERSION
// Yeh code aapke app.js me add karo
// ============================================================================

// Global variable to store selected jury members
let selectedJuryMembers = [];

/**
 * Search Users API Call
 */
async function searchUsers(query) {
    if (!query || query.length < 2) {
        return [];
    }

    try {
        const response = await apiRequest(`/user/search?q=${encodeURIComponent(query)}&limit=10`);
        return response.users || [];
    } catch (error) {
        console.error('User search error:', error);
        return [];
    }
}

/**
 * Create Contest Modal with Jury Autocomplete
 * 
 * This function shows the create contest modal, but only if user is logged in.
 * If not logged in, redirects to login page.
 */
function showCreateContest() {
    // Check authentication before showing create contest modal
    if (!currentUser) {
        showAlert('Please login to create a contest', 'warning');
        showSectionInternal('login');
        return;
    }
    
    const modalHTML = `
        <div class="modal fade" id="createContestModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Contest</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createContestForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="contestName" class="form-label">Contest Name *</label>
                                    <input type="text" class="form-control" id="contestName" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="projectName" class="form-label">Project Name *</label>
                                    <input type="text" class="form-control" id="projectName" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="contestDescription" class="form-label">Description</label>
                                <textarea class="form-control" id="contestDescription" rows="3"></textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="startDate" class="form-label">Start Date *</label>
                                    <input type="date" class="form-control" id="startDate" required>
                                    <div class="form-text">Contest will be categorized based on dates</div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="endDate" class="form-label">End Date *</label>
                                    <input type="date" class="form-control" id="endDate" required>
                                    <div class="form-text">Must be after start date</div>
                                </div>
                            </div>
                            
                            <!-- JURY MEMBERS WITH AUTOCOMPLETE -->
                            <div class="mb-3">
                                <label for="juryInput" class="form-label">
                                    Jury Members * 
                                    <span class="badge bg-info text-dark">Type to search users</span>
                                </label>
                                
                                <!-- Selected Jury Members Display -->
                                <div id="selectedJuryMembers" class="mb-2" style="min-height: 40px; border: 1px solid #dee2e6; border-radius: 0.375rem; padding: 8px; background-color: #f8f9fa;">
                                    <small class="text-muted">No jury members selected yet</small>
                                </div>
                                
                                <!-- Jury Input with Autocomplete -->
                                <div style="position: relative;">
                                    <input 
                                        type="text" 
                                        class="form-control" 
                                        id="juryInput" 
                                        placeholder="Type username to search..."
                                        autocomplete="off"
                                    >
                                    <!-- Autocomplete Dropdown -->
                                    <div id="juryAutocomplete" 
                                         style="position: absolute; 
                                                top: 100%; 
                                                left: 0; 
                                                right: 0; 
                                                background: white; 
                                                border: 1px solid #dee2e6; 
                                                border-top: none;
                                                border-radius: 0 0 0.375rem 0.375rem;
                                                max-height: 200px; 
                                                overflow-y: auto; 
                                                z-index: 1000;
                                                display: none;
                                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                    </div>
                                </div>
                                
                                <div class="form-text">
                                    <i class="fas fa-info-circle"></i> 
                                    Type to search and click to add jury members. At least one member required.
                                </div>
                                
                                <!-- Hidden input to store selected usernames -->
                                <input type="hidden" id="juryMembers">
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="marksAccepted" class="form-label">Points for Accepted Submissions</label>
                                    <input type="number" class="form-control" id="marksAccepted" value="10" min="0">
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="marksRejected" class="form-label">Points for Rejected Submissions</label>
                                    <input type="number" class="form-control" id="marksRejected" value="0" min="0">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="codeLink" class="form-label">Code Repository Link <span class="text-muted">(Optional)</span></label>
                                <input type="text" class="form-control" id="codeLink" placeholder="https://github.com/...">
                                <div class="form-text">Leave empty if not applicable</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="submitCreateContest()">Create Contest</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal
    const existingModal = document.getElementById('createContestModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createContestModal'));
    modal.show();

    // Set default dates
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);

    document.getElementById('startDate').value = tomorrow.toISOString().split('T')[0];
    document.getElementById('endDate').value = nextWeek.toISOString().split('T')[0];

    // Reset selected jury members
    selectedJuryMembers = [];

    // Initialize jury autocomplete
    initializeJuryAutocomplete();
}

/**
 * Initialize Jury Autocomplete
 */
function initializeJuryAutocomplete() {
    const juryInput = document.getElementById('juryInput');
    const juryAutocomplete = document.getElementById('juryAutocomplete');

    if (!juryInput || !juryAutocomplete) {
        console.error('Jury input elements not found');
        return;
    }

    let searchTimeout = null;

    // Input event handler
    juryInput.addEventListener('input', async function (e) {
        const query = e.target.value.trim();

        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        // Hide dropdown if query is too short
        if (query.length < 2) {
            juryAutocomplete.style.display = 'none';
            return;
        }

        // Debounce search
        searchTimeout = setTimeout(async () => {
            try {
                const users = await searchUsers(query);

                // Filter out already selected users
                const availableUsers = users.filter(
                    user => !selectedJuryMembers.includes(user.username)
                );

                // Display results
                displayJuryAutocomplete(availableUsers);

            } catch (error) {
                console.error('Autocomplete search error:', error);
            }
        }, 300);
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function (e) {
        if (!juryInput.contains(e.target) && !juryAutocomplete.contains(e.target)) {
            juryAutocomplete.style.display = 'none';
        }
    });
}

/**
 * Display Autocomplete Results
 */
function displayJuryAutocomplete(users) {
    const container = document.getElementById('juryAutocomplete');

    if (!container) return;

    // Clear previous results
    container.innerHTML = '';

    if (users.length === 0) {
        container.innerHTML = `
            <div style="padding: 10px; text-align: center; color: #6c757d;">
                <i class="fas fa-search"></i> No users found
            </div>
        `;
        container.style.display = 'block';
        return;
    }

    // Create result items
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.style.cssText = `
            padding: 10px; 
            cursor: pointer; 
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s;
        `;

        item.innerHTML = `
            <i class="fas fa-user me-2 text-primary"></i>
            <strong>${user.username}</strong>
        `;

        // Hover effects
        item.addEventListener('mouseenter', function () {
            this.style.backgroundColor = '#f8f9fa';
        });

        item.addEventListener('mouseleave', function () {
            this.style.backgroundColor = 'white';
        });

        // Click handler - ADD JURY MEMBER
        item.addEventListener('click', function () {
            addJuryMember(user.username);
        });

        container.appendChild(item);
    });

    container.style.display = 'block';
}

/**
 * Add Jury Member
 */
function addJuryMember(username) {
    if (!selectedJuryMembers.includes(username)) {
        selectedJuryMembers.push(username);
        updateJuryDisplay();

        // Clear input and hide dropdown
        const juryInput = document.getElementById('juryInput');
        if (juryInput) {
            juryInput.value = '';
        }

        const juryAutocomplete = document.getElementById('juryAutocomplete');
        if (juryAutocomplete) {
            juryAutocomplete.style.display = 'none';
        }
    }
}

/**
 * Remove Jury Member
 */
function removeJuryMember(username) {
    selectedJuryMembers = selectedJuryMembers.filter(u => u !== username);
    updateJuryDisplay();
}

/**
 * Update Jury Members Display
 */
function updateJuryDisplay() {
    const selectedDisplay = document.getElementById('selectedJuryMembers');
    const hiddenInput = document.getElementById('juryMembers');

    if (!selectedDisplay) return;

    if (selectedJuryMembers.length === 0) {
        selectedDisplay.innerHTML = '<small class="text-muted">No jury members selected yet</small>';
        if (hiddenInput) {
            hiddenInput.value = '';
        }
        return;
    }

    selectedDisplay.innerHTML = selectedJuryMembers.map(username => `
        <span class="badge bg-primary me-2 mb-2" style="font-size: 0.9rem; cursor: pointer;">
            ${username}
            <i class="fas fa-times ms-1" onclick="removeJuryMember('${username}')"></i>
        </span>
    `).join('');

    // Update hidden input
    if (hiddenInput) {
        hiddenInput.value = selectedJuryMembers.join(',');
    }
}

/**
 * Submit Create Contest
 */

async function submitCreateContest() {
    const form = document.getElementById('createContestForm');

    // Get form values
    const codeLinkElement = document.getElementById('codeLink');
    const codeLinkValue = codeLinkElement ? codeLinkElement.value.trim() : '';
    
    const contestData = {
        name: document.getElementById('contestName').value.trim(),
        project_name: document.getElementById('projectName').value.trim(),
        description: document.getElementById('contestDescription').value.trim(),
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        jury_members: selectedJuryMembers,
        marks_setting_accepted: parseInt(document.getElementById('marksAccepted').value) || 0,
        marks_setting_rejected: parseInt(document.getElementById('marksRejected').value) || 0,
        // Send null if code_link is empty (optional field)
        code_link: codeLinkValue || null
    };

    // Validate required fields
    if (!contestData.name) {
        showAlert('Contest name is required', 'warning');
        return;
    }

    if (!contestData.project_name) {
        showAlert('Project name is required', 'warning');
        return;
    }

    if (!contestData.start_date) {
        showAlert('Start date is required', 'warning');
        return;
    }

    if (!contestData.end_date) {
        showAlert('End date is required', 'warning');
        return;
    }

    if (contestData.jury_members.length === 0) {
        showAlert('At least one jury member is required', 'warning');
        return;
    }

    // Validate date logic
    if (new Date(contestData.start_date) >= new Date(contestData.end_date)) {
        showAlert('End date must be after start date', 'warning');
        return;
    }

    try {
        await createContest(contestData);

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createContestModal'));
        modal.hide();

        // Clear form
        form.reset();

    } catch (error) {
        // Error already handled in createContest function
    }
}

/**
 * Display contests in the UI, hiding points for non-logged-in users.
 * 
 * This function shows contest information but hides scoring details
 * (points, marks) for users who are not authenticated.
 * 
 * @param {string} category - Contest category ('current', 'upcoming', 'past')
 */
function displayContests(category = 'current') {
    const contestList = document.getElementById('contestList');
    const contests = currentContests[category] || [];

    // Check if user is logged in
    const isLoggedIn = currentUser !== null;

    if (contests.length === 0) {
        contestList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    No ${category} contests available.
                </div>
            </div>
        `;
        return;
    }

    contestList.innerHTML = contests.map(contest => `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${contest.name}</h5>
                    <p class="card-text">
                        <strong>Project:</strong> ${contest.project_name}<br>
                        <strong>Created by:</strong> ${contest.created_by}<br>
                        <strong>Submissions:</strong> ${contest.submission_count || 0}
                    </p>
                    ${contest.description ? `<p class="card-text text-muted">${contest.description.substring(0, 100)}${contest.description.length > 100 ? '...' : ''}</p>` : ''}
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary status-badge">${contest.status}</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewContest(${contest.id})">
                            View Details
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * View contest details in a modal.
 * 
 * This function displays contest information but hides scoring details
 * (points, marks) for non-logged-in users.
 * 
 * @param {number} contestId - ID of the contest to view
 */
async function viewContest(contestId) {
    try {
        const contest = await apiRequest(`/contest/${contestId}`);

        // Check if user is logged in to show/hide points
        const isLoggedIn = currentUser !== null;

        // Create modal for contest details
        const modalHTML = `
            <div class="modal fade" id="contestModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${contest.name}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Contest Details</h6>
                                    <p><strong>Project:</strong> ${contest.project_name}</p>
                                    <p><strong>Created by:</strong> ${contest.created_by}</p>
                                    <p><strong>Status:</strong> <span class="badge bg-primary">${contest.status}</span></p>
                                    ${contest.start_date ? `<p><strong>Start Date:</strong> ${new Date(contest.start_date).toLocaleDateString()}</p>` : ''}
                                    ${contest.end_date ? `<p><strong>End Date:</strong> ${new Date(contest.end_date).toLocaleDateString()}</p>` : ''}
                                </div>
                                <div class="col-md-6">
                                    ${isLoggedIn ? `
                                        <h6>Scoring</h6>
                                        <p><strong>Accepted:</strong> ${contest.marks_setting_accepted} points</p>
                                        <p><strong>Rejected:</strong> ${contest.marks_setting_rejected} points</p>
                                        <p><strong>Submissions:</strong> ${contest.submission_count}</p>
                                    ` : `
                                        <h6>Information</h6>
                                        <p><strong>Submissions:</strong> ${contest.submission_count}</p>
                                        <p class="text-muted"><small>Login to view scoring details</small></p>
                                    `}
                                </div>
                            </div>
                            ${contest.description ? `<div class="mt-3"><h6>Description</h6><p>${contest.description}</p></div>` : ''}
                            ${contest.jury_members && contest.jury_members.length > 0 ? `
                                <div class="mt-3">
                                    <h6>Jury Members</h6>
                                    <p>${contest.jury_members.join(', ')}</p>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            ${contest.status === 'current' && currentUser ? `
                                <button class="btn btn-primary" onclick="submitToContest(${contest.id})">
                                    Submit Article
                                </button>
                            ` : ''}
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('contestModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('contestModal'));
        modal.show();

    } catch (error) {
        showAlert('Failed to load contest details: ' + error.message, 'danger');
    }
}

/**
 * Show the article submission modal.
 * 
 * This function creates and displays a beautiful Bootstrap modal for submitting
 * an article to a contest. The modal includes form fields for article title and URL.
 * 
 * @param {number} contestId - The ID of the contest to submit to
 */
function showSubmitArticleModal(contestId) {
    // Create modal HTML with Bootstrap styling
    const modalHTML = `
        <div class="modal fade" id="submitArticleModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-paper-plane me-2"></i>Submit Article
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="submitArticleForm">
                            <div class="mb-3">
                                <label for="articleTitle" class="form-label">
                                    <i class="fas fa-heading me-2 text-primary"></i>Article Title <span class="text-danger">*</span>
                                </label>
                                <input 
                                    type="text" 
                                    class="form-control" 
                                    id="articleTitle" 
                                    placeholder="Enter the title of your article"
                                    required
                                    autofocus
                                >
                                <div class="form-text">Enter a descriptive title for your article</div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="articleUrl" class="form-label">
                                    <i class="fas fa-link me-2 text-primary"></i>Article URL <span class="text-danger">*</span>
                                </label>
                                <input 
                                    type="url" 
                                    class="form-control" 
                                    id="articleUrl" 
                                    placeholder="https://example.com/article"
                                    required
                                >
                                <div class="form-text">Enter the full URL of your article (must start with http:// or https://)</div>
                            </div>
                            
                            <div id="submitArticleError" class="alert alert-danger d-none" role="alert"></div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Cancel
                        </button>
                        <button type="button" class="btn btn-primary" id="submitArticleBtn" onclick="processArticleSubmission(${contestId})">
                            <i class="fas fa-paper-plane me-2"></i>Submit Article
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if it exists
    const existingModal = document.getElementById('submitArticleModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add new modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Get modal element after it's added to DOM
    const submitModalElement = document.getElementById('submitArticleModal');

    // Listen for when modal is shown to apply white background
    submitModalElement.addEventListener('shown.bs.modal', function () {
        // Add class to body to trigger white background CSS
        document.body.classList.add('submit-modal-open');
    });

    // Show modal
    const modal = new bootstrap.Modal(submitModalElement);
    modal.show();

    // Clear form when modal is hidden
    const modalElement = document.getElementById('submitArticleModal');
    modalElement.addEventListener('hidden.bs.modal', function () {
        const form = document.getElementById('submitArticleForm');
        if (form) {
            form.reset();
        }
        const errorDiv = document.getElementById('submitArticleError');
        if (errorDiv) {
            errorDiv.classList.add('d-none');
        }

        // Remove white background class from body
        document.body.classList.remove('submit-modal-open');
    });

    // Allow form submission on Enter key
    const form = document.getElementById('submitArticleForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            processArticleSubmission(contestId);
        });
    }
}

/**
 * Process article submission to a contest.
 * 
 * This function validates the form data, sends the submission to the backend,
 * and handles success/error responses. It shows a success message when the
 * submission is successful.
 * 
 * @param {number} contestId - The ID of the contest to submit to
 */
async function processArticleSubmission(contestId) {
    // Get form elements
    const titleInput = document.getElementById('articleTitle');
    const urlInput = document.getElementById('articleUrl');
    const submitBtn = document.getElementById('submitArticleBtn');
    const errorDiv = document.getElementById('submitArticleError');
    const form = document.getElementById('submitArticleForm');

    // Hide previous errors
    if (errorDiv) {
        errorDiv.classList.add('d-none');
        errorDiv.textContent = '';
    }

    // Get and trim input values
    const articleTitle = titleInput ? titleInput.value.trim() : '';
    const articleLink = urlInput ? urlInput.value.trim() : '';

    // Validate title
    if (!articleTitle) {
        if (errorDiv) {
            errorDiv.textContent = 'Please enter an article title';
            errorDiv.classList.remove('d-none');
        }
        if (titleInput) {
            titleInput.focus();
        }
        return;
    }

    // Validate URL
    if (!articleLink) {
        if (errorDiv) {
            errorDiv.textContent = 'Please enter an article URL';
            errorDiv.classList.remove('d-none');
        }
        if (urlInput) {
            urlInput.focus();
        }
        return;
    }

    // Validate URL format - must start with http:// or https://
    if (!articleLink.startsWith('http://') && !articleLink.startsWith('https://')) {
        if (errorDiv) {
            errorDiv.textContent = 'Article URL must start with http:// or https://';
            errorDiv.classList.remove('d-none');
        }
        if (urlInput) {
            urlInput.focus();
        }
        return;
    }

    // Show loading state
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';

        try {
            // Send submission to backend API
            const response = await apiRequest(`/contest/${contestId}/submit`, {
                method: 'POST',
                body: JSON.stringify({
                    article_title: articleTitle,
                    article_link: articleLink
                }),
            });

            // Close the submission modal
            const submitModal = document.getElementById('submitArticleModal');
            if (submitModal) {
                const modalInstance = bootstrap.Modal.getInstance(submitModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }

            // Close the contest modal if it's open
            const contestModal = document.getElementById('contestModal');
            if (contestModal) {
                const modalInstance = bootstrap.Modal.getInstance(contestModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }

            // Show success message
            showAlert('Article submitted successfully!', 'success');

            // Refresh contest list to show updated submission count
            loadContests();

        } catch (error) {
            // Submission failed - show error message
            if (errorDiv) {
                errorDiv.textContent = 'Failed to submit article: ' + error.message;
                errorDiv.classList.remove('d-none');
            }
            showAlert('Failed to submit article: ' + error.message, 'danger');

            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
}

/**
 * Submit an article to a contest (wrapper function for button onclick).
 * 
 * This function is called when the user clicks the "Submit Article" button.
 * It opens the submission modal instead of using browser prompts.
 * 
 * @param {number} contestId - The ID of the contest to submit to
 */
function submitToContest(contestId) {
    // Check authentication before submitting article
    if (!currentUser) {
        showAlert('Please login to submit an article', 'warning');
        showSectionInternal('login');
        return;
    }
    
    // Show the beautiful submission modal
    showSubmitArticleModal(contestId);
}

// Dashboard Functions
async function loadDashboard() {
    // Authentication check is already done in showSection() before calling this function
    // But we keep this check as a safety measure
    if (!currentUser) {
        showAlert('Please login to view dashboard', 'warning');
        showSectionInternal('login');
        return;
    }

    try {
        const response = await apiRequest('/user/dashboard');
        displayDashboard(response);
    } catch (error) {
        showAlert('Failed to load dashboard: ' + error.message, 'danger');
    }
}

function displayDashboard(data) {
    const dashboardContent = document.getElementById('dashboardContent');

    dashboardContent.innerHTML = `
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Total Score</h5>
                        <h2 class="text-primary">${data.total_score}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Created Contests</h5>
                        <h2 class="text-success">${data.created_contests.length}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Jury Member</h5>
                        <h2 class="text-warning">${data.jury_contests.length}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <h4>Recent Submissions</h4>
                <div class="card">
                    <div class="card-body">
                        ${data.submissions_by_contest.length > 0 ?
            data.submissions_by_contest.map(contest => `
                                <div class="mb-3">
                                    <h6>${contest.contest_name}</h6>
                                    ${contest.submissions.map(submission => `
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <span>${submission.article_title}</span>
                                            <span class="badge bg-${submission.status === 'accepted' ? 'success' : submission.status === 'rejected' ? 'danger' : 'warning'}">${submission.status}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            `).join('') :
            '<p class="text-muted">No submissions yet.</p>'
        }
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <h4>Contest Scores</h4>
                <div class="card">
                    <div class="card-body">
                        ${data.contest_wise_scores.length > 0 ?
            data.contest_wise_scores.map(score => `
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span>${score.contest_name}</span>
                                    <span class="badge bg-primary">${score.contest_score} points</span>
                                </div>
                            `).join('') :
            '<p class="text-muted">No scores yet.</p>'
        }
                    </div>
                </div>
            </div>
        </div>
    `;
}

// UI Functions
// List of sections that require authentication
const PROTECTED_SECTIONS = ['contests', 'dashboard', 'profile'];

/**
 * Show a section with authentication check.
 * 
 * If the section requires authentication and user is not logged in,
 * redirects to login page with a message.
 * 
 * @param {string} sectionName - Name of the section to show
 */
function showSection(sectionName) {
    // Check if section requires authentication
    if (PROTECTED_SECTIONS.includes(sectionName) && !currentUser) {
        showAlert('Please login to access this page', 'warning');
        showSectionInternal('login');
        return;
    }

    // Show the section
    showSectionInternal(sectionName);
}

/**
 * Internal function to show a section (without auth check).
 * 
 * @param {string} sectionName - Name of the section to show
 */
function showSectionInternal(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.add('hidden'));

    // Show selected section
    const targetSection = document.getElementById(sectionName + 'Section');
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }

    // Load section-specific data
    if (sectionName === 'contests') {
        loadContests();
    } else if (sectionName === 'dashboard') {
        loadDashboard();
    }
}

/**
 * Update UI elements based on authentication status.
 * 
 * This function shows/hides authentication-related UI elements
 * and the "Create Contest" button based on whether user is logged in.
 */
function updateAuthUI() {
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const userName = document.getElementById('userName');
    const createContestBtn = document.getElementById('createContestBtn');

    if (currentUser) {
        // User is logged in - show user menu, hide login buttons
        authButtons.classList.add('hidden');
        userMenu.classList.remove('hidden');
        userName.textContent = currentUser.username;

        // Show "Create Contest" button for logged-in users
        if (createContestBtn) {
            createContestBtn.classList.remove('hidden');
        }
    } else {
        // User is not logged in - show login buttons, hide user menu
        authButtons.classList.remove('hidden');
        userMenu.classList.add('hidden');

        // Hide "Create Contest" button for non-logged-in users
        if (createContestBtn) {
            createContestBtn.classList.add('hidden');
        }
    }
}

function showContestCategory(category) {
    // Update active tab
    document.querySelectorAll('#contestTabs .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // Display contests for category
    displayContests(category);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function () {
    // Check authentication status
    checkAuth();

    // Login form
    document.getElementById('loginForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        try {
            await login(email, password);
        } catch (error) {
            // Error already handled in login function
        }
    });

    // Register form
    document.getElementById('registerForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;

        try {
            await register(username, email, password);
        } catch (error) {
            // Error already handled in register function
        }
    });

    // Show home section by default
    showSection('home');
});
