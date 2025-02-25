document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("user-input");

  // Function to append messages to chat box
  function appendMessage(sender, message) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const textDiv = document.createElement("div");
    textDiv.classList.add("text");
    textDiv.textContent = message;

    messageDiv.appendChild(textDiv);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Function to send a message to the Flask backend
  async function sendMessage(message) {
    appendMessage("user", message);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      const data = await response.json();

      if (response.ok) {
        appendMessage("assistant", data.response);
      } else {
        appendMessage("assistant", `Error: ${data.error}`);
      }
    } catch (error) {
      appendMessage("assistant", `Error: ${error.message}`);
    }
  }

  // Handle form submission
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message) {
      sendMessage(message);
      userInput.value = "";
    }
  });
});
