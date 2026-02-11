from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database.db import Base


class ProductStock(Base):
    __tablename__ = "product_stocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(255), nullable=False)
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(255))

    supplier_id = Column(String(255))
    supplier_name = Column(String(500))

    quantity_on_hand = Column(Integer)
    quantity_reserved = Column(Integer)
    quantity_available = Column(Integer)

    minimum_stock_level = Column(Integer)
    reorder_point = Column(Integer)
    optimal_stock_level = Column(Integer)

    created_at = Column(DateTime, server_default=func.now())
    last_updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
