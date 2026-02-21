# Discord Bot Plan

## Overview

A stateless Discord bot that monitors multiple channels, fetches message history from the Discord API on each message, and calls the `/chat` API over HTTP. The assistant is **vibe-reactive**: it reads the room, picks up on when people are talking about wanting to play a game or suggesting a game night, and chimes in when it feels natural—e.g. "Want to lock in a time?" It's ready to help set up events when the moment is right, not pushy or annoying.

---

## Architecture

```
┌─────────────────┐     on_message      ┌──────────────────────┐
│  Discord API    │ ─────────────────► │  Channel Processor   │
│  (multiple      │                    │  (per-channel state) │
│   channels)     │ ◄───────────────── │                      │
└─────────────────┘   send response    └──────────┬───────────┘
                                                 │
                            ┌────────────────────┼────────────────────┐
                            │                    │                    │
                            ▼                    ▼                    ▼
                     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
                     │ Discord API  │     │ Build msg    │     │ HTTP POST    │
                     │ history(N)   │     │ history      │     │ /agents/channel  │
                     └──────────────┘     └──────────────┘     └──────────────┘
```

- **Separate process**: Bot runs independently, not on the FastAPI server.
- **HTTP client**: Calls `POST {API_BASE_URL}/api/agents/channel`.
- **Stateless, no DB**: No database. Every run fetches last N messages fresh from Discord API.

---

## Constraints

| Requirement | Approach |
|-------------|----------|
| HTTP, separate process | `httpx.post()` to API base URL |
| Stateless, no DB | No DB; every run fetches last N from Discord API |
| Per-message Discord fetch | `channel.history(limit=N)` on each processing run |
| Auth | Internal route with API key (e.g. `X-API-Key` header) |

---

## In-Memory Channel State

Runtime-only state (no persistence, lost on restart):

```python
channel_states: dict[int, ChannelState] = {}

class ChannelState:
    processing: bool = False  # True while /chat is running
    pending: bool = False    # Message arrived during processing
```

### Flow

1. **Message arrives** → Create `ChannelState` if missing.
2. **If `processing`** → Set `pending = True`, return.
3. **If not `processing`** → Set `processing = True`, run processing cycle.
4. **Processing cycle**:
   - Fetch last N messages from Discord API.
   - Build `AgentRequest` from messages.
   - HTTP POST to `/api/agents/channel`.
   - Send response to Discord.
5. **After cycle** → Set `processing = False`.
6. **If `pending`** → Set `pending = False`, go to step 3 (another cycle).
7. **Else** → Delete `channel_states[channel_id]` (cleanup when idle).

No need to track message IDs. A boolean is enough: "something new arrived, run again." The "last N" fetch includes all new messages.

---

## Integration Request Body (Required for `POST /api/agents/channel`)

The request body **must** include:

| Field | Required | Description |
|-------|----------|-------------|
| `channel_id` | **Yes** | Discord channel id, e.g. `str(channel.id)`. |
| `channel_member_ids` | **Yes** | List of Discord user IDs (snowflakes as strings) for everyone in that channel. The bot must fetch this via the Discord API (e.g. guild/channel member list for the channel) and send it on every request. The backend uses it only for validation (e.g. invite allowed only if invitee is in this list); it is **not** stored. |
| `messages` | Yes | Conversation history (unchanged). |

If `channel_id` or `channel_member_ids` is missing, the backend returns **400**.

---

## Message Flow (Per Run)

1. **Discord API**: `channel.history(limit=N)` — always fresh, no caching.
2. **Build request body**:
   - **`channel_id`**: Set to the Discord channel id, e.g. `str(channel.id)`.
   - **`channel_member_ids`**: List of Discord user IDs (snowflakes as strings) for everyone in that channel. Fetch via Discord API (e.g. guild/channel member list for the channel).
   - **`messages`**: Convert to `AgentRequest` format:
     - Human: `{type: "human", content: "...", name: "<discord_identifier>"}` — the `name` field **must** be the Discord identifier (e.g. `discord:{snowflake}` or bare snowflake). Display name is not required; Discord user id alone is sufficient.
     - AI: `{type: "ai", content: "..."}` (prior bot replies)
3. **HTTP**: `POST {API_BASE_URL}/api/agents/channel` with JSON body containing `channel_id`, `channel_member_ids`, and `messages`.
4. **Response**: Post agent reply to Discord channel.

---

## User Mapping

