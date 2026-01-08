from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import models so they register with SQLModel.metadata
from domains.users.model import User, Friendship
from domains.games.model import Game
from domains.events.model import Event, EventMembership, EventMessage

# Import routers
from domains.games.routes import router as games_router
from domains.users.routes import router as friends_router
from domains.events.routes import router as events_router
from agent.routes import router as agent_router
from domains.auth.dependencies import fastapi_users, jwt_authentication
from domains.users.schemas import UserPublic, UserCreate, UserUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
# Allow all origins in development for testing from mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(fastapi_users.get_register_router(UserPublic, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_auth_router(jwt_authentication), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserPublic, UserUpdate), prefix="/auth", tags=["auth"])
app.include_router(games_router)
app.include_router(friends_router)
app.include_router(events_router)
app.include_router(agent_router)

# cd backend
# fastapi dev main.py --host 0.0.0.0 --port 8000