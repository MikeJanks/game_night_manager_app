from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from api.database import SessionDep
from api.domains.auth.dependencies import current_active_user
from api.domains.users.model import User

from .schema import AgentRequest, AgentResponse, MessageResponse
from api.agents.shared.model import get_default_llm
from api.agents.shared.tools import create_agent_tools
from .graph import create_agent_graph
from .state import AgentState

router = APIRouter(prefix="/agent", tags=["agent"])


def to_message_response(msg: BaseMessage) -> MessageResponse:
    """Convert LangChain message to MessageResponse. Human/AI only; skips ToolMessage."""
    content = (msg.content or "").strip()
    if isinstance(msg, HumanMessage):
        return MessageResponse(type="human", content=content, name=getattr(msg, "name", None))
    return MessageResponse(type="ai", content=content)


def convert_final_message(chat_message: BaseMessage) -> MessageResponse:
    """Extract final AI reply; validates content and raises 502 if model produced none."""
    if not isinstance(chat_message, AIMessage) and getattr(chat_message, "tool_calls", None):
        raise HTTPException(status_code=502, detail="Model produced no final response.")

    content = (chat_message.content or "").strip()
    if not content:
        raise HTTPException(status_code=502, detail="Model produced no final response.")

    return MessageResponse(type="ai", content=content)


@router.post("/chat", response_model=AgentResponse)
def chat_with_agent(
    request: AgentRequest,
    session: SessionDep,
    current_user: User = Depends(current_active_user)
):
    try:
        llm = get_default_llm()
        tools = create_agent_tools(session)
        graph = create_agent_graph(llm, tools)

        initial_state: AgentState = {"messages": request.messages, "suggestions": None}
        final_state: AgentState = graph.invoke(initial_state, {"recursion_limit": 100})

        # request + final only; final_state has ToolMessages so we hide from UI
        final_msg = convert_final_message(final_state["messages"][-1])
        request_messages_responses = [to_message_response(m) for m in request.messages]
        all_messages = request_messages_responses + [final_msg]

        suggestions = final_state.get("suggestions")

        return AgentResponse(messages=all_messages, suggestions=suggestions)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
