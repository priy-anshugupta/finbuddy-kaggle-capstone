"""
Base Agent class for all AI agents in the system
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


def _patch_langgraph_prebuilt_exports() -> None:
    """Ensure `langgraph.prebuilt` exports symbols LangChain expects.

    Newer LangGraph versions expose these from `langgraph.prebuilt.tool_node` but
    may not re-export them from the namespace package root.
    """

    try:
        import langgraph.prebuilt as prebuilt
        from langgraph.prebuilt import tool_node

        for name in ("InjectedState", "InjectedStore", "ToolRuntime"):
            if not hasattr(prebuilt, name) and hasattr(tool_node, name):
                setattr(prebuilt, name, getattr(tool_node, name))
    except Exception:
        # Best-effort shim only; never block app startup.
        return


_patch_langgraph_prebuilt_exports()

from langchain_openai import ChatOpenAI

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
except Exception:  # pragma: no cover
    try:
        from langchain.agents.agent import AgentExecutor
        from langchain.agents.openai_tools.base import create_openai_tools_agent
    except Exception:  # pragma: no cover
        # LangChain 1.x moved these imports. Since we use Google ADK as primary,
        # gracefully degrade — legacy LangChain agents will be unavailable.
        import warnings
        warnings.warn(
            "LangChain agent helpers unavailable (langchain 1.x detected). "
            "Legacy agents disabled; Google ADK agents will be used instead."
        )
        AgentExecutor = None
        create_openai_tools_agent = None
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the financial assistant system.
    
    All agents use GPT-5.1 as specified in the requirements.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: Optional[List[BaseTool]] = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools or []
        
        # Initialize LLM.
        # NOTE: Token limit parameters vary across OpenAI/SDK/LangChain versions.
        # To avoid hard failures (e.g., unsupported `max_tokens` / `max_completion_tokens`),
        # we do not pass any token-limit parameter here.
        model_name = settings.OPENAI_MODEL

        llm_kwargs: Dict[str, Any] = {
            "model": model_name,
            "temperature": temperature or settings.OPENAI_TEMPERATURE,
            "api_key": settings.OPENAI_API_KEY,
        }

        self.llm = ChatOpenAI(**llm_kwargs)
        
        # Memory for conversation context using ChatMessageHistory
        self.chat_history = ChatMessageHistory()
        
        # Build the agent
        self._build_agent()
    
    def _build_agent(self):
        """Build the LangChain agent with tools."""
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        if self.tools:
            # Create agent with tools
            agent = create_openai_tools_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            
            self.executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=settings.DEBUG,
                handle_parsing_errors=True,
                max_iterations=10
            )
        else:
            # Simple LLM chain without tools
            self.executor = None
    
    async def run(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the agent with the given input.
        
        Args:
            input_text: User input or task description
            context: Additional context for the agent
            
        Returns:
            Agent response with output and metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare input with context
            full_input = input_text
            if context:
                context_str = json.dumps(context, indent=2)
                full_input = f"{input_text}\n\nContext:\n{context_str}"
            
            if self.executor:
                # Run with agent executor, including chat history
                result = await self.executor.ainvoke({
                    "input": full_input,
                    "chat_history": self.chat_history.messages
                })
                output = result.get("output", "")
                # Update chat history
                self.chat_history.add_user_message(full_input)
                self.chat_history.add_ai_message(output)
            else:
                # Run with simple LLM
                messages = [
                    SystemMessage(content=self.system_prompt),
                    *self.chat_history.messages,
                    HumanMessage(content=full_input)
                ]
                response = await self.llm.ainvoke(messages)
                output = response.content
                # Update chat history
                self.chat_history.add_user_message(full_input)
                self.chat_history.add_ai_message(output)
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.info(
                "Agent execution completed",
                agent=self.name,
                duration_ms=duration_ms
            )
            
            return {
                "success": True,
                "output": output,
                "agent_name": self.name,
                "duration_ms": duration_ms,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(
                "Agent execution failed",
                agent=self.name,
                error=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "agent_name": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def stream(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream the agent response.
        
        Yields chunks of the response as they're generated.
        """
        full_input = input_text
        if context:
            context_str = json.dumps(context, indent=2)
            full_input = f"{input_text}\n\nContext:\n{context_str}"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=full_input)
        ]
        
        async for chunk in self.llm.astream(messages):
            yield {
                "type": "content",
                "agent_name": self.name,
                "content": chunk.content
            }
    
    def add_to_memory(self, human_message: str, ai_message: str):
        """Add a conversation exchange to memory."""
        self.memory.chat_memory.add_user_message(human_message)
        self.memory.chat_memory.add_ai_message(ai_message)
    
    def clear_memory(self):
        """Clear the agent's conversation memory."""
        self.memory.clear()
    
    def get_memory_messages(self) -> List[Dict[str, str]]:
        """Get all messages from memory."""
        messages = []
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        return messages
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities."""
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
