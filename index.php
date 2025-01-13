<?php
session_start();

// Initialize conversation ID if not exists
if (!isset($_SESSION['conversation_id'])) {
    $_SESSION['conversation_id'] = uniqid();
}

// Function to save feedback
function save_feedback($data) {
    $feedback_file = "dataset/feedback.jsonl";
    $data['timestamp'] = date('Y-m-d H:i:s');
    $data['id'] = $_SESSION['conversation_id'];
    file_put_contents($feedback_file, json_encode($data) . "\n", FILE_APPEND);
}

// Handle feedback submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['feedback'])) {
    $feedback_data = [
        'user_message' => $_POST['user_message'],
        'bot_response' => $_POST['bot_response'],
        'rating' => $_POST['rating'],
        'comments' => $_POST['comments'] ?? ''
    ];
    save_feedback($feedback_data);
    echo json_encode(['status' => 'success']);
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Water Conservation Chatbot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            background-color: #f5f5f5;
        }
        .chat-container {
            max-width: 800px;
            margin: 30px auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chat-header {
            background: #007bff;
            color: white;
            padding: 20px;
            border-radius: 15px 15px 0 0;
            text-align: center;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
        }
        .user-message {
            justify-content: flex-end;
        }
        .message-content {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 0 10px;
        }
        .bot-message .message-content {
            background: #f0f2f5;
        }
        .user-message .message-content {
            background: #007bff;
            color: white;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        .bot-avatar {
            background: #e3f2fd;
            color: #007bff;
        }
        .user-avatar {
            background: #007bff;
            color: white;
        }
        .chat-input {
            padding: 20px;
            border-top: 1px solid #eee;
        }
        .feedback-form {
            display: none;
            padding: 15px;
            border-top: 1px solid #eee;
        }
        .star-rating {
            color: #ffd700;
            font-size: 24px;
            cursor: pointer;
        }
        .typing-indicator {
            display: none;
            padding: 10px;
            background: #f0f2f5;
            border-radius: 15px;
            margin: 10px;
        }
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #90949c;
            border-radius: 50%;
            margin-right: 5px;
            animation: typing 1s infinite;
        }
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="chat-container">
            <div class="chat-header">
                <h2><i class="fas fa-water"></i> Water Conservation Chatbot</h2>
                <p class="mb-0">Ask me anything about water conservation!</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <div class="avatar bot-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        Hello! I'm your water conservation assistant. How can I help you today?
                    </div>
                </div>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>

            <div class="feedback-form" id="feedbackForm">
                <h5>How helpful was this response?</h5>
                <div class="star-rating mb-3">
                    <i class="far fa-star" data-rating="1"></i>
                    <i class="far fa-star" data-rating="2"></i>
                    <i class="far fa-star" data-rating="3"></i>
                    <i class="far fa-star" data-rating="4"></i>
                    <i class="far fa-star" data-rating="5"></i>
                </div>
                <div class="mb-3">
                    <textarea class="form-control" id="feedbackComments" rows="2" placeholder="Additional comments (optional)"></textarea>
                </div>
                <button class="btn btn-primary" onclick="submitFeedback()">Submit Feedback</button>
            </div>

            <div class="chat-input">
                <form id="chatForm" class="d-flex mb-2">
                    <input type="text" class="form-control me-2" id="userInput" placeholder="Type your message..." required>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </form>
                <form id="fileUploadForm" class="d-flex align-items-center">
                    <div class="input-group">
                        <input type="file" class="form-control" id="fileInput" accept=".txt,.pdf,.doc,.docx">
                        <button type="submit" class="btn btn-secondary">
                            <i class="fas fa-upload"></i> Upload
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentUserMessage = '';
        let currentBotResponse = '';
        let selectedRating = 0;

        // Star rating handling
        $('.star-rating i').hover(
            function() {
                let rating = $(this).data('rating');
                updateStars(rating);
            },
            function() {
                updateStars(selectedRating);
            }
        );

        $('.star-rating i').click(function() {
            selectedRating = $(this).data('rating');
            updateStars(selectedRating);
        });

        function updateStars(rating) {
            $('.star-rating i').each(function() {
                let starRating = $(this).data('rating');
                $(this).toggleClass('fas', starRating <= rating);
                $(this).toggleClass('far', starRating > rating);
            });
        }

        function appendMessage(message, isUser = false) {
            const messageDiv = $('<div>').addClass('message').addClass(isUser ? 'user-message' : 'bot-message');
            const avatar = $('<div>').addClass('avatar').addClass(isUser ? 'user-avatar' : 'bot-avatar');
            const icon = $('<i>').addClass(isUser ? 'fas fa-user' : 'fas fa-robot');
            const content = $('<div>').addClass('message-content').text(message);

            avatar.append(icon);
            messageDiv.append(avatar).append(content);
            
            // Insert the message before the typing indicator
            $('.typing-indicator').before(messageDiv);
            
            // Scroll to bottom
            const chatMessages = $('#chatMessages');
            chatMessages.scrollTop(chatMessages[0].scrollHeight);
        }

        function showTypingIndicator() {
            $('.typing-indicator').show();
            const chatMessages = $('#chatMessages');
            chatMessages.scrollTop(chatMessages[0].scrollHeight);
        }

        function hideTypingIndicator() {
            $('.typing-indicator').hide();
        }

        function typeMessage(message, element, speed = 30) {
            let i = 0;
            element.text(''); // Clear the element
            
            function type() {
                if (i < message.length) {
                    element.text(element.text() + message.charAt(i));
                    i++;
                    setTimeout(type, speed);
                }
            }
            
            type();
        }

        $('#chatForm').submit(function(e) {
            e.preventDefault();
            const userInput = $('#userInput').val().trim();
            if (!userInput) return;

            // Clear input and store message
            $('#userInput').val('');
            currentUserMessage = userInput;

            // Append user message
            appendMessage(userInput, true);
            
            // Show typing indicator
            showTypingIndicator();

            // Send message to server
            $.ajax({
                url: '/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ message: userInput }),
                success: function(response) {
                    console.log('Received response:', response);
                    if (response && response.response) {
                        currentBotResponse = response.response;
                        
                        // Hide typing indicator after a short delay
                        setTimeout(() => {
                            hideTypingIndicator();
                            
                            // Create bot message elements
                            const messageDiv = $('<div>').addClass('message bot-message');
                            const avatar = $('<div>').addClass('avatar bot-avatar').append($('<i>').addClass('fas fa-robot'));
                            const content = $('<div>').addClass('message-content');
                            
                            messageDiv.append(avatar).append(content);
                            $('.typing-indicator').before(messageDiv);
                            
                            // Animate the message typing
                            typeMessage(currentBotResponse, content);
                            
                            // Show feedback form
                            $('#feedbackForm').show();
                            
                            // Scroll to bottom
                            const chatMessages = $('#chatMessages');
                            chatMessages.scrollTop(chatMessages[0].scrollHeight);
                        }, 1000);
                    } else {
                        console.error('Invalid response format:', response);
                        hideTypingIndicator();
                        appendMessage('Sorry, I received an invalid response. Please try again.', false);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                    console.error('Status:', status);
                    console.error('Response:', xhr.responseText);
                    hideTypingIndicator();
                    appendMessage('Sorry, I encountered an error. Please try again.', false);
                }
            });
        });

        $('#fileUploadForm').submit(function(e) {
            e.preventDefault();
            const fileInput = $('#fileInput')[0];
            if (!fileInput.files.length) {
                alert('Please select a file to upload');
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            // Show typing indicator
            showTypingIndicator();

            // Upload file
            $.ajax({
                url: '/upload',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response && response.response) {
                        currentBotResponse = response.response;
                        
                        // Hide typing indicator after a short delay
                        setTimeout(() => {
                            hideTypingIndicator();
                            
                            // Create bot message elements
                            const messageDiv = $('<div>').addClass('message bot-message');
                            const avatar = $('<div>').addClass('avatar bot-avatar').append($('<i>').addClass('fas fa-robot'));
                            const content = $('<div>').addClass('message-content');
                            
                            messageDiv.append(avatar).append(content);
                            $('.typing-indicator').before(messageDiv);
                            
                            // Animate the message typing
                            typeMessage(currentBotResponse, content);
                            
                            // Show feedback form
                            $('#feedbackForm').show();
                            
                            // Clear file input
                            fileInput.value = '';
                            
                            // Scroll to bottom
                            const chatMessages = $('#chatMessages');
                            chatMessages.scrollTop(chatMessages[0].scrollHeight);
                        }, 1000);
                    }
                },
                error: function(xhr, status, error) {
                    hideTypingIndicator();
                    appendMessage('Sorry, I encountered an error processing your file. Please try again.', false);
                    console.error('Error:', error);
                }
            });
        });

        function submitFeedback() {
            if (selectedRating === 0) {
                alert('Please select a rating before submitting feedback.');
                return;
            }

            const feedbackData = {
                user_message: currentUserMessage,
                bot_response: currentBotResponse,
                rating: selectedRating,
                comments: $('#feedbackComments').val()
            };

            $.ajax({
                url: window.location.href,
                method: 'POST',
                data: {
                    feedback: true,
                    ...feedbackData
                },
                success: function() {
                    $('#feedbackForm').hide();
                    $('#feedbackComments').val('');
                    selectedRating = 0;
                    updateStars(0);
                },
                error: function() {
                    alert('Error submitting feedback. Please try again.');
                }
            });
        }
    </script>
</body>
</html>
