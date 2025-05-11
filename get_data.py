from attom_client import get_properties, get_owner_details

# Example usage
properties = get_properties("82009", "COMMERCIAL (NEC)")
print(f"Fetched {len(properties)} properties.")

for prop in properties:
    attom_id = prop["identifier"]["attomId"]
    owner_data = get_owner_details(attom_id)

    if owner_data:
        owner = owner_data.get("owner", {})
        print(f"Property at {owner_data['address']['oneLine']}")
        print(f" - Owner1: {owner.get('owner1', {}).get('fullname')}")
        print(f" - Mailing Address: {owner.get('mailingaddressoneline')}")
