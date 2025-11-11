from uuid import uuid4
from functools import lru_cache
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, OperationalError
from src.places.queries import PlacesQueries


try:
    import pyplace
except Exception:
    pyplace = None


class PlacesService:
    def __init__(self):
        self.queries = PlacesQueries()

    def _sanitize_row(self, row): #turning row into dict
        if not row:
            return None
        try:
            d = dict(row)
        except Exception:
            d = {k: row[k] for k in row.keys()}
        if "id" in d and d["id"] is not None: #turning id and dates into string
            d["id"] = str(d["id"])
        for k in ("created_at", "updated_at"):
            if k in d and getattr(d[k], "isoformat", None):
                try:
                    d[k] = d[k].isoformat()
                except Exception:
                    d[k] = str(d[k])
        return d

    @lru_cache(maxsize=1024) # i honestly don't know what this is
    def _validate_country_with_pyplace(self, country_input: str):
        if not country_input:
            return None
        if pyplace is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="pyplace library is not available")

        try:
            if hasattr(pyplace, "countries") and hasattr(pyplace.countries, "lookup"):
                country = pyplace.countries.lookup(country_input)
            elif hasattr(pyplace, "lookup"):
                country = pyplace.lookup(country_input)
            else:
                raise RuntimeError("pyplace API not recognized")
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid country")

        alpha2 = None
        name = None
        if hasattr(country, "alpha_2"):
            alpha2 = getattr(country, "alpha_2")
        elif hasattr(country, "alpha2"):
            alpha2 = getattr(country, "alpha2")
        elif hasattr(country, "code"):
            alpha2 = getattr(country, "code")

        if hasattr(country, "name"):
            name = getattr(country, "name")
        elif hasattr(country, "common_name"):
            name = getattr(country, "common_name")


    def create_place(self, name, description, user_id, country=None, place_field=None):
        if not name or not user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name and user_id are required")

        country_norm = None
        if country:
            country_data = self._validate_country_with_pyplace(country)
            country_norm = country_data.get("alpha2") if country_data else None

        values = {
            "id": uuid4(),
            "name": name,
            "description": description,
            "user_id": user_id,
            "country": country_norm,
            "place": place_field,
        }

        try:
            created = self.queries.create_place(values)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        return self._sanitize_row(created)

    def get_place_by_id(self, place_id):
        try:
            row = self.queries.get_place(place_id)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        return self._sanitize_row(row)

    def list_places(self, filters=None, limit=None, offset=None, order_by=None):
        try:
            rows = self.queries.get_places(filters=filters, limit=limit, offset=offset, order_by=order_by)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        if rows is False:
            return []
        out = []
        for r in rows or []:
            out.append(self._sanitize_row(r))
        return out

    def update_place(self, place_id, data):
        try:
            updated = self.queries.update_place(place_id, data)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        return self._sanitize_row(updated)

    def delete_place(self, place_id):
        try:
            res = self.queries.delete_place(place_id)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
        return res

    def list_recommended_for_place(self, place_id, limit=None):
        try:
            rows = self.queries.get_recommended_for_place(place_id, limit=limit)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
        if rows is False:
            return []
        return [self._sanitize_row(r) for r in rows]

    def add_recommended(self, name, description, place_id, country=None, place_field=None):
        values = {
            "id": uuid4(),
            "name": name,
            "description": description,
            "place_id": place_id,
            "country": country,
            "place": place_field,
        }
        try:
            created = self.queries.create_recommended(values)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
        return self._sanitize_row(created)

    def remove_recommended(self, rec_id):
        try:
            res = self.queries.remove_recommended(rec_id)
        except OperationalError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
        return res