from collections.abc import AsyncGenerator
from datetime import datetime
from dotenv import load_dotenv
import os
import ssl

from fastapi import Depends
from fastapi_users.db import (
    SQLAlchemyUserDatabase,
    SQLAlchemyBaseUserTableUUID
)

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
    Integer,
    DateTime
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

from sqlalchemy.orm import DeclarativeBase, relationship


load_dotenv()


# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")


# Convert normal MySQL URL to async SQLAlchemy URL
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "mysql://",
        "mysql+aiomysql://",
        1
    )


# Remove ssl-mode parameter from Aiven URL
# SSL will be configured separately below
DATABASE_URL = DATABASE_URL.replace(
    "?ssl-mode=REQUIRED",
    ""
)


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship(
        "post",
        back_populates="user"
    )


class post(Base):
    __tablename__ = "posts"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        String(36),
        ForeignKey("user.id"),
        nullable=False
    )

    caption = Column(Text)

    url = Column(
        String(255),
        nullable=False
    )

    File_Type = Column(
        String(100),
        nullable=False
    )

    File_Name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="posts"
    )


# Create SSL context for Aiven MySQL
ssl_context = ssl.create_default_context()


# Database engine
Engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "ssl": ssl_context
    }
)


# Async session
async_session_maker = async_sessionmaker(
    Engine,
    expire_on_commit=False
)


async def Create_db_and_tables():
    async with Engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(
    session: AsyncSession = Depends(get_async_session)
):
    yield SQLAlchemyUserDatabase(
        session,
        User
    )