// Authentication state
let currentUser = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    const authModal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const authTabs = document.querySelectorAll('.auth-tab');
    const avatarOptions = document.querySelectorAll('.avatar-option');

    // Tab switching
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetForm = tab.dataset.tab;
            authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            if (targetForm === 'login') {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
        });
    });

    // Avatar selection
    let selectedIcon = null;
    avatarOptions.forEach(icon => {
        icon.addEventListener('click', () => {
            avatarOptions.forEach(i => i.classList.remove('selected'));
            icon.classList.add('selected');
            selectedIcon = icon.dataset.icon;
            document.getElementById('avatar-url').value = ''; // Clear URL when icon is selected
        });
    });

    // Login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (response.ok) {
                currentUser = data.user;
                authModal.style.display = 'none';
                updateUIForAuthenticatedUser();
                showNotification('Login successful!', 'success');
            } else {
                showNotification(data.message || 'Login failed', 'error');
            }
        } catch (error) {
            showNotification('An error occurred during login', 'error');
            console.error('Login error:', error);
        }
    });

    // Register form submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const password = document.getElementById('register-password').value;

        const userData = {
            username,
            password,
            avatar: 'default.png'
        };

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            
            if (response.ok) {
                currentUser = data;
                authModal.style.display = 'none';
                updateUIForAuthenticatedUser();
                showNotification('Registration successful!', 'success');
            } else {
                showNotification(data.error || 'Registration failed', 'error');
            }
        } catch (error) {
            showNotification('An error occurred during registration', 'error');
            console.error('Registration error:', error);
        }
    });
});

// Helper functions
function updateUIForAuthenticatedUser() {
    if (currentUser) {
        // Update navigation
        const nav = document.querySelector('.nav-links');
        const userSection = document.createElement('li');
        userSection.innerHTML = `
            <a href="#" class="user-profile">
                ${currentUser.avatar.startsWith('fa-') 
                    ? `<i class="fas ${currentUser.avatar}"></i>` 
                    : `<img src="${currentUser.avatar}" alt="${currentUser.username}">`}
                ${currentUser.username}
            </a>
        `;
        nav.appendChild(userSection);
        
        // Enable restricted features
        document.querySelectorAll('.requires-auth').forEach(el => {
            el.classList.remove('disabled');
        });
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Export authentication state
export { currentUser }; 