from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    price: Mapped[float] = mapped_column(Float)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    product: Mapped["Product"] = relationship(back_populates="variants")
    stock: Mapped["Stock"] = relationship(
        back_populates="variant",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Stock(Base):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id"),
        unique=True
    )

    variant: Mapped["ProductVariant"] = relationship(back_populates="stock")
