# Clible Web

A modern React web interface for the [Clible v2](../../README.md) Bible study tool. Search scriptures, analyze text, get AI-powered insights, and share results—all from a single Docker container or a Cloud Run deployment.

## 🎯 What You Can Do

- **Find Verses** — Look up Bible verses by reference (e.g., "John 3:16", "Romans 8")
- **Search Text** — Search full-text across your Bible translations with instant results
- **Analyze Text** — Get word counts, unique words, character counts, and word frequency charts
- **AI Insights** — Generate contextual study notes and tone analysis (if you add your Google Gemini API key)
- **Compare Verses** — View the same verse across different translations
- **Download Results** — Export your findings as CSV, Excel-friendly, JSON, HTML, Markdown, or plain text
- **Manage Multiple Translations** — Download and switch between Bible translations
- **Reading plans** — Pick a guided plan (e.g. Psalms in 30 days, New Testament in 90 days, Bible in a year), track daily readings, and see your streak
- **UI language** — English or Finnish for web interface copy (from settings)

## 🚀 Quick Start (No Technical Setup)

### Using Docker (Simplest)

The easiest way to run Clible Web is with Docker. You just need:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
2. A terminal (Command Prompt on Windows, Terminal on Mac/Linux)
3. A PostgreSQL connection string (see [CLOUD_SQL_SETUP.md](../../docs/CLOUD_SQL_SETUP.md) — [Neon](https://neon.tech) offers a free tier)

**One-time setup:**

```bash
# Build the container from the repository root
docker build -f src/clible-web/Dockerfile -t clible-web .
```

**Run it:**

```bash
docker run --rm -p 3000:3000 \
  -e DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require" \
  clible-web
```

Then open your browser to: **<http://localhost:3000>**

**Install a Bible translation** (one-time, in a new terminal):

```bash
docker ps  # Find your running container ID
docker exec <CONTAINER_ID> clible seed install web
```

Then refresh your browser and start searching!

### For Developers (Node.js + Python)

If you prefer running locally for development:

**Prerequisites:**

- [Node.js](https://nodejs.org) 20 or newer
- [Clible CLI](../../README.md) installed and at least one translation seeded

**Setup:**

```bash
# Install JavaScript dependencies
npm install

# Create your environment file
cp .env.example .env

# (Optional) Add your Google Gemini API key to .env for AI features
# GEMINI_API_KEY=AIza...
```

**Run both frontend and backend:**

```bash
npm run dev
```

This starts:

- **Frontend** at <http://localhost:5173> (auto-reloads when you edit code)
- **Backend** at <http://localhost:3000> (handles Bible lookups and AI)

To stop: Press `Ctrl+C` in the terminal.

## ⚙️ Configuration

### Adding Google Gemini AI (Optional)

AI features (tone analysis, study notes) are optional. To enable them:

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key" and copy it
3. Add to your `.env` file or Docker environment variable:

   ```bash
   GEMINI_API_KEY=AIza...
   ```

If you get a "API key not valid" error:

- Make sure you're using a **current** key from AI Studio (not an old Cloud Console key)
- Check your key has no spaces or extra characters
- If your key is restricted by IP/referrer, try using **No restrictions** for local testing

Without a Gemini API key, the app still works perfectly—AI features just show a friendly message.

### Managing Bible Translations

**List installed translations:**

```bash
# If using Docker
docker exec <CONTAINER_ID> clible seed list

# If using local setup
clible seed list
```

**Install more translations:**

```bash
# Web translation (often smallest)
clible seed install web

# King James Version
clible seed install kjv

# ESV (English Standard Version)
clible seed install esv

# See all available: clible seed list --all
```

The translation selector appears as a globe icon 🌐 in the app. Refresh the page after installing new translations.

## 📊 Understanding the UI

### Main Search Bar

- Type a verse reference: `John 3:16`, `Genesis 1`, `Psalm 23:4`
- Or search for text: `love`, `faith`, `kingdom`
- Toggle between **Verse** and **Search** tabs

### Results Views

**Reader View** (default)

- Shows the verse text
- Click **AI Insights** for contextual study notes
- Switch to Analytics to see word statistics

**Analytics View**

- **Reference**: Stats for the specific verse(s) you fetched
- **Chapter**: Stats for the entire chapter
- **Book**: Stats for the entire book
- Charts show word frequency (most common words)

**Search Results**

- Click any result to view the full verse
- See surrounding context

### Exporting

Click the **Download** icon to save your current view:

- **CSV** — Open in Excel or Google Sheets
- **JSON** — For developers / custom tools
- **HTML** — View in any web browser
- **Markdown** — For notes / documentation
- **XML** — For data processing

## 🐳 Docker Reference

### Build from Source

```bash
docker build -f src/clible-web/Dockerfile -t clible-web .
```

### Run with Custom Port

```bash
docker run -p 8080:3000 -e DATABASE_URL="..." clible-web  # Access at http://localhost:8080
```

### Add Custom Environment Variables

```bash
docker run \
  -e DATABASE_URL="postgresql://..." \
  -e GEMINI_API_KEY="your-key-here" \
  clible-web
```

### Check Container Logs

```bash
docker logs <CONTAINER_ID>
```

## 🔒 Security Notes

- **Your API Key is Safe**: The Gemini API key never reaches your browser—it only lives on the server
- **Bible Data is Offline**: Once a translation is seeded, all verse lookups and searches work without network access
- **User Accounts use PostgreSQL**: Passwords are hashed (bcrypt) and stored in your own PostgreSQL database; never sent to any external service
- **No Tracking**: Clible Web doesn't track you or send data anywhere

## 🆘 Troubleshooting

### "Verse not found" Error

- Make sure you've installed a translation: `clible seed install web`
- Refresh the page after installing
- Use the correct book name (e.g., `John` not `Jhn`)

### Search is Empty

- Check that a translation is installed
- Try a common word: `love`, `God`, `pray`
- Some translations are larger and take longer to index the first time

### AI Features Don't Work

- Verify `GEMINI_API_KEY` in your `.env` file or Docker env
- Check that the key is from [Google AI Studio](https://aistudio.google.com/apikey), not from Cloud Console
- Try disabling any VPN or proxy (they can block API calls)

### Can't Connect to <http://localhost:3000>

- Make sure the Docker container is running: `docker ps`
- Check that port 3000 isn't already in use
- Try a different port: `docker run -p 8080:3000 -e DATABASE_URL="..." clible-web`
- Verify `DATABASE_URL` is set and points to a reachable PostgreSQL instance

### Forgot Password

- Clible Web doesn't have a "forgot password" feature yet
- For now, delete your user data and create a new account (contact the app maintainer for help)

## 💡 Tips & Tricks

- **Keyboard Shortcut**: Press `Enter` to search after typing
- **Case Insensitive**: `john 3:16` works just like `John 3:16`
- **Verse Ranges**: `John 3:16-18` fetches multiple verses
- **Whole Chapters**: `John 3` fetches the entire chapter
- **Word Frequency**: Hover over bars in the analytics chart to see exact counts
- **Dark Mode**: Click the settings icon (⚙️) to toggle dark/light theme

## 📖 For Bible Scholars & Teachers

If you're using Clible Web for teaching or research:

- **Text Analytics** helps identify dominant themes and word patterns
- **Multiple Translations** let you compare nuances in language
- **Word Frequency Analysis** shows emphasis and repetition in passages
- **Export to Markdown** makes it easy to include results in lesson plans or papers

## 🤝 Contributing & Reporting Issues

Found a bug or have a feature request? Visit the [GitHub repository](../../) and open an issue.

## 📜 License

Apache License 2.0 — See [LICENSE](LICENSE) for details.

---

**Need more help?** Check the [WEB_INTEGRATION.md](WEB_INTEGRATION.md) guide for technical details, or [ARCHITECTURAL_STRUCTURE.md](ARCHITECTURAL_STRUCTURE.md) if you're diving into the code.
