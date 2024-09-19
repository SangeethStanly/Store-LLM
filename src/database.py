from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from . import config
from langchain_community.utilities import SQLDatabase

Base = declarative_base()

user = config.POSTGRES_USER
password = config.POSTGRES_PASSWORD
server = config.POSTGRES_SERVER
db = config.POSTGRES_DB

database_url = f"postgresql://{user}:{password}@{server}/{db}"
engine = create_engine(database_url)

sql_db = SQLDatabase(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
