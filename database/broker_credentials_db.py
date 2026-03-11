# database/broker_credentials_db.py

import base64
import os
from datetime import datetime

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from utils.logging import get_logger

logger = get_logger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Security: Require API_KEY_PEPPER environment variable (fail fast if missing)
_pepper_value = os.getenv("API_KEY_PEPPER")
if not _pepper_value:
    raise RuntimeError(
        "CRITICAL: API_KEY_PEPPER environment variable is not set. "
        "This is required for secure broker credential encryption."
    )
if len(_pepper_value) < 32:
    raise RuntimeError(
        f"CRITICAL: API_KEY_PEPPER must be at least 32 characters (got {len(_pepper_value)})."
    )
PEPPER = _pepper_value


# Setup Fernet encryption for broker credentials

def _get_encryption_key():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"openalgo_broker_creds_salt",
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(PEPPER.encode()))
    return Fernet(key)


fernet = _get_encryption_key()

# Conditionally create engine based on DB type
if DATABASE_URL and "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, echo=False, poolclass=NullPool, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL, echo=False, pool_size=50, max_overflow=100, pool_timeout=10
    )

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class BrokerCredentials(Base):
    __tablename__ = "broker_credentials"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)
    broker_name = Column(String(50), nullable=True)
    broker_api_environment = Column(String(20), nullable=True)
    broker_api_key_encrypted = Column(Text, nullable=True)
    broker_api_secret_encrypted = Column(Text, nullable=True)
    broker_api_key_market_encrypted = Column(Text, nullable=True)
    broker_api_secret_market_encrypted = Column(Text, nullable=True)
    redirect_url = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)



def init_db():
    from database.db_init_helper import init_db_with_logging

    init_db_with_logging(Base, engine, "Broker Credentials DB", logger)
    _migrate_add_broker_api_environment_column()


def _migrate_add_broker_api_environment_column():
    """Add broker_api_environment column if missing."""
    try:
        from sqlalchemy import inspect, text

        inspector = inspect(engine)
        if "broker_credentials" not in inspector.get_table_names():
            return

        columns = [col["name"] for col in inspector.get_columns("broker_credentials")]
        if "broker_api_environment" not in columns:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE broker_credentials "
                        "ADD COLUMN broker_api_environment VARCHAR(20)"
                    )
                )
                conn.commit()
                logger.info(
                    "Migration: Added 'broker_api_environment' column to broker_credentials table"
                )
    except Exception as e:
        logger.debug(f"Migration check for broker_api_environment column: {e}")



def _encrypt(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()



def _decrypt(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception as e:
        logger.exception(f"Error decrypting broker credential: {e}")
        return None



def get_user_broker_credentials(user_id: str) -> dict | None:
    if not user_id:
        return None
    creds = BrokerCredentials.query.filter_by(user_id=user_id).first()
    if not creds:
        return None
    return {
        "broker_name": creds.broker_name,
        "broker_api_environment": creds.broker_api_environment,
        "broker_api_key": _decrypt(creds.broker_api_key_encrypted),
        "broker_api_secret": _decrypt(creds.broker_api_secret_encrypted),
        "broker_api_key_market": _decrypt(creds.broker_api_key_market_encrypted),
        "broker_api_secret_market": _decrypt(creds.broker_api_secret_market_encrypted),
        "redirect_url": creds.redirect_url,
    }



def upsert_user_broker_credentials(
    user_id: str,
    broker_name: str | None = None,
    broker_api_environment: str | None = None,
    broker_api_key: str | None = None,
    broker_api_secret: str | None = None,
    broker_api_key_market: str | None = None,
    broker_api_secret_market: str | None = None,
    redirect_url: str | None = None,
) -> BrokerCredentials:
    if not user_id:
        raise ValueError("user_id is required")

    creds = BrokerCredentials.query.filter_by(user_id=user_id).first()
    if not creds:
        creds = BrokerCredentials(user_id=user_id)
        db_session.add(creds)

    if broker_name is not None:
        creds.broker_name = broker_name
    if broker_api_environment is not None:
        creds.broker_api_environment = broker_api_environment
    if broker_api_key is not None:
        creds.broker_api_key_encrypted = _encrypt(broker_api_key)
    if broker_api_secret is not None:
        creds.broker_api_secret_encrypted = _encrypt(broker_api_secret)
    if broker_api_key_market is not None:
        creds.broker_api_key_market_encrypted = _encrypt(broker_api_key_market)
    if broker_api_secret_market is not None:
        creds.broker_api_secret_market_encrypted = _encrypt(broker_api_secret_market)
    if redirect_url is not None:
        creds.redirect_url = redirect_url

    creds.updated_at = datetime.utcnow()
    db_session.commit()
    return creds
