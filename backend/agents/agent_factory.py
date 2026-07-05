"""
Agent Factory for creating and managing agent instances
"""

from typing import Dict, Optional, Type
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import AGENT_PROMPTS


class AgentFactory:
    """
    Factory for creating and managing agent instances.
    
    Provides centralized agent creation with proper configuration.
    """
    
    _instances: Dict[str, BaseAgent] = {}
    _agent_registry: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register_agent(cls, name: str, agent_class: Type[BaseAgent]):
        """Register an agent class."""
        cls._agent_registry[name] = agent_class
    
    @classmethod
    def create_agent(
        cls,
        agent_type: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> BaseAgent:
        """
        Create or retrieve an agent instance.
        
        Args:
            agent_type: Type of agent to create
            user_id: User ID for user-specific instances
            **kwargs: Additional arguments for agent creation
            
        Returns:
            Agent instance
        """
        # Create unique key for caching
        cache_key = f"{agent_type}_{user_id}" if user_id else agent_type
        
        if cache_key not in cls._instances:
            agent_class = cls._agent_registry.get(agent_type)
            if not agent_class:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            # Get system prompt
            system_prompt = AGENT_PROMPTS.get(agent_type, "")
            
            cls._instances[cache_key] = agent_class(
                system_prompt=system_prompt,
                **kwargs
            )
        
        return cls._instances[cache_key]
    
    @classmethod
    def get_agent(cls, agent_type: str, user_id: Optional[str] = None) -> Optional[BaseAgent]:
        """Get an existing agent instance."""
        cache_key = f"{agent_type}_{user_id}" if user_id else agent_type
        return cls._instances.get(cache_key)
    
    @classmethod
    def clear_agent(cls, agent_type: str, user_id: Optional[str] = None):
        """Clear an agent instance from cache."""
        cache_key = f"{agent_type}_{user_id}" if user_id else agent_type
        if cache_key in cls._instances:
            del cls._instances[cache_key]
    
    @classmethod
    def clear_all(cls):
        """Clear all agent instances."""
        cls._instances.clear()
    
    @classmethod
    def list_registered_agents(cls) -> list:
        """List all registered agent types."""
        return list(cls._agent_registry.keys())


# Import and register all agents
def register_all_agents():
    """Register all agent classes with the factory."""
    from agents.block_1.ocr_agent import OCRAgent
    from agents.block_1.watchdog_agent import WatchdogAgent
    from agents.block_1.categorize_agent import CategorizeAgent
    from agents.block_1.investment_detector_agent import InvestmentDetectorAgent
    from agents.block_1.money_growth_agent import MoneyGrowthAgent
    from agents.block_1.news_agent import Block1NewsAgent
    
    from agents.block_2.analysis_agent import AnalysisAgent
    from agents.block_2.stock_agent import StockAgent
    from agents.block_2.investment_agent import InvestmentAgent
    from agents.block_2.news_agent import Block2NewsAgent
    
    from agents.block_3.credit_card_agent import CreditCardAgent
    from agents.block_3.itr_agent import ITRAgent
    from agents.block_3.loan_agent import LoanAgent
    
    # Block 1 - Money Management
    AgentFactory.register_agent("ocr_agent", OCRAgent)
    AgentFactory.register_agent("watchdog_agent", WatchdogAgent)
    AgentFactory.register_agent("categorize_agent", CategorizeAgent)
    AgentFactory.register_agent("investment_detector_agent", InvestmentDetectorAgent)
    AgentFactory.register_agent("money_growth_agent", MoneyGrowthAgent)
    AgentFactory.register_agent("block1_news_agent", Block1NewsAgent)
    
    # Block 2 - Investment
    AgentFactory.register_agent("analysis_agent", AnalysisAgent)
    AgentFactory.register_agent("stock_agent", StockAgent)
    AgentFactory.register_agent("investment_agent", InvestmentAgent)
    AgentFactory.register_agent("block2_news_agent", Block2NewsAgent)
    
    # Block 3 - Financial Products
    AgentFactory.register_agent("credit_card_agent", CreditCardAgent)
    AgentFactory.register_agent("itr_agent", ITRAgent)
    AgentFactory.register_agent("loan_agent", LoanAgent)
