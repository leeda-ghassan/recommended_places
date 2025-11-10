from sqlalchemy import select, insert, update, delete, and_, or_
from src.database.execute import places as PlacesModel, recommended as RecommendedModel, DBClient


class PlacesQueries:
    def __init__(self):
        self.Places = PlacesModel
        self.Recommended = RecommendedModel
        self.db = DBClient()

    def get_place(self, place_id):
        stmt = select(self.Places).where(self.Places.c.id == place_id)
        return self.db.execute_one(stmt)

    def get_places(self, filters=None, limit=None, offset=None, order_by=None):
        stmt = select(self.Places)
        where = []

        if filters:
            name = filters.get("name")
            country = filters.get("country")
            place_field = filters.get("place")
            user_id = filters.get("user_id")
            q = filters.get("q")

            if name:
                where.append(self.Places.c.name.ilike(f"%{name}%"))
            if q:
                where.append(or_(
                    self.Places.c.name.ilike(f"%{q}%"),
                    self.Places.c.description.ilike(f"%{q}%")
                ))
            if country:
                where.append(self.Places.c.country == country)
            if place_field:
                where.append(self.Places.c.place.ilike(f"%{place_field}%"))
            if user_id:
                where.append(self.Places.c.user_id == user_id)

        if where:
            stmt = stmt.where(and_(*where))

        if order_by:
            if isinstance(order_by, str):
                if order_by.startswith("-"):
                    col = getattr(self.Places.c, order_by[1:], None)
                    if col is not None:
                        stmt = stmt.order_by(col.desc())
                else:
                    col = getattr(self.Places.c, order_by, None)
                    if col is not None:
                        stmt = stmt.order_by(col.asc())

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        return self.db.execute_all(stmt)

    def create_place(self, values):
        stmt = insert(self.Places).values(
            id=values.get("id"), #UUID
            name=values.get("name"),
            description=values.get("description"),
            user_id=values.get("user_id"),
            country=values.get("country"),
            place=values.get("place"),
        ).returning(self.Places)
        return self.db.execute_commit(stmt)

    def update_place(self, place_id, data):
        values = {}
        for key in ("name", "description", "country", "place", "user_id"):
            if key in data:
                values[key] = data[key]
        stmt = update(self.Places).where(self.Places.c.id == place_id).values(**values).returning(self.Places)
        return self.db.execute_commit(stmt)

    def delete_place(self, place_id):
        stmt = delete(self.Places).where(self.Places.c.id == place_id)
        return self.db.execute_all(stmt)

    def get_recommended_for_place(self, place_id, limit=None):
        stmt = select(self.Recommended).where(self.Recommended.c.place_id == place_id)
        if limit:
            stmt = stmt.limit(limit)
        return self.db.execute_all(stmt)

    def create_recommended(self, values):
        stmt = insert(self.Recommended).values(
            id=values.get("id"),
            name=values.get("name"),
            description=values.get("description"),
            place_id=values.get("place_id"),
            country=values.get("country"),
            place=values.get("place"),
        ).returning(self.Recommended)
        return self.db.execute_commit(stmt)

    def remove_recommended(self, rec_id):
        stmt = delete(self.Recommended).where(self.Recommended.c.id == rec_id)
        return self.db.execute_all(stmt)