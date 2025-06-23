# API Documentation

This document describes the RESTful API endpoints available in the Customer Care AI system.

## Table of Contents
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Authentication](#authentication-endpoints)
  - [Conversations](#conversation-endpoints)
  - [Analytics](#analytics-endpoints)
- [WebSocket API](#websocket-api)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Versioning](#versioning)

## Authentication

All API requests require authentication using JWT (JSON Web Tokens). Include the token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

## Base URL

- **Development**: `http://localhost:5005`
- **Production**: `https://api.yourdomain.com/v1`

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-06-23T03:20:00Z"
}
```

### Authentication Endpoints

#### POST /auth/register

Register a new user.

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2025-06-23T03:20:00Z"
}
```

#### POST /auth/login

Authenticate a user and get an access token.

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Conversation Endpoints

#### POST /conversations

Start a new conversation.

**Request Headers**
```
Authorization: Bearer <your_jwt_token>
```

**Response**
```json
{
  "conversation_id": "conv_123",
  "created_at": "2025-06-23T03:20:00Z"
}
```

#### POST /conversations/{conversation_id}/messages

Send a message in a conversation.

**Path Parameters**
- `conversation_id` (string, required): The ID of the conversation

**Request Headers**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body**
```json
{
  "message": "Hello, how can I help you today?",
  "metadata": {
    "device": "web",
    "language": "en"
  }
}
```

**Response**
```json
{
  "message_id": "msg_123",
  "conversation_id": "conv_123",
  "sender": "user_123",
  "message": "Hello, how can I help you today?",
  "timestamp": "2025-06-23T03:20:00Z",
  "response": {
    "text": "I'm here to help! What can I assist you with?",
    "intent": "greet",
    "confidence": 0.98,
    "entities": []
  }
}
```

### Analytics Endpoints

#### GET /analytics/conversations

Get conversation analytics.

**Query Parameters**
- `start_date` (string, optional): Start date in ISO format
- `end_date` (string, optional): End date in ISO format
- `timeframe` (string, optional): Timeframe for grouping (hourly, daily, weekly, monthly)

**Request Headers**
```
Authorization: Bearer <your_jwt_token>
```

**Response**
```json
{
  "total_conversations": 1250,
  "active_users": 342,
  "messages_per_conversation": 5.2,
  "intent_distribution": [
    { "intent": "greeting", "count": 450 },
    { "intent": "question", "count": 320 },
    { "intent": "complaint", "count": 120 },
    { "intent": "feedback", "count": 80 },
    { "intent": "other", "count": 280 }
  ],
  "time_series": [
    { "timestamp": "2025-06-01T00:00:00Z", "count": 42 },
    { "timestamp": "2025-06-02T00:00:00Z", "count": 56 },
    { "timestamp": "2025-06-03T00:00:00Z", "count": 38 }
  ]
}
```

## WebSocket API

### WebSocket Endpoint

```
ws://localhost:5005/ws/conversations/{conversation_id}
```

### Authentication

Send the JWT token as a query parameter:

```
ws://localhost:5005/ws/conversations/conv_123?token=<your_jwt_token>
```

### Messages

#### Send Message

```json
{
  "type": "message",
  "content": "Hello, bot!"
}
```

#### Receive Message

```json
{
  "type": "message",
  "content": "Hello! How can I help you today?",
  "timestamp": "2025-06-23T03:20:00Z",
  "metadata": {
    "intent": "greeting",
    "confidence": 0.97
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field_name": "Additional error details"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Rate Limiting

- **Public Endpoints**: 100 requests per minute per IP
- **Authenticated Endpoints**: 1000 requests per minute per user
- **WebSocket Connections**: 10 concurrent connections per user

## Versioning

API versioning is done through the URL path:

```
https://api.yourdomain.com/v1/endpoint
```

Current API version: `v1`

## Pagination

Endpoints that return lists of items support pagination using `limit` and `offset` query parameters:

```
GET /conversations?limit=20&offset=40
```

**Response Headers**
```
X-Total-Count: 1250
X-Page-Size: 20
X-Page: 3
X-Total-Pages: 63
```

## Webhooks

### Incoming Webhooks

Configure webhook URLs to receive real-time events:

1. **Conversation Started**
2. **Message Received**
3. **Conversation Ended**
4. **Error Occurred**

### Outgoing Webhooks

Configure external services to receive events from your application.

## Testing

### Test Environment

Use the test environment for development and testing:

```
https://staging-api.yourdomain.com/v1
```

### Test Credentials

```
Email: test@example.com
Password: testpassword123
```

## Support

For API support, please contact:

- **Email**: support@yourdomain.com
- **Slack**: #api-support
- **Documentation**: https://docs.yourdomain.com/api
