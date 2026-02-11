from dotenv import load_dotenv

# Load .env from project root (parent directory of api)
load_dotenv()

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from api.domains.events.routes import router as events_router
from api.agents.chat.routes import router as agent_router
from api.domains.auth.dependencies import fastapi_users, jwt_authentication
from api.domains.users.schemas import UserPublic, UserCreate, UserUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
api = APIRouter(prefix="/api")

@api.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

api.include_router(fastapi_users.get_register_router(UserPublic, UserCreate), prefix="/auth", tags=["auth"])
api.include_router(fastapi_users.get_auth_router(jwt_authentication), prefix="/auth", tags=["auth"])
api.include_router(fastapi_users.get_users_router(UserPublic, UserUpdate), prefix="/auth", tags=["auth"])
api.include_router(events_router)
api.include_router(agent_router)

app.include_router(api)

# fastapi dev api/index.py --host 0.0.0.0 --port 8000
