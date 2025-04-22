document.addEventListener('DOMContentLoaded', () => {
    fetchLeaderboard();
    setupNavigation();
    setupNewSessionForm();
    setupTimeFilters();
    loadDashboard();
    setupProfileModal();
    setupProfilePictureChange();
    setupFriendSystem();
});

// Navigation setup
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.dataset.page;

            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show target page
            pages.forEach(page => {
                page.classList.remove('active');
                if (page.id === targetPage) {
                    page.classList.add('active');
                }
            });
        });
    });
}

// New Session Form setup
function setupNewSessionForm() {
    const form = document.getElementById('new-session-form');
    const playersList = document.getElementById('players-list');
    const addPlayerBtn = document.getElementById('add-player-btn');
    let players = [];

    // Set current date by default
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    document.getElementById('session-date').value = formattedDate;

    // Add player button handler
    addPlayerBtn.addEventListener('click', () => {
        const playerName = prompt('Enter player name:');
        if (playerName && !players.includes(playerName)) {
            players.push(playerName);
            updatePlayersList();
        }
    });

    // Update players list display
    function updatePlayersList() {
        playersList.innerHTML = '';
        players.forEach(player => {
            const playerDiv = document.createElement('div');
            playerDiv.className = 'player-item';
            playerDiv.innerHTML = `
                <span>${player}</span>
                <button class="btn btn-danger" onclick="removePlayer('${player}')">×</button>
            `;
            playersList.appendChild(playerDiv);
        });
    }

    // Remove player function
    window.removePlayer = (playerName) => {
        players = players.filter(p => p !== playerName);
        updatePlayersList();
    };

    // Form submission handler
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const sessionData = {
            date: document.getElementById('session-date').value,
            buy_in_amount: parseFloat(document.getElementById('buy-in').value),
            notes: document.getElementById('notes').value,
            players: players
        };

        try {
            const response = await fetch('/api/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(sessionData)
            });

            if (response.ok) {
                alert('Session created successfully!');
                form.reset();
                // Reset date to current date
                document.getElementById('session-date').value = formattedDate;
                players = [];
                updatePlayersList();
                // Switch to dashboard
                document.querySelector('[data-page="dashboard"]').click();
            } else {
                throw new Error('Failed to create session');
            }
        } catch (error) {
            console.error('Error creating session:', error);
            alert('Failed to create session. Please try again.');
        }
    });
}

// Load dashboard data
async function loadDashboard(days = 1) {
    try {
        const response = await fetch(`/api/dashboard?days=${days}`);
        if (response.ok) {
            const data = await response.json();
            updateDashboardUI(data);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update dashboard UI
function updateDashboardUI(data) {
    // Update profile summary
    document.getElementById('dashboard-total-sessions').textContent = data.total_sessions || 0;
    document.getElementById('dashboard-win-rate').textContent = `${data.win_rate || 0}%`;
    document.getElementById('dashboard-total-profit').textContent = `$${data.total_profit || 0}`;

    // Update game statistics
    document.getElementById('best-session').textContent = `$${data.best_session || 0}`;
    document.getElementById('worst-session').textContent = `$${data.worst_session || 0}`;
    document.getElementById('avg-profit').textContent = `$${data.avg_profit || 0}`;

    // Update recent sessions
    const sessionsList = document.getElementById('recent-sessions-list');
    if (data.recent_sessions && data.recent_sessions.length > 0) {
        sessionsList.innerHTML = data.recent_sessions.map(session => `
            <div class="session-item">
                <span class="session-date">${session.date}</span>
                <span class="session-profit ${session.profit_loss >= 0 ? 'positive' : 'negative'}">
                    $${session.profit_loss.toFixed(2)}
                </span>
            </div>
        `).join('');
    } else {
        sessionsList.innerHTML = '<p>No recent sessions</p>';
    }

    // Update profit chart if data exists
    if (data.profit_chart) {
        updateProfitChart(data.profit_chart);
    }
}

// Update profit chart
function updateProfitChart(data) {
    const ctx = document.getElementById('profitChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.profitChart) {
        window.profitChart.destroy();
    }

    // Calculate cumulative profit
    let runningTotal = 0;
    const cumulativeData = data.data.map(value => {
        runningTotal += value;
        return runningTotal;
    });

    window.profitChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Daily Profit/Loss',
                    data: data.data,
                    borderColor: 'rgba(75, 192, 192, 0.5)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    yAxisID: 'y'
                },
                {
                    label: 'Cumulative Profit',
                    data: cumulativeData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Daily Profit/Loss'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Cumulative Profit'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '$' + context.parsed.y.toFixed(2);
                            return label;
                        }
                    }
                }
            }
        }
    });
}

// Setup time filter buttons
function setupTimeFilters() {
    const buttons = document.querySelectorAll('.time-filters .btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active state
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Load data for selected time period
            const days = parseInt(button.dataset.days);
            loadDashboard(days);
        });
    });
}

