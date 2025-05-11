import uuid
from datetime import datetime
from db import Session, Owner, Property, OwnerProperty
from attom_client import get_owner_details, get_property_financial_details
import os
from dotenv import load_dotenv

load_dotenv()

def normalize_name(name: str) -> str:
    return name.strip().upper() if name else None

def normalize_address(addr: str) -> str:
    return addr.strip().upper() if addr else None

def insert_or_get_owner(session, full_name: str, mailing_address: str) -> str:
    full_name = normalize_name(full_name)
    mailing_address = normalize_address(mailing_address)

    owner = session.query(Owner).filter_by(
        full_name=full_name,
        mailing_address=mailing_address
    ).first()

    if owner:
        return owner.id

    owner_id = str(uuid.uuid4())
    owner = Owner(
        id=owner_id,
        full_name=full_name,
        mailing_address=mailing_address
    )
    session.add(owner)
    session.commit()
    return owner_id

def insert_or_update_property(session, financial_data: dict) -> str:
    attom_id = financial_data.get("attom_id")
    property_obj = session.query(Property).filter_by(attom_id=attom_id).first()

    if not property_obj:
        property_id = str(uuid.uuid4())
        property_obj = Property(id=property_id, attom_id=attom_id)
        session.add(property_obj)
    else:
        property_id = property_obj.id

    # Update financial data
    property_obj.site_address = financial_data.get("address")
    property_obj.city = financial_data.get("city")
    property_obj.state = financial_data.get("state")
    property_obj.zip_code = financial_data.get("zip_code")

    # AVM
    property_obj.avm_value = financial_data.get("avm_value")
    property_obj.avm_low = financial_data.get("avm_low")
    property_obj.avm_high = financial_data.get("avm_high")
    property_obj.avm_score = financial_data.get("avm_score")
    if financial_data.get("avm_last_updated"):
        try:
            property_obj.avm_last_updated = datetime.strptime(financial_data["avm_last_updated"], "%Y-%m-%d")
        except Exception:
            pass

    # Sale
    property_obj.sale_amount = financial_data.get("sale_amount")
    property_obj.sale_date = financial_data.get("sale_date")
    property_obj.sale_type = financial_data.get("sale_type")

    # Assessment
    property_obj.assessed_total_value = financial_data.get("assessed_total_value")
    property_obj.market_total_value = financial_data.get("market_total_value")
    property_obj.tax_amount = financial_data.get("tax_amount")
    property_obj.tax_year = financial_data.get("tax_year")

    session.commit()
    return property_id

def link_owner_to_property(session, owner_id: str, property_id: str):
    link = session.query(OwnerProperty).filter_by(
        owner_id=owner_id,
        property_id=property_id
    ).first()
    if not link:
        session.add(OwnerProperty(owner_id=owner_id, property_id=property_id))
        session.commit()

def process_attom_id(attom_id: int):
    session = Session()
    try:
        # Get enriched owner & financial data
        owner_data = get_owner_details(attom_id)
        if not owner_data:
            print(f"Skipping attom_id={attom_id}: no owner data")
            return

        financial_data = get_property_financial_details(attom_id)
        if not financial_data:
            print(f"Skipping attom_id={attom_id}: no financial data")
            return

        # Insert/update property
        property_id = insert_or_update_property(session, financial_data)

        # Process owners (could be multiple)
        owner_block = owner_data.get("owner", {})
        for key in ["owner1", "owner3"]:
            owner = owner_block.get(key, {})
            full_name = owner.get("fullname")
            mailing_address = owner_block.get("mailingaddressoneline")

            if full_name and mailing_address:
                owner_id = insert_or_get_owner(session, full_name, mailing_address)
                link_owner_to_property(session, owner_id, property_id)
    finally:
        session.close()
