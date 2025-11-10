from sqlalchemy import select, insert, update, delete, and_, or_
from src.database.execute import users as UsersModel, places as PlacesModel, favorites as FavoritesModel, DBClient


class UsersQueries:
    def __init__(self):
        self.Users = UsersModel
        self.Places = PlacesModel
        self.Favorites = FavoritesModel
        self.db_client = DBClient()

    def get_user(self, user_id):
        stmt = select(self.Users).where(self.Users.c.id == user_id)
        return self.db_client.execute_one(stmt)

    def get_user_by_email(self, email):
        stmt = select(self.Users).where(self.Users.c.email == email)
        return self.db_client.execute_one(stmt)


    def create_user(self, values):
        stmt = insert(self.Users).values(
            id=values.get("id"),
            name=values.get("name"),
            email=values.get("email"),
            password_hash=values.get("password_hash"),
            role=values.get("role", "user"),
        ).returning(self.Users)
        return self.db_client.execute_commit(stmt)

    def create_favorite(self, values):
        stmt = insert(self.Favorites).values(
            id=values.get("id"),
            user_id=values.get("user_id"),
            places_id=values.get("places_id"),
        ).returning(self.Favorites)
        return self.db_client.execute_commit(stmt)


    def update_user(self, user_id, data):
        values = {}
        for key in ("name", "email", "role", "password_hash"):
            if key in data:
                values[key] = data[key]

        stmt = update(self.Users).where(self.Users.c.id == user_id).values(**values).returning(self.Users)
        return self.db_client.execute_commit(stmt)

    def remove_favorite(self, user_id, place_id):
        stmt = delete(self.Favorites).where(
            and_(self.Favorites.c.user_id == user_id, self.Favorites.c.places_id == place_id)
        )
        return self.db_client.execute_all(stmt)

    def get_favorites_rows_for_user(self, user_id, limit=None, offset=None):
        stmt = select(self.Favorites).where(self.Favorites.c.user_id == user_id)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return self.db_client.execute_all(stmt)

    def get_favorite_places_for_user(self, user_id, limit=None, offset=None):
        stmt = select(self.Places).select_from(
            self.Favorites.join(self.Places, self.Favorites.c.places_id == self.Places.c.id)
        ).where(self.Favorites.c.user_id == user_id)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return self.db_client.execute_all(stmt)

    def get_places_owned_by_user(self, user_id, limit=None, offset=None):
        stmt = select(self.Places).where(self.Places.c.user_id == user_id)
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        return self.db_client.execute_all(stmt)