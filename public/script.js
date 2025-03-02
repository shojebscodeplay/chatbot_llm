document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const loader = document.getElementById("loader");  // Loading spinner element

    // Show loading spinner
    function showLoading() {
        loader.style.display = 'block';
    }

    // Hide loading spinner
    function hideLoading() {
        loader.style.display = 'none';
    }

    // Append user and bot messages
    function appendMessage(sender, message) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(sender);
        messageDiv.innerText = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message
    }

    // Send the user input to the server
    async function sendMessage(message) {
        try {
            showLoading();
            const response = await fetch("https://chatbot-llm-qldo.onrender.com/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message: message }),
            });

            hideLoading();

            if (!response.ok) {
                throw new Error("Failed to fetch response from the server");
            }

            const data = await response.json();
            if (data.response) {
                appendMessage("bot", data.response);
            } else {
                appendMessage("bot", "Sorry, I didn't get that.");
            }
        } catch (error) {
            hideLoading();
            appendMessage("bot", "Error: Unable to get a response. Please try again later.");
            console.error("Error:", error);
        }
    }

    // Handle form submission
    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            appendMessage("user", message);
            userInput.value = "";  // Clear the input field
            sendMessage(message);
        }
    });
});
