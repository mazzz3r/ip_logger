from sqlalchemy import Column, Integer, String

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    redirect_url = Column(String, nullable=False)
    address = Column(String, nullable=False)
