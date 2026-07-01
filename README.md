# FinBuddy — AI Financial Assistant Coach

<div align="center">
  <img src="https://img.shields.io/badge/Google%20ADK-1.0+-green?style=for-the-badge&logo=google" alt="Google ADK">
  <img src="https://img.shields.io/badge/Gemini-2.5+-blue?style=for-the-badge&logo=google" alt="Gemini">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-blue?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js" alt="Next.js">
  <img src="https://img.shields.io/badge/MCP-1.0+-orange?style=for-the-badge" alt="MCP">
</div>

<br>

**FinBuddy** is an intelligent, multi-agent AI financial assistant built for Indian users. It automates transaction tracking, provides personalized investment advice, and proactively manages your financial health — all while keeping your personal data secure. Originally built as a LangChain project, it was fully migrated to **Google ADK + Gemini** to demonstrate the capabilities taught in the **Kaggle 5-Day AI Agents: Intensive Vibe Coding Course with Google**.

---

## 🌟 What Problem It Solves

Managing personal finances in India is fragmented, overwhelming, and error-prone:
- **Cash disappears**: ATM withdrawals are rarely tracked
- **Tax confusion**: Old vs new regime, 80C/80D deductions — most people leave money on the table
- **Investment paralysis**: Too many options (FDs, PPF, SIPs, stocks) with no personalized guidance
- **Reactive tools**: Existing apps only show what already happened; they don't act on your behalf

FinBuddy solves this with a **13-agent, 3-orchestrator system** that not only answers your questions but **works autonomously** in the background to keep your finances on track.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              User Interface                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Dashboard│  │Chat      │  │Investment│  │News      │  │Cash      │   │
│  │ (Next.js)│  │ (ADK)    │  │Advisory  │  │Feed      │  │Widget    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │             │
        ▼             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend (Python 3.11)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Google ADK Orchestrator                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │   │
│  │  │  Block 1    │  │  Block 2    │  │  Block 3                    │ │   │
│  │  │ Money Mgmt  │  │ Investment  │  │  Financial Products         │ │   │
│  │  │ 6 agents    │  │ 4 agents    │  │  3 agents                   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MCP Financial Data Server (7 tools)  │  Security Layer            │   │
│  │  - get_stock_quote                    │  - PII Redaction           │   │
│  │  - calculate_emi                    │  - Rate Limiting           │   │
│  │  - get_inflation_rate               │  - Audit Logging           │   │
│  │  - convert_currency                 │  - Field Encryption        │   │
│  │  - get_mutual_fund_nav              │  - JWT Auth + Refresh    │   │
│  │  - calculate_compound_interest      │                            │   │
│  │  - get_market_indices               │                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Agents CLI (finbuddy-cli)                                          │   │
│  │  chat | test | list-agents | deploy --check | mcp-server            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ PostgreSQL│  │   Redis   │  │ ChromaDB  │  │ Android   │
│ (users,   │  │ (cache,   │  │ (vector   │  │ (SMS      │
│  trans,   │  │  Celery)  │  │  store)   │  │  sync)    │
│  convos)  │  │           │  │           │  │           │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

---

## 🤖 Agent System (Google ADK + Gemini)

All 13 agent prompts were **prototyped and refined in Google AI Studio** before being exported into the Google ADK framework. The system uses **Gemini 2.5 Flash** for fast routing and **Gemini 2.5 Pro** for complex reasoning (tax, portfolio analysis).

### Orchestrator 1: Money Management (6 agents)
| Agent | Purpose | Model |
|-------|---------|-------|
| OCR Agent | Extract transactions from SMS, receipts, PDFs | Gemini 2.5 Flash |
| Watchdog Agent | Detect anomalies, duplicates, fraud | Gemini 2.5 Flash |
| Categorize Agent | 8-category classification (Needs/Spends/Investments...) | Gemini 2.5 Flash |
| Recurring Detector | Identify SIPs, subscriptions, EMIs | Gemini 2.5 Flash |
| Money Growth | Budgeting, savings analysis, projections | Gemini 2.5 Flash |
| News Agent | Personal finance news & inflation updates | Gemini 2.5 Flash |

