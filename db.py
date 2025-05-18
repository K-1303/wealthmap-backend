import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, String, Integer, BigInteger, Float,
    ForeignKey, UniqueConstraint, TIMESTAMP, func
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env")


Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# ─────────────────────────────────────
# Core Models
# ─────────────────────────────────────

class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    mailing_address = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    type = Column(String, default="individual")  
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    estimated_net_worth = Column(Float, nullable=True)
    confidence_level = Column(String, nullable=True)  # high, medium, low


    __table_args__ = (
        UniqueConstraint("full_name", "mailing_address", name="uq_owner"),
    )

class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True)
    attom_id = Column(BigInteger, unique=True, nullable=False)

    # Basic fields
    site_address = Column(String)        # oneLine
    address_line1 = Column(String)       # line1
    address_line2 = Column(String)       # line2
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    propertytype = Column(String)        # Property type (e.g., Residential, Commercial)
    year_built = Column(Integer)
    size = Column(Float)                # Living size or building size

    # Coordinates (optional, for mapping or future spatial indexing)
    latitude = Column(Float)
    longitude = Column(Float)

    # Sales
    sale_amount = Column(Float)
    sale_date = Column(String)
    sale_type = Column(String)

    # Valuation
    avm_value = Column(Float)
    avm_low = Column(Float)
    avm_high = Column(Float)
    avm_score = Column(Integer)
    avm_last_updated = Column(TIMESTAMP)

    # Assessment
    assessed_total_value = Column(Float)
    market_total_value = Column(Float)
    tax_amount = Column(Float)
    tax_year = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())

class OwnerProperty(Base):
    __tablename__ = "owner_property"

    owner_id = Column(String, ForeignKey("owners.id"), primary_key=True)
    property_id = Column(String, ForeignKey("properties.id"), primary_key=True)

# ─────────────────────────────────────
# Schema Init
# ─────────────────────────────────────

def create_tables():
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
