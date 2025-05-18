import uuid
from datetime import datetime
from db import Session, Owner, Property, OwnerProperty
from attom_client import get_owner_details, get_property_financial_details
from dotenv import load_dotenv
from wealth_estimator import compute_owner_wealth
from typing import List

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
    owner = Owner(id=owner_id, full_name=full_name, mailing_address=mailing_address)
    session.add(owner)
    session.commit()
    return owner_id

def insert_or_update_property(session, data: dict, propertytype) -> str:
    attom_id = data.get("attom_id")
    property_obj = session.query(Property).filter_by(attom_id=attom_id).first()

    if not property_obj:
        property_id = str(uuid.uuid4())
        property_obj = Property(id=property_id, attom_id=attom_id)
        session.add(property_obj)
    else:
        property_id = property_obj.id

    # Basic Details
    property_obj.site_address = data.get("site_address")
    property_obj.address_line1 = data.get("address_line1")
    property_obj.address_line2 = data.get("address_line2")
    property_obj.city = data.get("city")
    property_obj.state = data.get("state")
    property_obj.zip_code = data.get("zip_code")
    property_obj.latitude = data.get("latitude")
    property_obj.longitude = data.get("longitude")
    property_obj.propertytype = propertytype
    property_obj.size = data.get("size")
    property_obj.year_built = data.get("year_built")

    # Sale
    property_obj.sale_amount = data.get("sale_amount")
    property_obj.sale_date = data.get("sale_date")
    property_obj.sale_type = data.get("sale_type")
    property_obj.sale_date = data.get("sale_date")

    # AVM
    property_obj.avm_value = data.get("avm_value")
    property_obj.avm_low = data.get("avm_low")
    property_obj.avm_high = data.get("avm_high")
    property_obj.avm_score = data.get("avm_score")
    if data.get("avm_last_updated"):
        try:
            property_obj.avm_last_updated = datetime.strptime(data["avm_last_updated"], "%Y-%m-%d")
        except Exception:
            pass

    # Assessment
    property_obj.assessed_total_value = data.get("assessed_total_value")
    property_obj.market_total_value = data.get("market_total_value")
    property_obj.tax_amount = data.get("tax_amount")
    property_obj.tax_year = data.get("tax_year")

    session.commit()
    return property_id

def link_owner_to_property(session, owner_id: str, property_id: str):
    link = session.query(OwnerProperty).filter_by(owner_id=owner_id, property_id=property_id).first()
    if not link:
        session.add(OwnerProperty(owner_id=owner_id, property_id=property_id))
        session.commit()

def process_attom_id(attom_id: int, propertytype) -> List[str]:
    session = Session()
    updated_owners = set()

    try:
        owner_data = get_owner_details(attom_id)
        if not owner_data:
            print(f"Skipping attom_id={attom_id}: no owner data")
            return []

        financial_data = get_property_financial_details(attom_id)
        if not financial_data:
            print(f"Skipping attom_id={attom_id}: no financial data")
            return []

        property_id = insert_or_update_property(session, financial_data, propertytype)

        owner_block = owner_data.get("owner", {})
        mailing_address = normalize_address(owner_block.get("mailingaddressoneline"))

        if not mailing_address:
            print(f"Skipping attom_id={attom_id}: missing mailing address")
            return []

        # Loop through all keys that start with "owner" and have a fullname
        for key, value in owner_block.items():
            if key.startswith("owner") and isinstance(value, dict):
                full_name = normalize_name(value.get("fullname"))
                if full_name:
                    owner_id = insert_or_get_owner(session, full_name, mailing_address)
                    link_owner_to_property(session, owner_id, property_id)
                    updated_owners.add(owner_id)

        session.close()  # Close this session early to avoid locking issues

        # Compute wealth
        for oid in updated_owners:
            result = compute_owner_wealth(oid)

        return list(updated_owners)

    except Exception as e:
        print(f"Error processing attom_id={attom_id}: {e}")
        return []

    finally:
        if session:
            session.close()


