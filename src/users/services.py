from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, or_
from src.database.connection import engine
from src.database.execute import users

#do i need to convert row/RowMapping into plain dict?


def get_user_by_email(email):
    stmt = select(users).where(users.c.email == email)
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    return row


def get_user_by_id(uid):
    stmt = select(users).where(users.c.id == uid)
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    return row


def get_user_by_identifier_raw(identifier): #apparently this identifier looks for matching email or name
    stmt = select(users).where(or_(users.c.email == identifier, users.c.name == identifier))
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    return row


def create_user(data):
    uid = uuid4()
    password_hash = generate_password_hash(data["password"])
    insert_stmt = users.insert().values(
        id=uid,
        name=data["name"],
        email=data["email"],
        role=data.get("role", "user"),
        password_hash=password_hash,
    )
    with engine.begin() as conn:
        conn.execute(insert_stmt)
        sel = select(users).where(users.c.id == uid)
        row = conn.execute(sel).mappings().first()
    return row


def verify_user_credentials(identifier, password):
    row = get_user_by_identifier_raw(identifier)
    if not row:
        return None
    stored_hash = row["password_hash"]
    if not stored_hash:
        return None
    if check_password_hash(stored_hash, password):
        return row
    return None