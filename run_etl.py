from attom_client import get_properties
from etl import process_attom_id
from db import create_tables
import time
import os
from dotenv import load_dotenv

load_dotenv()

def process_zip_and_type(zipcode: str, propertytype: str, delay: float = 1.5, limit: int = 50):
    print(f"Fetching {limit} properties in {zipcode} [{propertytype}]...")
    properties = get_properties(zipcode, propertytype)
    if not properties:
        print("No properties found.")
        return

    for i, prop in enumerate(properties[:limit]):
        attom_id = prop.get("identifier", {}).get("attomId")
        if not attom_id:
            continue
        print(f"[{i+1}/{limit}] Processing Attom ID: {attom_id}")
        process_attom_id(attom_id)
        time.sleep(delay)

if __name__ == "__main__":
    # Uncomment on first run
    create_tables()

    jobs = [
        ("90210", "RESIDENTIAL (NEC)"),
        ("90210", "COMMERCIAL (NEC)"),
        # ("90210", "CONDOMINIUM"),
        # ("90210", "APARTMENT"),
        # ("90210", "DUPLEX/TRIPLEX"),
        # ("90210", "INDUSTRIAL"),
        # ("90210", "MOBILE HOME"),
        # ("90210", "VACANT LAND"),
    ]

    for zipcode, propertytype in jobs:
        process_zip_and_type(zipcode, propertytype, delay=2.0, limit=50)

    print("All jobs completed.")
