// Delete feedback function
async function deleteFeedback(feedbackId) {
    if (!confirm('Are you sure you want to delete this feedback?')) {
        return;
    }

    try {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
        console.log('Deleting feedback with ID:', feedbackId);
        
        const response = await fetch(`/admin/delete_feedback/${feedbackId}`, {
            method: 'POST',
            headers: {
                'X-CSRF-Token': csrfToken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ csrf_token: csrfToken }),
            credentials: 'same-origin'
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('Successfully deleted feedback');
                // Remove the feedback element from DOM
                const feedbackElement = document.querySelector(`tr[data-feedback-id="${feedbackId}"]`);
                if (feedbackElement) {
                    feedbackElement.remove();
                } else {
                    window.location.reload();
                }
            } else {
                throw new Error(data.error || 'Failed to delete feedback');
            }
        } else {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                throw new Error(data.error || `Server error: ${response.status}`);
            } else {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete feedback: ' + error.message);
    }
}

// Logout function
function logout() {
    window.location.href = '/logout';
}

// Session timer functionality
function startSessionTimer() {
    const sessionTimeout = 20 * 60 * 1000; // 20 minutes in milliseconds
    const warningTime = 2 * 60 * 1000; // Show warning 2 minutes before expiry
    let timeLeft = sessionTimeout;
    
    const timerElement = document.getElementById('session-timer');
    if (!timerElement) return;
    
    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60000);
        const seconds = Math.floor((timeLeft % 60000) / 1000);
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= warningTime) {
            timerElement.classList.add('text-red-500');
        }
        
        if (timeLeft <= 0) {
            window.location.href = '/logout';
            return;
        }
        
        timeLeft -= 1000;
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    startSessionTimer();
    
    // Check feedback structure on load
    fetch('/admin/feedback_structure')
        .then(response => response.json())
        .then(data => {
            console.log('Feedback table structure:', data);
        })
        .catch(error => {
            console.error('Error fetching feedback structure:', error);
        });
});
