from sqlmodel import create_engine, Session

from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT
)

def get_session():
    with Session(engine) as session:
        yield session
