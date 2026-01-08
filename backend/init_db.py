from dotenv import load_dotenv
load_dotenv()

# Import models so they register with SQLModel.metadata
from domains.users.model import User, Friendship
from domains.games.model import Game
from domains.events.model import Event, EventMembership, EventMessage

from database import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables created successfully!")
