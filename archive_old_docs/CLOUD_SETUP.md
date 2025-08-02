# Free Cloud LLM Setup Guide for Vercel Deployment

This guide helps you set up free/low-cost cloud LLM providers that work on Vercel (serverless) deployment.

## Quick Start (Recommended: Groq)

**Groq is the best free option - fast, generous limits, and reliable.**

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up with your email
3. Navigate to API Keys section
4. Create a new API key
5. In your Vercel project settings, add environment variable:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Alternative Free Providers

### Hugging Face (Free)
1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Create an account and generate an access token
3. Add environment variable:
   ```
   HUGGINGFACE_API_KEY=your_hf_token_here
   ```

### Together AI (Good Free Tier)
1. Go to [Together AI](https://api.together.xyz/)
2. Sign up and get API key
3. Add environment variable:
   ```
   TOGETHER_API_KEY=your_together_key_here
   ```

### OpenRouter (Free Models Available)
1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up and get API key
3. Add environment variable:
   ```
   OPENROUTER_API_KEY=your_openrouter_key_here
   ```

## Confluence URL Support

The app now supports pasting Confluence URLs directly! Supported formats:

- **Page URLs**: `https://company.atlassian.net/wiki/spaces/TEAM/pages/123456/Page+Title`
- **Old format**: `https://company.atlassian.net/wiki/display/TEAM/Page+Title`
- **Direct page**: `https://company.atlassian.net/wiki/pages/viewpage.action?pageId=123456`
- **Space overview**: `https://company.atlassian.net/wiki/spaces/TEAM/overview`

Just paste the URL and the app will automatically extract the space key and page ID!

## Features Now Available

### 1. **File Upload** (Requires OpenAI for images/PDFs)
- Upload PNG, JPG, PDF files
- Full image analysis with vision models
- PDF text extraction and analysis

### 2. **Text Analysis** (Works with Free Cloud LLMs)
- Paste design descriptions
- Requirements documents
- Design specifications
- Any text content for review

### 3. **Confluence Integration** (Works with Free Cloud LLMs)
- Paste Confluence URLs directly
- Automatically loads page content
- Reviews multiple pages if needed
- No more manual space/page ID entry!

## Environment Variables for Vercel

In your Vercel project settings, add these variables:

```bash
# Choose ONE of these free LLM providers:
GROQ_API_KEY=your_groq_key_here          # Recommended
# OR
HUGGINGFACE_API_KEY=your_hf_key_here     # Alternative
# OR  
TOGETHER_API_KEY=your_together_key_here  # Alternative
# OR
OPENROUTER_API_KEY=your_openrouter_key_here # Alternative

# For Confluence integration (if needed):
CONFLUENCE_URL=https://yourcompany.atlassian.net
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_KEY=your_confluence_api_key

# Optional - for image/PDF analysis:
OPENAI_API_KEY=your_openai_key_here
```

## Usage Examples

### Text Analysis
1. Select "📝 Text Content"
2. Paste your design requirements or description
3. Choose review type and detail level
4. Click "🔍 Analyze Design"

### Confluence Analysis  
1. Select "🔗 Confluence URL"
2. Paste any Confluence page URL
3. Choose review type and detail level
4. Click "🔍 Analyze Design"

### File Upload (OpenAI required)
1. Select "📎 Upload File"
2. Upload PNG, JPG, or PDF
3. Choose review type and detail level
4. Click "🔍 Analyze Design"

## Why This Solves Your Issues

✅ **Works on Vercel**: Cloud LLMs don't need local servers  
✅ **Free options**: Groq and others offer generous free tiers  
✅ **Confluence URLs**: Just paste the URL, no more space/page ID hunting  
✅ **Multiple input types**: File, text, or Confluence content  
✅ **Fallback options**: If one provider fails, others are available  

## Troubleshooting

- **"No AI provider configured"**: Set up at least one of the cloud LLM API keys
- **"Image analysis requires OpenAI"**: Cloud LLMs currently only support text analysis
- **"Invalid Confluence URL"**: Make sure the URL includes `/wiki/` and is from Atlassian
- **Rate limits**: Free tiers have limits, but they're usually generous for testing

Start with **Groq** - it's the fastest and most reliable free option!
