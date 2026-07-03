"""
Financial Products Orchestrator (Orchestrator 3)
Coordinates credit cards, loans, and tax planning
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import ORCHESTRATOR_3_PROMPT
from app.core.logging import get_logger


logger = get_logger(__name__)


class FinancialProductsOrchestrator(BaseAgent):
    """
    Orchestrator 3: Financial Products
    
    Coordinates:
    - Credit Card Agent
    - ITR Agent
    - Loan Agent
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="financial_products_orchestrator",
            description="Orchestrates credit cards, loans, and tax planning",
            system_prompt=ORCHESTRATOR_3_PROMPT,
            **kwargs
        )
        
        self._credit_card_agent = None
        self._itr_agent = None
        self._loan_agent = None
    
    def get_capabilities(self) -> List[str]:
        return [
            "credit_card_recommendations",
            "credit_card_comparison",
            "tax_calculation",
            "tax_optimization",
            "loan_eligibility",
            "loan_comparison",
            "emi_calculation"
        ]
    
    async def route_request(
        self,
        intent: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route request to appropriate financial product agent."""
        results = {}
        
        if intent in ["credit_card", "card", "rewards"]:
            results["credit_card"] = await self._run_credit_card_agent(user_input, context)
        
        elif intent in ["tax", "itr", "income_tax", "deduction"]:
            results["itr"] = await self._run_itr_agent(user_input, context)
        
        elif intent in ["loan", "emi", "borrow", "mortgage"]:
            results["loan"] = await self._run_loan_agent(user_input, context)
        
        else:
            # Provide overview
            results["overview"] = await self.run(user_input, context)
        
        return self._aggregate_results(results)
    
    async def calculate_tax(
        self,
        income_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate income tax with old vs new regime comparison."""
        context = {"income_details": income_details}
        
        result = await self._run_itr_agent(
            "Calculate income tax and compare old vs new regime",
            context
        )
        
        return {
            "calculation": result.get("output", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def recommend_credit_cards(
        self,
        spending_patterns: Dict[str, float]
    ) -> Dict[str, Any]:
        """Recommend credit cards based on spending."""
        context = {"spending_patterns": spending_patterns}
        
        result = await self._run_credit_card_agent(
            "Recommend best credit cards based on spending patterns",
            context
        )
        
        return {
            "recommendations": result.get("output", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def check_loan_eligibility(
        self,
        loan_type: str,
        income: float,
        existing_obligations: float = 0
    ) -> Dict[str, Any]:
        """Check loan eligibility and get options."""
        context = {
            "loan_type": loan_type,
            "income": income,
            "existing_obligations": existing_obligations
        }
        
        result = await self._run_loan_agent(
            f"Check eligibility for {loan_type} loan",
            context
        )
        
        return {
            "eligibility": result.get("output", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _run_credit_card_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._credit_card_agent is None:
            from agents.block_3.credit_card_agent import CreditCardAgent
            self._credit_card_agent = CreditCardAgent()
        return await self._credit_card_agent.run(input_text, context)
    
    async def _run_itr_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._itr_agent is None:
            from agents.block_3.itr_agent import ITRAgent
            self._itr_agent = ITRAgent()
        return await self._itr_agent.run(input_text, context)
    
    async def _run_loan_agent(self, input_text: str, context: Optional[Dict] = None) -> Dict:
        if self._loan_agent is None:
            from agents.block_3.loan_agent import LoanAgent
            self._loan_agent = LoanAgent()
        return await self._loan_agent.run(input_text, context)
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from agents."""
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
