from sqlmodel import create_engine, Session

from core.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=settings.db.DB_POOL_SIZE,
    max_overflow=settings.db.DB_MAX_OVERFLOW,
    pool_timeout=settings.db.DB_POOL_TIMEOUT,
)


def get_session():
    with Session(engine) as session:
        yield session
