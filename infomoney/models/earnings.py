from sqlalchemy import Column, DateTime, Numeric, String

from .base import Base


class AssetEarningsModel(Base):
    __tablename__ = 'assets_earnings'

    _id = Column(String(32), nullable=False, unique=True)  # Prevent duplicates
    asset_code = Column(String(10), nullable=False)
    type = Column(String, nullable=False)
    value = Column(Numeric(scale=3))
    pct_factor = Column(Numeric(scale=3))
    emission_value = Column(Numeric(scale=3))
    date_of_approval = Column(DateTime)
    date_of_record = Column(DateTime)
    date_of_payment = Column(DateTime)
