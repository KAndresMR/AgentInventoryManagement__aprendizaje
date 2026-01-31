from sqlalchemy import Column, Integer, String
from database.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    stock = Column(Integer, nullable=False, default=0)