from dotenv import load_dotenv
load_dotenv()

# Import models so they register with SQLModel.metadata
from sqlmodel import SQLModel
from database import engine
from domains.users.model import User, Friendship
from domains.games.model import Game
from domains.events.model import Event, EventMembership, EventMessage

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")
