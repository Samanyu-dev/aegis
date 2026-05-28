import os
import logging
from datetime import datetime
from uuid import uuid4
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, JSON
from apps.backend.config import settings

logger = logging.getLogger("aegis.database")

Base = declarative_base()

class DBInvestigation(Base):
    __tablename__ = "investigations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    target = Column(String(255), nullable=False)
    focus = Column(JSON, nullable=True)  # List of focus strings
    status = Column(String(50), default="running")  # running, complete, failed
    risk_score = Column(Float, default=0.0)
    report = Column(JSON, nullable=True)  # Full IntelligenceReport object as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class DBSignal(Base):
    __tablename__ = "signals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    signal_type = Column(String(100), nullable=False)  # HIRING_SPIKE, BREACH_SIGNAL, etc.
    entity = Column(String(255), nullable=False)
    detail = Column(String(1000), nullable=True)
    severity = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBWorkflowEvent(Base):
    __tablename__ = "workflow_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_type = Column(String(100), nullable=False)  # HIGH_RISK_DETECTED, etc.
    payload = Column(JSON, nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)

class DBMemoryNode(Base):
    __tablename__ = "memory_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    entity = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)  # COMPANY, PERSON, etc.
    properties = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Store 1536 float array natively as JSON
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Configure dynamic database URL (PostgreSQL asyncpg vs SQLite)
db_url = settings.DATABASE_URL
if not db_url:
    # Local fallback to SQLite database
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "aegis.db"))
    db_url = f"sqlite+aiosqlite:///{db_path}"
    logger.warning(f"DATABASE_URL not configured. Utilizing local SQLite fallback at: {db_url}")
else:
    # Ensure correct asynchronous driver prefix for postgres
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://")

# Create Async Engine
engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    # Standard connection pool configs for postgres; sqlite does not require typical pooling
    **({"pool_size": 5, "max_overflow": 10} if "sqlite" not in db_url else {})
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """
    Initializes database tables on start.
    Creates schema definitions dynamically.
    """
    try:
        async with engine.begin() as conn:
            # Recreate all tables safely
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for FastAPI route endpoints.
    Provides session control context.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
