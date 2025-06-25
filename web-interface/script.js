// Configuration
const CONFIG = {
    RASA_SERVER_URL: 'http://localhost:5005',
    SENDER_ID: 'user_' + Math.floor(Math.random() * 1000000)
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const quickReplies = document.getElementById('quickReplies');

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    sendButton.onclick = () => {
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    };
    
    userInput.onkeydown = (e) => {
        if (e.key === 'Enter') {
            const message = userInput.value.trim();
            if (message) {
                sendMessage(message);
            }
            e.preventDefault();
        }
    };
    
    // Make sure input is focusable
    userInput.tabIndex = 0;
    
    // Start with welcome message
    sendWelcomeMessage();
});

// Helper Functions
function formatTimestamp(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Message Handling
function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = formatTimestamp(new Date());
    
    messageDiv.append(content, timestamp);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addProductCard(product) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = `
        <img src="${product.image || 'https://via.placeholder.com/100'}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p>${product.description || ''}</p>
        <span class="price">${product.price || ''}</span>
    `;
    
    messageDiv.appendChild(card);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Quick Replies
function addQuickReplies(replies) {
    quickReplies.innerHTML = '';
    
    if (!replies?.length) return;
    
    replies.forEach(reply => {
        const button = document.createElement('button');
        button.className = 'quick-reply';
        button.textContent = reply.title;
        button.onclick = () => {
            sendMessage(reply.payload || reply.title);
            quickReplies.innerHTML = '';
        };
        quickReplies.appendChild(button);
    });
}

// Typing Indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<div class="typing-dot"></div>'.repeat(3);
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    indicator?.remove();
}

// Message Sending & Handling
async function sendMessage(message, isQuickReply = false) {
    if (!message?.trim() && !isQuickReply) return;
    
    if (!isQuickReply) {
        addMessage(message, true);
        userInput.value = '';
    }
    
    quickReplies.innerHTML = '';
    showTypingIndicator();
    
    try {
        const response = await fetch(`${CONFIG.RASA_SERVER_URL}/webhooks/rest/webhook`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sender: CONFIG.SENDER_ID,
                message: message
            })
        });
        
        const data = await response.json();
        
        setTimeout(() => {
            removeTypingIndicator();
            const currentQuickReplies = [];
            
            if (!data.length) {
                addMessage("I'm sorry, I didn't understand that. Can you rephrase?");
                return;
            }
            
            data.forEach(msg => {
                if (msg.text) addMessage(msg.text);
                
                if (msg.buttons) {
                    currentQuickReplies.push(...msg.buttons.map(btn => ({
                        title: btn.title,
                        payload: btn.payload
                    })));
                }
                
                if (msg.custom?.product) {
                    addProductCard(msg.custom.product);
                }
                
                if (msg.custom?.quick_replies) {
                    currentQuickReplies.push(...msg.custom.quick_replies);
                }
            });
            
            if (currentQuickReplies.length) {
                addQuickReplies(currentQuickReplies);
            }
        }, 1000);
        
    } catch (error) {
        removeTypingIndicator();
        addMessage("Sorry, I'm having trouble connecting to the server. Please try again later.");
        console.error('Error:', error);
    }
}

// Welcome Message
function sendWelcomeMessage() {
    setTimeout(() => {
        addMessage("👋 Welcome to Customer Care AI! How can I help you today?");
        
        addQuickReplies([
            { title: "Product Recommendations", payload: "/request_product_recommendations" },
            { title: "Track My Order", payload: "/track_order" },
            { title: "Return Policy", payload: "/return_policy" },
            { title: "Speak to a Human", payload: "/request_human" }
        ]);
    }, 500);
}

// Initialize Chat
function initChat() {
    // Set up event listeners
    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        refreshBtn.onclick = () => {
            chatMessages.innerHTML = '';
            quickReplies.innerHTML = '';
            sendWelcomeMessage();
        };
    }
    
    // Initial welcome message
    sendWelcomeMessage();
}

// Initialize chat
initChat();
