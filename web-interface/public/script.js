// Configuration
const CONFIG = {
    RASA_SERVER_URL: window.location.hostname === 'localhost' ? 'http://localhost:5005' : 'http://rasa:5005',
    SENDER_ID: 'user_' + Math.floor(Math.random() * 1000000),
    TYPING_DELAY: 1000,
    MAX_RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 2000,
    MONITORING_ENABLED: true,
    MONITORING_INTERVAL: 30000 // 30 seconds
};

// Track user session start
function trackSessionStart() {
    if (!CONFIG.MONITORING_ENABLED) return;
    
    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event: 'session_start',
            data: {
                userAgent: navigator.userAgent,
                screenResolution: `${window.screen.width}x${window.screen.height}`,
                language: navigator.language
            }
        })
    }).catch(console.error);
}

// Track user message
function trackUserMessage(message) {
    if (!CONFIG.MONITORING_ENABLED) return;
    
    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event: 'user_message',
            data: {
                message: message,
                timestamp: new Date().toISOString(),
                conversationId: CONFIG.SENDER_ID
            }
        })
    }).catch(console.error);
}

// Track bot response
function trackBotResponse(message, responseTime) {
    if (!CONFIG.MONITORING_ENABLED) return;
    
    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event: 'bot_response',
            data: {
                message: message,
                responseTime: responseTime,
                timestamp: new Date().toISOString(),
                conversationId: CONFIG.SENDER_ID
            }
        })
    }).catch(console.error);
}

// Track quick reply selection
function trackQuickReply(quickReply) {
    if (!CONFIG.MONITORING_ENABLED) return;
    
    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event: 'quick_reply',
            data: {
                quickReply: quickReply,
                timestamp: new Date().toISOString(),
                conversationId: CONFIG.SENDER_ID
            }
        })
    }).catch(console.error);
}

// Track error
function trackError(error, context = {}) {
    if (!CONFIG.MONITORING_ENABLED) return;
    
    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            event: 'error',
            data: {
                error: error.message || String(error),
                stack: error.stack,
                context: context,
                timestamp: new Date().toISOString(),
                conversationId: CONFIG.SENDER_ID
            }
        })
    }).catch(console.error);
}

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
        ${product.stock ? `<span class="stock ${product.stock < 10 ? 'low-stock' : ''}">${product.stock < 10 ? 'Only ' + product.stock + ' left!' : 'In Stock'}</span>` : ''}
        <button class="buy-button">Add to Cart</button>
    `;
    
    messageDiv.appendChild(card);
    chatMessages.appendChild(messageDiv);
    
    // Add event listener to the buy button
    const buyButton = card.querySelector('.buy-button');
    if (buyButton) {
        buyButton.addEventListener('click', () => {
            addMessage(`I'd like to purchase ${product.name}`, true);
            sendMessage(`/purchase_product{"product_id":"${product.id || ''}"}`);  
        });
    }
    
    scrollToBottom();
}

