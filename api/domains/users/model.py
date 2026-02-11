from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from sqlmodel import Field
from uuid import UUID, uuid4


class User(SQLModelBaseUserDB, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False)