- **Human message `name`**: Must be the Discord identifier — e.g. `discord:{snowflake}` or bare snowflake. Display name is **not** required; Discord user id alone is sufficient.
- **Backend resolution**: The integration route implies Discord. The backend resolves `discord:{snowflake}` or bare snowflake to an external member: `EventMembership` with `user_id=None`, `external_source=DISCORD`, `external_id` = snowflake. No separate "source" parameter is needed; the integration endpoint and the request body (`channel_id`, `channel_member_ids`) define the context.
- **External members**: Discord users are represented as external members (`external_source = DISCORD`, `external_id` = Discord user ID string). `display_name` can remain null.

### Invites (Channel Path)

When using the integration endpoint (channel path), **only Discord ids** may be used for invites. The invitee's Discord id must be in the request's `channel_member_ids`; the backend rejects invites for users not in that list. App user UUIDs are **not** used for invites on the channel path.

---

## Agent Behavior: Vibe-Reactive, Chill Event Detection

The assistant reads the room and reacts to the current conversation. It's ready to help when people are talking about wanting to play something or suggesting a game night—e.g. "We've been wanting to play Catan for a while" + friend agrees → assistant: "Want to lock in a time?"

Discord-specific prompt addition:

- **Vibe-reactive**: Pay attention to what's actually being discussed. Pick up on casual mentions of wanting to play a game, nostalgia about a game, or suggestions that a game night would be fun. React to the current vibe, not just explicit commands.
- **Read the room**: In casual group chat, people discuss games, plans, or just chat. If the vibe suggests someone wants to make it happen, offer to help—only if it feels natural. Do not push.
- **Ready to help**: When the moment is right, offer to lock in a time, create an event, or invite people. One light offer is enough (e.g. "Want to lock in a time?" or "I can help set that up if you'd like").
- **Chill by default**: If off-topic or no event suggestion, keep it brief or don't respond. Never be salesy or repetitive. Default to lurking: only chime in when it clearly adds value.

**Response filtering**: If the agent returns "no action needed" or similar, don't post to Discord.

---

## API Integration

### Auth

The existing `/api/agents/user` requires JWT (`current_active_user`). For the bot:

- Use `/api/agents/channel`; require `X-API-Key` header (or equivalent).
- Same request/response schema as `/api/agents/user`.
- No user auth; bot calls on behalf of the channel.

---

## Config (Environment Variables)

```bash
DISCORD_BOT_TOKEN=...
API_BASE_URL=https://your-api.vercel.app
DISCORD_API_KEY=...                  # For X-API-Key on /api/agents/channel
```

`MESSAGE_HISTORY_LIMIT` is a constant in config (default 25).

**No channel IDs.** The bot responds in any channel it can read. Each `on_message` event includes the channel; the bot fetches history from and replies to that channel. No allow-list or config needed.

---

## Suggested File Structure

```
bot/
├── __init__.py
├── discord/
│   ├── PLAN.md           # This file
│   ├── __init__.py
│   ├── main.py           # Entry point, Discord client setup
│   ├── config.py         # Load env vars (N, API URL, etc.)
│   ├── message_builder.py # Discord messages → AgentRequest format
│   ├── channel_processor.py # Per-channel state, processing loop
│   └── client.py         # HTTP client for /chat API
```

---

## Implementation Phases

### Phase 1: Core
- Discord client, `on_message` handler.
- Fetch last N messages via Discord API.
- Fetch channel member list for `channel_member_ids`.
- Build request body: `channel_id`, `channel_member_ids`, `messages` (human message `name` = Discord identifier, e.g. `discord:{snowflake}`).
- HTTP POST to `/api/agents/channel`.
- Send response to Discord.

### Phase 2: Queue & Cleanup
- Per-channel in-memory state (`processing`, `pending`).
- Block new processing while one is in progress.
- Process again if `pending` when done.
- Delete channel state when idle.

### Phase 3: User Mapping
- Message builder: use `discord:{snowflake}` (or bare snowflake) as `name` for human messages. Backend resolves to external member automatically on the integration route.
- Backend already supports external identifiers; no app-side change needed beyond sending `channel_id` and `channel_member_ids`.

### Phase 4: Vibe-Reactive Behavior
- Discord-specific prompt (read the room, react to vibe, ready to help when moment is right).
- Response filtering (don't post when nothing useful).

### Phase 5: Multi-Channel
- Respond in any channel the bot can read (channel is inherent to each message).
- Verify per-channel isolation (in-memory state keyed by channel_id).

---

---

## Edge Cases

| Case | Approach |
|------|----------|
| Rate limits | Respect Discord API limits; add delays if needed. |
| Long processing | Optional: show typing indicator while processing. |
| Errors | Log, optionally retry; don't block channel. |
| Empty history | Agent can still work with a single message. |
| Bot's own messages | Exclude from history when building context. |
| Restart | In-memory state is lost; bot resumes fresh. |
