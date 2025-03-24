## AI Voice Agent API

This API manages the AI voice agent functionality, including voice configuration, conversation handling, and real-time interactions.

### Base URL
```
/api/voice-agent
```

### Endpoints

#### 1. Voice Agent Management

##### Get Voice Agent Status
```http
GET /api/voice-agent/status
```
Returns the current status of the voice agent (active/inactive, current call status, etc.)

**Response:**
```json
{
  "status": "active|inactive|on_call",
  "currentCallId": "string|null",
  "lastActiveTimestamp": "ISO-8601 timestamp",
  "activeSessionDuration": "number (seconds)"
}
```

##### Configure Voice Agent
```http
PUT /api/voice-agent/configure
```
Update voice agent configuration settings

**Request Body:**
```json
{
  "voice": {
    "id": "string",
    "gender": "male|female",
    "accent": "string",
    "speed": "number (0.5-2.0)",
    "pitch": "number (0.5-2.0)"
  },
  "behavior": {
    "personality": "string",
    "responseStyle": "formal|casual|friendly",
    "interruptionHandling": "strict|lenient",
    "conversationStyle": "direct|elaborate"
  },
  "rules": {
    "maxCallDuration": "number (minutes)",
    "silenceThreshold": "number (seconds)",
    "interruptionThreshold": "number (seconds)"
  }
}
```

#### 2. Real-time Control

##### Start Voice Agent
```http
POST /api/voice-agent/start
```
Activate the voice agent for handling calls

**Response:**
```json
{
  "status": "active",
  "startedAt": "ISO-8601 timestamp",
  "agentId": "string"
}
```

##### Stop Voice Agent
```http
POST /api/voice-agent/stop
```
Deactivate the voice agent

**Response:**
```json
{
  "status": "inactive",
  "stoppedAt": "ISO-8601 timestamp",
  "totalActiveTime": "number (seconds)"
}
```

#### 3. Conversation Management

##### Get Active Conversation
```http
GET /api/voice-agent/conversation/active
```
Get details of the currently active conversation

**Response:**
```json
{
  "conversationId": "string",
  "startTime": "ISO-8601 timestamp",
  "duration": "number (seconds)",
  "leadId": "string",
  "status": "active|on_hold|wrapping_up",
  "metrics": {
    "speakingTime": "number (seconds)",
    "turnsCount": "number",
    "silenceDuration": "number (seconds)"
  }
}
```

##### Control Conversation
```http
POST /api/voice-agent/conversation/{conversationId}/control
```
Control the flow of an active conversation

**Request Body:**
```json
{
  "action": "pause|resume|end|transfer",
  "reason": "string",
  "transferTo": "string (optional)"
}
```

#### 4. Real-time Analytics

##### Get Live Metrics
```http
GET /api/voice-agent/metrics/live
```
Get real-time metrics for the current/recent conversations

**Response:**
```json
{
  "currentCall": {
    "duration": "number (seconds)",
    "sentiment": "positive|neutral|negative",
    "engagementScore": "number (0-100)",
    "speechClarity": "number (0-100)"
  },
  "realtimeMetrics": {
    "volumeLevel": "number (dB)",
    "noiseLevel": "number (dB)",
    "speechRate": "number (words/minute)"
  }
}
```

#### 5. Training and Learning

##### Update Knowledge Base
```http
PUT /api/voice-agent/knowledge
```
Update the voice agent's knowledge base

**Request Body:**
```json
{
  "documents": [
    {
      "type": "script|faq|guideline",
      "content": "string",
      "priority": "number (1-5)"
    }
  ],
  "rules": [
    {
      "condition": "string",
      "response": "string",
      "priority": "number (1-5)"
    }
  ]
}
```

##### Get Learning Progress
```http
GET /api/voice-agent/learning/progress
```
Get the voice agent's learning and adaptation progress

**Response:**
```json
{
  "totalInteractions": "number",
  "successRate": "number (percentage)",
  "learningMetrics": {
    "adaptationScore": "number (0-100)",
    "knowledgeRetention": "number (0-100)",
    "improvementRate": "number (percentage)"
  },
  "lastUpdated": "ISO-8601 timestamp"
}
```

### Error Responses

All endpoints follow standard HTTP status codes and return error responses in this format:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

### Rate Limiting

- Rate limit: 100 requests per minute per API key
- Real-time endpoints (/metrics/live): 300 requests per minute per API key

### Authentication

All endpoints require a valid JWT token in the Authorization header:
```http
Authorization: Bearer <token>
``` 