"""User context instruction for prompt templates."""

USER_CONTEXT_TEMPLATE = """The `name` field on each human message contains that sender's user UUID. When calling tools, use the appropriate user_id for each parameter: for the person making the request or performing the action, use the `name` from their message (often the most recent human message). When the request involves another participant, use the `name` from that participant's message. Never use message content (e.g. "my name", "whats my name") as the user_id parameter."""

ADDRESS_USER_BY_USERNAME = "When addressing this user specifically, use their username exactly as stored: {username}."
ADDRESS_DISCORD_BY_MENTION = "When addressing a specific user, use Discord mention format <@snowflake>. Extract the snowflake from that user's message name field (strip 'discord:' prefix if present). Use when you need clarification from a specific person or want a specific user to respond."
