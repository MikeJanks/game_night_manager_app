"""LangGraph state graph definition for the chat agent."""

from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool

from .state import AgentState
from .prompts.templates import SYSTEM_PROMPT_TEMPLATE, SUGGESTIONS_PROMPT_TEMPLATE
from .schema import Suggestions


def create_agent_graph(llm: BaseChatModel, tools: list[BaseTool]) -> StateGraph:
    system_messages = SYSTEM_PROMPT_TEMPLATE.format_messages()
    tool_node = ToolNode(tools)

    def agent_node(state: AgentState) -> dict:
        model_msgs = system_messages + state["messages"]
        message = llm.bind_tools(tools).invoke(model_msgs)
        return {"messages": [message]}

    def suggestions_node(state: AgentState) -> dict:
        suggestions_prompt = SUGGESTIONS_PROMPT_TEMPLATE.format_messages()
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
