"""User context instruction for prompt templates."""

USER_CONTEXT_TEMPLATE = """The `name` field on each human message contains that sender's user UUID. When calling tools, use the appropriate user_id for each parameter: for the person making the request or performing the action, use the `name` from their message (often the most recent human message). When the request involves another participant, use the `name` from that participant's message. Never use message content (e.g. "my name", "whats my name") as the user_id parameter."""
