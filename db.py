import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, String, Integer, BigInteger, Float,
    ForeignKey, UniqueConstraint, TIMESTAMP, func
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class Owner(Base):
    __tablename__ = "owners"

    id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    mailing_address = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("full_name", "mailing_address", name="uq_owner"),
    )


class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True)
    attom_id = Column(BigInteger, unique=True, nullable=False)
    site_address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # AVM (Automated Valuation Model)
    avm_value = Column(Float)
    avm_low = Column(Float)
    avm_high = Column(Float)
    avm_score = Column(Integer)
    avm_last_updated = Column(TIMESTAMP)

    # Sale
    sale_amount = Column(Float)
    sale_date = Column(String)
    sale_type = Column(String)

    # Assessment (latest)
    assessed_total_value = Column(Float)
    market_total_value = Column(Float)
    tax_amount = Column(Float)
    tax_year = Column(Integer)

class OwnerProperty(Base):
    __tablename__ = "owner_property"

    owner_id = Column(String, ForeignKey("owners.id"), primary_key=True)
    property_id = Column(String, ForeignKey("properties.id"), primary_key=True)


def create_tables():
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