### Orchestrator 2: Investment (4 agents)
| Agent | Purpose | Model |
|-------|---------|-------|
| Analysis Agent | Risk profile + investable surplus calculation | Gemini 2.5 Pro |
| Stock Agent | Top 5 NSE/BSE equity/MF/SIP picks | Gemini 2.5 Pro |
| Fixed Income Agent | Top 5 FD/PPF/NPS/RBI Bond picks | Gemini 2.5 Pro |
| Market News Agent | Nifty/Sensex sentiment & sector trends | Gemini 2.5 Flash |

### Orchestrator 3: Financial Products (3 agents)
| Agent | Purpose | Model |
|-------|---------|-------|
| Credit Card Agent | Match cards to spending patterns | Gemini 2.5 Flash |
| ITR Agent | Old vs new regime + 80C/80D optimization | Gemini 2.5 Pro |
| Loan Agent | EMI, eligibility, lender comparison | Gemini 2.5 Flash |

---

## 🛡️ Security Features

- **PII Redaction**: Auto-masks Aadhaar, PAN, bank accounts, UPI IDs, phone numbers in all logs and LLM prompts
- **Rate Limiting**: Per-user sliding-window request throttling (Redis-backed)
- **Audit Logging**: Immutable append-only log with SHA-256 checksums for every financial action
- **Field Encryption**: Fernet (AES-128-CBC + HMAC) encryption for sensitive database columns
- **JWT Authentication**: Access + refresh tokens with bcrypt password hashing
- **Input Sanitization**: Regex validators for all financial inputs

---

## 📡 MCP Financial Data Server

A standalone **Model Context Protocol (MCP)** server exposes 7 financial tools for external clients and ADK agents:

| Tool | Input | Output |
|------|-------|--------|
| `get_stock_quote` | `RELIANCE.NS` | Price, change, volume, 52W high/low |
| `get_market_indices` | — | Nifty 50, Sensex, Bank Nifty live data |
| `calculate_emi` | ₹50L, 8.5%, 240mo | EMI ₹43,391, total interest ₹54.1L |
| `calculate_compound_interest` | ₹1L, 7%, 5yr | Maturity ₹1,40,255 |
| `get_mutual_fund_nav` | `120437` | NAV, date, fund name |
| `get_inflation_rate` | — | Indian CPI ~4.83% |
| `convert_currency` | 1000 USD → INR | ₹83,500 |

---

## 🎮 Agents CLI (finbuddy-cli)

```bash
# Interactive chat with ADK backend
finbuddy-cli chat --agent=adk

# Run agent evaluation tests
finbuddy-cli test

# List all 13 registered agents
finbuddy-cli list-agents

# Pre-deployment health check
finbuddy-cli deploy --check

# Start MCP server
finbuddy-cli mcp-server --port 8001
```

---

## 🚀 Deployability

### Docker Compose (Recommended for Local / Self-Hosted)
```bash
# One-command full stack
docker-compose up -d
# → PostgreSQL + Redis + Backend + Frontend + Celery + MCP Server
```

### Cloud Deployment
- **Google Cloud Run**: Serverless, scales to zero, auto-HTTPS
- **Railway / Render**: One-click GitHub deploy, managed PostgreSQL & Redis
- **CI/CD**: GitHub Actions runs linting, tests, and Docker builds on every push

See [deploy/README.md](deploy/README.md) for full instructions.

---

## 🧪 Antigravity (Autonomous Background Execution)

FinBuddy isn't just a chatbot — it's an **agent that works while you sleep**:

- **Celery Beat @ 11 PM IST**: Cash Watchdog scans all ATM withdrawals, compares against logged expenses, and proactively nudges the user if cash is untracked
- **Android SMS Connector**: Background service intercepts bank SMS, auto-syncs transactions without opening the app
- **Recurring Detection**: Auto-identifies SIPs, subscriptions, insurance premiums from transaction patterns
- **Investment Watchlist Alerts**: Monitors price thresholds and notifies users autonomously

---

## 📦 Tech Stack

