# Secure GitHub Commit Strategy

## Pre-Commit Security Checklist

### 1. Secrets Detection

**Before every commit, verify:**

```bash
# Check for potential secrets in staged files
git diff --cached | grep -iE "(api_key|password|secret|token|credential)" || echo "✓ No obvious secrets"

# Check .env files are ignored
git status --porcelain | grep -E "^[AM].*\.env$" && echo "⚠️  WARNING: .env file staged!" || echo "✓ No .env files"

# Verify .gitignore is working
git check-ignore .env .env.production .env.local || echo "⚠️  WARNING: .env not ignored!"
```

### 2. Files That Must NEVER Be Committed

```
.env
.env.local
.env.production
.env.development
.env.test
*.db (except test fixtures)
*_secrets*
*.key
*.pem
credentials.json
service-account*.json
```

### 3. Safe Commit Workflow

```bash
# 1. Check what's staged
git status

# 2. Review actual changes
git diff --cached

# 3. Scan for secrets
git diff --cached | grep -iE "(AIza|sk-|ghp_|gho_)" && echo "⚠️  STOP: Possible API key!" || echo "✓ Safe"

# 4. Commit with descriptive message
git commit -m "feat: add rate limiting for beta testing"

# 5. Before push, final check
git log -1 -p | grep -iE "(api_key|password|secret)" && echo "⚠️  ABORT PUSH!" || git push
```

### 4. If You Accidentally Commit Secrets

**DO NOT just delete and recommit - secrets remain in git history!**

```bash
# Option 1: Remove from last commit (if not pushed)
git reset --soft HEAD~1
# Remove the secret from files
git add .
git commit -m "your message"

# Option 2: If already pushed (NUCLEAR option)
# 1. Revoke the exposed secret immediately (API key, token, etc.)
# 2. Use git-filter-repo or BFG Repo-Cleaner
# 3. Force push (breaks history for collaborators)

# Option 3: Best practice
# 1. Revoke the secret immediately
# 2. Rotate to new secret
# 3. Add to .gitignore
# 4. Continue with new secret (old one in history but revoked)
```

### 5. Environment Variable Strategy

**Development (.env - local only, never committed):**
```bash
GEMINI_API_KEY=AIza...your-dev-key
GEMINI_API_KEY_FOR_BETA_TESTERS=AIza...your-beta-key
SESSION_SECRET=local-dev-secret
```

**Production (Cloud Run env vars):**
```bash
# Set via deployment script or gcloud command
gcloud run services update clible-web \
  --set-env-vars="GEMINI_API_KEY_FOR_BETA_TESTERS=AIza..." \
  --region=europe-north1
```

**Example files (committed):**
```bash
# .env.example - safe to commit
GEMINI_API_KEY=your_key_here
GEMINI_API_KEY_FOR_BETA_TESTERS=your_beta_key_here
SESSION_SECRET=generate_with_openssl_rand
```

### 6. Automated Security Checks

**Add to `.git/hooks/pre-commit`:**

```bash
#!/bin/bash
# Pre-commit hook to prevent secret leaks

# Check for common secret patterns
if git diff --cached | grep -qiE "(AIza[0-9A-Za-z_-]{35}|sk-[0-9A-Za-z]{48}|ghp_[0-9A-Za-z]{36})"; then
    echo "❌ ERROR: Possible API key detected in staged changes!"
    echo "Review your changes and remove any secrets."
    exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -qE "^\.env(\.|$)"; then
    echo "❌ ERROR: .env file is staged!"
    echo "Run: git reset HEAD .env"
    exit 1
fi

echo "✓ Pre-commit security check passed"
exit 0
```

**Install the hook:**
```bash
chmod +x .git/hooks/pre-commit
```

### 7. Current Repository Status

**Safe to commit:**
- `src/clible-web/middleware/rateLimit.ts` - no secrets
- `src/clible-web/server.ts` - uses env vars, no hardcoded secrets
- `scripts/deploy-beta.sh` - prompts for secrets, doesn't contain them
- `BETA_DEPLOY.md` - documentation only
- `.env.example` - example values only

**Never commit:**
- `.env` - already in `.gitignore` ✓
- `.env.production` - already in `.gitignore` ✓
- Any file with actual API keys

### 8. Recommended Commit Structure

```bash
# Feature commits
git add src/clible-web/middleware/rateLimit.ts
git add src/clible-web/server.ts
git commit -m "feat: add rate limiting for AI endpoints (20 req/hour)"

# Documentation commits
git add docs/BETA_DEPLOYMENT.md BETA_DEPLOY.md
git commit -m "docs: add beta testing deployment guide"

# Infrastructure commits
git add scripts/deploy-beta.sh
git commit -m "chore: add Cloud Run beta deployment script"

# Configuration commits (safe examples only)
git add src/clible-web/.env.example
git commit -m "chore: add GEMINI_API_KEY_FOR_BETA_TESTERS to env example"
```

### 9. GitHub Security Features

**Enable in repository settings:**
- ✓ Secret scanning (GitHub Advanced Security)
- ✓ Dependabot alerts
- ✓ Code scanning (CodeQL)
- ✓ Branch protection (require reviews for main)

### 10. Emergency Response

**If a secret is exposed:**

1. **Immediate (< 5 minutes):**
   - Revoke the exposed secret (Google AI Studio for Gemini keys)
   - Generate new secret
   - Update production environment

2. **Short-term (< 1 hour):**
   - Review git history: `git log -p | grep -i "secret_pattern"`
   - Check if pushed to GitHub
   - Notify team if applicable

3. **Long-term:**
   - Consider rewriting history if critical
   - Update security procedures
   - Add to pre-commit hooks

## Summary

**Golden Rules:**
1. Never commit `.env` files
2. Always use `.env.example` for documentation
3. Review `git diff --cached` before every commit
4. Use environment variables for all secrets
5. Revoke immediately if exposed
