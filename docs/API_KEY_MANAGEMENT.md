# API Key Management & Rate Limiting Guide

How to safely share your Gemini API key with users while preventing abuse on Cloud Run.

## Architecture Overview

```mermaid
User Request → Cloud Run → Rate Limiter → Gemini API
                    ↓
              SQLite (usage tracking)
              Cloud Storage (backups)
```

## Strategy: Shared API Key with Rate Limiting

Since you already use GCS and have GCP infrastructure, Cloud Run is the best choice:

**Benefits**:

- Integrated with your existing GCP setup
- Built-in monitoring and logging
- Easy to add Cloud Firestore for distributed rate limiting
- Can use Cloud Armor for DDoS protection
- Scales automatically with usage

---

## Implementation Plan

### 1. Rate Limiting Layers

Implement multiple protection layers:

#### Layer 1: IP-based Rate Limiting (Express middleware)

```javascript
// server/middleware/rateLimiter.js
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { createClient } from 'redis';

// For Cloud Run: use Memorystore (Redis) or in-memory for single instance
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per 15min per IP
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
  
  // Optional: use Redis for distributed rate limiting
  // store: new RedisStore({
  //   client: createClient({ url: process.env.REDIS_URL }),
  //   prefix: 'rl:',
  // }),
});

export const geminiLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 20, // 20 Gemini API calls per hour per IP
  message: 'Gemini API quota exceeded. Please try again later.',
  keyGenerator: (req) => {
    // Use IP + user session for better tracking
    return req.ip + (req.session?.id || '');
  },
});
```

#### Layer 2: User Session Tracking

```javascript
// server/middleware/usageTracker.js
import { db } from '../db.js';

export async function trackUsage(req, res, next) {
  const sessionId = req.session.id;
  const ip = req.ip;
  const endpoint = req.path;
  
  try {
    // Log usage to SQLite
    await db.run(`
      INSERT INTO api_usage (session_id, ip_address, endpoint, timestamp)
      VALUES (?, ?, ?, datetime('now'))
    `, [sessionId, ip, endpoint]);
    
    // Check daily quota
    const today = await db.get(`
      SELECT COUNT(*) as count 
      FROM api_usage 
      WHERE session_id = ? 
        AND endpoint LIKE '%/api/gemini%'
        AND date(timestamp) = date('now')
    `, [sessionId]);
    
    if (today.count >= 50) { // 50 Gemini calls per day per session
      return res.status(429).json({
        error: 'Daily quota exceeded',
        message: 'You have reached your daily limit. Try again tomorrow.',
        resetAt: new Date().setHours(24, 0, 0, 0)
      });
    }
    
    next();
  } catch (error) {
    console.error('Usage tracking error:', error);
    next(); // Don't block on tracking errors
  }
}
```

#### Layer 3: Cost-based Limiting

```javascript
// server/middleware/costLimiter.js
const GEMINI_COST_PER_1K_TOKENS = 0.00025; // Gemini Flash pricing
const MAX_DAILY_COST_PER_USER = 0.10; // $0.10 per user per day

export async function checkCostLimit(req, res, next) {
  const sessionId = req.session.id;
  
  try {
    const usage = await db.get(`
      SELECT SUM(tokens_used) as total_tokens
      FROM api_usage
      WHERE session_id = ?
        AND date(timestamp) = date('now')
    `, [sessionId]);
    
    const estimatedCost = (usage?.total_tokens || 0) / 1000 * GEMINI_COST_PER_1K_TOKENS;
    
    if (estimatedCost >= MAX_DAILY_COST_PER_USER) {
      return res.status(429).json({
        error: 'Cost limit exceeded',
        message: 'Daily cost limit reached. Please try again tomorrow.',
        estimatedCost: estimatedCost.toFixed(4)
      });
    }
    
    // Add cost info to request for logging
    req.costTracking = {
      currentCost: estimatedCost,
      remainingBudget: MAX_DAILY_COST_PER_USER - estimatedCost
    };
    
    next();
  } catch (error) {
    console.error('Cost limit check error:', error);
    next();
  }
}
```

### 2. Database Schema for Usage Tracking

```sql
-- Add to your SQLite schema
CREATE TABLE IF NOT EXISTS api_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  tokens_used INTEGER DEFAULT 0,
  response_time_ms INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  user_agent TEXT
);

CREATE INDEX idx_api_usage_session ON api_usage(session_id, timestamp);
CREATE INDEX idx_api_usage_ip ON api_usage(ip_address, timestamp);
CREATE INDEX idx_api_usage_date ON api_usage(date(timestamp));

-- Table for blocked IPs/sessions
CREATE TABLE IF NOT EXISTS blocked_users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  identifier TEXT UNIQUE NOT NULL, -- IP or session_id
  reason TEXT,
  blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  blocked_until DATETIME
);

CREATE INDEX idx_blocked_identifier ON blocked_users(identifier);
```

