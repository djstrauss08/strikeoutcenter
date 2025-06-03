# 🔐 Security Setup Guide - API Key Configuration

## ⚠️ IMPORTANT: API Key Security

**Your API key should NEVER be visible in your code or public repository.** We've updated the scripts to use environment variables for security.

## 🛠️ Local Development Setup

### Step 1: Set Environment Variable Locally

**Option A: Temporary (for current session):**
```bash
export THE_ODDS_API_KEY="fc2d8ba3268ab0b6e5e08a8344b6e797"
```

**Option B: Permanent (recommended):**

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`):
```bash
echo 'export THE_ODDS_API_KEY="fc2d8ba3268ab0b6e5e08a8344b6e797"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Test Local Setup
```bash
# Verify the environment variable is set
echo $THE_ODDS_API_KEY

# Test the scripts
python3 export_json_feed.py --pretty
```

## 🚀 GitHub Actions Setup (For Automatic Updates)

### Step 1: Add GitHub Secret

1. Go to your repository: https://github.com/djstrauss08/strikeoutcenter
2. Click **Settings** (top right)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. **Name:** `THE_ODDS_API_KEY`
6. **Secret:** `fc2d8ba3268ab0b6e5e08a8344b6e797`
7. Click **Add secret**

### Step 2: Update GitHub Actions Workflow

The workflow is already configured to use the secret. It will automatically use `secrets.THE_ODDS_API_KEY` when running.

## 🔄 How It Works

### Local Development:
```python
# Scripts now look for environment variable
API_KEY = os.getenv('THE_ODDS_API_KEY')
if not API_KEY:
    print("❌ Error: THE_ODDS_API_KEY environment variable not set")
    sys.exit(1)
```

### GitHub Actions:
```yaml
# Workflow automatically has access to GitHub Secrets
env:
  THE_ODDS_API_KEY: ${{ secrets.THE_ODDS_API_KEY }}
```

## 🛡️ Security Benefits

✅ **API key not visible in code**  
✅ **API key not in public repository**  
✅ **Different people can use different API keys**  
✅ **Easy to rotate API keys if needed**  
✅ **GitHub Secrets are encrypted and secure**

## 🔧 Alternative: .env File (Local Only)

For local development, you can also use a `.env` file:

### Step 1: Create .env file
```bash
echo "THE_ODDS_API_KEY=fc2d8ba3268ab0b6e5e08a8344b6e797" > .env
```

### Step 2: Load .env in scripts
```python
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('THE_ODDS_API_KEY')
```

### Step 3: Add to requirements.txt
```bash
echo "python-dotenv" >> requirements.txt
```

**Note:** The `.env` file is already in `.gitignore` so it won't be committed.

## 🔄 API Key Rotation

If you need to change your API key:

### Local:
```bash
export THE_ODDS_API_KEY="new-api-key-here"
```

### GitHub:
1. Go to repo Settings → Secrets and variables → Actions
2. Click on `THE_ODDS_API_KEY`
3. Click **Update** and enter new key

## ⚠️ URGENT: Current Situation

**Your current API key was exposed in the public repository.** For maximum security, consider:

1. **Rotating your API key** at The Odds API dashboard
2. **Setting up the new key** using the secure methods above
3. **Monitoring your API usage** for any unexpected activity

## 📞 Support

If your API key was compromised:
- Contact The Odds API support to rotate your key
- Monitor your account for unexpected usage
- Set up usage alerts if available 