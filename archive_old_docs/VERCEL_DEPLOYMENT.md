# Vercel Deployment Guide for Margo Design Review Agent

## Current Status: ✅ Ready for Deployment

Your project is now properly configured for Vercel deployment with the following setup:

### 📁 Project Structure
```
/api/index.py       # Flask app for Vercel serverless functions
/vercel.json        # Vercel deployment configuration
/requirements.txt   # Python dependencies (includes Flask)
/.vercelignore      # Files to exclude from deployment
```

### 🚀 Deployment Steps

1. **Install Vercel CLI** (if you haven't already):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   cd /Users/stevenvillarino/margo-agent
   vercel --prod
   ```

3. **Set Environment Variables in Vercel Dashboard**:
   - Go to your Vercel project dashboard
   - Navigate to Settings → Environment Variables
   - Add the following variables:

   **Required for OpenAI (File uploads, images, PDFs):**
   ```
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

   **Optional for Free Cloud LLMs (Text analysis):**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   HUGGINGFACE_API_KEY=your_hf_api_key_here
   TOGETHER_API_KEY=your_together_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

   **Optional for Confluence Integration:**
   ```
   CONFLUENCE_URL=https://yourcompany.atlassian.net
   CONFLUENCE_USERNAME=your_email@company.com
   CONFLUENCE_API_KEY=your_confluence_api_key
   ```

   **Optional for Figma Integration:**
   ```
   FIGMA_ACCESS_TOKEN=your_figma_access_token
   ```

### 🤖 AI Provider Options

Your deployment supports multiple AI providers:

1. **OpenAI (Recommended for full features)**
   - ✅ Image analysis
   - ✅ PDF processing
   - ✅ Roku TV design review
   - ❌ Costs money (but very capable)

2. **Free Cloud LLMs (Great for text analysis)**
   - ✅ Text-based design review
   - ✅ Completely free options available
   - ✅ Fast inference (especially Groq)
   - ❌ No image/PDF analysis
   - **Recommended: Groq** - Sign up at https://console.groq.com/

### 🌐 Features Available After Deployment

**With OpenAI API Key:**
- 📁 File upload analysis (images, PDFs)
- 📝 Text-based design review
- 🎨 Figma integration
- 📚 Confluence integration
- 🏆 Roku TV design review with grading

**With Free Cloud LLMs Only:**
- 📝 Text-based design review
- 🎯 Multiple review types (UI/UX, Accessibility, etc.)
- 💡 Detailed suggestions and feedback

### 🔧 Current Configuration

- **vercel.json**: ✅ Configured for Python serverless functions
- **Flask API**: ✅ Located in `/api/index.py`
- **Dependencies**: ✅ Flask added to requirements.txt
- **Import test**: ✅ Flask app imports successfully
- **Cloud LLM support**: ✅ Integrated with fallback options

### 🚨 Troubleshooting

If you get a 404 error after deployment:

1. **Check Vercel logs**:
   ```bash
   vercel logs --follow
   ```

2. **Verify environment variables are set** in the Vercel dashboard

3. **Ensure the build completed successfully** - check the Vercel deployment logs

4. **Test the health endpoint**:
   ```
   https://your-app.vercel.app/health
   ```

### 🆓 Free AI Setup (Recommended)

For the best free experience, set up Groq:

1. Go to https://console.groq.com/
2. Sign up for a free account
3. Generate an API key
4. Add `GROQ_API_KEY=your_key_here` to Vercel environment variables
5. Users can then use the "📝 Text Description" option for free AI-powered design reviews

### 📝 Next Steps

1. Deploy to Vercel: `vercel --prod`
2. Set up at least one AI provider (Groq recommended for free option)
3. Test the deployment
4. Share the URL with your team!

### 🎯 Two Interface Options

After deployment, you'll have:

1. **Streamlit Interface** (local development):
   ```bash
   streamlit run app.py
   ```
   - Full-featured with chat, VP preferences, learning
   - Best for development and power users

2. **Flask Interface** (Vercel deployment):
   ```
   https://your-app.vercel.app/
   ```
   - Streamlined web interface
   - Optimized for serverless deployment
   - Works great on mobile devices