// Fetch leaderboard data
async function fetchLeaderboard() {
    try {
        const response = await fetch('/api/leaderboard');
        if (response.ok) {
            const data = await response.json();
            updateLeaderboard(data);
            updateDashboardLeaderboard(data);
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
    }
}

// Update leaderboard UI
function updateLeaderboard(data) {
    const leaderboardList = document.getElementById('leaderboardList');
    if (data && data.length > 0) {
        leaderboardList.innerHTML = data.map((player, index) => `
            <div class="player-item">
                <div class="player-info">
                    <div class="player-avatar">
                        <img src="${player.avatar || '/static/default-avatar.png'}" alt="${player.username}">
                    </div>
                    <div class="player-details">
                        <div class="player-name">${player.username}</div>
                        <div class="player-score ${player.total_profit >= 0 ? 'positive' : 'negative'}">
                            $${player.total_profit.toFixed(2)}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        leaderboardList.innerHTML = '<p>No players found</p>';
    }
}

function updateDashboardLeaderboard(data) {
    const dashboardLeaderboard = document.getElementById('dashboard-leaderboard');
    if (data && data.length > 0) {
        // Show only top 5 players in the dashboard
        const topPlayers = data.slice(0, 5);
        dashboardLeaderboard.innerHTML = topPlayers.map((player, index) => `
            <div class="player-item">
                <div class="player-info">
                    <div class="player-avatar">
                        <img src="${player.avatar || '/static/default-avatar.png'}" alt="${player.username}">
                    </div>
                    <div class="player-details">
                        <div class="player-name">${player.username}</div>
                        <div class="player-score ${player.total_profit >= 0 ? 'positive' : 'negative'}">
                            $${player.total_profit.toFixed(2)}
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        dashboardLeaderboard.innerHTML = '<p>No players found</p>';
    }
}

// Refresh leaderboard every minute
setInterval(fetchLeaderboard, 60000);

// Profile Modal Setup
function setupProfileModal() {
    const profileButton = document.querySelector('.profile-button');
    const modal = document.getElementById('profile-modal');
    const closeButton = document.getElementById('close-profile-modal');
    const saveButton = document.getElementById('save-profile');
    const avatarUpload = document.getElementById('avatar-upload');
    const currentAvatar = document.getElementById('current-avatar');
    const navProfilePic = document.getElementById('nav-profile-pic');
    const dashboardProfilePic = document.getElementById('dashboard-profile-pic');

    // Open modal
    profileButton.addEventListener('click', (e) => {
        e.preventDefault();
        modal.style.display = 'block';
    });

    // Close modal
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Handle avatar upload
    avatarUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const newAvatar = e.target.result;
                currentAvatar.src = newAvatar;
                navProfilePic.src = newAvatar;
                dashboardProfilePic.src = newAvatar;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle save changes
    saveButton.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const avatarData = currentAvatar.src;

        try {
            const response = await fetch('/api/profile/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    avatar: avatarData
                })
            });

            if (response.ok) {
                // Update UI with new profile data
                document.getElementById('dashboard-username').textContent = username;
                modal.style.display = 'none';
            } else {
                throw new Error('Failed to update profile');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('Failed to update profile. Please try again.');
        }
    });
}

function setupProfilePictureChange() {
    const changeProfileBtn = document.getElementById('change-profile-btn');
    const modal = document.getElementById('profile-modal');
    const closeButton = document.getElementById('close-profile-modal');
    const saveButton = document.getElementById('save-profile');
    const avatarUpload = document.getElementById('avatar-upload');
    const currentAvatar = document.getElementById('current-avatar');
    const navProfilePic = document.getElementById('nav-profile-pic');
    const dashboardProfilePic = document.getElementById('dashboard-profile-pic');

    // Open modal when clicking the change profile picture button
    changeProfileBtn.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    // Close modal
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Handle avatar upload
    avatarUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const newAvatar = e.target.result;
                currentAvatar.src = newAvatar;
                navProfilePic.src = newAvatar;
                dashboardProfilePic.src = newAvatar;
            };
            reader.readAsDataURL(file);
        }
    });

    // Handle save changes
    saveButton.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const avatarData = currentAvatar.src;

        try {
            const response = await fetch('/api/profile/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    avatar: avatarData
                })
            });

            if (response.ok) {
                // Update UI with new profile data
                document.getElementById('dashboard-username').textContent = username;
                modal.style.display = 'none';
            } else {
                throw new Error('Failed to update profile');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('Failed to update profile. Please try again.');
        }
    });
}

