from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import Config

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={}
    if "sqlite" not in Config.DATABASE_URL
    else {"check_same_thread": False},
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
