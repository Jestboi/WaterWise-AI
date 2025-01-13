// Enhanced Chat Functionality
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

let isProcessing = false;

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isProcessing) return;

    const message = userInput.value.trim();
    if (!message) return;

    isProcessing = true;
    userInput.value = '';
    addMessage(message, false);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        addMessage(data.response, true);
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your request.', true);
    } finally {
        isProcessing = false;
    }
});

function addMessage(message, isBot) {
    const template = document.getElementById('message-template').innerHTML;
    const rendered = template
        .replace('{{ message }}', message)
        .replace('{{ is_bot }}', isBot);
    
    const wrapper = document.createElement('div');
    wrapper.innerHTML = rendered;
    chatMessages.appendChild(wrapper.firstElementChild);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function copyToClipboard(button) {
    const message = button.closest('.message').querySelector('p').textContent;
    navigator.clipboard.writeText(message);
    
    const icon = button.querySelector('i');
    icon.classList.remove('fa-copy');
    icon.classList.add('fa-check');
    setTimeout(() => {
        icon.classList.remove('fa-check');
        icon.classList.add('fa-copy');
    }, 2000);
}