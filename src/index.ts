import { Hono } from 'hono';

type Bindings = {
  AI: any;
  CACHE_KV: KVNamespace;
  SLACK_BOT_TOKEN: string;
  SLACK_SIGNING_SECRET: string;
  OPENAI_API_KEY: string;
  EXA_API_KEY?: string;
  JIRA_API_TOKEN?: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Health check endpoint
app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy', 
    service: 'roku-design-review-bot',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
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
    
    // Handle file uploads
    if (body.event.type === 'file_shared') {
      console.log('Design file uploaded:', body.event.file);
      // TODO: Process design file
    }
    
    // Handle app mentions
    if (body.event.type === 'app_mention') {
      console.log('App mentioned:', body.event.text);
      // TODO: Respond to mention
    }
  }
  
  return c.json({ status: 'ok' });
});

// Slack slash commands
app.post('/slack/slash', async (c) => {
  const formData = await c.req.formData();
  const command = formData.get('command');
  const text = formData.get('text');
  const userId = formData.get('user_id');
  const channelId = formData.get('channel_id');
  
  console.log(`Received command: ${command} from user: ${userId} in channel: ${channelId}`);
  
  if (command === '/design-review') {
    return c.json({
      response_type: 'in_channel',
      text: '🎨 Roku Design Review Bot is starting your review...',
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: '*🎨 Roku Design Review Bot*\n\nYour design review is being processed. Please upload your design file or provide a URL.\n\n✨ *What I can review:*\n• UI/UX designs\n• Roku-specific interfaces\n• Accessibility compliance\n• Brand guidelines\n• User experience flows'
          }
        },
        {
          type: 'context',
          elements: [
            {
              type: 'mrkdwn',
              text: '💡 *Tip:* For best results, upload high-resolution images or Figma links'
            }
          ]
        }
      ]
    });
  }
  
  if (command === '/roku-admin') {
    const adminCommands = {
      'status': '✅ System Status: All systems operational',
      'metrics': '📊 Reviews today: 42 | Avg response time: 1.2s',
      'help': '🤖 Available commands: status, metrics, help'
    };
    
    const response = adminCommands[text as keyof typeof adminCommands] || adminCommands.help;
    
    return c.json({
      response_type: 'ephemeral',
      text: `🔧 Roku Design Bot Admin\n\n${response}`
    });
  }
  
  return c.json({ 
    text: 'Unknown command. Try `/design-review` or `/roku-admin help`' 
  });
});

// Design review API endpoint
app.post('/api/review', async (c) => {
  try {
    const { imageUrl, reviewType = 'standard' } = await c.req.json();
    
    // TODO: Implement actual design review logic using Workers AI
    const mockResult = {
      overall_score: 8.5,
      review_type: reviewType,
      strengths: [
        'Clean and modern Roku-appropriate design',
        'Good use of whitespace and hierarchy',
        'Consistent with Roku brand guidelines',
        'Clear navigation patterns'
      ],
      issues: [
        'Text size may be too small for TV viewing distance',
        'Focus states need more prominence for remote navigation',
        'Color contrast could be improved for accessibility'
      ],
      recommendations: [
        'Increase font sizes for 10-foot experience',
        'Add more visual emphasis to focused elements',
        'Consider accessibility improvements for WCAG compliance',
        'Test on actual Roku devices for optimal viewing'
      ],
      roku_specific: {
        'remote_navigation': 7.5,
        'tv_optimized': 8.0,
        'brand_compliance': 9.0
      },
      timestamp: new Date().toISOString()
    };
    
    return c.json(mockResult);
  } catch (error) {
    return c.json({ error: 'Failed to process review' }, 500);
  }
});

// Figma webhook endpoint
app.post('/api/figma-webhook', async (c) => {
  const body = await c.req.json();
  console.log('Figma webhook received:', body);
  
  // TODO: Process Figma file updates
  return c.json({ status: 'received' });
});

// JIRA integration endpoint
app.post('/api/jira-create', async (c) => {
  const { summary, description, reviewResult } = await c.req.json();
  
  // TODO: Create JIRA ticket with review results
  const mockTicket = {
    key: 'DESIGN-123',
    url: 'https://roku.atlassian.net/browse/DESIGN-123',
    status: 'created'
  };
  
  return c.json(mockTicket);
});

export default app;
