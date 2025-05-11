from attom_client import get_properties
from etl import process_attom_id
from db import create_tables
import time
import os
from dotenv import load_dotenv

load_dotenv()

def process_zip_and_type(zipcode: str, propertytype: str, delay: float = 1.0):
    print(f"Fetching properties in {zipcode} [{propertytype}]...")
    properties = get_properties(zipcode, propertytype)

    print(f"🔍 Found {len(properties)} properties. Processing each Attom ID...")
    for i, prop in enumerate(properties):
        attom_id = prop.get("identifier", {}).get("attomId")
        if not attom_id:
            continue
        print(f"[{i+1}/{len(properties)}] Processing Attom ID: {attom_id}")
        process_attom_id(attom_id)
        time.sleep(delay)

if __name__ == "__main__":
    #print("Creating tables if they don't exist...")
    #create_tables()

    # Example ZIP + property type combos for batch processing
    jobs = [
        ("82009", "COMMERCIAL (NEC)"),
    ]

    for zipcode, propertytype in jobs:
        process_zip_and_type(zipcode, propertytype)

    print("All done.")
