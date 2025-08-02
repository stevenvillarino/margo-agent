# 🤖 Slack Bot Setup Guide for Margo Design Review Agent

This guide will help you set up the Slack integration for Margo's AI Design Review system.

## Step 1: Create a Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Name your app: **"Margo Design Review Bot"**
5. Select your workspace

## Step 2: Configure Bot User

1. In your app dashboard, go to **"OAuth & Permissions"**
2. Scroll down to **"Scopes"** → **"Bot Token Scopes"**
3. Add these scopes:
   - `app_mentions:read` - Listen for mentions
   - `channels:history` - Read message history
   - `channels:read` - View basic channel info
   - `chat:write` - Send messages
   - `files:read` - Access files shared with bot
   - `files:write` - Upload files
   - `groups:history` - Read private channel history
   - `groups:read` - View private channel info
   - `im:history` - Read DM history
   - `im:read` - View DM info
   - `im:write` - Send DMs
   - `mpim:history` - Read group DM history
   - `mpim:read` - View group DM info
   - `mpim:write` - Send group DMs
   - `commands` - Use slash commands
   - `users:read` - View user info

## Step 3: Install App to Workspace

1. Scroll to top of **"OAuth & Permissions"** page
2. Click **"Install to Workspace"**
3. Review permissions and click **"Allow"**
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

## Step 4: Enable Socket Mode

1. Go to **"Socket Mode"** in left sidebar
2. Enable **"Enable Socket Mode"**
3. Click **"Generate Token and Scopes"**
4. Name: **"Margo Bot Connection"**
5. Add scope: `connections:write`
6. Click **"Generate"**
7. Copy the **"App-Level Token"** (starts with `xapp-`)

## Step 5: Configure Event Subscriptions

1. Go to **"Event Subscriptions"** in left sidebar
2. **Do NOT enable** "Enable Events" (we use Socket Mode instead)

## Step 6: Set Up Slash Commands

1. Go to **"Slash Commands"** in left sidebar
2. Click **"Create New Command"**
3. Command: `/design-review`
4. Request URL: (leave blank for Socket Mode)
5. Short Description: `Start a comprehensive design review`
6. Usage Hint: `[type:ui|web|mobile] [focus:accessibility|branding|ux]`

## Step 7: Configure Interactive Components

1. Go to **"Interactivity & Shortcuts"**
2. **Do NOT enable** "Interactivity" (Socket Mode handles this)

## Step 8: Update Environment Variables

Add these tokens to your `.env` file:

```bash
# Replace with your actual tokens from steps above
SLACK_BOT_TOKEN=xoxb-your-bot-token-from-step-3
SLACK_APP_TOKEN=xapp-your-app-token-from-step-4
```

## Step 9: Test the Bot

Run the setup script:
```bash
chmod +x scripts/setup_slack.sh
./scripts/setup_slack.sh
```

## Step 10: Start the Bot

```bash
source venv/bin/activate
python slack_bot.py
```

## Usage Examples

Once the bot is running, you can:

1. **Mention the bot with a file:**
   ```
   @Margo please review this design
   ```

2. **Use slash commands:**
   ```
   /design-review type:ui focus:accessibility
   ```

3. **Upload a file and mention:**
   ```
   @Margo check this mobile mockup for brand compliance
   ```

## Troubleshooting

- **Bot not responding:** Check Socket Mode is enabled and app token is correct
- **Permission errors:** Verify all bot scopes are added
- **File access issues:** Ensure `files:read` scope is granted
- **Command not found:** Verify slash command is created and app is installed

## Security Notes

- Keep your tokens secure and never commit them to version control
- Regenerate tokens if they're ever compromised
- Use workspace-specific installations for better security
