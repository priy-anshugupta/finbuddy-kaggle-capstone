"""
News Agent (Block 2) for market news with web search
"""

from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import NEWS_AGENT_BLOCK2_PROMPT
from agents.tools.web_search_tool import get_news_tools, search_financial_news


class Block2NewsAgent(BaseAgent):
    """Agent for market and investment news with real-time web search."""
    
    def __init__(self, **kwargs):
        tools = kwargs.pop("tools", None) or get_news_tools()
        super().__init__(
            name="block2_news_agent",
            description="Provides real-time market news and investment updates using web search",
            system_prompt=NEWS_AGENT_BLOCK2_PROMPT,
            tools=tools,
            **kwargs
        )
    
    async def fetch_news(self, query: str = "Indian stock market", max_results: int = 10) -> Dict[str, Any]:
        """
        Fetch financial news from web sources.
        
        Args:
            query: Search query for news
            max_results: Maximum number of articles
            
        Returns:
            Dictionary with news articles and metadata
        """
        try:
            # search_financial_news is a LangChain @tool (StructuredTool). Use ainvoke with a dict.
            if hasattr(search_financial_news, "ainvoke"):
                return await search_financial_news.ainvoke({"query": query, "max_results": max_results})

            # Fallback: if it's a plain async function (shouldn't happen), call it normally.
            return await search_financial_news(query=query, max_results=max_results)
        except Exception as e:
            print(f"News fetch error: {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[str]:
        return [
            "market_news",
            "sector_analysis",
            "economic_indicators",
            "earnings_calendar",
            "web_search"
        ]
