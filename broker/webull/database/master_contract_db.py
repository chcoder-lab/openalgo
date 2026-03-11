# database/master_contract_db.py

import os

from sqlalchemy import Column, Float, Index, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from utils.logging import get_logger

logger = get_logger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class SymToken(Base):
    __tablename__ = "symtoken"
    id = Column(Integer, Sequence("symtoken_id_seq"), primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    brsymbol = Column(String, nullable=False, index=True)
    name = Column(String)
    exchange = Column(String, index=True)
    brexchange = Column(String, index=True)
    token = Column(String, index=True)
    expiry = Column(String)
    strike = Column(Float)
    lotsize = Column(Integer)
    instrumenttype = Column(String)
    tick_size = Column(Float)

    __table_args__ = (Index("idx_symbol_exchange", "symbol", "exchange"),)


def init_db():
    logger.info("Initializing Webull Master Contract DB")
    Base.metadata.create_all(bind=engine)


def download_master_contract():
    logger.warning(
        "Webull OpenAPI does not expose a public symbol master in this integration. "
        "Master contract download is not implemented."
    )