// Friend System Setup
function setupFriendSystem() {
    const addFriendBtn = document.getElementById('add-friend-btn');
    const friendModal = document.getElementById('add-friend-modal');
    const closeFriendModal = document.getElementById('close-friend-modal');
    const sendRequestBtn = document.getElementById('send-friend-request');
    const searchInput = document.getElementById('friend-username');
    const searchResults = document.getElementById('search-results');
    let selectedPlayerId = null;

    // Load initial friends and requests
    loadFriends();
    loadFriendRequests();

    // Setup search functionality with debounce
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                searchResults.innerHTML = '';
                return;
            }

            try {
                const response = await fetch(`/api/users/search?query=${encodeURIComponent(query)}`);
                if (response.ok) {
                    const users = await response.json();
                    displaySearchResults(users);
                }
            } catch (error) {
                console.error('Error searching users:', error);
            }
        }, 300);
    });

    function displaySearchResults(users) {
        if (users.length === 0) {
            searchResults.innerHTML = `
                <div class="search-empty-state">
                    <p>No users found</p>
                </div>
            `;
            return;
        }

        searchResults.innerHTML = users.map(user => `
            <div class="search-result-item" data-player-id="${user.player_id}">
                <img src="${user.avatar || '/static/default-avatar.png'}" alt="${user.username}" class="search-result-avatar">
                <div class="search-result-info">
                    <div class="search-result-username">${user.username}</div>
                    <div class="search-result-playerid">#${user.player_id}</div>
                </div>
            </div>
        `).join('');

        // Add click handlers to search results
        searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                selectedPlayerId = item.dataset.playerId;
                searchInput.value = item.querySelector('.search-result-username').textContent;
                searchResults.innerHTML = '';
            });
        });
    }

    // Open modal
    addFriendBtn.addEventListener('click', () => {
        friendModal.style.display = 'block';
        searchInput.value = '';
        searchResults.innerHTML = '';
        selectedPlayerId = null;
    });

    // Close modal
    closeFriendModal.addEventListener('click', () => {
        friendModal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === friendModal) {
            friendModal.style.display = 'none';
        }
    });

    // Send friend request
    sendRequestBtn.addEventListener('click', async () => {
        if (!selectedPlayerId) {
            alert('Please select a user from the search results');
            return;
        }

        try {
            const response = await fetch('/api/friends/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ player_id: selectedPlayerId })
            });

            if (response.ok) {
                alert('Friend request sent successfully!');
                friendModal.style.display = 'none';
                searchInput.value = '';
                searchResults.innerHTML = '';
                selectedPlayerId = null;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to send friend request');
            }
        } catch (error) {
            console.error('Error sending friend request:', error);
            alert(error.message || 'Failed to send friend request. Please try again.');
        }
    });
}

// Load friends list
async function loadFriends() {
    try {
        const response = await fetch('/api/friends');
        if (response.ok) {
            const friends = await response.json();
            updateFriendsList(friends);
        }
    } catch (error) {
        console.error('Error loading friends:', error);
    }
}

// Load friend requests
async function loadFriendRequests() {
    try {
        const response = await fetch('/api/friends/pending');
        if (response.ok) {
            const requests = await response.json();
            updateFriendRequests(requests);
        }
    } catch (error) {
        console.error('Error loading friend requests:', error);
    }
}

// Update friends list UI
function updateFriendsList(friends) {
    const friendsList = document.getElementById('friends-list');
    if (friends && friends.length > 0) {
        friendsList.innerHTML = friends.map(friend => `
            <div class="friend-item">
                <img src="${friend.avatar || '/static/default-avatar.png'}" alt="${friend.username}" class="friend-avatar">
                <div class="friend-info">
                    <div class="friend-name">${friend.username}</div>
                    <div class="friend-status ${friend.status === 'Online' ? '' : 'offline'}">${friend.status || 'Offline'}</div>
                </div>
            </div>
        `).join('');
    } else {
        friendsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-user-friends" style="font-size: 3rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                <p style="color: var(--text-secondary); text-align: center;">No friends added yet</p>
            </div>
        `;
    }
}

// Update friend requests UI
function updateFriendRequests(requests) {
    const requestsList = document.querySelector('.friend-requests-list');
    if (requests && requests.length > 0) {
        requestsList.innerHTML = requests.map(request => `
            <div class="request-item">
                <img src="${request.avatar || '/static/default-avatar.png'}" alt="${request.username}" class="friend-avatar">
                <div class="friend-info">
                    <div class="friend-name">${request.username}</div>
                </div>
                <div class="request-actions">
                    <button class="btn btn-primary" onclick="acceptFriendRequest('${request.id}')">Accept</button>
                    <button class="btn" onclick="rejectFriendRequest('${request.id}')">Decline</button>
                </div>
            </div>
        `).join('');
    } else {
        requestsList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox" style="font-size: 2rem; color: var(--text-secondary); margin-bottom: 0.5rem;"></i>
                <p style="color: var(--text-secondary); text-align: center;">No pending friend requests</p>
            </div>
        `;
    }
}

// Accept friend request
window.acceptFriendRequest = async (requestId) => {
    try {
        const response = await fetch(`/api/friends/accept/${requestId}`, {
            method: 'POST'
        });

        if (response.ok) {
            loadFriends();
            loadFriendRequests();
        } else {
            throw new Error('Failed to accept friend request');
        }
    } catch (error) {
        console.error('Error accepting friend request:', error);
        alert('Failed to accept friend request. Please try again.');
    }
};

// Reject friend request
window.rejectFriendRequest = async (requestId) => {
    try {
        const response = await fetch(`/api/friends/reject/${requestId}`, {
            method: 'POST'
        });

        if (response.ok) {
            loadFriendRequests();
        } else {
            throw new Error('Failed to reject friend request');
        }
    } catch (error) {
        console.error('Error rejecting friend request:', error);
        alert('Failed to reject friend request. Please try again.');
    }
}; 