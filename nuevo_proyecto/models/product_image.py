from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database.db import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_stock_id = Column(UUID(as_uuid=True), ForeignKey("product_stocks.id"))
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
