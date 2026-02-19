"""LangGraph state graph definition for the chat agent."""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage

from .state import AgentState
from .prompts.templates import SYSTEM_PROMPT_TEMPLATE, SUGGESTIONS_PROMPT_TEMPLATE
from .schema import Suggestions
from .tools import create_user_agent_tools, create_channel_agent_tools
from sqlmodel import Session


def _build_agent_graph(
    llm: BaseChatModel,
    tools: list[BaseTool],
    system_prompt: list[BaseMessage],
    suggestions_prompt: list[BaseMessage],
) -> StateGraph:
    """Build agent graph with given tools and prompts.
    
    Args:
        llm: Language model instance.
        tools: List of tools available to the agent.
        system_prompt: Formatted system prompt (instructions) prepended to conversation history.
        suggestions_prompt: Formatted suggestions prompt for generating followups.
    
    Returns:
        Compiled StateGraph.
    """
    tool_node = ToolNode(tools)

    def agent_node(state: AgentState) -> dict:
        model_msgs = system_prompt + state["messages"]
        message = llm.bind_tools(tools).invoke(model_msgs)
        return {"messages": [message]}

    def suggestions_node(state: AgentState) -> dict:
        model_msgs = suggestions_prompt + state["messages"]
        try:
            structured_llm = llm.with_structured_output(Suggestions, method="json_schema")
            result = structured_llm.invoke(model_msgs)
            suggestions_list = result.suggestions if result.suggestions else []
        except Exception:
            suggestions_list = []
        return {"suggestions": suggestions_list[:5]}

    def route(state: AgentState) -> Literal["tools", "done"]:
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else "done"

    graph = StateGraph(AgentState)
    graph.add_node("plan", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("suggestions", suggestions_node)

    graph.set_entry_point("plan")
    graph.add_conditional_edges("plan", route, {"tools": "tools", "done": "suggestions"})
    graph.add_edge("tools", "plan")
    graph.add_edge("suggestions", END)

    return graph.compile()


def create_user_agent_graph(
    llm: BaseChatModel,
    session: Session,
) -> StateGraph:
    """Create agent graph for user (session) path. Uses user-scoped event tools."""
    tools = create_user_agent_tools(session)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format_messages()
    suggestions_prompt = SUGGESTIONS_PROMPT_TEMPLATE.format_messages()
    return _build_agent_graph(llm, tools, system_prompt, suggestions_prompt)


def create_channel_agent_graph(
    llm: BaseChatModel,
    session: Session,
    channel_id: str,
    channel_member_ids: list[str],
    platform: str,
) -> StateGraph:
    """Create agent graph for channel (integration) path. Uses channel-scoped event tools."""
    tools = create_channel_agent_tools(session, channel_id, channel_member_ids, platform)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format_messages()
    suggestions_prompt = SUGGESTIONS_PROMPT_TEMPLATE.format_messages()
    return _build_agent_graph(llm, tools, system_prompt, suggestions_prompt)
