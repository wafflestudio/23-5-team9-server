from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from carrot.db.settings import DB_SETTINGS


class DatabaseManager:
    def __init__(self) -> None:
        # DB_SETTINGS.url 예: mysql+aiomysql://user:pw@host:3306/db
        self.engine: AsyncEngine = create_async_engine(
            DB_SETTINGS.url,
            pool_recycle=28000,
            pool_size=10,
            pool_pre_ping=True,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

db = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with db.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_session_factory():
    """
    세션 객체가 아닌, 세션 생성기(factory)를 반환합니다.
    웹소켓 루프 안에서 'async with factory() as session:' 형태로 사용하기 위함입니다.
    """
    return db.session_factory