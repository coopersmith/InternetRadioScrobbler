# Fixing GitHub Authentication

## The Issue

GitHub no longer accepts passwords for HTTPS authentication. You need either:
1. **Personal Access Token** (recommended for HTTPS)
2. **SSH keys** (recommended for long-term)

## Solution 1: Use Personal Access Token (Quick Fix)

### Step 1: Create a Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Radio Scrobbler"
4. Select scopes: Check `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Use Token Instead of Password

When you push, use the token as your password:

```bash
git push -u origin main
# Username: coopersmith
# Password: <paste your token here>
```

### Step 3: Save Credentials (Optional)

To avoid entering it every time:

**macOS:**
```bash
git config --global credential.helper osxkeychain
```

Then push once with the token, and it will be saved.

## Solution 2: Switch to SSH (Better Long-term)

### Step 1: Check if you have SSH keys

```bash
ls -al ~/.ssh
```

Look for `id_rsa.pub` or `id_ed25519.pub`

### Step 2: Generate SSH key (if needed)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location
# Press Enter twice for no passphrase (or set one)
```

### Step 3: Add SSH key to GitHub

```bash
# Copy your public key
cat ~/.ssh/id_ed25519.pub
# Or if using RSA:
cat ~/.ssh/id_rsa.pub
```

1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste the key
4. Click "Add SSH key"

### Step 4: Change remote to SSH

```bash
cd /Users/coopersmith/radio-scrobbler
git remote set-url origin git@github.com:coopersmith/InternetRadioScrobbler.git
```

### Step 5: Test SSH connection

```bash
ssh -T git@github.com
```

Should say: "Hi coopersmith! You've successfully authenticated..."

### Step 6: Push

```bash
git push -u origin main
```

## Quick Fix Right Now

**Easiest immediate solution:**

1. Get a token: https://github.com/settings/tokens/new
2. Change remote to use token in URL (temporary):

```bash
git remote set-url origin https://YOUR_TOKEN@github.com/coopersmith/InternetRadioScrobbler.git
git push -u origin main
```

Then change it back:
```bash
git remote set-url origin https://github.com/coopersmith/InternetRadioScrobbler.git
```

## Troubleshooting

**"Permission denied" with SSH:**
- Make sure SSH key is added to GitHub
- Test: `ssh -T git@github.com`

**"Authentication failed" with HTTPS:**
- Make sure you're using a token, not password
- Token needs `repo` scope

**"Repository not found":**
- Make sure the repo exists on GitHub
- Check you have access to it
