// Feedback Modal Functions
const feedbackModal = document.getElementById('feedback-popup');
const feedbackBtn = document.getElementById('feedback-btn');
const closeBtn = document.getElementById('close-feedback');
const flashMessage = document.getElementById('flash-message');
const starRating = document.getElementById('star-rating');
const ratingInput = document.getElementById('rating');
let selectedRating = 0;

// Initialize star rating functionality
function initStarRating() {
    const starLabels = starRating.querySelectorAll('label');
    
    starLabels.forEach((label) => {
        const radioInput = label.querySelector('input');
        const starSpan = label.querySelector('span');

        // Hover effects
        label.addEventListener('mouseover', () => {
            const rating = parseInt(radioInput.value);
            updateStarsDisplay(rating);
        });

        label.addEventListener('mouseout', () => {
            updateStarsDisplay(selectedRating);
        });

        // Click handling
        radioInput.addEventListener('change', () => {
            selectedRating = parseInt(radioInput.value);
            ratingInput.value = selectedRating;
            updateStarsDisplay(selectedRating);
        });
    });
}

// Update star display
function updateStarsDisplay(rating) {
    const starLabels = starRating.querySelectorAll('label');
    starLabels.forEach((label, index) => {
        const starSpan = label.querySelector('span');
        if (index < rating) {
            starSpan.classList.remove('text-gray-300');
            starSpan.classList.add('text-yellow-400');
        } else {
            starSpan.classList.remove('text-yellow-400');
            starSpan.classList.add('text-gray-300');
        }
    });
}

// Show feedback modal
function showFeedbackModal() {
    feedbackModal.classList.remove('hidden');
}

// Close feedback modal
function closeFeedbackModal() {
    feedbackModal.classList.add('hidden');
    resetFeedbackForm();
}

// Reset feedback form
function resetFeedbackForm() {
    const form = document.getElementById('feedback-form');
    form.reset();
    selectedRating = 0;
    ratingInput.value = '';
    updateStarsDisplay(0);
}

// Show flash message
function showFlashMessage(message, type = 'success') {
    const flashDiv = document.createElement('div');
    flashDiv.className = `fixed top-4 right-4 p-4 rounded-xl shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white z-50 animate-fade-in-out`;
    flashDiv.textContent = message;
    document.body.appendChild(flashDiv);
    
    setTimeout(() => {
        flashDiv.remove();
    }, 3000);
}

// Handle feedback form submission
document.getElementById('feedback-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!ratingInput.value) {
        showFlashMessage('Please select a rating', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    try {
        const response = await fetch('/submit_feedback', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': csrfToken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                rating: parseInt(ratingInput.value),
                comment: formData.get('comment'),
                name: formData.get('name') || 'Anonymous',
                email: formData.get('email') || 'anonymous@example.com',
                csrf_token: csrfToken
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showFlashMessage('Thank you for your feedback!');
            closeFeedbackModal();
        } else {
            throw new Error(data.error || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Error:', error);
        showFlashMessage(error.message, 'error');
    }
});

// Event Listeners
feedbackBtn?.addEventListener('click', showFeedbackModal);
closeBtn?.addEventListener('click', closeFeedbackModal);

// Initialize star rating on page load
document.addEventListener('DOMContentLoaded', initStarRating);
