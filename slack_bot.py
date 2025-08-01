"""
Slack Bot Integration for Margo Design Review Agent

This module provides Slack bot functionality for the multi-agent design review system,
allowing teams to request design reviews directly through Slack with file uploads
and interactive results.
"""

import os
import json
import asyncio
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO

import aiohttp
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from agents.enhanced_system import EnhancedDesignReviewSystem
from agents.orchestrator import ReviewResult, OrchestratedReview


class SlackDesignReviewBot:
    """
    Slack bot for conducting design reviews through Slack interface.
    
    Features:
    - File upload handling for design images
    - Interactive slash commands for reviews
    - Real-time progress updates
    - Threaded review results
    - Admin commands for system management
    """
    
    def __init__(self, 
                 slack_bot_token: str,
                 slack_app_token: str,
                 openai_api_key: str,
                 exa_api_key: Optional[str] = None,
                 confluence_config: Optional[Dict[str, str]] = None):
        """
        Initialize Slack bot with review system.
        
        Args:
            slack_bot_token: Slack bot OAuth token
            slack_app_token: Slack app-level token for socket mode
            openai_api_key: OpenAI API key
            exa_api_key: Optional Exa API key for research
            confluence_config: Optional Confluence configuration
        """
        # Initialize Slack app
        self.app = AsyncApp(token=slack_bot_token)
        self.client = AsyncWebClient(token=slack_bot_token)
        self.app_token = slack_app_token
        
        # Initialize review system
        self.review_system = EnhancedDesignReviewSystem(
            openai_api_key=openai_api_key,
            exa_api_key=exa_api_key
        )
        
        # Bot configuration
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.pdf', '.figma']
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.review_channel_types = ['public_channel', 'private_channel', 'mpim', 'im']
        
        # Active reviews tracking
        self.active_reviews = {}
        self.review_history = []
        
        # Setup event handlers
        self._setup_event_handlers()
        
        print("🤖 Slack Design Review Bot initialized")
        print(f"📊 Review system ready with {len(self.review_system.agents)} agents")
    
    def _setup_event_handlers(self):
        """Setup Slack event handlers for the bot."""
        
        # Slash command for design review
        @self.app.command("/design-review")
        async def handle_design_review_command(ack, respond, command, client):
            await ack()
            await self._handle_design_review_command(respond, command, client)
        
        # File upload handler
        @self.app.event("file_shared")
        async def handle_file_shared(event, client, say):
            await self._handle_file_upload(event, client, say)
        
        # Message handler for @ mentions
        @self.app.event("app_mention")
        async def handle_app_mention(event, client, say):
            await self._handle_app_mention(event, client, say)
        
        # Shortcut for quick review
        @self.app.shortcut("quick_design_review")
        async def handle_quick_review_shortcut(ack, shortcut, client):
            await ack()
            await self._handle_quick_review_shortcut(shortcut, client)
        
        # Admin commands
        @self.app.command("/margo-admin")
        async def handle_admin_command(ack, respond, command):
            await ack()
            await self._handle_admin_command(respond, command)
        
        # Interactive components (buttons, select menus)
        @self.app.action("review_action")
        async def handle_review_action(ack, body, client):
            await ack()
            await self._handle_review_action(body, client)
    
    async def _handle_design_review_command(self, respond, command, client):
        """Handle /design-review slash command."""
        try:
            user_id = command['user_id']
            channel_id = command['channel_id']
            text = command.get('text', '').strip()
            
            # Parse command arguments
            args = self._parse_command_args(text)
            
            if not args or args.get('help'):
                await self._send_help_message(respond)
                return
            
            # Check for file in recent messages
            recent_files = await self._get_recent_files(client, channel_id, user_id)
            
            if not recent_files:
                await respond({
                    "response_type": "ephemeral",
                    "text": "🖼️ Please upload a design file first, then run the command.",
                    "blocks": self._create_upload_prompt_blocks()
                })
                return
            
            # Start review process
            file_info = recent_files[0]  # Use most recent file
            review_id = await self._start_design_review(
                client, channel_id, user_id, file_info, args
            )
            
            await respond({
                "response_type": "in_channel",
                "text": f"🚀 Starting design review for {file_info['name']}",
                "blocks": self._create_review_started_blocks(review_id, file_info)
            })
            
        except Exception as e:
            await respond({
                "response_type": "ephemeral",
                "text": f"❌ Error starting review: {str(e)}"
            })
    
    async def _handle_file_upload(self, event, client, say):
        """Handle file upload events."""
        try:
            file_id = event['file_id']
            user_id = event['user_id']
            
            # Get file info
            file_info = await client.files_info(file=file_id)
            file_data = file_info['file']
            
            # Check if it's a design file
            if not self._is_design_file(file_data):
                return
            
            # Send quick review option
            await say({
                "text": f"📎 Design file detected: {file_data['name']}",
                "blocks": self._create_quick_review_blocks(file_id, file_data)
            })
            
        except Exception as e:
            print(f"Error handling file upload: {e}")
    
    async def _handle_app_mention(self, event, client, say):
        """Handle @ mentions of the bot."""
        try:
            text = event.get('text', '').lower()
            user_id = event['user']
            channel_id = event['channel']
            
            if 'review' in text:
                # Look for attached files
                files = event.get('files', [])
                
                if files:
                    file_data = files[0]
                    if self._is_design_file(file_data):
                        review_id = await self._start_design_review(
                            client, channel_id, user_id, file_data, {}
                        )
                        
                        await say({
                            "text": f"🎯 Got it! Starting review for {file_data['name']}",
                            "thread_ts": event['ts']
                        })
                    else:
                        await say({
                            "text": "🤔 That doesn't look like a design file. I can review PNG, JPG, PDF, or Figma files.",
                            "thread_ts": event['ts']
                        })
                else:
                    await say({
                        "text": "👋 Hi! Mention me with a design file to start a review, or use `/design-review` command.",
                        "thread_ts": event['ts']
                    })
            elif 'help' in text:
                await say({
                    "text": "🤖 *Margo Design Review Bot Help*",
                    "blocks": self._create_help_blocks(),
                    "thread_ts": event['ts']
                })
            else:
                await say({
                    "text": "🤖 I'm here to help with design reviews! Mention me with a file or use `/design-review`.",
                    "thread_ts": event['ts']
                })
                
        except Exception as e:
            print(f"Error handling app mention: {e}")
    
    async def _start_design_review(self, 
                                 client: AsyncWebClient,
                                 channel_id: str,
                                 user_id: str,
                                 file_info: Dict[str, Any],
                                 args: Dict[str, Any]) -> str:
        """Start a comprehensive design review."""
        
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        try:
            # Download file
            file_data = await self._download_file(client, file_info)
            
            # Get file as base64
            image_data = base64.b64encode(file_data).decode('utf-8')
            
            # Prepare context from args
            context = {
                'design_type': args.get('type', 'ui_design'),
                'target_audience': args.get('audience', 'roku_users'),
                'review_focus': args.get('focus', 'comprehensive'),
                'urgency': args.get('urgency', 'normal'),
                'user_id': user_id,
                'channel_id': channel_id,
                'file_name': file_info['name'],
                'review_id': review_id
            }
            
            # Store active review
            self.active_reviews[review_id] = {
                'status': 'in_progress',
                'start_time': datetime.now(),
                'context': context,
                'file_info': file_info,
                'user_id': user_id,
                'channel_id': channel_id
            }
            
            # Send progress message
            progress_message = await client.chat_postMessage(
                channel=channel_id,
                text=f"🔄 Conducting comprehensive design review...",
                blocks=self._create_progress_blocks(review_id, 0)
            )
            
            # Start async review
            asyncio.create_task(self._conduct_async_review(
                client, review_id, image_data, context, progress_message['ts']
            ))
            
            return review_id
            
        except Exception as e:
            self.active_reviews[review_id] = {
                'status': 'failed',
                'error': str(e),
                'start_time': datetime.now()
            }
            raise e
    
    async def _conduct_async_review(self,
                                  client: AsyncWebClient,
                                  review_id: str,
                                  image_data: str,
                                  context: Dict[str, Any],
                                  progress_ts: str):
        """Conduct the actual design review asynchronously."""
        
        try:
            channel_id = context['channel_id']
            
            # Update progress - Starting review
            await self._update_progress(client, channel_id, progress_ts, review_id, 1)
            
            # Conduct comprehensive review
            review_result = await self.review_system.conduct_comprehensive_review(
                image_data=image_data,
                design_type=context['design_type'],
                context=context,
                progress_callback=lambda step: asyncio.create_task(
                    self._update_progress(client, channel_id, progress_ts, review_id, step)
                )
            )
            
            # Update progress - Complete
            await self._update_progress(client, channel_id, progress_ts, review_id, 5)
            
            # Send results
            await self._send_review_results(client, channel_id, review_id, review_result)
            
            # Update active reviews
            self.active_reviews[review_id]['status'] = 'completed'
            self.active_reviews[review_id]['result'] = review_result
            self.active_reviews[review_id]['end_time'] = datetime.now()
            
            # Add to history
            self.review_history.append(self.active_reviews[review_id])
            
        except Exception as e:
            # Handle error
            await client.chat_postMessage(
                channel=context['channel_id'],
                text=f"❌ Review failed: {str(e)}",
                thread_ts=progress_ts
            )
            
            self.active_reviews[review_id]['status'] = 'failed'
            self.active_reviews[review_id]['error'] = str(e)
    
    async def _send_review_results(self,
                                 client: AsyncWebClient,
                                 channel_id: str,
                                 review_id: str,
                                 review_result: OrchestratedReview):
        """Send comprehensive review results to Slack."""
        
        try:
            # Create summary message
            summary_blocks = self._create_summary_blocks(review_result)
            
            summary_message = await client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Design Review Complete - Score: {review_result.overall_score:.1f}/10",
                blocks=summary_blocks
            )
            
            # Send detailed results in thread
            thread_ts = summary_message['ts']
            
            # Agent-by-agent results
            for phase_name, phase_results in review_result.phase_results.items():
                phase_blocks = self._create_phase_blocks(phase_name, phase_results)
                
                await client.chat_postMessage(
                    channel=channel_id,
                    text=f"📊 {phase_name.replace('_', ' ').title()} Results",
                    blocks=phase_blocks,
                    thread_ts=thread_ts
                )
            
            # Consensus analysis
            if hasattr(review_result, 'consensus_analysis'):
                consensus_blocks = self._create_consensus_blocks(review_result.consensus_analysis)
                
                await client.chat_postMessage(
                    channel=channel_id,
                    text="🤝 Agent Consensus Analysis",
                    blocks=consensus_blocks,
                    thread_ts=thread_ts
                )
            
            # Quality metrics
            if hasattr(review_result, 'quality_metrics'):
                quality_blocks = self._create_quality_blocks(review_result.quality_metrics)
                
                await client.chat_postMessage(
                    channel=channel_id,
                    text="📈 Quality Metrics",
                    blocks=quality_blocks,
                    thread_ts=thread_ts
                )
            
            # Learning insights
            if hasattr(review_result, 'learning_insights'):
                learning_blocks = self._create_learning_blocks(review_result.learning_insights)
                
                await client.chat_postMessage(
                    channel=channel_id,
                    text="🧠 Learning Insights",
                    blocks=learning_blocks,
                    thread_ts=thread_ts
                )
                
        except Exception as e:
            await client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Error sending results: {str(e)}"
            )
    
    # Utility methods for Slack integration
    def _is_design_file(self, file_data: Dict[str, Any]) -> bool:
        """Check if uploaded file is a design file."""
        name = file_data.get('name', '').lower()
        filetype = file_data.get('filetype', '').lower()
        
        return any(ext in name for ext in self.supported_formats) or filetype in ['png', 'jpg', 'jpeg', 'pdf']
    
    async def _download_file(self, client: AsyncWebClient, file_info: Dict[str, Any]) -> bytes:
        """Download file from Slack."""
        file_url = file_info['url_private_download']
        
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {client.token}'}
            
            async with session.get(file_url, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception(f"Failed to download file: {response.status}")
    
    def _parse_command_args(self, text: str) -> Dict[str, str]:
        """Parse command arguments from text."""
        args = {}
        
        if not text:
            return args
        
        # Simple parsing - can be enhanced
        parts = text.split()
        
        for i, part in enumerate(parts):
            if part.startswith('--'):
                key = part[2:]
                value = parts[i + 1] if i + 1 < len(parts) and not parts[i + 1].startswith('--') else True
                args[key] = value
        
        return args
    
    async def _get_recent_files(self, client: AsyncWebClient, channel_id: str, user_id: str) -> List[Dict]:
        """Get recent files from channel."""
        try:
            # Get recent messages
            response = await client.conversations_history(
                channel=channel_id,
                limit=20
            )
            
            files = []
            for message in response['messages']:
                if message.get('user') == user_id and 'files' in message:
                    for file_data in message['files']:
                        if self._is_design_file(file_data):
                            files.append(file_data)
            
            return files
            
        except Exception as e:
            print(f"Error getting recent files: {e}")
            return []
    
    # Block builders for Slack UI
    def _create_summary_blocks(self, review_result: OrchestratedReview) -> List[Dict]:
        """Create summary blocks for review result."""
        
        score_emoji = "🟢" if review_result.overall_score >= 8 else "🟡" if review_result.overall_score >= 6 else "🔴"
        
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{score_emoji} Design Review Complete"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Overall Score:*\n{review_result.overall_score:.1f}/10"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Agents Consulted:*\n{len([agent for phase_results in review_result.phase_results.values() for agent in phase_results])}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Review Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Quality Grade:*\n{getattr(review_result, 'quality_grade', 'B')}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 View Details"
                        },
                        "action_id": "review_action",
                        "value": "view_details"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📈 Export Report"
                        },
                        "action_id": "review_action",
                        "value": "export_report"
                    }
                ]
            }
        ]
    
    def _create_progress_blocks(self, review_id: str, step: int) -> List[Dict]:
        """Create progress blocks."""
        
        steps = [
            "🔄 Initializing review",
            "👥 Peer review analysis", 
            "🎯 VP product evaluation",
            "♿ Accessibility assessment",
            "🔍 Quality validation",
            "✅ Finalizing results"
        ]
        
        progress_text = steps[min(step, len(steps) - 1)]
        
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Review ID:* `{review_id}`\n*Status:* {progress_text}"
                }
            }
        ]
    
    def _create_help_blocks(self) -> List[Dict]:
        """Create help blocks."""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Margo Design Review Bot"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Commands:*\n• `/design-review` - Start a comprehensive review\n• `@margo` + file - Quick review\n• `/margo-admin` - Admin commands"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Supported Files:*\nPNG, JPG, PDF, Figma files up to 10MB"
                }
            }
        ]
    
    async def _update_progress(self, client: AsyncWebClient, channel_id: str, message_ts: str, review_id: str, step: int):
        """Update progress message."""
        try:
            await client.chat_update(
                channel=channel_id,
                ts=message_ts,
                blocks=self._create_progress_blocks(review_id, step)
            )
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    async def start(self):
        """Start the Slack bot."""
        handler = AsyncSocketModeHandler(self.app, self.app_token)
        await handler.start_async()


