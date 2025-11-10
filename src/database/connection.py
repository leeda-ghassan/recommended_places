from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from typing import Optional
from utils.config import get_database_url

engine: Optional[Engine] = None
metadata = MetaData()


def init_engine(url: Optional[str] = None, *, echo: bool = False) -> Engine:
    global engine
    if engine is None:
        db_url = url or get_database_url()
        engine = create_engine(db_url, future=True, echo=echo, pool_pre_ping=True)
        metadata.bind = engine
    return engine


def get_engine() -> Engine:
    global engine
    if engine is None:
        return init_engine()
    return engine
