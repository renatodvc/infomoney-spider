from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from infomoney.settings import DATABASE_URI, SHOW_SQL_STATEMENTS
from .base import Base
from .earnings import AssetEarningsModel
from .price import AssetPriceModel


engine = create_engine(DATABASE_URI, echo=SHOW_SQL_STATEMENTS)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


__all__ = ['Base', 'AssetEarningsModel', 'AssetPriceModel']
