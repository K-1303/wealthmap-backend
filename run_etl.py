from attom_client import get_properties, get_owner_details
from db import create_tables, Session
from etl import insert_owner, insert_property, link_owner_to_property

def process_zip_and_type(zipcode, propertytype):
    session = Session()
    properties = get_properties(zipcode, propertytype)
    print(f"Fetched {len(properties)} properties for {zipcode} - {propertytype}")

    for prop in properties:
        attom_id = prop["identifier"]["attomId"]
        owner_data = get_owner_details(attom_id)

        if not owner_data:
            continue

        property_id = insert_property(session, owner_data)
        owner_block = owner_data.get("owner", {})

        for owner_key in ["owner1", "owner3"]:
            owner_info = owner_block.get(owner_key, {})
            name = owner_info.get("fullname")
            mailing = owner_block.get("mailingaddressoneline")

            if name and mailing:
                owner_id = insert_owner(session, name, mailing)
                link_owner_to_property(session, owner_id, property_id)

if __name__ == "__main__":
    create_tables()
    process_zip_and_type("82009", "COMMERCIAL (NEC)")
