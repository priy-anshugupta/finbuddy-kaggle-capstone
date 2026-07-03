"""
Money Management Orchestrator (Orchestrator 1)
Coordinates transaction analysis and spending insights
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import ORCHESTRATOR_1_PROMPT
from app.core.logging import get_logger


logger = get_logger(__name__)


class MoneyManagementOrchestrator(BaseAgent):
    """
    Orchestrator 1: Money Management
    
    Coordinates:
    - OCR Agent
    - Watchdog Agent
    - Categorize Agent
    - Investment Detector Agent
    - Money Growth Agent
    - News Agent (Block 1)
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="money_management_orchestrator",
            description="Orchestrates transaction analysis and spending insights",
            system_prompt=ORCHESTRATOR_1_PROMPT,
            **kwargs
        )
        
        # Lazy load sub-agents
        self._ocr_agent = None
        self._watchdog_agent = None
        self._categorize_agent = None
        self._investment_detector_agent = None
        self._money_growth_agent = None
        self._news_agent = None
    
    def get_capabilities(self) -> List[str]:
        return [
            "transaction_extraction",
            "transaction_validation",
            "transaction_categorization",
            "recurring_payment_detection",
            "spending_analysis",
            "budget_recommendations",
            "savings_opportunities",
            "personal_finance_news"
        ]
    
    async def route_request(
        self,
        intent: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route the request to appropriate sub-agent(s).
        
        Args:
            intent: Detected intent from user input
            user_input: Original user message
            context: Additional context
            
        Returns:
            Aggregated response from sub-agents
        """
        results = {}
        
        if intent in ["ocr", "extract_transactions"]:
            results["ocr"] = await self._run_ocr_agent(user_input, context)
        
        elif intent in ["validate", "check_duplicates", "anomaly"]:
            results["watchdog"] = await self._run_watchdog_agent(user_input, context)
        
        elif intent in ["categorize", "classify"]:
            results["categorize"] = await self._run_categorize_agent(user_input, context)
        
        elif intent in ["recurring", "sip", "subscription"]:
            results["investment_detector"] = await self._run_investment_detector_agent(user_input, context)
        
        elif intent in ["analyze", "spending", "budget", "savings"]:
            results["money_growth"] = await self._run_money_growth_agent(user_input, context)
        
        elif intent in ["news", "trends"]:
            results["news"] = await self._run_news_agent(user_input, context)
        
        else:
            # Default: Run analysis
            results["analysis"] = await self._run_money_growth_agent(user_input, context)
        
        return self._aggregate_results(results)
    
    async def process_transaction_workflow(
        self,
        raw_data: Any,
        source: str = "manual"
    ) -> Dict[str, Any]:
        """
        Complete transaction processing workflow.
        
        1. OCR extraction (if needed)
        2. Watchdog validation
        3. Categorization
        4. Recurring detection
        """
        workflow_result = {
            "steps": [],
            "transactions": [],
            "alerts": [],
            "recurring_detected": []
        }
        
        # Step 1: OCR if source is image/SMS
        if source in ["image", "sms", "pdf"]:
            ocr_result = await self._run_ocr_agent(
                str(raw_data),
                {"source": source}
            )
            workflow_result["steps"].append({"ocr": ocr_result})
            extracted = ocr_result.get("output", {})
        else:
            extracted = raw_data
        
        # Step 2: Validation
        watchdog_result = await self._run_watchdog_agent(
            str(extracted),
            {"action": "validate"}
        )
        workflow_result["steps"].append({"watchdog": watchdog_result})
        workflow_result["alerts"] = watchdog_result.get("alerts", [])
        
        # Step 3: Categorization
        categorize_result = await self._run_categorize_agent(
            str(extracted),
            {"action": "categorize"}
        )
        workflow_result["steps"].append({"categorize": categorize_result})
        
        # Step 4: Recurring detection
        detector_result = await self._run_investment_detector_agent(
            str(extracted),
            {"action": "detect_recurring"}
        )
        workflow_result["steps"].append({"detector": detector_result})
        workflow_result["recurring_detected"] = detector_result.get("recurring", [])
        
        return workflow_result
    
    async def get_spending_insights(
        self,
        user_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Get comprehensive spending insights for a user."""
        context = {
            "user_id": user_id,
            "period": period,
            "analysis_type": "comprehensive"
        }
        
        # Run money growth agent for analysis
        growth_result = await self._run_money_growth_agent(
            f"Analyze spending for {period} and provide insights",
            context
        )
        
        # Get relevant news
        news_result = await self._run_news_agent(
            "Get relevant personal finance news",
            context
        )
        
        return {
            "insights": growth_result.get("output", ""),
            "news": news_result.get("output", ""),
            "recommendations": growth_result.get("recommendations", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _run_ocr_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._ocr_agent is None:
            from agents.block_1.ocr_agent import OCRAgent
            self._ocr_agent = OCRAgent()
        return await self._ocr_agent.run(input_text, context)
    
    async def _run_watchdog_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._watchdog_agent is None:
            from agents.block_1.watchdog_agent import WatchdogAgent
            self._watchdog_agent = WatchdogAgent()
        return await self._watchdog_agent.run(input_text, context)
    
    async def _run_categorize_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._categorize_agent is None:
            from agents.block_1.categorize_agent import CategorizeAgent
            self._categorize_agent = CategorizeAgent()
        return await self._categorize_agent.run(input_text, context)
    
    async def _run_investment_detector_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._investment_detector_agent is None:
            from agents.block_1.investment_detector_agent import InvestmentDetectorAgent
            self._investment_detector_agent = InvestmentDetectorAgent()
        return await self._investment_detector_agent.run(input_text, context)
    
    async def _run_money_growth_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._money_growth_agent is None:
            from agents.block_1.money_growth_agent import MoneyGrowthAgent
            self._money_growth_agent = MoneyGrowthAgent()
        return await self._money_growth_agent.run(input_text, context)
    
    async def _run_news_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._news_agent is None:
            from agents.block_1.news_agent import Block1NewsAgent
            self._news_agent = Block1NewsAgent()
        return await self._news_agent.run(input_text, context)
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from multiple agents."""
        aggregated = {
            "success": all(r.get("success", False) for r in results.values()),
            "agents_used": list(results.keys()),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Combine outputs
        outputs = []
        for agent_name, result in results.items():
            if result.get("success") and result.get("output"):
                outputs.append(f"**{agent_name.title()}:**\n{result['output']}")
        
        aggregated["combined_output"] = "\n\n".join(outputs)
        
        return aggregated
