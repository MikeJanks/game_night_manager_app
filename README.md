# Game Night Manager 🎲

**Turn "we should play sometime" into actual game nights.** 🎯

Your game night buddy catches the vibe in your chat, rallies the crew, and helps turn "that sounds fun" into real plans.

---

## The Problem 🤔

Friends keep saying they want to play but nobody sets a date. Group chats are full of "that sounds fun" with no follow-through. Planning game nights feels like herding cats.

---

## The Solution ✨

Your buddy lives where you already convene—chat apps. You and a friend are talking about wanting to play Catan—it picks up on the vibe and chimes in: "Want to lock in a time?" No commands. No forms. Just talk.

- 🎮 **Discord** — Add the bot to your server. It joins your channels, listens in, and when someone mentions wanting to play something or suggests a game night, it's ready to help. Chill and non-pushy; it only chimes in when it adds value.

- 🌐 **Web** — A standalone chat interface for when you prefer a dedicated UI. Same buddy, same capabilities.

Both use the same backend. Create events, invite people, set dates and locations—all in natural language.

---

## See It in Action 🎬

- 🗓️ **"I want to organize a Catan night next Friday at 7pm"** — Event created. No forms, no back-and-forth.
- 💬 **Two friends chatting about wanting to play** — It reads the room and offers: "Want to lock in a time?"
- 👋 **Invite by mention** — Invite people with a @mention. They accept or decline right in the chat.

---

## Features 🎉

- 🎲 **Vibe-reactive** — Picks up when people are talking about games or wanting to play. Offers to lock in a time when the moment feels right—no awkward setup.
- 💬 **Natural language** — "Create a Catan night next Friday at 7pm" or "Invite Alex to the game night." Talk like you normally do; no commands to memorize.
- 📅 **Event lifecycle** — Planning → confirmed → cancelled. Hosts update plans; everyone accepts or declines. Everyone knows where things stand.
- 🎧 **Multi-channel Discord** — Joins any channel, fetches recent context on each message. Works everywhere; no per-channel setup.
- 🔒 **Privacy by Design** — Messages processed in real time, never stored. We compute, suggest, and move on. Your privacy stays yours.

---

## Where It Lives 📍

- 🎮 **Discord** — Primary. Add the bot; it joins channels, listens, and helps when it makes sense.
- 🌐 **Web** — Secondary. Standalone chat UI when you prefer a dedicated interface.

Both use the same backend and capabilities.

---

## For Developers 🔧

### Architecture

```mermaid
flowchart TB
    subgraph clients [Clients]
        Discord[Discord Bot]
        Web[Web UI]
    end

    subgraph api [API]
        FastAPI[FastAPI]
        Agent[LangGraph Agent]
        Groq[Groq LLM]
        Tools[Event + User Tools]
    end

    subgraph data [Data]
        DB[(PostgreSQL)]
    end

    Discord -->|HTTP| FastAPI
    Web -->|HTTP| FastAPI
    FastAPI --> Agent
    Agent --> Groq
    Agent --> Tools
    Tools --> DB
```

- **Backend**: FastAPI, SQLModel, PostgreSQL, Alembic
- **Agent**: LangGraph, LangChain, Groq LLM
- **Frontend**: React, Vite, React Router
- **Bot**: discord.py, httpx (separate process, calls API over HTTP)

### Project Structure

```
api/           # FastAPI app, agents, domains (events, auth, users)
frontend/      # React SPA
bot/discord/   # Discord bot (separate process)
```

### Getting Started

**Prerequisites**

- Python 3.12+
- Node.js
- PostgreSQL

**Environment Variables**

API & Frontend:
```
DATABASE_URL=postgresql://...
SECRET_KEY=...
GROQ_API_KEY=...
```

Discord Bot:
```
DISCORD_BOT_TOKEN=...
API_BASE_URL=https://your-api.vercel.app
DISCORD_API_KEY=...              # For X-API-Key on /api/agents/channel
```

The bot responds in any channel it can read. No channel IDs to configure—each message includes its channel context.

**Run Locally**

1. **Migrations**: `alembic upgrade head`
2. **API**: `fastapi dev api/index.py` (or `uvicorn api.index:app`)
3. **Frontend**: `cd frontend && npm install && npm run dev`
4. **Discord Bot**: `python -m bot.discord.main` (runs separately)

**Deployment**

- **Vercel** — API and frontend deploy together. `vercel.json` routes `/api/*` to FastAPI and `/*` to the SPA.
- **Discord Bot** — Runs as a separate process (Railway, Fly.io, or a VPS).

### Docs 📚

- [PRODUCT_SPEC.md](PRODUCT_SPEC.md) — Full product specification
- [bot/discord/PLAN.md](bot/discord/PLAN.md) — Discord bot design and implementation plan
