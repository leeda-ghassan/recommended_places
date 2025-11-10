from src.database.connection import engine
from typing import Union, List, Dict, Any, Optional
from sqlalchemy import (text as sa_text)
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.engine import Executable
from fastapi import HTTPException, status
from src.database.connection import get_engine


class DBClient:
    def __init__(self, engine=None):
        self.engine = engine or get_engine()

    def _prepare(self, query: Union[str, Executable]):
        if isinstance(query, str):
            return sa_text(query)
        return query

    def execute_all(self, query: Union[str, Executable]) -> Union[List[Dict[str, Any]], bool]:
        q = self._prepare(query)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(q)

                if result.returns_rows:
                    rows = result.mappings().all()
                    if not rows:
                        return False
                    return [dict(row) for row in rows]

                return True

        except IntegrityError as e:
            detail = f"Database integrity constraint violated: {str(e)}."
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        except OperationalError as e:
            detail = f"Unexpected database error: {str(e)}"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        except Exception as e:
            detail = f"Unexpected error: {str(e)}"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    def execute_one(self, query: Union[str, Executable]) -> Optional[Dict[str, Any]]:
        q = self._prepare(query)
        try:
            with self.engine.begin() as conn:
                result = conn.execute(q)

                if result.returns_rows:
                    row = result.mappings().first()
                    if not row:
                        return None
                    return dict(row)

                return None

        except IntegrityError as e:
            detail = f"Database integrity constraint violated: {str(e)}."
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        except OperationalError as e:
            detail = f"Unexpected database error: {str(e)}"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
        except Exception as e:
            detail = f"Unexpected error: {str(e)}"
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)