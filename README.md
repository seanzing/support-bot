# ZING Customer Support Agent

AI-powered customer support for ZING Business Management Software (https://www.zing.work). It searches a knowledge base, creates support tickets via email, and tracks customer sessions in real time.

![ZING Support Agent](https://img.shields.io/badge/ZING-Support%20Agent-6366F1?style=for-the-badge)

## What It Does

- AI Support Agent: OpenAI-powered chat that knows ZING inside and out
- Knowledge Base: 40+ FAQs covering billing, CRM, scheduling, and more
- Smart Escalation: Creates tickets via email that auto-sync to HubSpot
- AI Insights: Figures out sentiment, issue type, and urgency
- Session Tracking: Shows real-time stats and activity timeline
- Conversation Reset: New Chat button clears state and starts fresh
- Embeddable Widget: Drop-in chat bubble for any website
- Professional UI: Clean design with dark and light mode

## Demo

Widget mode shows a floating chat bubble on a mock ZING landing page. Try it at `localhost:5173/?mode=widget`

### 1. Widget Bubble (Closed)
![Widget Bubble Closed](support-01-widget-bubble-closed.png)

The chat bubble appears in the bottom-right corner of the page, ready for customers to click and get help.

### 2. Widget Open (Empty State)
![Widget Open Empty](support-02-widget-open-empty.png)

When opened, shows the welcome screen with starter prompts like "What is ZING?" and "Pricing plans" to guide users.

### 3. Knowledge Base Answer - Pricing
![KB Pricing Answer](support-03-kb-pricing-answer.png)

Asked "How much does a ZING website cost?" - Agent searches KB and returns full pricing breakdown ($59-$249/month plans).

### 4. Knowledge Base Answer - ZING Local
![KB ZING Local Answer](support-04-kb-zing-local-answer.png)

Asked "What is ZING Local?" - Agent explains the local SEO and directory listing features with detailed capabilities.

### 5. Escalation - Email Collection
![Escalation Email Request](support-05-escalation-email-request.png)

Customer reports "I was charged twice, need a refund" - Issue not in KB, agent begins ticket escalation and asks for email.

### 6. Ticket Confirmation
![Ticket Confirmation Prompt](support-06-ticket-confirmation-prompt.png)

After collecting customer details (email, date, card info), agent confirms the ticket details before creating.

### 7. Ticket Created
![Ticket Created Confirmation](support-07-ticket-created-confirmation.png)

Ticket successfully created and sent via SMTP2GO to HubSpot inbox. Shows confirmation with ticket details.

### What You See
- Dark mode theme with ZING purple branding
- Chat bubble in bottom-right corner
- "ZING Support - AI Assistant" header
- Thinking indicators while agent processes
- Copy and regenerate buttons on responses
- Full ticket escalation workflow from issue to confirmation

## How It Works

```
Frontend (React)     Backend (FastAPI)     External Services
-----------------    ------------------    ------------------
ChatKit UI      -->  OpenAI Agent     -->  OpenAI API
Session Panel        Knowledge Base        SMTP2GO (Email)
Theme Toggle         Email Templates       HubSpot (Auto)
```

When a customer needs help beyond what the AI can handle: Agent creates ticket, SMTP2GO sends email, HubSpot auto-creates ticket from inbox.

## Getting Started

### You'll Need
- Python 3.11+
- Node.js 20+ with pnpm
- OpenAI API Key
- SMTP2GO API Key (for email escalation)

### 1. Install Everything

```bash
git clone https://github.com/nclaydev/zing-customer-support-agent.git
cd zing-customer-support-agent
pnpm install
```

### 2. Set Up Environment

Backend (backend/.env):
```env
OPENAI_API_KEY=sk-proj-your-key
SMTP2GO_API_KEY=api-your-smtp2go-key
ZING_SUPPORT_MODEL=gpt-4.1
```

Frontend (frontend/.env):
```env
VITE_SUPPORT_API_BASE=http://localhost:8001/support
VITE_SUPPORT_CHATKIT_API_URL=http://localhost:8001/support/chatkit
VITE_SUPPORT_CUSTOMER_URL=http://localhost:8001/support/customer
VITE_SUPPORT_CHATKIT_API_DOMAIN_KEY=any-value-for-local-dev
```

### 3. Run It

```bash
pnpm start  # Runs both frontend and backend
```

Or run them separately:
```bash
# Backend (terminal 1)
cd backend && uv run uvicorn app.main:app --reload --port 8001

# Frontend (terminal 2)
cd frontend && pnpm dev
```

### 4. Open It

- App: http://localhost:5171
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

## Embeddable Widget

Add the ZING support chat to any website:

```html
<script src="https://your-domain.vercel.app/widget.js" async></script>
```

With custom settings:
```html
<script>
  window.ZING_WIDGET_CONFIG = {
    position: 'bottom-right',  // or 'bottom-left'
    buttonColor: '#6366F1',
    greeting: 'Need help?'
  };
</script>
<script src="https://your-domain.vercel.app/widget.js" async></script>
```

JavaScript API:
```javascript
ZingChat.open();   // Open chat
ZingChat.close();  // Close chat
ZingChat.toggle(); // Toggle chat
```

## What the Agent Can Do

### Knowledge Base Search
The agent checks 40+ FAQs before responding:
- Pricing and Plans
- Billing and Payments
- Account Management
- Technical Support
- Feature Guides

### Ticket Escalation
Tickets get created when:
1. Customer asks for human help
2. KB search doesn't solve the problem
3. Issue needs account access

Escalated tickets include:
- Full conversation transcript
- AI-generated insights (sentiment, category, urgency)
- Priority level
- Recommended actions for L2 support

### Security
- Prompt injection defense
- No made-up information
- Stays on topic (ZING stuff only)
- Email validation for tickets

## Project Structure

```
zing-customer-support-agent/
├── docker-compose.yml           # Docker orchestration
├── backend/
│   ├── Dockerfile               # Backend container
│   ├── app/
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── zing_support_agent.py # Agent instructions and tools
│   │   ├── knowledge_base.py    # FAQ database
│   │   ├── hubspot_integration.py # Email to HubSpot flow
│   │   └── email_templates.py   # HTML email builder
│   └── .env                     # API keys (not in git)
├── frontend/
│   ├── Dockerfile               # Frontend container
│   ├── nginx.conf               # Nginx config (SPA + proxy)
│   ├── src/
│   │   ├── components/          # React UI components
│   │   ├── hooks/               # Custom React hooks
│   │   └── lib/                 # Config and utilities
│   └── public/
│       └── widget.js            # Embeddable chat widget
└── README.md
```

## API Endpoints

- POST /support/chatkit - ChatKit WebSocket connection
- GET /support/customer - Session data and statistics
- GET /health - Service health check

Session Response:
```json
{
  "customer": {
    "session_id": "thread_abc123",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "questions_asked": 3,
    "kb_articles_viewed": 2,
    "tickets_created": 1,
    "interactions": [...]
  }
}
```

## Docker Deployment

The whole thing is Dockerized so you can deploy it anywhere.

### Quick Start (Docker)
```bash
# Build and run
docker compose build
docker compose up -d

# Access at http://localhost
```

### What's Included
- Backend: python:3.11-slim + uv, port 8001, ~335MB
- Frontend: nginx:alpine, port 80, ~80MB

### Deploy to Any Server
```bash
# 1. Clone repo to your server
git clone https://github.com/nclaydev/zing-customer-support-agent.git
cd zing-customer-support-agent

# 2. Configure backend/.env with your API keys
cp backend/.env.example backend/.env
# Edit backend/.env with your OPENAI_API_KEY, SMTP2GO_API_KEY

# 3. Deploy
docker compose up -d
```

### Cloud Options
- AWS Lightsail Containers: $7-40/month, about 15 min setup
- DigitalOcean App Platform: Similar pricing
- Any VPS with Docker: Full control

### Costs
- Hosting: $7-40/month (varies by provider)
- Email: SMTP2GO (1000 free/month)
- AI: OpenAI (~$0.01-0.03/conversation)

## Tech Stack

- Agent: OpenAI Agents SDK, GPT-4.1
- Backend: FastAPI, Python 3.11+, HTTPX
- Frontend: React 18, TypeScript, Vite
- Styling: TailwindCSS, shadcn/ui
- Chat UI: OpenAI ChatKit
- Email: SMTP2GO API
- Ticketing: HubSpot Conversations

## Environment Variables

- OPENAI_API_KEY (required): OpenAI API key
- SMTP2GO_API_KEY (required): SMTP2GO email API key
- ZING_SUPPORT_MODEL: Model name (default: gpt-4.1)
- SMTP2GO_SENDER: Sender email (default: support@zing-work.com)
- SUPPORT_INBOX: HubSpot inbox email
- ALLOWED_ORIGINS: CORS origins for production

## License

MIT License - See LICENSE for details.

## Support

- Website: https://www.zing.work
- Email: support@zing-work.com
- Phone: 1-888-716-1113

---

Built with OpenAI Agents SDK (https://openai.com/agents) for ZING Business Management Software (https://www.zing.work)
