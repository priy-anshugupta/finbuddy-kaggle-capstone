# FinBuddy MCP Financial Data Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that exposes real-time financial data tools for Indian markets. Designed for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Capstone Project.

## Tools Exposed

| Tool | Description | Example |
|------|-------------|---------|
| `get_stock_quote` | Real-time NSE/BSE stock quote | `RELIANCE.NS` → ₹2,450.30 |
| `get_mutual_fund_nav` | Latest mutual fund NAV | `120437` → ₹845.32 |
| `calculate_emi` | EMI calculator for Indian loans | ₹50L, 8.5%, 240mo → ₹43,391 EMI |
| `get_inflation_rate` | Indian CPI inflation | ~4.83% (RBI approximate) |
| `convert_currency` | Currency conversion | USD → INR @ 83.5 |
| `calculate_compound_interest` | FD/PPF/RD maturity projection | ₹1L, 7%, 5yr → ₹1,40,255 |
| `get_market_indices` | Nifty 50, Sensex, Bank Nifty | Live index data |

## Usage

### Run with stdio (for MCP clients like Claude Desktop, Cursor)
```bash
cd backend
python -m mcp_server.server
```

### Run with SSE (for web clients)
```bash
pip install mcp[server]
python -m mcp_server.server --transport sse --port 8001
```

### Connect from FinBuddy ADK Agents
```python
from mcp_server.server import mcp
from google.adk.tools import FunctionTool

tools = [FunctionTool(func=get_stock_quote), ...]
```

## Architecture

```
┌─────────────────┐     MCP (stdio/SSE)     ┌────────────────────────┐
│   MCP Client    │ ◄──────────────────────► │  FinBuddy MCP Server   │
│ (ADK Agent /    │   JSON-RPC over stdio   │  FastMCP               │
│  Claude Desktop)│                         │  ┌─────────────────┐   │
│                 │                         │  │ get_stock_quote │   │
│                 │                         │  │ calculate_emi   │   │
│                 │                         │  │ get_inflation   │   │
│                 │                         │  │ ... 7 tools     │   │
│                 │                         │  └─────────────────┘   │
│                 │                         │         │              │
│                 │                         │    yfinance /        │
│                 │                         │    pandas /          │
│                 │                         │    approximate       │
└─────────────────┘                         └────────────────────────┘
```

## Development

```bash
# Test a tool locally
python -c "from mcp_server.server import get_stock_quote; print(get_stock_quote('RELIANCE.NS'))"
```