### 3. Apply Middleware to Routes

```javascript
// server/routes/gemini.js
import express from 'express';
import { geminiLimiter } from '../middleware/rateLimiter.js';
import { trackUsage } from '../middleware/usageTracker.js';
import { checkCostLimit } from '../middleware/costLimiter.js';

const router = express.Router();

// Apply all protection layers
router.use(geminiLimiter);
router.use(trackUsage);
router.use(checkCostLimit);

router.post('/api/gemini/chat', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Your Gemini API call
    const response = await callGeminiAPI(req.body);
    
    // Track token usage
    await db.run(`
      UPDATE api_usage 
      SET tokens_used = ?, response_time_ms = ?
      WHERE id = (SELECT MAX(id) FROM api_usage WHERE session_id = ?)
    `, [
      response.usageMetadata?.totalTokenCount || 0,
      Date.now() - startTime,
      req.session.id
    ]);
    
    res.json(response);
  } catch (error) {
    console.error('Gemini API error:', error);
    res.status(500).json({ error: 'API request failed' });
  }
});

export default router;
```

---

## Cloud Run Specific Configuration

### 1. Enable Cloud Armor (DDoS Protection)

```bash
# Create security policy
gcloud compute security-policies create clible-security-policy \
  --description "Rate limiting and DDoS protection for clible"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy clible-security-policy \
  --expression "true" \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 100 \
  --rate-limit-threshold-interval-sec 60 \
  --ban-duration-sec 600 \
  --conform-action allow \
  --exceed-action deny-429

# Apply to Cloud Run (requires Load Balancer)
# See: https://cloud.google.com/armor/docs/integrating-cloud-armor
```

### 2. Use Cloud Firestore for Distributed Rate Limiting

For multiple Cloud Run instances, use Firestore instead of SQLite for rate limiting:

```javascript
// server/middleware/firestoreRateLimiter.js
import { Firestore } from '@google-cloud/firestore';

const firestore = new Firestore();

export async function checkFirestoreRateLimit(req, res, next) {
  const identifier = req.ip + (req.session?.id || '');
  const docRef = firestore.collection('rate_limits').doc(identifier);
  
  try {
    await firestore.runTransaction(async (transaction) => {
      const doc = await transaction.get(docRef);
      const now = Date.now();
      const hourAgo = now - 60 * 60 * 1000;
      
      let data = doc.exists ? doc.data() : { requests: [] };
      
      // Remove old requests
      data.requests = data.requests.filter(ts => ts > hourAgo);
      
      if (data.requests.length >= 20) { // 20 requests per hour
        throw new Error('RATE_LIMIT_EXCEEDED');
      }
      
      data.requests.push(now);
      transaction.set(docRef, data);
    });
    
    next();
  } catch (error) {
    if (error.message === 'RATE_LIMIT_EXCEEDED') {
      return res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Too many requests. Please try again later.'
      });
    }
    console.error('Firestore rate limit error:', error);
    next();
  }
}
```

### 3. Environment Variables for Cloud Run

```bash
# Deploy with rate limiting configuration
gcloud run deploy clible-web \
  --image=europe-north1-docker.pkg.dev/PROJECT_ID/clible/clible-web:latest \
  --region=europe-north1 \
  --set-env-vars="
    GEMINI_API_KEY=${GEMINI_API_KEY},
    SESSION_SECRET=${SESSION_SECRET},
    MAX_REQUESTS_PER_HOUR=20,
    MAX_REQUESTS_PER_DAY=50,
    MAX_DAILY_COST_PER_USER=0.10,
    ENABLE_RATE_LIMITING=true,
    USE_FIRESTORE_RATE_LIMIT=true
  " \
  --max-instances=10 \
  --concurrency=80 \
  --cpu=1 \
  --memory=512Mi
```

---

## Monitoring & Alerts

### 1. Cloud Monitoring Dashboard

```bash
# Create custom metrics for API usage
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

**dashboard.json**:

```json
{
  "displayName": "clible API Usage",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Gemini API Calls per Hour",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/gemini_api_calls\""
                }
              }
            }]
          }
        }
      },
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Rate Limit Violations",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/rate_limit_exceeded\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

### 2. Set Up Alerts

```bash
# Alert when daily cost exceeds threshold
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High API Cost Alert" \
  --condition-display-name="Daily cost > $5" \
  --condition-threshold-value=5.0 \
  --condition-threshold-duration=3600s
```

### 3. Log Analysis Queries

```bash
# View top API consumers
gcloud logging read "
  resource.type=cloud_run_revision
  AND jsonPayload.endpoint=~'/api/gemini'
" --limit=100 --format=json | \
  jq -r '.[] | .jsonPayload.ip_address' | \
  sort | uniq -c | sort -rn | head -20

# Check rate limit violations
gcloud logging read "
  resource.type=cloud_run_revision
  AND jsonPayload.message=~'Rate limit exceeded'
" --limit=50
```

