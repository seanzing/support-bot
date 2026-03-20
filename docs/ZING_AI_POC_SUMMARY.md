# ZING AI Proof-of-Concept: Technical Summary

## Executive Overview

This document summarizes two major AI-powered applications developed for ZING as proof-of-concept demonstrations. Both applications have been **fully Dockerized** and are ready for deployment or handoff to ZING's development team.

---

## 1. ZING Customer Support Agent

### What It Does

An AI-powered customer support system that provides 24/7 automated support for ZING customers. It answers common questions using a knowledge base, and when it can't help, escalates issues by creating support tickets that automatically trigger ZING's existing HubSpot ticket automation workflows.

### Key Features

| Feature | Description |
|---------|-------------|
| **Admin Panel** | Dashboard for tracking questions, articles accessed, and tickets created per session |
| **Embeddable Widget** | Floating chat bubble that can be embedded on any ZING website |
| **Knowledge Base** | 20+ FAQ entries covering pricing, services, billing, technical support |
| **AI Contextualization** | Uses GPT-5.1 with reasoning to understand customer intent and provide accurate answers |
| **Ticket Escalation** | Creates support tickets via email, which triggers HubSpot ticket automation |
| **Generative UI** | Ticket confirmation widget renders directly in the chat conversation |
| **Help Center Integration** | Direct link to ZING's Zendesk Help Center (support.zing.work) |
| **Manual Ticket Creation** | Button for staff to create tickets manually from the admin panel |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZING Customer Support Agent                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────────────────────┐  │
│  │   React Frontend  │     │          FastAPI Backend          │  │
│  │                  │     │                                  │  │
│  │  ┌────────────┐  │     │  ┌──────────────────────────┐   │  │
│  │  │  ChatKit   │──┼─────┼──│   ChatKit Agent Adapter   │   │  │
│  │  │  (iframe)  │  │     │  │                          │   │  │
│  │  └────────────┘  │     │  │  ┌────────────────────┐  │   │  │
│  │                  │     │  │  │ AI Support Agent   │  │   │  │
│  │  ┌────────────┐  │     │  │  │ (GPT-5.1 + Tools)  │  │   │  │
│  │  │   Admin    │  │     │  │  └────────────────────┘  │   │  │
│  │  │   Panel    │  │     │  │          ↓               │   │  │
│  │  └────────────┘  │     │  │  ┌────────────────────┐  │   │  │
│  │                  │     │  │  │  Knowledge Base    │  │   │  │
│  │  ┌────────────┐  │     │  │  │  (20+ FAQ entries) │  │   │  │
│  │  │  Widget    │  │     │  │  └────────────────────┘  │   │  │
│  │  │   Demo     │  │     │  │          ↓               │   │  │
│  │  └────────────┘  │     │  │  ┌────────────────────┐  │   │  │
│  └──────────────────┘     │  │  │  HubSpot Manager   │  │   │  │
│                           │  │  │  (Email → Ticket)  │  │   │  │
│                           │  │  └────────────────────┘  │   │  │
│                           │  └──────────────────────────┘   │  │
│                           │              ↓                   │  │
│                           │  ┌──────────────────────────┐   │  │
│                           │  │   SMTP2GO Email API      │   │  │
│                           │  └──────────────────────────┘   │  │
│                           └──────────────────────────────────┘  │
│                                          ↓                       │
│                           ┌──────────────────────────┐          │
│                           │  HubSpot Ticket Workflow  │          │
│                           │  (Existing Automation)    │          │
│                           └──────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Modes

1. **Admin Panel Mode** (`/`) - Full dashboard with session tracking
2. **Widget Demo Mode** (`/?mode=widget`) - Simulated ZING website with floating chat
3. **Embed Mode** (`/?embed=true`) - Clean iframe-only view for integration

### How Ticket Escalation Works

1. Customer asks a question the AI can't answer from the knowledge base
2. AI offers to create a support ticket
3. Customer provides their email address
4. AI confirms ticket details with customer
5. **create_support_ticket** tool is called:
   - Extracts full conversation transcript
   - Sends formatted email via SMTP2GO
   - Email triggers HubSpot ticket creation workflow
6. **Generative UI Widget** displays ticket confirmation in chat
7. Customer sees ticket reference and expected response time

---

## 2. ZING Data Chat

### What It Does

An AI-powered data analytics tool that allows users to query ZING's HubSpot contact database (133,000+ contacts) using natural language, and visualize results directly in the chat with professional charts.

### Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language Queries** | Ask questions like "How many customers are in Colorado?" |
| **Direct Database Access** | Connects to Supabase PostgreSQL via MCP (Model Context Protocol) |
| **12+ Chart Types** | Bar, Pie, Doughnut, Line, Area, Radar, Scatter, and more |
| **Automatic Data Cleaning** | Filters NULL/Unknown values from charts for clean visualizations |
| **In-Chat Visualization** | Charts render as images directly in the conversation |
| **Embeddable Widget** | Same floating chat widget design as Support Agent |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       ZING Data Chat                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────────────────────┐  │
│  │   React Frontend  │     │          FastAPI Backend          │  │
│  │                  │     │                                  │  │
│  │  ┌────────────┐  │     │  ┌──────────────────────────┐   │  │
│  │  │  ChatKit   │──┼─────┼──│   ChatKit Agent Adapter   │   │  │
│  │  │  (iframe)  │  │     │  │                          │   │  │
│  │  └────────────┘  │     │  │  ┌────────────────────┐  │   │  │
│  │                  │     │  │  │ Data Analyst Agent │  │   │  │
│  │  ┌────────────┐  │     │  │  │ (GPT-4o + Tools)   │  │   │  │
│  │  │   Widget   │  │     │  │  └────────────────────┘  │   │  │
│  │  │   Demo     │  │     │  │          ↓               │   │  │
│  │  └────────────┘  │     │  │  ┌────────────────────┐  │   │  │
│  └──────────────────┘     │  │  │ MCP Wrapper Tools  │  │   │  │
│                           │  │  │ - run_database_query│  │   │  │
│                           │  │  │ - list_tables       │  │   │  │
│                           │  │  │ - describe_table    │  │   │  │
│                           │  │  │ - generate_chart    │  │   │  │
│                           │  │  └────────────────────┘  │   │  │
│                           │  └──────────────────────────┘   │  │
│                           │              ↓                   │  │
│                           │  ┌──────────────────────────┐   │  │
│                           │  │  Postgres MCP Pro        │   │  │
│                           │  │  (Subprocess via uv)     │   │  │
│                           │  └──────────────────────────┘   │  │
│                           └──────────────────────────────────┘  │
│                                          ↓                       │
│           ┌──────────────────┐     ┌──────────────────┐         │
│           │  Supabase        │     │  QuickChart.io   │         │
│           │  PostgreSQL DB   │     │  (Chart Render)  │         │
│           │  (133K contacts) │     │                  │         │
│           └──────────────────┘     └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### How Chart Visualization Works

The chart system uses a sophisticated pipeline to generate professional visualizations:

```
┌─────────────────────────────────────────────────────────────────┐
│                   Chart Generation Pipeline                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. USER QUESTION                                                │
│     "Show me a pie chart of contacts by lifecycle stage"        │
│                           ↓                                      │
│  2. AI GENERATES SQL                                             │
│     SELECT lifecycle_stage, COUNT(*) FROM contacts              │
│     GROUP BY lifecycle_stage ORDER BY count DESC                │
│                           ↓                                      │
│  3. MCP EXECUTES QUERY                                           │
│     Returns: Customer: 45,000, Lead: 30,000, etc.               │
│                           ↓                                      │
│  4. AI CALLS generate_chart()                                    │
│     chart_type: "pie"                                           │
│     labels: ["Customer", "Lead", "Subscriber"...]               │
│     values: [45000, 30000, 25000...]                            │
│                           ↓                                      │
│  5. DATA CLEANING (_clean_chart_data)                            │
│     - Removes NULL/Unknown values                                │
│     - Validates data types                                       │
│     - Limits to chart-appropriate count (5 for pie)             │
│                           ↓                                      │
│  6. CHART CONFIG BUILT (build_quickchart_url)                    │
│     - Selects ZING brand colors                                  │
│     - Configures Chart.js options                                │
│     - Handles chart-specific styling                            │
│                           ↓                                      │
│  7. QUICKCHART.IO URL GENERATED                                  │
│     https://quickchart.io/chart?c={config}&w=500&h=340          │
│                           ↓                                      │
│  8. IMAGE WIDGET STREAMED TO CHAT                                │
│     User sees professional chart embedded in conversation       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Supported Chart Types

| Category | Chart Types | Best For |
|----------|-------------|----------|
| **Categorical** | `bar`, `horizontalBar`, `stackedBar`, `groupedBar` | Comparing categories, rankings |
| **Part-of-Whole** | `pie`, `doughnut`, `polarArea` | Percentage breakdowns, proportions |
| **Trends** | `line`, `area`, `smoothLine` | Time series, continuous data |
| **Comparison** | `radar` | Multi-dimensional comparison |
| **Statistical** | `scatter` | Correlation analysis |

### Database Schema

The data chat connects to ZING's Supabase database containing HubSpot contact data:

| Field | Type | Description |
|-------|------|-------------|
| email | string | Contact email address |
| firstname | string | First name |
| lastname | string | Last name |
| lifecycle_stage | string | Customer, Lead, Subscriber, Opportunity, Evangelist, Other |
| company | string | Company name |
| city | string | City |
| state | string | State/Province |
| country | string | Country |
| jobtitle | string | Job title |
| phone | string | Phone number |
| created_at | timestamp | Record creation date |
| updated_at | timestamp | Last update date |

---

## Docker Deployment

### Both Projects Are Fully Dockerized

Each project includes:
- `backend/Dockerfile` - Python 3.11 + FastAPI + uv package manager
- `frontend/Dockerfile` - Node 20 + pnpm → nginx for production
- `docker-compose.yml` - Orchestrates backend + frontend services
- `frontend/nginx.conf` - SPA routing + reverse proxy to backend

### Quick Start (Either Project)

```bash
# 1. Clone and navigate to project
cd zing-customer-support-agent  # or zing-supabase-chat

