"""LangGraph state graph definition for the Groq agent."""

from pprint import pprint
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from .state import AgentState
from .prompts.templates import SYSTEM_PROMPT_TEMPLATE, SUGGESTIONS_PROMPT_TEMPLATE
from .schema import Suggestions
from backend.domains.users.model import User

def create_agent_graph(llm: BaseChatModel, tools: list[BaseTool], current_user: User) -> StateGraph:
    # Validate required user fields exist
    if not all([current_user.username, current_user.email, current_user.id]):
        raise ValueError("User missing required fields for agent context")
    
    # Format prompt templates with user context
    system_messages = SYSTEM_PROMPT_TEMPLATE.format_messages(**{
        "username": current_user.username,
        "email": current_user.email,
        "user_id": str(current_user.id)
    })
    
    llm_with_tools = llm.bind_tools(tools)
    suggestions_llm = llm.with_config(
        configurable={"model_kwargs": {"tool_choice": "None"}}
    ).with_structured_output(Suggestions)
    tool_node = ToolNode(tools)

    def agent_node(state: AgentState) -> dict:
        model_msgs = system_messages + state["messages"]
        message = llm_with_tools.invoke(model_msgs)
        return {"messages": [message]}

    def suggestions_node(state: AgentState) -> dict:
        suggestions_prompt = SUGGESTIONS_PROMPT_TEMPLATE.format_messages()
        model_msgs = suggestions_prompt + state["messages"]
        result = suggestions_llm.invoke(model_msgs)
        
        suggestions_list = result.suggestions if result.suggestions else []
        suggestions_list = suggestions_list[:5]
        
        return {"suggestions": suggestions_list}

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
