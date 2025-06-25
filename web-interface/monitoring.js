const os = require('os');

class MonitoringService {
    constructor() {
        this.metrics = {
            conversations: {},
            system: {
                startTime: new Date(),
                hostname: os.hostname(),
                platform: os.platform(),
                version: process.version
            },
            stats: {
                totalMessages: 0,
                totalUsers: 0,
                avgResponseTime: 0,
                errorRate: 0,
                errors: []
            }
        };
    }

    trackMessage(senderId, message, isUser = true, metadata = {}) {
        this.metrics.stats.totalMessages++;
        
        if (!this.metrics.conversations[senderId]) {
            this.metrics.conversations[senderId] = {
                startTime: new Date(),
                messages: [],
                userMessageCount: 0,
                botMessageCount: 0,
                lastActivity: new Date(),
                metadata: {}
            };
            this.metrics.stats.totalUsers = Object.keys(this.metrics.conversations).length;
        }

        const conversation = this.metrics.conversations[senderId];
        const messageEntry = {
            timestamp: new Date(),
            message: typeof message === 'string' ? message : JSON.stringify(message),
            isUser,
            ...metadata
        };

        conversation.messages.push(messageEntry);
        conversation.lastActivity = new Date();

        if (isUser) {
            conversation.userMessageCount++;
        } else {
            conversation.botMessageCount++;
            
            // Calculate response time if this is a bot response to a user message
            const userMessages = conversation.messages
                .filter(m => m.isUser)
                .sort((a, b) => b.timestamp - a.timestamp);
                
            if (userMessages.length > 0) {
                const lastUserMessage = userMessages[0];
                const responseTime = (messageEntry.timestamp - lastUserMessage.timestamp) / 1000; // in seconds
                this.metrics.stats.avgResponseTime = 
                    ((this.metrics.stats.avgResponseTime * (this.metrics.stats.totalMessages - 1)) + responseTime) / 
                    this.metrics.stats.totalMessages;
            }
        }

        return messageEntry;
    }

    trackError(error, context = {}) {
        const errorEntry = {
            timestamp: new Date(),
            error: error.toString(),
            stack: error.stack,
            context
        };
        
        this.metrics.stats.errors.push(errorEntry);
        this.metrics.stats.errorRate = (this.metrics.stats.errors.length / this.metrics.stats.totalMessages) * 100 || 0;
        
        return errorEntry;
    }

    getConversationMetrics(senderId) {
        return this.metrics.conversations[senderId] || null;
    }

    getSystemMetrics() {
        const memoryUsage = process.memoryUsage();
        const load = os.loadavg();
        
        return {
            ...this.metrics.system,
            uptime: process.uptime(),
            memory: {
                rss: memoryUsage.rss,
                heapTotal: memoryUsage.heapTotal,
                heapUsed: memoryUsage.heapUsed,
                external: memoryUsage.external
            },
            cpu: {
                load1: load[0],
                load5: load[1],
                load15: load[2],
                cores: os.cpus().length
            },
            stats: {
                ...this.metrics.stats,
                activeConversations: Object.keys(this.metrics.conversations).length,
                avgMessagesPerUser: this.metrics.stats.totalMessages / (this.metrics.stats.totalUsers || 1)
            },
            timestamp: new Date().toISOString()
        };
    }
    
    getActiveConversations() {
        return Object.entries(this.metrics.conversations)
            .map(([id, data]) => ({
                id,
                ...data,
                duration: (new Date() - new Date(data.startTime)) / 1000,
                lastActivity: data.lastActivity.toISOString()
            }))
            .sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity));
    }
    
    getErrorMetrics() {
        return {
            totalErrors: this.metrics.stats.errors.length,
            errorRate: this.metrics.stats.errorRate,
            recentErrors: this.metrics.stats.errors
                .slice(-10)
                .map(err => ({
                    timestamp: err.timestamp.toISOString(),
                    error: err.error,
                    context: err.context
                }))
        };
    }
}

module.exports = new MonitoringService();
