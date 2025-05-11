import uuid
from db import Session, Owner, Property, OwnerProperty

def normalize_name(name: str) -> str:
    return name.upper().strip() if name else None

def normalize_address(addr: str) -> str:
    return addr.upper().strip() if addr else None

def insert_owner(session, full_name: str, mailing_address: str):
    full_name = normalize_name(full_name)
    mailing_address = normalize_address(mailing_address)

    owner = session.query(Owner).filter_by(full_name=full_name, mailing_address=mailing_address).first()
    if owner:
        return owner.id

    owner_id = str(uuid.uuid4())
    owner = Owner(id=owner_id, full_name=full_name, mailing_address=mailing_address)
    session.add(owner)
    session.commit()
    return owner_id

def insert_property(session, prop_data):
    attom_id = prop_data["identifier"]["attomId"]
    existing = session.query(Property).filter_by(attom_id=attom_id).first()
    if existing:
        return existing.id

    prop_id = str(uuid.uuid4())
    addr = prop_data.get("address", {})
    summary = prop_data.get("summary", {})
    size = prop_data.get("building", {}).get("size", {})
    rooms = prop_data.get("building", {}).get("rooms", {})

    prop = Property(
        id=prop_id,
        attom_id=attom_id,
        apn=prop_data["identifier"].get("apn"),
        site_address=addr.get("oneLine"),
        city=addr.get("locality"),
        state=addr.get("countrySubd"),
        zip_code=addr.get("postal1"),
        year_built=summary.get("yearbuilt"),
        sqft=size.get("livingsize"),
        bedrooms=rooms.get("beds"),
        bathrooms=rooms.get("bathstotal")
    )
    session.add(prop)
    session.commit()
    return prop_id

def link_owner_to_property(session, owner_id, property_id):
    link = session.query(OwnerProperty).filter_by(owner_id=owner_id, property_id=property_id).first()
    if not link:
        session.add(OwnerProperty(owner_id=owner_id, property_id=property_id))
        session.commit()
