"""Prompt template definitions that combine prompts with user context."""

from langchain_core.prompts import ChatPromptTemplate

from api.agents.shared.prompts.system import SYSTEM_PROMPT
from api.agents.shared.prompts.user_context import USER_CONTEXT_TEMPLATE
from .suggestions import SUGGESTIONS_PROMPT

SYSTEM_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", USER_CONTEXT_TEMPLATE)
])

SUGGESTIONS_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SUGGESTIONS_PROMPT)
])
