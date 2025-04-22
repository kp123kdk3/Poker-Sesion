document.addEventListener('DOMContentLoaded', () => {
    const avatarOptions = document.querySelectorAll('.avatar-option');
    const updateAvatarBtn = document.getElementById('update-avatar-btn');
    let selectedIcon = null;

    // Avatar selection
    avatarOptions.forEach(icon => {
        icon.addEventListener('click', () => {
            avatarOptions.forEach(i => i.classList.remove('selected'));
            icon.classList.add('selected');
            selectedIcon = icon.dataset.icon;
            document.getElementById('avatar-url').value = selectedIcon;
        });
    });

    // Update avatar button handler
    updateAvatarBtn.addEventListener('click', async () => {
        const avatar = document.getElementById('avatar-url').value;
        
        if (!avatar) {
            showNotification('Please select an avatar', 'error');
            return;
        }

        try {
            const response = await fetch('/api/profile/avatar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ avatar })
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('profile-picture').src = `/static/uploads/${data.avatar}`;
                showNotification('Avatar updated successfully!', 'success');
            } else {
                const error = await response.json();
                showNotification(error.error || 'Failed to update avatar', 'error');
            }
        } catch (error) {
            showNotification('An error occurred while updating avatar', 'error');
            console.error('Update avatar error:', error);
        }
    });
});

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
} 