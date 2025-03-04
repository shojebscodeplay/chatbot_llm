// Get the chat form and message input element
const form = document.getElementById('chat-form');
const messageInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');

// Function to send chat message and receive response
async function sendMessage(message) {
    try {
        // Sending user input to the backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        // Check if the response was okay
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Parse JSON response
        const data = await response.json();

        // Handle the response from the backend
        if (data.response) {
            displayMessage('Bot: ' + data.response, 'bot');
        } else if (data.error) {
            displayMessage('Error: ' + data.error, 'bot');
        } else {
            displayMessage('Error: Unexpected response', 'bot');
        }
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
        displayMessage('Error: Something went wrong', 'bot');
    }
}

// Function to display messages in the chat
function displayMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.classList.add(sender);
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;  // Auto scroll to the bottom
}

// Event listener for form submission
form.addEventListener('submit', (event) => {
    event.preventDefault();  // Prevent form from submitting the default way
    const userMessage = messageInput.value;
    if (userMessage.trim()) {
        displayMessage('You: ' + userMessage, 'user');  // Display user's message
        sendMessage(userMessage);  // Send the message to the server
        messageInput.value = '';  // Clear the input field
    }
});
