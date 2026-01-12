"""Reusable helper for JSON-only LLM calls with automatic retries and Pydantic validation."""

import json
import re
from typing import List, Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage

T = TypeVar("T", bound=BaseModel)


def extract_json_from_text(text: str) -> str:
    """Extract JSON from text, handling markdown code blocks and extra text."""
    text = text.strip()
    
    # Try to find JSON in markdown code blocks
    json_block_pattern = r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```"
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # Try to find JSON object or array directly
    json_pattern = r"(\{.*\}|\[.*\])"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # If no pattern matches, return the original text (will fail parsing if invalid)
    return text


def invoke_json_llm(
    llm: BaseChatModel,
    messages: List[BaseMessage],
    schema: Type[T],
    max_retries: int = 3,
    json_instruction: Optional[str] = None
) -> T:
    """
    Invoke LLM with JSON-only output requirement, parse and validate response.
    
    Args:
        llm: BaseChatModel instance (should not have tools bound)
        messages: List of LangChain messages to send to the LLM
        schema: Pydantic BaseModel class to validate against
        max_retries: Maximum number of retry attempts on parse/validation errors
        json_instruction: Optional custom JSON instruction. If None, generates default.
    
    Returns:
        Validated Pydantic model instance
    
    Raises:
        ValueError: If JSON parsing or validation fails after max_retries
    """
    # Generate default JSON instruction if not provided
    if json_instruction is None:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        json_instruction = (
            "You must respond with valid JSON only. No markdown, no code blocks, "
            "no explanatory text, no tool calls. The JSON must match this schema:\n"
            f"{schema_json}"
        )
    
    # Add JSON instruction as a system message
    instruction_message = SystemMessage(content=json_instruction)
    messages_with_instruction = messages + [instruction_message]
    
    last_error = None
    for attempt in range(max_retries):
        try:
            # Invoke LLM with plain invoke (no structured output, no tools)
            response = llm.invoke(messages_with_instruction)
            
            # Extract content from response
            content = response.content if hasattr(response, "content") else str(response)
            if not content:
                raise ValueError("LLM returned empty response")
            
            # Extract JSON from content (handles markdown code blocks, etc.)
            json_str = extract_json_from_text(content)
            
            # Parse JSON
            try:
                parsed_json = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON: {e}. Content: {content[:200]}")
            
            # Validate against Pydantic schema
            try:
                validated = schema.model_validate(parsed_json)
                return validated
            except ValidationError as e:
                raise ValueError(f"Schema validation failed: {e}. Parsed JSON: {parsed_json}")
        
        except ValueError as e:
            last_error = e
            if attempt < max_retries - 1:
                # Retry with the same messages (LLM will generate different response)
                continue
            else:
                # Max retries exhausted
                raise ValueError(
                    f"Failed to get valid JSON response after {max_retries} attempts. "
                    f"Last error: {last_error}"
                ) from last_error
    
    # Should never reach here, but just in case
    raise ValueError(f"Unexpected error: {last_error}")