# 2. Copy environment file
cp backend/.env.example backend/.env
# Edit .env with your API keys

# 3. Build and run
docker compose build
docker compose up

# 4. Access the application
# http://localhost        - Main application
# http://localhost?mode=widget  - Widget demo
```

### Environment Variables

**Customer Support Agent:**
```env
OPENAI_API_KEY=sk-...
SMTP2GO_API_KEY=api-...
SMTP2GO_SENDER=support@zing-work.com
SUPPORT_INBOX=support@zing-work.com
```

**Data Chat:**
```env
OPENAI_API_KEY=sk-...
DATABASE_URI=postgresql://user:pass@host:5432/db?sslmode=require
```

---

## Roadmap Opportunity: ZING Data Chat

### Contract Expansion Proposal

ZING Data Chat represents a significant opportunity for the next contract phase. The current POC demonstrates the core capabilities, and a production-ready version could be delivered quickly.

### What's Already Built (POC)

- Natural language database querying
- 12+ chart types with professional styling
- Automatic data cleaning and normalization
- Embeddable widget interface
- Docker deployment configuration

### What Would Be Added (Production)

| Feature | Estimated Effort | Value |
|---------|------------------|-------|
| User authentication | 1-2 weeks | Secure access for staff |
| Saved queries/dashboards | 1-2 weeks | Reusable analytics |
| Export to PDF/CSV | 1 week | Share insights externally |
| Additional data sources | 2-3 weeks | Beyond HubSpot contacts |
| Custom branding options | 1 week | White-label capability |
| Performance optimization | 1 week | Handle larger datasets |

### Business Value

- **Self-service analytics**: Staff can answer their own data questions
- **Faster decision making**: No need to wait for analyst availability
- **Cost reduction**: Reduces load on technical staff for basic queries
- **Democratized data**: Makes data accessible to non-technical users

### Suggested Positioning

*"The Data Chat POC demonstrates how ZING can unlock the value in your HubSpot data with AI. For the next 6-month contract, we can rapidly build this into a production-ready internal tool that will give your entire team instant access to customer insights."*

---

## Technical Stack Summary

| Component | Customer Support | Data Chat |
|-----------|------------------|-----------|
| **Backend** | Python 3.11 + FastAPI | Python 3.11 + FastAPI |
| **AI Model** | GPT-5.1 (reasoning) | GPT-4o |
| **Frontend** | React 19 + Vite | React 19 + Vite |
| **Chat UI** | OpenAI ChatKit SDK | OpenAI ChatKit SDK |
| **Styling** | Tailwind CSS | Tailwind CSS |
| **Data Access** | Knowledge Base (in-memory) | MCP + PostgreSQL |
| **Visualization** | Generative UI Widgets | QuickChart.io Images |
| **Email** | SMTP2GO | N/A |
| **Integration** | HubSpot (via email trigger) | Supabase (direct DB) |
| **Deployment** | Docker Compose | Docker Compose |

---

## Handoff Readiness

Both applications are ready for ZING's development team to:

1. **Deploy immediately** using Docker Compose
2. **Customize** the knowledge base or data queries
3. **Extend** with additional features
4. **Integrate** into existing ZING infrastructure

All code is well-documented with inline comments explaining key architectural decisions.
