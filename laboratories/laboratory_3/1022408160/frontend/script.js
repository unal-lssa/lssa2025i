
// --- Configuration ---
const GATEWAY_URL = 'http://localhost:5001';

// --- DOM Elements ---
const loginSection = document.getElementById('login-section');
const appSection = document.getElementById('app-section');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const appError = document.getElementById('app-error');
const welcomeTitle = document.getElementById('welcome-title');
const seeMeetingsBtn = document.getElementById('see-meetings-btn');
const extraMeetingsBtn = document.getElementById('extra-meetings-btn');
const meetingsOutput = document.getElementById('meetings-output');
const logoutBtn = document.getElementById('logout-btn'); // <-- Get reference to logout button

// --- State ---
// These are mostly for convenience now, primary source of truth after login is localStorage
let jwtToken = null;
let userRole = null;
let username = null;

// --- Functions ---


function parseJwt (token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload);
}


function displayError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
}

function clearError(element) {
    element.textContent = '';
    element.style.display = 'none';
}

async function handleLogin(event) {
    event.preventDefault();
    clearError(loginError);

    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;

    try {
        const response = await fetch(`${GATEWAY_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({ username: usernameInput, password: passwordInput }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }

        if (data.token) {
            // Decode token client-side to get username/role
            try {
                const decodedToken = parseJwt(data.token);
                // Store token and user info in localStorage
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('username', decodedToken.username);
                localStorage.setItem('userRole', decodedToken.role); // Assuming role is in token
                showAppView();
            } catch (decodeError) {
                 console.error('Failed to decode token:', decodeError);
                 displayError(loginError, 'Login successful, but failed to process user details.');
            }
        } else {
            displayError(loginError, data.message || 'Login failed: No token received.');
        }

    } catch (error) {
        console.error('Login error:', error);
        displayError(loginError, `Login failed: ${error.message}`);
    }
}
function handleMeetingType(endpoint, meetings) {
    // if enpdpoint is "meetings" then show meetings
    if (endpoint === "meetings") {
        let outputHtml = '<ul>';
        meetings.forEach(meeting => {
            outputHtml += `<li><b>${meeting.title || 'No Title'}</b> 
                (${new Date(meeting.start_time).toLocaleString()}) - 
                ${meeting.location || 'N/A'} - ${meeting.description || 'N/A'} </li>`;
        });
        outputHtml += '</ul>';
        meetingsOutput.innerHTML = outputHtml;
    }
    else if (endpoint === "extra-meetings") {
        let outputHtml = '<ul>';
        meetings.forEach(meeting => {
            outputHtml += `<li><b>${meeting.secret_meeting_id || 'No ID'}</b> 
            (${new Date(meeting.scheduled_time).toLocaleString()}) -
             ${meeting.location_details || 'N/A'} - 
             ${meeting.objective || 'N/A'} -
             Security Level: ${meeting.security_level || 'N/A'}
             </li>`;
        });
        outputHtml += '</ul>';
        meetingsOutput.innerHTML = outputHtml;
    };   
}
async function fetchMeetings(endpoint) {
    clearError(appError);
    meetingsOutput.innerHTML = 'Loading...';

    const storedToken = localStorage.getItem('authToken');
    if (!storedToken) {
        displayError(appError, 'Error: Not logged in or token missing.');
        showLoginView();
        return;
    }

    try {
        const response = await fetch(`${GATEWAY_URL}/${endpoint}`, {
            method: 'GET',
            headers: { 'Authorization': `${storedToken}` },
        });

        if (!response.ok) {
            let errorMsg = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                errorMsg = errorData.error || errorData.message || errorMsg;
                if(errorData.upstream_details) { errorMsg += ` (Upstream: ${JSON.stringify(errorData.upstream_details)})`; }
            } catch (parseError) { /* Ignore if response not JSON */ }
            throw new Error(errorMsg);
        }

        const meetings = await response.json();
        if (meetings && meetings.length > 0) {
            if (endpoint === "meetings") {
                let outputHtml = '<ul>';
                meetings.forEach(meeting => {
                    outputHtml += `<li><b>${meeting.title || 'No Title'}</b> 
                        (${new Date(meeting.start_time).toLocaleString()}) - 
                        ${meeting.location || 'N/A'} - ${meeting.description || 'N/A'} </li>`;
                });
                outputHtml += '</ul>';
                meetingsOutput.innerHTML = outputHtml;
            }
            else if (endpoint === "extra-meetings") {
                let outputHtml = '<ul>';
                meetings.forEach(meeting => {
                    outputHtml += `<li><b>${meeting.codename || 'No Title'}</b> (${new Date(meeting.scheduled_time).toLocaleString()}) -
                     ${meeting.location_details || 'N/A'} - ${meeting.objective || 'N/A'} -
                     Security Level: ${meeting.security_level || 'N/A'}
                     </li>`;
                });
                outputHtml += '</ul>';
                meetingsOutput.innerHTML = outputHtml;
            }  
        } else {
            meetingsOutput.innerHTML = 'No meetings found.';
        }

    } catch (error) {
        console.error('Failed to fetch meetings:', error);
        displayError(appError, `Failed to fetch meetings: ${error.message}`);
        meetingsOutput.innerHTML = 'Could not load meetings data.';
        if (error.message.includes('401') || error.message.includes('403')) {
             handleLogout(); // If unauthorized, perform logout
        }
    }
}

async function handleMeetings() {
    await fetchMeetings("meetings");
};

async function handleExtraMeetings() {
    await fetchMeetings("extra-meetings");
};

// --- NEW: Logout Handler ---
function handleLogout() {
    console.log("Logging out...");
    // Remove token and user info from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');

    // Clear in-memory state (optional but good practice)
    jwtToken = null;
    userRole = null;
    username = null;

    // Switch back to login view
    showLoginView();
}
// --- END NEW ---


function showAppView() {
    // Read directly from localStorage when showing the view
    const storedRole = localStorage.getItem('userRole');
    const storedUsername = localStorage.getItem('username');
    if (storedRole && storedUsername) {
        welcomeTitle.textContent = `Welcome, ${storedUsername} (Role: ${storedRole})`;
        loginSection.style.display = 'none';
        appSection.style.display = 'block';
        clearError(loginError);
        clearError(appError);
        meetingsOutput.innerHTML = '';
    } else {
        showLoginView(); // If info missing, force login
    }
}

function showLoginView() {
    welcomeTitle.textContent = 'Welcome!'; // Reset title
    loginSection.style.display = 'block';
    appSection.style.display = 'none';
    // Clear localStorage just in case logout wasn't called explicitly
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');
    // Clear in-memory state
    jwtToken = null;
    userRole = null;
    username = null;
    // Reset form fields
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    // Clear errors and outputs
    clearError(loginError);
    clearError(appError);
    meetingsOutput.innerHTML = '';
}

// --- Initialization and Event Listeners ---

loginForm.addEventListener('submit', handleLogin);
seeMeetingsBtn.addEventListener('click', handleMeetings);
extraMeetingsBtn.addEventListener('click', handleExtraMeetings);
logoutBtn.addEventListener('click', handleLogout); // <-- Add listener for logout button

// --- Initial Check ---
// Check if valid info exists in localStorage on page load
const existingToken = localStorage.getItem('authToken');
const existingRole = localStorage.getItem('userRole');
const existingUsername = localStorage.getItem('username');

// Basic check: In a real app, you might validate token expiry here too
if (existingToken && existingRole && existingUsername) {
    // Optionally decode here to re-populate state vars if needed,
    // but showAppView reads directly from localStorage anyway
    showAppView();
} else {
    showLoginView(); // Default to login view
}