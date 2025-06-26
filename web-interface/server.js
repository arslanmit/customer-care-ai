const express = require('express');
const path = require('path');
const cors = require('cors');
const http = require('http');
const monitoring = require('./monitoring');

const app = express();
const PORT = 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        monitoring.trackMessage(
            req.ip,
            `${req.method} ${req.originalUrl} - ${res.statusCode}`,
            false,
            { 
                type: 'request',
                method: req.method,
                path: req.path,
                status: res.statusCode,
                duration
            }
        );
    });
    
    next();
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    monitoring.trackError(err, { 
        path: req.path,
        method: req.method,
        body: req.body 
    });
    
    res.status(500).json({ 
        error: 'Internal server error',
        requestId: req.id
    });
});

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Helper function to make HTTP requests
function makeRequest(options, data) {
    return new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
            let responseData = '';
            
            res.on('data', (chunk) => {
                responseData += chunk;
            });
            
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const parsedData = JSON.parse(responseData);
                        resolve({
                            status: res.statusCode,
                            data: parsedData
                        });
                    } catch (e) {
                        reject(new Error(`Error parsing response: ${e.message}`));
                    }
                } else {
                    reject(new Error(`Request failed with status ${res.statusCode}`));
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        
        req.end();
    });
}

// API Routes
app.post('/api/message', async (req, res) => {
    try {
        const { message, sender = 'default' } = req.body;
        
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }
        
        // Forward message to Rasa
        const options = {
            hostname: 'localhost',
            port: 5005,
            path: '/webhooks/rest/webhook',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const response = await makeRequest(options, {
            sender: sender,
            message: message
        });
        
        res.json({ status: 'success', data: response.data });
        
        // Track successful message processing
        monitoring.trackMessage(
            req.ip,
            'Message processed successfully',
            false,
            { 
                type: 'message',
                message: message,
                response: response.data
            }
        );
    } catch (error) {
        console.error('Error forwarding message to Rasa:', error);
        monitoring.trackError(error, { 
            route: '/api/message',
            message: req.body.message
        });
        res.status(500).json({ 
            status: 'error', 
            message: 'Failed to process message',
            error: error.message 
        });
    }
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

app.get('/api/metrics', (req, res) => {
    try {
        res.json({
            status: 'success',
            data: monitoring.getSystemMetrics()
        });
    } catch (error) {
        monitoring.trackError(error, { route: '/api/metrics' });
        res.status(500).json({
            status: 'error',
            message: 'Failed to fetch metrics'
        });
    }
});

app.get('/api/analytics/conversations', (req, res) => {
    try {
        res.json({
            status: 'success',
            data: {
                activeConversations: monitoring.getActiveConversations(),
                stats: monitoring.getSystemMetrics().stats
            }
        });
    } catch (error) {
        monitoring.trackError(error, { route: '/api/analytics/conversations' });
        res.status(500).json({
            status: 'error',
            message: 'Failed to fetch conversation analytics'
        });
    }
});

app.get('/api/analytics/errors', (req, res) => {
    try {
        res.json({
            status: 'success',
            data: monitoring.getErrorMetrics()
        });
    } catch (error) {
        monitoring.trackError(error, { route: '/api/analytics/errors' });
        res.status(500).json({
            status: 'error',
            message: 'Failed to fetch error metrics'
        });
    }
});

// Track custom events
app.post('/api/track', (req, res) => {
    try {
        const { event, data } = req.body;
        if (!event) {
            return res.status(400).json({ error: 'Event name is required' });
        }
        
        monitoring.trackMessage(
            req.ip,
            event,
            false,
            { type: 'event', ...data }
        );
        
        res.json({ status: 'success' });
    } catch (error) {
        monitoring.trackError(error, { route: '/api/track' });
        res.status(500).json({
            status: 'error',
            message: 'Failed to track event'
        });
    }
});

// Default route
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Metrics available at http://localhost:${PORT}/api/metrics`);
    console.log(`Health check at http://localhost:${PORT}/api/health`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received. Shutting down gracefully...');
    server.close(() => {
        console.log('Process terminated');
        process.exit(0);
    });
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err);
    monitoring.trackError(err, { type: 'unhandledRejection' });
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
    monitoring.trackError(err, { type: 'uncaughtException' });
    process.exit(1);
});

module.exports = { app, server };
