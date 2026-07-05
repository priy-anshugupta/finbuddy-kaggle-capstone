"""
Google ADK Agent Orchestrator for FinBuddy

This module implements the Google Agent Development Kit (ADK) layer
for FinBuddy's multi-agent financial assistant system.

Designed for the Kaggle 5-Day AI Agents: Intensive Vibe Coding Capstone Project,
this module demonstrates the course concepts:
  - Agent / Multi-agent system (ADK)
  - Agent skills (via ADK sub-agents)
  - Integration with existing LangChain tools via FunctionTool wrappers

All prompts were prototyped and refined in Google AI Studio before
being exported into this ADK implementation.
"""

from typing import Optional
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import ADK to avoid hard failures when dependencies aren't installed yet.
_adk_available = False

try:
    from google.adk.agents import Agent, LlmAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import FunctionTool
    from google.adk.models.lite_llm import LiteLlm
    _adk_available = True
except ImportError as e:
    logger.warning("Google ADK not installed. Run: pip install google-adk google-genai", error=str(e))


class ADKOrchestrator:
    """
    Top-level ADK orchestrator for FinBuddy.

    Architecture:
        Root Agent (LlmAgent) --routes--> Block 1 (Money Management)
                                      |--> Block 2 (Investment)
                                      |--> Block 3 (Financial Products)

    Each block is a SequentialAgent that coordinates its sub-agents.
    The root agent uses semantic intent classification (Gemini) instead of
    brittle keyword matching, demonstrating modern agent routing.
    """

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or "default"
        self.session_service: Optional[InMemorySessionService] = None
        self.runner: Optional[Runner] = None
        self._build_agents()

    def _build_agents(self):
        """Build the ADK agent hierarchy using Gemini via Google AI Studio."""
        if not _adk_available:
            logger.error("ADK is not available. Cannot build agent hierarchy.")
            return

        # --- 1. Gemini Model Configuration ---
        # Primary model: gemini-2.5-flash (fast, cost-effective)
        # Fallback model: gemini-2.5-pro (complex reasoning, tax, portfolio)
        self.model_flash = LiteLlm(
            model=f"gemini/{settings.GEMINI_MODEL}",
            api_key=settings.GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE,
            max_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        )
        self.model_pro = LiteLlm(
            model=f"gemini/{settings.GEMINI_MODEL_PRO}",
            api_key=settings.GEMINI_API_KEY,
            temperature=0.2,
            max_tokens=8192,
        )

        # --- 2. Block 1: Money Management (6 sub-agents) ---
        self.block1_money = self._build_block1()

        # --- 3. Block 2: Investment (4 sub-agents) ---
        self.block2_investment = self._build_block2()

        # --- 4. Block 3: Financial Products (3 sub-agents) ---
        self.block3_products = self._build_block3()

        # --- 5. Root Router Agent ---
        self.root_agent = LlmAgent(
            model=self.model_flash,
            name="finbuddy_root",
            description="Top-level router that classifies user intent and delegates to the appropriate block agent.",
            instruction=(
                "You are FinBuddy, an AI financial assistant for Indian users.\n"
                "Your job is to understand the user's intent and route to the correct specialist block.\n\n"
                "Block 1 – Money Management: handles transactions, budgeting, spending analysis, "
                "cash tracking, expense categorization, and savings recommendations.\n"
                "Block 2 – Investment: handles stock/MF research, portfolio planning, SIP advice, "
                "risk profiling, and market news.\n"
                "Block 3 – Financial Products: handles credit cards, loans, EMI calculators, "
                "tax planning (ITR old vs new regime), and insurance.\n\n"
                "Route the user's request to the correct block. If unclear, ask clarifying questions."
            ),
            sub_agents=[self.block1_money, self.block2_investment, self.block3_products],
        )

        # --- 6. Session Service & Runner ---
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.root_agent,
            app_name="finbuddy",
            session_service=self.session_service,
        )

        logger.info("ADK orchestrator built successfully", user_id=self.user_id)

    def _build_block1(self) -> Agent:
        """Build Block 1: Money Management agents."""
        from google.adk.agents import LlmAgent

        ocr_agent = LlmAgent(
            model=self.model_flash,
            name="block1_ocr",
            description="Extracts transaction data from SMS, receipts, and bank statements.",
            instruction=(
                "You are an OCR Agent. Extract financial transactions from the provided text/image.\n"
                "Return structured JSON with: amount, date, merchant, type (credit/debit), confidence."
            ),
        )

        watchdog_agent = LlmAgent(
            model=self.model_flash,
            name="block1_watchdog",
            description="Validates transactions and detects anomalies or duplicates.",
            instruction=(
                "You are a Watchdog Agent. Analyze the transaction list for:\n"
                "1. Duplicate transactions (same amount, merchant, within 24h)\n"
                "2. Unusual spending (3x above 90-day average for that category)\n"
                "3. Potential fraud (rapid successive transactions, odd hours)\n"
                "Return alerts with severity: info, warning, or critical."
            ),
        )

        categorize_agent = LlmAgent(
            model=self.model_flash,
            name="block1_categorize",
            description="Classifies transactions into 8 spending categories.",
            instruction=(
                "You are a Categorization Agent. Assign each transaction to exactly one category:\n"
                "NEEDS (groceries, utilities, rent, healthcare), ESSENTIALS (insurance, maintenance), "
                "SPENDS (entertainment, dining, shopping), BILLS (subscriptions, EMIs), "
                "SAVINGS (general savings), INVESTMENTS (SIP, stocks, PPF), INCOME (salary, dividends), "
                "TRANSFER (between own accounts).\n"
                "Return category + 1-sentence rationale per transaction."
            ),
        )

        detector_agent = LlmAgent(
            model=self.model_flash,
            name="block1_detector",
            description="Identifies recurring payments and investment opportunities.",
            instruction=(
                "You are a Recurring Payment Detector. Given transaction history, identify:\n"
                "1. Recurring payments (SIPs, insurance, subscriptions, EMIs) with frequency and amount.\n"
                "2. Upcoming expected payments and their dates.\n"
                "3. Suggest pausing or skipping if cash flow is tight."
            ),
        )

        money_growth_agent = LlmAgent(
            model=self.model_flash,
            name="block1_growth",
            description="Analyzes spending patterns and creates budget recommendations.",
            instruction=(
                "You are a Money Growth Agent. Analyze the user's spending and provide:\n"
                "1. Monthly spending vs income ratio\n"
                "2. Category-wise trend analysis\n"
                "3. Potential savings by reducing specific categories\n"
                "4. Personalized budget recommendation\n"
                "Be encouraging but realistic. All amounts in INR (₹)."
            ),
        )

        news_agent = LlmAgent(
            model=self.model_flash,
            name="block1_news",
            description="Curates personal finance news relevant to the user.",
            instruction=(
                "You are a Personal Finance News Agent. Summarize recent news relevant to:\n"
                "- Indian inflation and cost-of-living updates\n"
                "- RBI policy changes affecting savings rates\n"
                "- Deals/discounts in the user's top spending categories\n"
                "Keep it brief and actionable."
            ),
        )

        block1 = LlmAgent(
            model=self.model_flash,
            name="block1_money_management",
            description="Orchestrates all Money Management agents for transaction analysis, budgeting, and cash tracking.",
            instruction=(
                "You are the Money Management Orchestrator.\n"
                "Coordinate the following sub-agents in order when processing transaction workflows:\n"
                "1. OCR Agent → extract raw data\n"
                "2. Watchdog Agent → validate and detect anomalies\n"
                "3. Categorize Agent → classify transactions\n"
                "4. Detector Agent → find recurring payments\n"
                "5. Growth Agent → analyze spending and recommend budgets\n"
                "6. News Agent → add relevant context\n"
                "For simple queries, invoke only the relevant sub-agent(s)."
            ),
            sub_agents=[ocr_agent, watchdog_agent, categorize_agent, detector_agent, money_growth_agent, news_agent],
        )
        return block1

    def _build_block2(self) -> Agent:
        """Build Block 2: Investment agents."""
        from google.adk.agents import LlmAgent

        analysis_agent = LlmAgent(
            model=self.model_pro,
            name="block2_analysis",
            description="Analyzes investable surplus and risk profile for Indian users.",
            instruction=(
                "You are the Investment Analysis Agent for INDIAN users.\n"
                "1. Analyze income vs expenses to calculate monthly investable surplus.\n"
                "2. Assess risk profile (Conservative/Moderate/Aggressive) based on spending stability and age.\n"
                "3. Recommend Equity:Debt split per Indian norms (e.g., 100-age rule).\n"
                "4. Output a Financial Health Report with surplus, risk score, and allocation.\n"
                "All amounts in INR (₹). Emergency fund = 6 months expenses."
            ),
        )

        stock_agent = LlmAgent(
            model=self.model_pro,
            name="block2_stocks",
            description="Recommends Top 5 Indian equity/MF/SIP picks.",
            instruction=(
                "You are the Stock Agent for INDIAN MARKETS.\n"
                "Given the user's investable surplus and risk profile, recommend exactly TOP 5:\n"
                "- NSE/BSE stocks (e.g., RELIANCE.NS, TCS.NS, HDFCBANK.NS)\n"
                "- Indian Mutual Funds (HDFC, ICICI Pru, Axis, SBI, Nippon)\n"
                "- SIPs in Indian AMCs\n"
                "For each: Name, Symbol, Current Price (₹), Expected CAGR, Rationale, Allocation.\n"
                "DO NOT recommend US/international stocks. Use only Indian market data."
            ),
        )

        fixed_income_agent = LlmAgent(
            model=self.model_pro,
            name="block2_fixed_income",
            description="Recommends Top 5 Indian fixed income options.",
            instruction=(
                "You are the Fixed Income Agent for INDIAN MARKETS.\n"
                "Given the user's surplus and risk profile, recommend exactly TOP 5 safe options:\n"
                "- Bank FDs (SBI, HDFC, ICICI, Axis)\n"
                "- Post Office Schemes (NSC, KVP, SCSS)\n"
                "- Government schemes (PPF, SSY, NPS, RBI Bonds, SGBs)\n"
                "For each: Scheme Name, Interest Rate %, Lock-in, Safety Rating, Maturity Value (₹)."
            ),
        )

        market_news_agent = LlmAgent(
            model=self.model_flash,
            name="block2_market_news",
            description="Tracks Indian market trends and sentiment.",
            instruction=(
                "You are the Market News Agent for INDIAN markets.\n"
                "Provide:\n"
                "1. Nifty 50, Sensex, Bank Nifty sentiment (Positive/Negative/Neutral)\n"
                "2. Hot topics (e.g., 'Banking Rally', 'IT Correction', 'Budget Impact')\n"
                "3. RBI policy updates and FII/DII activity\n"
                "Keep it concise and actionable for investment decisions."
            ),
        )

        block2 = LlmAgent(
            model=self.model_pro,
            name="block2_investment",
            description="Orchestrates the strict 4-step investment workflow for Indian users.",
            instruction=(
                "You are the Investment Orchestrator.\n"
                "Follow this STRICT sequence for investment queries:\n"
                "1. Analysis Agent → calculate surplus + risk profile\n"
                "2. Market News Agent → get current trends and sentiment\n"
                "3. Stock Agent → Top 5 Equity/MF/SIP recommendations\n"
                "4. Fixed Income Agent → Top 5 safe instrument recommendations\n"
                "5. Aggregate into a comprehensive investment plan with INR amounts.\n"
                "Do NOT deviate from this sequence."
            ),
            sub_agents=[analysis_agent, stock_agent, fixed_income_agent, market_news_agent],
        )
        return block2

    def _build_block3(self) -> Agent:
        """Build Block 3: Financial Products agents."""
        from google.adk.agents import LlmAgent

        credit_card_agent = LlmAgent(
            model=self.model_flash,
            name="block3_credit_card",
            description="Recommends credit cards based on spending patterns.",
            instruction=(
                "You are the Credit Card Agent for INDIAN users.\n"
                "Analyze spending patterns and recommend the best credit cards.\n"
                "Consider: annual fee vs benefits, reward rates per category, welcome bonuses, "
                "fuel surcharge waivers, lounge access, co-branded cards.\n"
                "Provide a comparison table with clear recommendation."
            ),
        )

        itr_agent = LlmAgent(
            model=self.model_pro,
            name="block3_itr",
            description="Compares old vs new tax regime and optimizes deductions.",
            instruction=(
                "You are the ITR Agent for INDIAN tax planning.\n"
                "1. Calculate tax under OLD regime (deductions: 80C, 80D, 80E, HRA, LTA, standard deduction)\n"
                "2. Calculate tax under NEW regime (lower slabs, fewer deductions)\n"
                "3. Identify additional 80C/80D opportunities\n"
                "4. Recommend the better regime with projected savings\n"
                "Use current FY 2025-26 slabs. All amounts in INR (₹)."
            ),
        )

        loan_agent = LlmAgent(
            model=self.model_flash,
            name="block3_loan",
            description="Calculates EMI, eligibility, and compares loan options.",
            instruction=(
                "You are the Loan Agent for INDIAN users.\n"
                "1. Calculate EMI using standard formula: P × r × (1+r)^n / ((1+r)^n - 1)\n"
                "2. Assess eligibility based on income and existing EMIs\n"
                "3. Compare lenders (SBI, HDFC, ICICI, Bajaj) on rate, fees, tenure\n"
                "4. Advise on prepayment strategies\n"
                "Loan types: Personal, Home, Auto, Education. All amounts in INR (₹)."
            ),
        )

        block3 = LlmAgent(
            model=self.model_flash,
            name="block3_financial_products",
            description="Orchestrates credit card, tax, and loan advisors.",
            instruction=(
                "You are the Financial Products Orchestrator.\n"
                "Route queries to the correct specialist:\n"
                "- Credit cards → Credit Card Agent\n"
                "- Tax, ITR, deductions → ITR Agent\n"
                "- Loans, EMI, eligibility → Loan Agent\n"
                "For complex queries, coordinate multiple agents and present a unified recommendation."
            ),
            sub_agents=[credit_card_agent, itr_agent, loan_agent],
        )
        return block3

    async def run(self, user_message: str, session_id: Optional[str] = None) -> dict:
        """
        Run the ADK agent hierarchy with a user message.

        Args:
            user_message: The user's natural language query.
            session_id: Optional session ID for persistent memory.

        Returns:
            dict with {"output": str, "agent_name": str, "duration_ms": float, ...}
        """
        if not _adk_available or self.runner is None:
            return {
                "success": False,
                "error": "Google ADK is not available. Install dependencies: pip install google-adk google-genai",
                "output": "",
            }

        import asyncio
        from datetime import datetime

        start = datetime.utcnow()
        sid = session_id or f"session_{self.user_id}_{int(start.timestamp())}"

        # Create or retrieve session
        user_session = self.session_service.create_session(
            app_name="finbuddy",
            user_id=self.user_id,
            session_id=sid,
        )

        # Build the ADK content object
        content = {"role": "user", "parts": [{"text": user_message}]}

        # Run the agent (async wrapper for ADK Runner.run)
        output_parts = []
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=sid,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        output_parts.append(part.text)

        full_output = "\n".join(output_parts).strip()
        duration_ms = (datetime.utcnow() - start).total_seconds() * 1000

        logger.info(
            "ADK agent run completed",
            user_id=self.user_id,
            session_id=sid,
            duration_ms=duration_ms,
        )

        return {
            "success": True,
            "output": full_output or "(No response generated)",
            "agent_name": "finbuddy_root",
            "duration_ms": duration_ms,
            "session_id": sid,
        }

    def get_session_history(self, session_id: str) -> list:
        """Retrieve chat history for a session."""
        if not _adk_available or self.session_service is None:
            return []
        try:
            session = self.session_service.get_session(
                app_name="finbuddy",
                user_id=self.user_id,
                session_id=session_id,
            )
            return session.events if session else []
        except Exception as e:
            logger.warning("Failed to get session history", error=str(e))
            return []