// Quick Replies
function addQuickReplies(replies) {
    // Clear existing quick replies
    quickReplies.innerHTML = '';
    
    if (!replies?.length) return;
    
    // Create and append new quick reply buttons
    replies.forEach(reply => {
        const button = document.createElement('button');
        button.className = 'quick-reply';
        button.textContent = reply.title;
        button.onclick = () => {
            // Display the selected option as a user message
            addMessage(reply.title, true);
            
            // Send the payload to the bot and mark it as a quick reply
            sendMessage(reply.payload || reply.title, true);
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
    if (indicator) {
        indicator.remove();
    }
}

// Message Sending & Handling
async function sendMessage(message, isQuickReply = false, retryCount = 0) {
    const startTime = Date.now();
    
    // Track user message
    if (!isQuickReply) {
        trackUserMessage(message);
    }
    
    // Add user message to chat
    addMessage(message, true);
    userInput.value = '';
    userInput.focus();
    
    // Always clear quick replies when sending a new message
    quickReplies.innerHTML = '';
    showTypingIndicator();
    
    try {
        // Send message to Rasa server
        fetch(`${CONFIG.RASA_SERVER_URL}/webhooks/rest/webhook`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: CONFIG.SENDER_ID,
                message: message
            })
        })
        .then(response => {
            if (!response.ok) {
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.status = response.status;
                throw error;
            }
            return response.json();
        })
        .then(data => {
            const responseTime = Date.now() - startTime;
            removeTypingIndicator();
            
            // Track successful response
            if (data && data.length > 0) {
                // Process bot responses
                data.forEach(response => {
                    if (response.text) {
                        addMessage(response.text, false);
                        trackBotResponse(response.text, responseTime);
                    } else if (response.image) {
                        // Handle image response
                        const img = document.createElement('img');
                        img.src = response.image;
                        img.className = 'chat-image';
                        chatMessages.appendChild(img);
                        scrollToBottom();
                        trackBotResponse('[Image Response]', responseTime);
                    } else if (response.quick_replies) {
                        addQuickReplies(response.quick_replies);
                        trackBotResponse('[Quick Replies]', responseTime);
                    }
                });
            } else {
                const noResponseMessage = "I'm not sure how to respond to that. Could you rephrase?";
                addMessage(noResponseMessage, false);
                trackBotResponse(noResponseMessage, responseTime);
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            
            // Track the error
            trackError(error, {
                message: message,
                isQuickReply: isQuickReply,
                retryCount: retryCount,
                senderId: CONFIG.SENDER_ID
            });
            
            if (retryCount < CONFIG.MAX_RETRY_ATTEMPTS) {
                // Retry with exponential backoff
                const retryDelay = CONFIG.RETRY_DELAY * Math.pow(2, retryCount);
                setTimeout(() => {
                    sendMessage(message, isQuickReply, retryCount + 1);
                }, retryDelay);
                
                const retryMessage = `Having trouble connecting. Retrying in ${retryDelay/1000} seconds...`;
                addMessage(retryMessage, false);
                trackBotResponse(retryMessage, Date.now() - startTime);
            } else {
                const errorMessage = "Sorry, I'm having trouble connecting to the server. Please try again later.";
                addMessage(errorMessage, false);
                trackBotResponse(errorMessage, Date.now() - startTime);
                
                // Add some contextual quick replies as fallback
                addQuickReplies([
                    { title: "Tell me more", payload: "/more_information" },
                    { title: "Main Menu", payload: "/restart" }
                ]);
            }
        })
            
        // Add a retry button
        addQuickReplies([
            { title: "Try Again", payload: message }
        ]);
    } catch (error) {
        console.error('Unexpected error in sendMessage:', error);
        removeTypingIndicator();
        addMessage("An unexpected error occurred. Please try again.", false);
        trackError(error, { context: 'sendMessage' });
    }
}

// Welcome Message
function sendWelcomeMessage() {
    setTimeout(() => {
        addMessage("👋 Welcome to Customer Care AI! How can I help you today?");
        
        addQuickReplies([
            { title: "Product Recommendations", payload: "/request_product_recommendations" },
            { title: "Track My Order", payload: "/track_order" },
            { title: "Return an Item", payload: "/return_item" },
            { title: "Order Status", payload: "/check_order_status" },
            { title: "Speak to a Human", payload: "/request_human" }
        ]);
    }, 500);
}

// Add new function to display order status cards
function addOrderStatusCard(orderStatus) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    
    const card = document.createElement('div');
    card.className = 'order-status-card';
    card.innerHTML = `
        <h3>Order #${orderStatus.order_number || 'Unknown'}</h3>
        <div class="status-info">
            <span class="status-label">Status:</span>
            <span class="status-value ${orderStatus.status?.toLowerCase() || ''}">${orderStatus.status || 'Unknown'}</span>
        </div>
        <div class="order-details">
            <p><strong>Order Date:</strong> ${orderStatus.date || 'N/A'}</p>
            <p><strong>Estimated Delivery:</strong> ${orderStatus.delivery_date || 'N/A'}</p>
            ${orderStatus.tracking_number ? `<p><strong>Tracking:</strong> ${orderStatus.tracking_number}</p>` : ''}
        </div>
        <div class="order-items">
            <p><strong>Items:</strong> ${orderStatus.items || 'No items found'}</p>
        </div>
    `;
    
    messageDiv.appendChild(card);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
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
    
    // Add event listener for keydown on document
    document.addEventListener('keydown', (e) => {
        // Focus on input when any key is pressed if input is not already focused
        if (e.key.length === 1 && document.activeElement !== userInput) {
            userInput.focus();
        }
    });
    
    // Initial welcome message
    sendWelcomeMessage();
}

// Initialize chat
initChat();
