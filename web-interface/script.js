document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const quickReplies = document.getElementById('quickReplies');
    const refreshBtn = document.querySelector('.refresh-btn');
    
    // Rasa server URL
    const RASA_SERVER_URL = 'http://localhost:5005';
    const SENDER_ID = 'user_' + Math.floor(Math.random() * 1000000);
    
    // Function to format timestamp
    function formatTimestamp(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Function to add message to the chat
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        
        const now = new Date();
        
        // Message content
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.innerText = message;
        messageDiv.appendChild(messageContent);
        
        // Timestamp
        const timestamp = document.createElement('div');
        timestamp.classList.add('message-timestamp');
        timestamp.innerText = formatTimestamp(now);
        messageDiv.appendChild(timestamp);
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Function to add rich content (product card)
    function addProductCard(product) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        
        const productCard = document.createElement('div');
        productCard.classList.add('product-card');
        
        // Product image
        const img = document.createElement('img');
        img.src = product.image || 'https://via.placeholder.com/200x120';
        img.alt = product.name;
        img.classList.add('product-image');
        productCard.appendChild(img);
        
        // Product info
        const infoDiv = document.createElement('div');
        infoDiv.classList.add('product-info');
        
        const nameDiv = document.createElement('div');
        nameDiv.classList.add('product-name');
        nameDiv.innerText = product.name;
        infoDiv.appendChild(nameDiv);
        
        const priceDiv = document.createElement('div');
        priceDiv.classList.add('product-price');
        priceDiv.innerText = product.price;
        infoDiv.appendChild(priceDiv);
        
        if (product.description) {
            const descDiv = document.createElement('div');
            descDiv.classList.add('product-description');
            descDiv.innerText = product.description;
            infoDiv.appendChild(descDiv);
        }
        
        productCard.appendChild(infoDiv);
        
        // Action button
        const actionDiv = document.createElement('div');
        actionDiv.classList.add('product-action');
        actionDiv.innerText = 'View Product';
        actionDiv.addEventListener('click', () => {
            sendMessage(`Tell me more about ${product.name}`);
        });
        productCard.appendChild(actionDiv);
        
        messageContent.appendChild(productCard);
        messageDiv.appendChild(messageContent);
        
        // Timestamp
        const timestamp = document.createElement('div');
        timestamp.classList.add('message-timestamp');
        timestamp.innerText = formatTimestamp(new Date());
        messageDiv.appendChild(timestamp);
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // Function to add quick replies
    function addQuickReplies(replies) {
        // Clear any existing quick replies
        quickReplies.innerHTML = '';
        
        if (!replies || replies.length === 0) return;
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.classList.add('quick-reply');
            button.innerText = reply.title;
            button.addEventListener('click', () => {
                sendMessage(reply.payload || reply.title);
                quickReplies.innerHTML = ''; // Clear quick replies after selection
            });
            quickReplies.appendChild(button);
        });
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.id = 'typingIndicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('typing-dot');
            typingDiv.appendChild(dot);
        }
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    // Function to send message to Rasa and handle response
    async function sendMessage(message, isQuickReply = false) {
        if (!message.trim() && !isQuickReply) return;
        
        if (!isQuickReply) {
            // Add user message to chat
            addMessage(message, true);
            userInput.value = '';
        }
        
        // Clear quick replies when user sends new message
        quickReplies.innerHTML = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            const response = await fetch(`${RASA_SERVER_URL}/webhooks/rest/webhook`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: SENDER_ID,
                    message: message
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator after a short delay to make it feel more natural
            setTimeout(() => {
                removeTypingIndicator();
                
                // Process responses
                const currentQuickReplies = [];
                
                if (data.length === 0) {
                    addMessage("I'm sorry, I didn't understand that. Can you rephrase?");
                }
                
                data.forEach(msg => {
                    if (msg.text) {
                        addMessage(msg.text);
                    }
                    
                    // Handle buttons as quick replies
                    if (msg.buttons) {
                        const replies = msg.buttons.map(btn => ({
                            title: btn.title,
                            payload: btn.payload
                        }));
                        currentQuickReplies.push(...replies);
                    }
                    
                    // Handle custom responses
                    if (msg.custom) {
                        if (msg.custom.product) {
                            addProductCard(msg.custom.product);
                        }
                        
                        if (msg.custom.quick_replies) {
                            currentQuickReplies.push(...msg.custom.quick_replies);
                        }
                    }
                });
                
                // Add all collected quick replies
                if (currentQuickReplies.length > 0) {
                    addQuickReplies(currentQuickReplies);
                }
            }, 1000);
            
        } catch (error) {
            removeTypingIndicator();
            addMessage("Sorry, I'm having trouble connecting to the server. Please try again later.");
            console.error('Error:', error);
        }
    }
    
    // Function to scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event listeners
    sendButton.addEventListener('click', () => {
        sendMessage(userInput.value);
    });
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(userInput.value);
        }
    });
    
    refreshBtn.addEventListener('click', () => {
        // Clear the chat and send a reset message
        chatMessages.innerHTML = '';
        quickReplies.innerHTML = '';
        sendWelcomeMessage();
    });
    
    // Define welcome message function
    function sendWelcomeMessage() {
        // Directly add the welcome message
        setTimeout(() => {
            addMessage("👋 Welcome to Customer Care AI! How can I help you today?");
            
            // Add initial quick replies
            const initialQuickReplies = [
                { title: "Product Recommendations", payload: "/request_product_recommendations" },
                { title: "Track My Order", payload: "/track_order" },
                { title: "Return Policy", payload: "/return_policy" },
                { title: "Speak to a Human", payload: "/request_human" }
            ];
            
            addQuickReplies(initialQuickReplies);
        }, 500);
    }
    
    // Start with welcome message
    sendWelcomeMessage();
});
