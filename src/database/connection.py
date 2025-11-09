from sqlalchemy import create_engine
from sqlalchemy import MetaData
from utils.config import get_database_url


engine = create_engine(get_database_url())

metadata = MetaData()

metadata.bind=engine