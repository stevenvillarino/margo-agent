# Deploy to Streamlit Cloud Instructions

## Option 1: Streamlit Cloud (Recommended)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Create new app with:
   - Repository: `stevenvillarino/margo-agent`
   - Branch: `main`
   - Main file path: `app.py`
4. Set environment variables:
   - `OPENAI_API_KEY=your_openai_key`
   - `EXA_API_KEY=your_exa_key`

## Option 2: Update Vercel to use Streamlit

Replace the old static HTML with a proper Streamlit deployment.

## Option 3: Keep Current Infrastructure

Update `/api/index.py` to proxy to your Streamlit app instead of serving static HTML.

## Current Issue

- **Vercel deployment**: Serves old static HTML from `/api/index.py`
- **Local development**: Modern Streamlit app with multi-agent AI
- **Solution needed**: Deploy the Streamlit app, not the static HTML

## Quick Fix Commands

```bash
# Deploy to Streamlit Cloud (after setting up account)
streamlit run app.py --server.port=8501

# Or update Vercel deployment
# (requires modifying vercel.json and api/index.py)
```
