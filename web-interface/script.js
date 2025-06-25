// Configuration
const CONFIG = {
    RASA_SERVER_URL: 'http://localhost:5005',
    SENDER_ID: 'user_' + Math.floor(Math.random() * 1000000),
    TYPING_DELAY: 1000,
    MAX_RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 2000
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
    indicator?.remove();
}

// Message Sending & Handling
async function sendMessage(message, isQuickReply = false, retryCount = 0) {
    if (!message?.trim() && !isQuickReply) return;
    
    if (!isQuickReply) {
        addMessage(message, true);
        userInput.value = '';
        userInput.focus();
    }
    
    // Always clear quick replies when sending a new message
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
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        setTimeout(() => {
            removeTypingIndicator();
            const currentQuickReplies = [];
            
            if (!data.length) {
                addMessage("I'm sorry, I didn't understand that. Can you rephrase?");
                // Add default quick replies for fallback
                addQuickReplies([
                    { title: "Help", payload: "/help" },
                    { title: "Start Over", payload: "/restart" }
                ]);
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
                
                // Handle order tracking information
                if (msg.custom?.order_status) {
                    addOrderStatusCard(msg.custom.order_status);
                }
            });
            
            // Always add quick replies after bot response
            // If no specific quick replies were provided, add default ones
            if (currentQuickReplies.length) {
                addQuickReplies(currentQuickReplies);
            } else {
                // Add some contextual quick replies as fallback
                addQuickReplies([
                    { title: "Tell me more", payload: "/more_information" },
                    { title: "Main Menu", payload: "/restart" }
                ]);
            }
        }, CONFIG.TYPING_DELAY);
        
    } catch (error) {
        console.error('Error:', error);
        
        // Auto retry logic
        if (retryCount < CONFIG.MAX_RETRY_ATTEMPTS) {
            removeTypingIndicator();
            addMessage("I'm having trouble connecting. Retrying...");
            
            setTimeout(() => {
                sendMessage(message, isQuickReply, retryCount + 1);
            }, CONFIG.RETRY_DELAY);
        } else {
            removeTypingIndicator();
            addMessage("Sorry, I'm having trouble connecting to the server. Please try again later.");
            
            // Add a retry button
            addQuickReplies([
                { title: "Try Again", payload: message }
            ]);
        }
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