# Example deployment script
async def main():
    """Main function to run the Slack bot."""
    
    # Load environment variables
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_app_token = os.getenv('SLACK_APP_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    exa_api_key = os.getenv('EXA_API_KEY')
    
    if not all([slack_bot_token, slack_app_token, openai_api_key]):
        print("❌ Missing required environment variables:")
        print("   - SLACK_BOT_TOKEN")
        print("   - SLACK_APP_TOKEN") 
        print("   - OPENAI_API_KEY")
        return
    
    # Optional Confluence config
    confluence_config = None
    if all([os.getenv('CONFLUENCE_URL'), os.getenv('CONFLUENCE_USERNAME'), os.getenv('CONFLUENCE_API_KEY')]):
        confluence_config = {
            'url': os.getenv('CONFLUENCE_URL'),
            'username': os.getenv('CONFLUENCE_USERNAME'),
            'api_key': os.getenv('CONFLUENCE_API_KEY')
        }
    
    # Create and start bot
    bot = SlackDesignReviewBot(
        slack_bot_token=slack_bot_token,
        slack_app_token=slack_app_token,
        openai_api_key=openai_api_key,
        exa_api_key=exa_api_key,
        confluence_config=confluence_config
    )
    
    print("🚀 Starting Slack Design Review Bot...")
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
