#!/bin/bash

# 🚀 VP of Design Agent - Quick Cloudflare + Slack Deployment Script
# This script automates the deployment process

set -e

echo "🎨 VP of Design Agent - Cloudflare + Slack Deployment"
echo "======================================================"

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required. Please install from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required. Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Wrangler if not already installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi

echo "✅ Wrangler CLI ready"

# Create TypeScript project structure
echo "🏗️  Setting up TypeScript project structure..."

# Create package.json
cat > package.json << 'EOF'
{
  "name": "vp-design-agent",
  "version": "1.0.0",
  "description": "VP of Design Agent on Cloudflare Workers",
  "main": "src/index.ts",
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "deploy:staging": "wrangler deploy --env staging",
    "deploy:production": "wrangler deploy --env production"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20240729.0",
    "typescript": "^5.5.4",
    "wrangler": "^3.65.1"
  },
  "dependencies": {
    "hono": "^4.5.8"
  }
}
EOF

# Create tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "types": ["@cloudflare/workers-types"],
    "resolveJsonModule": true,
    "allowJs": true,
    "checkJs": false,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF

# Create wrangler.toml
cat > wrangler.toml << 'EOF'
name = "vp-design-agent"
main = "src/index.ts"
compatibility_date = "2024-08-01"
node_compat = true

[env.production]
name = "vp-design-agent-prod"
vars = { ENVIRONMENT = "production" }

[env.staging]  
name = "vp-design-agent-staging"
vars = { ENVIRONMENT = "staging" }

# KV Storage for caching
[[kv_namespaces]]
binding = "CACHE_KV"
preview_id = ""
id = ""

# Workers AI binding
[ai]
binding = "AI"

# Variables (secrets set separately)
[vars]
ENVIRONMENT = "development"
EOF

# Create src directory structure
mkdir -p src/{agents,integrations,utils,types}

# Create main index.ts
cat > src/index.ts << 'EOF'
import { Hono } from 'hono';

type Bindings = {
  AI: any;
  CACHE_KV: KVNamespace;
  SLACK_BOT_TOKEN: string;
  SLACK_SIGNING_SECRET: string;
  OPENAI_API_KEY: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Health check endpoint
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    service: 'vp-design-agent',
    timestamp: new Date().toISOString()
  });
});

// Slack events webhook
app.post('/slack/events', async (c) => {
  const body = await c.req.json();
  
  // URL verification challenge
  if (body.type === 'url_verification') {
    return c.json({ challenge: body.challenge });
  }
  
  // Handle actual events
  if (body.event) {
    console.log('Received Slack event:', body.event.type);
    // TODO: Process Slack events (file uploads, mentions, etc.)
  }
  
  return c.json({ status: 'ok' });
});

// Slack slash commands
app.post('/slack/slash', async (c) => {
  const formData = await c.req.formData();
  const command = formData.get('command');
  const text = formData.get('text');
  const userId = formData.get('user_id');
  
  console.log(`Received command: ${command} from user: ${userId}`);
  
  if (command === '/design-review') {
    return c.json({
      response_type: 'in_channel',
      text: '🎨 VP of Design Agent is starting your review...',
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: '*🎨 VP of Design Agent*\n\nYour design review is being processed. Please upload your design file or provide a URL.'
          }
        }
      ]
    });
  }
  
  if (command === '/vp-admin') {
    return c.json({
      text: `🔧 VP Admin - ${text || 'Available commands: status, metrics, help'}`
    });
  }
  
  return c.json({ text: 'Unknown command' });
});

// Design review API endpoint
app.post('/api/review', async (c) => {
  try {
    const { imageUrl, reviewType = 'standard' } = await c.req.json();
    
    // TODO: Implement actual design review logic
    const mockResult = {
      overall_score: 8.5,
      strengths: [
        'Clean and modern design',
        'Good use of whitespace',
        'Consistent color scheme'
      ],
      issues: [
        'Text hierarchy could be improved',
        'Call-to-action button could be more prominent'
      ],
      recommendations: [
        'Increase font size for better readability',
        'Add more visual emphasis to primary actions',
        'Consider accessibility improvements'
      ],
      timestamp: new Date().toISOString()
    };
    
    return c.json(mockResult);
  } catch (error) {
    return c.json({ error: 'Failed to process review' }, 500);
  }
});

export default app;
EOF

# Create types
cat > src/types/index.ts << 'EOF'
export interface ReviewRequest {
  imageUrl: string;
  userId: string;
  channel: string;
  reviewType: 'standard' | 'accessibility' | 'roku-specific';
}

export interface ReviewResult {
  overall_score: number;
  strengths: string[];
  issues: string[];
  recommendations: string[];
  accessibility_score?: number;
  timestamp: string;
}

export interface SlackEvent {
  type: string;
  user: string;
  channel: string;
  text?: string;
  file?: {
    url_private: string;
    mimetype: string;
    filetype: string;
  };
}
EOF

echo "✅ Project structure created"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo "✅ Dependencies installed"

# Check if user is logged into Wrangler
echo "🔐 Checking Wrangler authentication..."
if ! wrangler whoami &> /dev/null; then
    echo "🔑 Please log into Wrangler:"
    wrangler login
fi

echo "✅ Wrangler authentication verified"

# Create KV namespace
echo "🗄️  Creating KV namespace for caching..."
KV_ID=$(wrangler kv:namespace create "CACHE_KV" --preview false 2>/dev/null | grep -o 'id = "[^"]*"' | cut -d'"' -f2 || echo "")

if [ -n "$KV_ID" ]; then
    # Update wrangler.toml with KV ID
    sed -i.bak "s/id = \"\"/id = \"$KV_ID\"/" wrangler.toml
    echo "✅ KV namespace created: $KV_ID"
else
    echo "⚠️  KV namespace creation failed or already exists"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables:"
echo "   wrangler secret put SLACK_BOT_TOKEN"
echo "   wrangler secret put SLACK_SIGNING_SECRET"
echo "   wrangler secret put OPENAI_API_KEY"
echo ""
echo "2. Deploy to Cloudflare:"
echo "   npm run deploy"
echo ""
echo "3. Configure your Slack app with the Worker URL:"
echo "   Events URL: https://vp-design-agent.YOUR_SUBDOMAIN.workers.dev/slack/events"
echo "   Slash commands URL: https://vp-design-agent.YOUR_SUBDOMAIN.workers.dev/slack/slash"
echo ""
echo "4. Test the deployment:"
echo "   curl https://vp-design-agent.YOUR_SUBDOMAIN.workers.dev/health"
echo ""
echo "📖 Complete guide: DEPLOYMENT_STEPS.md"
