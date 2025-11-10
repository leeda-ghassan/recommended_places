from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from src.users.queries import UsersQueries
from src.database.execute import DBClient


class UsersService:

    def __init__(self):
        self.queries = UsersQueries()
        self.db = self.queries.db_client

    def _sanitize_row(self, row):
        if not row:
            return None
        try:
            data = dict(row)
        except Exception:
            data = {k: row[k] for k in row.keys()}
        data.pop("password_hash", None)

        if "id" in data and data["id"] is not None:
            data["id"] = str(data["id"])
        for k in ("created_at", "updated_at"):
            if k in data and getattr(data[k], "isoformat", None):
                try:
                    data[k] = data[k].isoformat()
                except Exception:
                    data[k] = str(data[k])

        return data


    def register_user(self, name: str, email: str, password: str, role: str = "user"):
        if not name or not email or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name, email and password are required")

        # extra step to check duplicate email
        try:
            existing = self.queries.get_user_by_email(email)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")

        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        password_hash = generate_password_hash(password)
        values = {
            "id": uuid4(),
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
        }

        try:
            created_row = self.queries.create_user(values)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Integrity error: {str(exc)}")
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")

        return self._sanitize_row(created_row)

    def get_user_by_id(self, user_id):
        try:
            row = self.queries.get_user(user_id)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self._sanitize_row(row)

    def authenticate_user(self, identifier: str, password: str):
        if not identifier or not password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="identifier and password are required")

        try: #find by email
            row = self.queries.get_user_by_email(identifier)
        except OperationalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
        
        if not row: #find by name if email doesn't work
            try:
                stmt = select(self.queries.Users).where(self.queries.Users.c.name == identifier)
                row = self.db.execute_one(stmt)
            except OperationalError:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        stored_hash = None
        try:
            stored_hash = row.get("password_hash") if hasattr(row, "get") else row["password_hash"]
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Malformed user record")

        if not stored_hash or not check_password_hash(stored_hash, password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return self._sanitize_row(row)


    def add_favorite(self, user_id, place_id):
        values = {"id": uuid4(), "user_id": user_id, "places_id": place_id}
        try:
            fav_row = self.queries.create_favorite(values)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Integrity error: {str(exc)}")
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")

        return self._sanitize_row(fav_row)

    def remove_favorite(self, user_id, place_id):
        try:
            result = self.queries.remove_favorite(user_id, place_id)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")
        return result

    def list_favorite_places(self, user_id, limit=None, offset=None):
        try:
            rows = self.queries.get_favorite_places_for_user(user_id, limit=limit, offset=offset)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")
        out = []
        for r in rows or []:
            try:
                d = dict(r)
            except Exception:
                d = {k: r[k] for k in r.keys()}
            # stringify id/created fields
            if "id" in d and d["id"] is not None:
                d["id"] = str(d["id"])
            for k in ("created_at", "updated_at"):
                if k in d and getattr(d[k], "isoformat", None):
                    try:
                        d[k] = d[k].isoformat()
                    except Exception:
                        d[k] = str(d[k])
            out.append(d)
        return out

    def list_places_owned(self, user_id, limit=None, offset=None):
        try:
            rows = self.queries.get_places_owned_by_user(user_id, limit=limit, offset=offset)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(exc)}")

        out = []
        for r in rows or []:
            try:
                d = dict(r)
            except Exception:
                d = {k: r[k] for k in r.keys()}
            if "id" in d and d["id"] is not None:
                d["id"] = str(d["id"])
            for k in ("created_at", "updated_at"):
                if k in d and getattr(d[k], "isoformat", None):
                    try:
                        d[k] = d[k].isoformat()
                    except Exception:
                        d[k] = str(d[k])
            out.append(d)
        return out