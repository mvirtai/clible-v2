# API Key Security Guide

**Last updated:** 2026-05-07

This guide explains how to safely manage the Google Gemini API key in clible-v2.

---

## ⚠️ Important: Google Gemini API Key Restrictions

**Deadline: June 19, 2026**

Google has mandated that all unrestricted API keys must be restricted to specific APIs. After June 19, 2026, **unrestricted keys will no longer work with the Gemini API**.

**Action Required:**
- Restrict all existing unrestricted keys to **Gemini API only**, OR
- Generate new restricted keys and update your configuration

See [Google's announcement](https://ai.google.dev/docs/api_key_policy) for details.

---

## Getting a Restricted Gemini API Key

### Step 1: Create a Restricted Key in Google AI Studio

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **"Create API Key"**
3. Choose **"Create API key in a new Google Cloud project"** (recommended for isolation)
4. Copy the generated key

### Step 2: Verify the Key is Restricted

1. Open [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services → Credentials**
3. Find your API key
4. Click **Edit** and verify:
   - **API restrictions:** Set to **"Gemini API (generativelanguage.googleapis.com)"** ✅
   - **Application restrictions:** Set to **"None"** (optional; set to specific IPs/referrers if needed)
5. Save changes

**Keys created in AI Studio are automatically restricted to Gemini API.**

---

## Using the Key in clible-v2

### Local Development

1. Create a `.env` file in the project root (do NOT commit):
   ```bash
   GEMINI_API_KEY=AIza...your_restricted_key_here...
   ```

2. Load it when running the web app:
   ```bash
   cd src/clible-web
   npm run dev    # Reads .env automatically
   ```

### Docker

Pass the key as an environment variable:

```bash
docker run \
  -p 3000:3000 \
  -e DATABASE_URL="postgresql://..." \
  -e GEMINI_API_KEY="AIza...your_restricted_key_here..." \
  clible-web
```

### Cloud Deployment (Google Cloud Run)

1. Store the key in **Secret Manager**:
   ```bash
   gcloud secrets create gemini-api-key --data-file=- <<< "AIza...your_key..."
   ```

2. Reference it in your **Cloud Run service**:
   - In the Cloud Console: **Service → Edit and Deploy → Runtime settings → Secret references**
   - Or in your deployment config: Mount the secret as an environment variable

3. Verify the key is restricted to **Gemini API only** in Cloud Console → Credentials

---

## Security Best Practices

| Practice | Reason |
|----------|--------|
| **Restrict keys to Gemini API** | Limits exposure if key is compromised |
| **Use application restrictions** | Optional: bind to specific IPs, referrers, or Android packages |
| **Rotate keys regularly** | Replace old keys every 90 days |
| **Never commit `.env` files** | `.env` is in `.gitignore`; use secrets management for production |
| **Use Secret Manager (Cloud)** | Centralized, auditable secret storage |
| **Monitor API usage** | Check Cloud Console for unexpected quota spikes |

---

## Checking for Unrestricted Keys

If you have old, unrestricted keys lying around:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **APIs & Services → Credentials**
3. Look for keys with **API restrictions: None** or **"All APIs"**
4. Click **Delete** or **Restrict** them immediately

---

## Testing the Key

### Quick test (Python):

```python
import os
from google.generativeai import Client

api_key = os.getenv("GEMINI_API_KEY")
client = Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-pro",
    contents="Hello, world!"
)
print(response.text)
```

### Quick test (CLI):

```bash
export GEMINI_API_KEY="AIza...your_key..."
uv run clible analytics reference "John 3:16" # Triggers AI if key is valid
```

If you see AI insights, the key is working. If you see an error like `API key not valid`, check:
- The key is copied completely (no spaces)
- The key is restricted to **Gemini API**
- The key is not rate-limited

---

## Troubleshooting

### "API key not valid"
- ✅ Copy the key directly from [AI Studio](https://aistudio.google.com/apikey)
- ✅ Verify **no extra spaces** in `.env` or environment variables
- ✅ Check the key restriction: must be **Gemini API only**
- ✅ If restricted by IP/referrer, make sure your client IP is allowed

### "Quota exceeded"
- Check [Google Cloud Console → APIs → Quotas](https://console.cloud.google.com/iam-admin/quotas)
- Request a quota increase if needed
- Consider using a new project with a fresh quota

### Key mysteriously stops working after June 19
- You likely had an unrestricted key
- Generate a new restricted key in [AI Studio](https://aistudio.google.com/apikey)
- Update `.env` and deployment secrets

---

## Related Documentation

- **[Google AI Studio Docs](https://ai.google.dev/docs/)** — Official API documentation
- **[API Key Security Policy](https://ai.google.dev/docs/api_key_policy)** — Google's API key policy
- **[Secret Manager Guide](https://cloud.google.com/docs/authentication/provide-credentials-adc)** — Cloud deployment
- **[clible README](../../README.md#configuration)** — Configuration reference

---

## Questions?

If you encounter issues:
1. Check the [clible troubleshooting guide](../../README.md#troubleshooting)
2. Open an issue on [GitHub](https://github.com/mvirtai/clible-v2/issues)
3. Contact the maintainer
