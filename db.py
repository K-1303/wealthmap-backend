from sqlalchemy import create_engine, Column, String, Integer, BigInteger, ForeignKey, UniqueConstraint, Table, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from dotenv import load_dotenv

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

    __table_args__ = (UniqueConstraint("full_name", "mailing_address", name="uq_owner"),)

class Property(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True)
    attom_id = Column(BigInteger, unique=True, nullable=False)
    apn = Column(String)
    site_address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    year_built = Column(Integer)
    sqft = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

class OwnerProperty(Base):
    __tablename__ = "owner_property"

    owner_id = Column(String, ForeignKey("owners.id"), primary_key=True)
    property_id = Column(String, ForeignKey("properties.id"), primary_key=True)

def create_tables():
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
