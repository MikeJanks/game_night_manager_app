from typing import List
from fastapi import APIRouter, HTTPException, Depends
from langchain_core.messages import BaseMessage, AIMessage
from database import SessionDep
from domains.auth.dependencies import current_active_user
from domains.users.model import User

from .schema import AgentRequest, AgentResponse, Message
from .model import get_default_llm
from .tools import create_agent_tools
from .graph import create_agent_graph
from .state import AgentState

router = APIRouter(prefix="/agent", tags=["agent"])


def convert_from_langchain_message(chat_message: BaseMessage) -> Message:
    if not isinstance(chat_message, AIMessage) and getattr(chat_message, "tool_calls", None):
        raise HTTPException(status_code=502, detail="Model produced no final response.")

    content = (chat_message.content or "").strip()
    if not content:
        raise HTTPException(status_code=502, detail="Model produced no final response.")
    
    return ["assistant", content]


@router.post("/chat", response_model=AgentResponse)
def chat_with_agent(
    request: AgentRequest, 
    session: SessionDep,
    current_user: User = Depends(current_active_user)
):
    try:
        llm = get_default_llm()
        tools = create_agent_tools(session, current_user.id)
        graph = create_agent_graph(llm, tools, current_user)

        initial_state: AgentState = {"messages": request.messages, "suggestions": None}
        final_state: AgentState = graph.invoke(initial_state, {"recursion_limit": 100})

        final_msg: Message = convert_from_langchain_message(final_state["messages"][-1])
        
        # Extract suggestions from final state
        suggestions = final_state.get("suggestions")
        
        return AgentResponse(
            messages=request.messages + [final_msg],
            suggestions=suggestions
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