---

## Cost Estimation & Budgets

### Gemini API Pricing (Flash 2.0)

- **Input**: $0.075 per 1M tokens
- **Output**: $0.30 per 1M tokens
- **Average**: ~$0.00025 per 1K tokens

### Example Budget Scenarios

| Users/Day | Requests/User | Tokens/Request | Daily Cost | Monthly Cost |
|-----------|---------------|----------------|------------|--------------|
| 10 | 20 | 1,000 | $0.05 | $1.50 |
| 50 | 20 | 1,000 | $0.25 | $7.50 |
| 100 | 20 | 1,000 | $0.50 | $15.00 |
| 500 | 20 | 1,000 | $2.50 | $75.00 |

### Set GCP Budget Alerts

```bash
# Create budget with email alerts
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="clible Monthly Budget" \
  --budget-amount=50 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## User Communication

### 1. Display Usage to Users

```javascript
// Add endpoint to show user their usage
router.get('/api/usage', async (req, res) => {
  const sessionId = req.session.id;
  
  const stats = await db.get(`
    SELECT 
      COUNT(*) as requests_today,
      SUM(tokens_used) as tokens_today,
      MAX(timestamp) as last_request
    FROM api_usage
    WHERE session_id = ?
      AND date(timestamp) = date('now')
  `, [sessionId]);
  
  const cost = (stats.tokens_today || 0) / 1000 * 0.00025;
  
  res.json({
    requestsToday: stats.requests_today || 0,
    requestsRemaining: 50 - (stats.requests_today || 0),
    tokensUsed: stats.tokens_today || 0,
    estimatedCost: cost.toFixed(4),
    lastRequest: stats.last_request,
    limits: {
      requestsPerHour: 20,
      requestsPerDay: 50,
      maxDailyCost: 0.10
    }
  });
});
```

### 2. Frontend Usage Display

```typescript
// Show usage in UI
function UsageIndicator() {
  const [usage, setUsage] = useState(null);
  
  useEffect(() => {
    fetch('/api/usage')
      .then(r => r.json())
      .then(setUsage);
  }, []);
  
  if (!usage) return null;
  
  return (
    <div className="usage-indicator">
      <p>Requests today: {usage.requestsToday} / 50</p>
      <p>Remaining: {usage.requestsRemaining}</p>
      <progress 
        value={usage.requestsToday} 
        max={50}
      />
      {usage.requestsRemaining < 10 && (
        <p className="warning">
          You're approaching your daily limit!
        </p>
      )}
    </div>
  );
}
```

---

## Advanced: User Authentication (Optional)

For better control, add optional user accounts:

```javascript
// Simple email-based authentication
router.post('/api/auth/register', async (req, res) => {
  const { email } = req.body;
  
  // Generate verification token
  const token = crypto.randomBytes(32).toString('hex');
  
  await db.run(`
    INSERT INTO users (email, verification_token, tier)
    VALUES (?, ?, 'free')
  `, [email, token]);
  
  // Send verification email
  // Free tier: 50 requests/day
  // Paid tier: unlimited with their own API key
  
  res.json({ message: 'Verification email sent' });
});
```

---

## Deployment Checklist

- [ ] Add rate limiting middleware
- [ ] Create usage tracking tables
- [ ] Set up Cloud Monitoring dashboard
- [ ] Configure budget alerts
- [ ] Test rate limits locally
- [ ] Deploy to Cloud Run
- [ ] Enable Cloud Armor (optional)
- [ ] Set up Firestore for distributed rate limiting
- [ ] Add usage display to frontend
- [ ] Document limits in UI
- [ ] Monitor costs for first week
- [ ] Adjust limits based on actual usage

---

## Quick Deploy with Rate Limiting

```bash
# 1. Update environment variables
export MAX_REQUESTS_PER_HOUR=20
export MAX_REQUESTS_PER_DAY=50
export MAX_DAILY_COST_PER_USER=0.10

# 2. Deploy
./scripts/deploy-gcp.sh

# 3. Monitor
gcloud logging tail "resource.type=cloud_run_revision" --format=json
```

---

## Summary

**Recommended Configuration for Cloud Run**:

1. **IP-based rate limiting**: 100 requests/15min
2. **Gemini API limiting**: 20 calls/hour, 50 calls/day per session
3. **Cost limiting**: $0.10/day per user (~400 Gemini requests)
4. **Total monthly budget**: $50 (supports ~500 active users)
5. **Monitoring**: Cloud Monitoring + budget alerts
6. **Protection**: Cloud Armor for DDoS (optional)

This setup allows you to safely share your API key while keeping costs predictable and preventing abuse.
