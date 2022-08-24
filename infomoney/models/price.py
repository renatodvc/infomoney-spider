from sqlalchemy import Column, DateTime, Numeric, String, TIMESTAMP

from .base import Base


class AssetPriceModel(Base):
    __tablename__ = 'assets_prices'

    _id = Column(String(32), nullable=False, unique=True)  # Prevent duplicates
    asset_code = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    timestamp = Column(TIMESTAMP)
    open = Column(Numeric(scale=2))
    high = Column(Numeric(scale=2))
    low = Column(Numeric(scale=2))
    close = Column(Numeric(scale=2))
    volume = Column(String)
    variation = Column(Numeric(scale=2))
