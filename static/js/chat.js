// Enhanced Chat Functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    let isProcessing = false;

    // Function to add a message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-2' + (isUser ? ' justify-end' : '');
        
        const content = `
            ${!isUser ? `
                <div class="flex-shrink-0">
                    <i class="fas fa-robot text-2xl text-blue-500"></i>
                </div>
            ` : ''}
            <div class="${isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'} rounded-lg p-3 max-w-[80%]">
                <p class="whitespace-pre-wrap">${message}</p>
            </div>
            ${isUser ? `
                <div class="flex-shrink-0">
                    <i class="fas fa-user text-2xl text-blue-500"></i>
                </div>
            ` : ''}
        `;
        
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Handle form submission
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (isProcessing) {
            return;
        }
        
        const message = messageInput.value.trim();
        if (!message) {
            return;
        }

        // Add user message
        addMessage(message, true);
        
        // Clear input and disable it
        messageInput.value = '';
        messageInput.disabled = true;
        isProcessing = true;
        
        try {
            const response = await fetch('/new-chat-endpoint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: JSON.stringify({ 
                    message: message,
                    file_content: '' // Add this to match the backend expectation
                })
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // Add AI response
            if (data.response) {
                addMessage(data.response);
            } else {
                addMessage('Üzgünüm, boş bir yanıt aldım. Lütfen tekrar deneyin.');
            }
            
        } catch (error) {
            console.error('Error:', error);
            addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.');
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            isProcessing = false;
            messageInput.focus();
        }
    });

    // Initial focus
    messageInput.focus();
});