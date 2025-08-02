# 🤖 Margo Slack Bot - Quick Start

The Margo Design Review Bot brings AI-powered design analysis directly to your Slack workspace. Get instant feedback from a team of 7 specialized AI agents.

## ⚡ Quick Setup (5 minutes)

### Option A: Guided Setup (Recommended)
```bash
./configure_slack.sh
```

### Option B: Manual Setup

1. **Create your Slack app** at [api.slack.com/apps](https://api.slack.com/apps)
2. **Configure permissions** (see SLACK_SETUP.md for details)
3. **Update .env file** with your tokens:
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```
4. **Test setup:**
   ```bash
   ./scripts/setup_slack.sh
   ```

## 🚀 Start the Bot

```bash
python run_slack_bot.py
```

## 💡 Usage Examples

### Basic Usage
- Upload a design file and mention: `@Margo please review this`
- Use slash command: `/design-review`
- Ask for help: `@Margo help`

### Advanced Usage
- Specific review type: `/design-review type:mobile focus:accessibility`
- Brand compliance check: `@Margo check this for Roku brand guidelines`
- UX analysis: `@Margo analyze the user flow in this mockup`

## 🎯 What Margo Can Review

- **UI/UX Designs** - Mobile, web, TV interfaces
- **Brand Compliance** - Logo usage, color schemes, typography  
- **Accessibility** - WCAG compliance, color contrast, readability
- **Visual Hierarchy** - Layout, spacing, information architecture
- **User Experience** - Flow analysis, usability concerns

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check tokens in .env, verify app is installed |
| Permission errors | Add required scopes in Slack app settings |
| Import errors | Run `pip install -r requirements.txt` |
| File upload issues | Ensure `files:read` scope is granted |

## 📁 Supported File Types

- PNG, JPG, JPEG images
- PDF documents  
- Figma links (with API token)
- Sketch files (exported as images)

## 🔐 Security

- Tokens are encrypted in transit
- No design files are permanently stored
- All analysis is done in real-time
- SOC2 compliant infrastructure

## 📞 Support

- Check `SLACK_SETUP.md` for detailed setup instructions
- Run `./scripts/setup_slack.sh` to test configuration
- Join #margo-support for help

---

**Ready to transform your design review process?** Start with `./configure_slack.sh` and have Margo reviewing your designs in under 5 minutes! 🎨✨
