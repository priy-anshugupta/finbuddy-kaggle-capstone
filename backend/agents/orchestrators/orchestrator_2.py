"""
Investment Orchestrator (Orchestrator 2)
Coordinates investment analysis and portfolio management
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import ORCHESTRATOR_2_PROMPT
from app.core.logging import get_logger


logger = get_logger(__name__)


class InvestmentOrchestrator(BaseAgent):
    """
    Orchestrator 2: Investment Management
    
    Coordinates:
    - Analysis Agent
    - Stock Agent
    - Investment Agent
    - News Agent (Block 2)
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="investment_orchestrator",
            description="Orchestrates investment analysis and portfolio management",
            system_prompt=ORCHESTRATOR_2_PROMPT,
            **kwargs
        )
        
        self._analysis_agent = None
        self._stock_agent = None
        self._investment_agent = None
        self._news_agent = None
    
    def get_capabilities(self) -> List[str]:
        return [
            "risk_assessment",
            "portfolio_analysis",
            "stock_research",
            "mutual_fund_analysis",
            "investment_recommendations",
            "market_news",
            "sip_planning"
        ]
    
    async def route_request(
        self,
        intent: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route request to appropriate investment agent."""
        results = {}
        
        if intent in ["advisory", "plan", "recommend", "guide"]:
            return await self.run_comprehensive_advisory(user_input, context)

        elif intent in ["risk", "profile", "assessment"]:
            results["analysis"] = await self._run_analysis_agent(user_input, context)
        
        elif intent in ["stock", "equity", "share", "mutual fund"]:
            results["stock"] = await self._run_stock_agent(user_input, context)
        
        elif intent in ["invest", "fd", "ppf", "nps", "bonds", "sip", "fixed income"]:
            results["investment"] = await self._run_investment_agent(user_input, context)
        
        elif intent in ["market", "news", "trends"]:
            results["news"] = await self._run_news_agent(user_input, context)
        
        else:
            # Default to comprehensive advisory for vague investment queries
            return await self.run_comprehensive_advisory(user_input, context)
        
        return self._aggregate_results(results)
    
    async def generate_investment_report(
        self,
        user_id: str,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive investment report."""
        context = {"user_id": user_id}
        
        # Get risk profile
        analysis = await self._run_analysis_agent(
            "Analyze user's risk profile and investment capacity",
            context
        )
        
        # Get portfolio analysis
        portfolio = await self._run_investment_agent(
            "Analyze current portfolio performance",
            context
        )
        
        # Get market context
        market = await self._run_news_agent(
            "Summarize current market conditions",
            context
        )
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "risk_profile": analysis.get("output", ""),
            "portfolio_analysis": portfolio.get("output", ""),
            "market_context": market.get("output", ""),
        }
        
        if include_recommendations:
            recommendations = await self._run_investment_agent(
                "Provide investment recommendations based on profile",
                {**context, "risk_profile": analysis.get("output")}
            )
            report["recommendations"] = recommendations.get("output", "")
        
        return report
    
    async def run_comprehensive_advisory(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the specific investment workflow:
        Analysis (Surplus) -> News (Trends) -> Stock (Growth) + Investment (Safety)
        """
        context = context or {}
        results = {}
        
        # Step 1: Analysis Agent - Determine Investable Surplus & Risk
        logger.info("Step 1: Running Analysis Agent")
        analysis_input = f"Analyze spending behavior from transactions to calculate investable surplus and risk profile. Context: {user_input}"
        analysis_result = await self._run_analysis_agent(analysis_input, context)
        results["analysis"] = analysis_result
        
        # Extract context for next steps
        surplus_context = analysis_result.get("output", "")
        
        # Step 2: News Agent - Get Market Trends
        logger.info("Step 2: Running News Agent")
        news_input = "Find top current market trends, hot sectors, and economic outlook for investment."
        news_result = await self._run_news_agent(news_input, context)
        results["news"] = news_result
        
        market_context = news_result.get("output", "")
        
        # Step 3: Stock Agent - Growth Recommendations (Top 5)
        logger.info("Step 3: Running Stock Agent")
        stock_input = (
            f"Based on this financial profile: {surplus_context}\n"
            f"And these market trends: {market_context}\n"
            f"Recommend exactly TOP 5 Stocks, Mutual Funds, or SIPs for growth."
        )
        stock_result = await self._run_stock_agent(stock_input, context)
        results["stock"] = stock_result
        
        # Step 4: Investment Agent - Safety Recommendations (Top 5)
        logger.info("Step 4: Running Investment Agent")
        invest_input = (
            f"Based on this financial profile: {surplus_context}\n"
            f"Recommend exactly TOP 5 Fixed Income options (FD, RD, PSU) for safety and stability."
        )
        invest_result = await self._run_investment_agent(invest_input, context)
        results["investment"] = invest_result
        
        return self._aggregate_results(results)

    async def research_stock(
        self,
        symbol: str,
        include_news: bool = True
    ) -> Dict[str, Any]:
        """Research a specific stock."""
        context = {"symbol": symbol}
        
        stock_analysis = await self._run_stock_agent(
            f"Provide detailed analysis of {symbol}",
            context
        )
        
        result = {
            "symbol": symbol,
            "analysis": stock_analysis.get("output", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if include_news:
            news = await self._run_news_agent(
                f"Get recent news about {symbol}",
                context
            )
            result["recent_news"] = news.get("output", "")
        
        return result
    
    async def _run_analysis_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._analysis_agent is None:
            from agents.block_2.analysis_agent import AnalysisAgent
            self._analysis_agent = AnalysisAgent()
        return await self._analysis_agent.run(input_text, context)
    
    async def _run_stock_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._stock_agent is None:
            from agents.block_2.stock_agent import StockAgent
            self._stock_agent = StockAgent()
        return await self._stock_agent.run(input_text, context)
    
    async def _run_investment_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._investment_agent is None:
            from agents.block_2.investment_agent import InvestmentAgent
            self._investment_agent = InvestmentAgent()
        return await self._investment_agent.run(input_text, context)
    
    async def _run_news_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._news_agent is None:
            from agents.block_2.news_agent import Block2NewsAgent
            self._news_agent = Block2NewsAgent()
        return await self._news_agent.run(input_text, context)
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from multiple agents."""
        aggregated = {
            "success": all(r.get("success", False) for r in results.values()),
            "agents_used": list(results.keys()),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        outputs = []
        for agent_name, result in results.items():
            if result.get("success") and result.get("output"):
                outputs.append(f"**{agent_name.title()}:**\n{result['output']}")
        
        aggregated["combined_output"] = "\n\n".join(outputs)
        return aggregated
