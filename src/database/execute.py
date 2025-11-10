# Create execute file here that will contians the logic to execute database queries
# 

from sqlalchemy import (
    Table, Column, Text, String, ForeignKey, DateTime, MetaData, func
)
from sqlalchemy.dialects.postgresql import UUID
from src.database.connection import engine


metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", Text),
    Column("role", Text),
    Column("email", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

places = Table(
    "places",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", Text),
    Column("description", Text),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("country", Text),
    Column("place", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

recommended = Table(
    "recommended",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", Text),
    Column("description", Text),
    Column("place_id", UUID(as_uuid=True), ForeignKey("places.id")),
    Column("country", Text),
    Column("place", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

favorites = Table(
    "favorites",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("places_id", UUID(as_uuid=True), ForeignKey("places.id")),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now()),
)

class DBClient: #added this for the users queries
    def __init__(self, engine_instance=None):
        self.engine = engine_instance or engine

    def execute_one(self, stmt):
        with self.engine.connect() as conn:
            res = conn.execute(stmt)
            try:
                return res.mappings().first()
            except Exception:
                return res.first()

    def execute_all(self, stmt):
        with self.engine.connect() as conn:
            res = conn.execute(stmt)
            try:
                return res.mappings().all()
            except Exception:
                return res.fetchall()

    def execute_commit(self, stmt):
        with self.engine.begin() as conn:
            res = conn.execute(stmt)
            try:
                return res.mappings().first()
            except Exception:
                return res.first()