### Backend
- **Google ADK** — Agent orchestration (LlmAgent, SequentialAgent, Runner, SessionService)
- **Google Gemini 2.5** — Flash for routing, Pro for reasoning
- **Google AI Studio** — Prompt prototyping and refinement
- **FastAPI** — Async REST API + WebSocket streaming
- **MCP** — Model Context Protocol server for financial tools
- **PostgreSQL + asyncpg** — Primary database
- **Redis** — Caching, Celery broker, rate limiting
- **Celery + Flower** — Background task scheduling
- **cryptography** — Field-level encryption (Fernet)
- **Click + Rich** — Agents CLI

### Frontend
- **Next.js 14** — App Router, React Server Components
- **TypeScript + Tailwind CSS** — Type-safe, responsive UI
- **Redux Toolkit** — State management
- **Framer Motion** — Animations
- **Recharts** — Financial data visualization

---

## 📋 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Google AI Studio API key (for Gemini)

### 1. Clone and Configure
```bash
git clone https://github.com/yourusername/finbuddy.git
cd finbuddy

# Copy and edit environment
cp .env.example .env
# Set GEMINI_API_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY
```

### 2. Start with Docker
```bash
docker-compose up -d
```

### 3. Or Start Manually
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install
npm run dev
```

### 4. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MCP Server: http://localhost:8001

---

## 📝 Project Structure

```
finbuddy/
├── backend/
│   ├── app/                    # FastAPI core (API, models, services, config)
│   ├── agents/                 # Legacy LangChain agents (backward compatible)
│   ├── google_adk/             # NEW: Google ADK orchestrator + tools + service
│   ├── mcp_server/             # NEW: MCP Financial Data Server (7 tools)
│   ├── cli/                     # NEW: finbuddy-cli (chat, test, deploy, mcp)
│   ├── skills/                  # NEW: Reusable agent skills (market, budget, tax, risk)
│   ├── requirements.txt         # Updated: google-adk, google-genai, mcp, click, cryptography
│   └── Dockerfile             # Production-ready multi-stage build
├── frontend/                    # Next.js 14 + TypeScript + Tailwind
├── android-connector/           # Kotlin SMS sync app
├── docker-compose.yml           # Full stack orchestration
├── deploy/                      # Cloud deployment guides
├── .github/workflows/ci.yml     # CI/CD pipeline
└── README.md                    # This file
```

---

## 🔐 Security

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- PII redaction on all logs and LLM prompts
- Rate limiting per user (Redis sliding window)
- Immutable audit logs with SHA-256 checksums
- Field-level encryption (Fernet) for PAN, Aadhaar, bank accounts
- CORS configured for allowed origins only

---

## 🧪 Testing

```bash
# Backend tests (includes ADK, MCP, CLI, Skills)
cd backend
pytest --cov=app --cov=google_adk --cov=mcp_server --cov=cli --cov=skills

# Frontend tests
cd frontend
npm test

# CLI health check
finbuddy-cli deploy --check
```

---

## 🏆 Kaggle Capstone Submission

This project is submitted to the **Kaggle 5-Day AI Agents: Intensive Vibe Coding Capstone Project** in the **Concierge Agents** track.

### Course Concepts Demonstrated
| Concept | Implementation |
|---------|----------------|
| **Agent / Multi-agent System (ADK)** | `google_adk/root_agent.py` — Root + 3 Block orchestrators + 13 LlmAgents |
| **MCP Server** | `mcp_server/server.py` — 7 financial tools via FastMCP |
| **Antigravity** | Celery Beat nightly cash checks, background SMS sync, proactive alerts |
| **Security Features** | PII redaction, rate limiting, audit logging, field encryption, JWT |
| **Deployability** | Docker Compose, Cloud Run, Railway, CI/CD pipeline |
| **Agent Skills (CLI)** | `cli/main.py` + `skills/financial_skills.py` — chat, test, deploy, skills |

### Submission Links
- **Kaggle Writeup**: [Kaggle Writeup](KAGGLE_WRITEUP.md)
- **YouTube Video**: [Video Script](VIDEO_SCRIPT.md) (record and upload to YouTube)
- **Project Repository**: [GitHub](https://github.com/yourusername/finbuddy)
- **Live Demo**: [Deploy URL](https://your-deploy-url.com)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>Built with ❤️ for financial freedom — powered by Google ADK + Gemini</strong>
</div>
