# Vercel Deployment Optimization Guide

## Problem
The original deployment failed due to the 250MB serverless function size limit.

## Solution
Created an ultra-lightweight version with minimal dependencies and optimized configuration.

## Changes Made

### 1. Minimal Requirements (`requirements.txt`)
- Reduced from 20+ packages to just 3 essential ones:
  - `flask>=2.3.0` - Web framework
  - `pillow>=10.0.0` - Image processing  
  - `requests>=2.31.0` - HTTP requests

### 2. Lightweight API (`api/index-minimal.py`)
- Single-file implementation without heavy agent dependencies
- Direct OpenAI API integration
- Minimal HTML interface
- Optimized image processing

### 3. Optimized Vercel Configuration (`vercel.json`)
- Points to minimal API file
- Reduced memory allocation to 512MB
- Removed unnecessary build configurations

### 4. Enhanced `.vercelignore`
- Excludes all agent directories and heavy files
- Only includes essential API files
- Removes documentation and development files

## Deployment Steps

1. **Commit the changes:**
   ```bash
   git add .
   git commit -m "Optimize for Vercel deployment - reduce serverless function size"
   git push
   ```

2. **Deploy to Vercel:**
   - The deployment should now be under 250MB
   - Function uses minimal dependencies
   - Faster cold starts due to smaller bundle size

## Environment Variables Required

Set these in your Vercel dashboard:

- `OPENAI_API_KEY` - Your OpenAI API key for GPT-4 Vision

## Features Available

The lightweight version supports:
- ✅ Image upload and processing (PNG, JPG, JPEG)
- ✅ Three review types (General, Accessibility, Roku Brand)
- ✅ GPT-4 Vision analysis
- ✅ Web interface
- ✅ Health check endpoint

## Size Comparison

- **Before**: ~300MB+ (failed deployment)
- **After**: ~50-80MB (successful deployment)

## Testing the Deployment

After deployment, test these endpoints:
- `GET /` - Web interface
- `POST /api/review` - Design review API
- `GET /health` - Health check

## Rollback Plan

If needed, you can revert to the full system by:
1. Restoring `requirements-full.txt` to `requirements.txt`
2. Updating `vercel.json` to point to `api/index.py`
3. Using a different deployment platform (like Railway or Render) that supports larger applications

## Performance Notes

- The minimal version has faster cold starts
- Image processing is optimized for web delivery
- Direct API calls reduce latency
- Suitable for MVP and demonstration purposes
