users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", Text, unique=True, nullable=False),
    Column("email", Text, unique=True, nullable=False),
    Column("password_hash", Text, nullable=False),
)

places = Table(
    "places", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False),
    Column("description", Text),
    Column("location", Text),
    Column("country", Text),  #dropdown list from api
    Column("features", Text),  # for AI
)

favorites = Table(
    "favorites", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("place_id", Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
)

