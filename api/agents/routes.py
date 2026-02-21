from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from sqlmodel import Session
from api.database import SessionDep
from api.domains.auth.dependencies import current_active_user, verify_integration_api_key
from api.domains.users.model import User

from .schema import AgentRequest, AgentResponse, MessageResponse
from .llm import get_default_llm
from .graph import create_user_agent_graph, create_channel_agent_graph
from .state import AgentState

router = APIRouter(prefix="/agents", tags=["agents"])


def to_message_response(msg: BaseMessage) -> MessageResponse:
    """Convert LangChain message to MessageResponse. Expects HumanMessage or AIMessage only."""
    if isinstance(msg, HumanMessage):
        return MessageResponse(
            type="human",
            content=msg.export_for_response(),
            name=msg.name,
            timestamp=msg.response_metadata.get("timestamp"),
        )
    if isinstance(msg, AIMessage):
        return MessageResponse(
            type="ai",
            content=msg.export_for_response(),
            timestamp=msg.response_metadata.get("timestamp"),
        )
    raise TypeError(f"Expected HumanMessage or AIMessage, got {type(msg).__name__}")


def convert_final_message(chat_message: BaseMessage) -> MessageResponse:
    """Extract final AI reply; validates content and raises 502 if model produced none."""
    if not isinstance(chat_message, AIMessage) and getattr(chat_message, "tool_calls", None):
        raise HTTPException(status_code=502, detail="Model produced no final response.")

    content = (chat_message.content or "").strip()
    if not content:
        raise HTTPException(status_code=502, detail="Model produced no final response.")

    timestamp = datetime.utcnow().isoformat() + "Z"
    return MessageResponse(type="ai", content=content, timestamp=timestamp)


@router.post("/user", response_model=AgentResponse)
def chat_user(
    request: AgentRequest,
    session: SessionDep,
    current_user: User = Depends(current_active_user),
):
    """User agent - authenticated user session."""
    try:
        llm = get_default_llm()
        graph = create_user_agent_graph(llm, session, current_user.username)

        initial_state: AgentState = {"messages": request.messages, "suggestions": None}
        final_state: AgentState = graph.invoke(initial_state, {"recursion_limit": 100})

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


@router.post("/channel", response_model=AgentResponse)
def chat_channel(
    request: AgentRequest,
    session: SessionDep,
    platform: str = Depends(verify_integration_api_key),
):
    """Channel agent - external integrations (e.g. Discord bot) via API key. Requires channel_id and channel_member_ids."""
    if not request.channel_id or request.channel_member_ids is None:
        raise HTTPException(
            status_code=400,
            detail="channel_id and channel_member_ids are required for the channel endpoint",
        )
    try:
        llm = get_default_llm()
        graph = create_channel_agent_graph(
            llm, session, request.channel_id, request.channel_member_ids, platform,
        )

        initial_state: AgentState = {"messages": request.messages, "suggestions": None}
        final_state: AgentState = graph.invoke(initial_state, {"recursion_limit": 100})

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
