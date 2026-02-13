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
                     │ history(N)   │     │ history      │     │ /agent/chat  │
                     └──────────────┘     └──────────────┘     └──────────────┘
```

- **Separate process**: Bot runs independently, not on the FastAPI server.
- **HTTP client**: Calls `POST {API_BASE_URL}/api/agent/chat` (or internal endpoint).
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
   - HTTP POST to `/agent/chat`.
   - Send response to Discord.
5. **After cycle** → Set `processing = False`.
6. **If `pending`** → Set `pending = False`, go to step 3 (another cycle).
7. **Else** → Delete `channel_states[channel_id]` (cleanup when idle).

No need to track message IDs. A boolean is enough: "something new arrived, run again." The "last N" fetch includes all new messages.

---

## Message Flow (Per Run)

1. **Discord API**: `channel.history(limit=N)` — always fresh, no caching.
2. **Build history**: Convert to `AgentRequest` format:
   - Human: `{type: "human", content: "...", name: "<user_uuid>"}`
   - AI: `{type: "ai", content: "..."}` (prior bot replies)
3. **HTTP**: `POST {API_URL}/api/agent/chat` with JSON body.
4. **Response**: Post agent reply to Discord channel.

---

## User Mapping

Tools expect `user_id` (UUID) in the `name` field of human messages. For Discord users:

**Chosen approach** — Use `EventMembership.external_source`, `external_id`, `display_name` for external members.

- Discord users who are not linked to app accounts are represented as external members.
- `external_source = DISCORD`, `external_id` = Discord user ID (snowflake string), `display_name` = Discord username/nick.
- When building messages for the agent, use a consistent identifier for the `name` field (e.g. `discord:{snowflake}`) so the agent/tools can resolve external members.
- Tools may need to accept external identifiers (e.g. `discord:123456789`) in addition to UUIDs, and resolve via `EventMembership` when `user_id` is null and `external_source`/`external_id` are set.

### Source Identification (Open Design Decision)

**Revisit this when implementing.** The backend must know that a request came from Discord so it can set `EventMembership.external_source = DISCORD` when tools create or update memberships.

**The issue:** Tools receive `user_id` from the agent (who copies it from the message `name`). When `user_id` is `"discord:123456789"` or a bare snowflake, the tool must not treat it as a UUID. Instead it must create `EventMembership` with `user_id=None`, `external_source=DISCORD`, `external_id="123456789"`. The system needs a reliable way to know that non-UUID identifiers in this request are Discord snowflakes.

**Option A: Route-level `source` param** — Add `source: "discord"` to the request body or query. The handler passes it through to the graph/tools. Tools receive `source` via shared context; when `user_id` isn't a valid UUID, they use `source` to parse it and set `external_source`. *Pros:* Single place to declare source; easy to add Slack/Telegram later. *Cons:* Requires threading `source` through handler → graph → tools.

**Option B: Dedicated route** — Create `POST /api/bot/discord` (or `/api/agent/chat/discord`). The route itself implies `source = "discord"`; handler hardcodes it. Same tool logic as Option A. *Pros:* No extra param; URL is self-documenting. *Cons:* New route per integration.

**Option C: Message-level `source` on NamedHumanMessage** — Add `source: "discord"` to each human message (e.g. in `additional_kwargs`). *Problem:* Tools only receive `user_id` from the agent's tool call, not the original message. The agent would need to pass `source` in the tool call too (schema change), or the graph would need to aggregate source from messages and pass it to tools (effectively Option A). *Pros:* Per-message granularity; could support mixed sources in one request. *Cons:* More complex; tools still need request-level source unless the agent is explicitly taught to pass it.

**Option D: Self-describing format in `name` (no separate source)** — Use `name="discord:123456789"`. The format encodes the source. Tools parse: if `user_id` matches `discord:(\d+)`, set `external_source=DISCORD`, `external_id=group(1)`; otherwise treat as UUID. *Pros:* No route changes; no extra params; tools can parse locally. *Cons:* Convention must be documented; future sources need new prefixes (`slack:`, `telegram:`).

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

The existing `/agent/chat` requires JWT (`current_active_user`). For the bot:

- Add internal route or extend existing; require `X-API-Key` header (or equivalent).
- Same request/response schema as `/agent/chat`.
- No user auth; bot calls on behalf of the channel.

---

## Config (Environment Variables)

```bash
DISCORD_BOT_TOKEN=...
API_BASE_URL=https://your-api.vercel.app
DISCORD_API_KEY=...              # For X-API-Key on internal route
DISCORD_CHANNEL_IDS=123,456,789  # Comma-separated channel IDs
MESSAGE_HISTORY_LIMIT=25
```

---

## Suggested File Structure

```
bot/
├── __init__.py
├── discord/
│   ├── PLAN.md           # This file
│   ├── __init__.py
│   ├── main.py           # Entry point, Discord client setup
│   ├── config.py         # Load env vars (channel IDs, N, API URL, etc.)
│   ├── message_builder.py # Discord messages → AgentRequest format
│   ├── channel_processor.py # Per-channel state, processing loop
│   └── client.py         # HTTP client for /chat API
```

---

## Implementation Phases

### Phase 1: Core
- Discord client, `on_message` handler.
- Fetch last N messages via Discord API.
- Build `AgentRequest` from messages.
- HTTP POST to `/agent/chat` (or internal endpoint).
- Send response to Discord.
- **Revisit**: Source Identification (User Mapping section).

### Phase 2: Queue & Cleanup
- Per-channel in-memory state (`processing`, `pending`).
- Block new processing while one is in progress.
- Process again if `pending` when done.
- Delete channel state when idle.

### Phase 3: User Mapping
- Use `EventMembership.external_source`, `external_id`, `display_name` for Discord users.
- Message builder: use `discord:{snowflake}` as `name` for human messages.
- Tools: support external identifiers; resolve via `EventMembership` when `user_id` is null.
- **Revisit**: Source Identification (route param vs. dedicated route vs. message-level vs. self-describing format).

### Phase 4: Vibe-Reactive Behavior
- Discord-specific prompt (read the room, react to vibe, ready to help when moment is right).
- Response filtering (don't post when nothing useful).

### Phase 5: Multi-Channel
- Config-driven channel list.
- Verify per-channel isolation.

---

## Open Decisions (Revisit During Implementation)

- **Source Identification**: Route param vs. dedicated route vs. message-level keyword vs. self-describing format. See User Mapping → Source Identification.

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
