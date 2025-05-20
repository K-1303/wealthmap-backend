from attom_client import get_properties
from etl import process_attom_id, run_batch_wealth_estimation
import time

def process_zip_and_type(zipcode: str, propertytype: str, delay: float = 1.5, limit: int = 100):
    properties = get_properties(zipcode, propertytype)

    print(f"Fetching {len(properties)} properties in {zipcode} [{propertytype}]...")

    if not properties:
        print("No properties found.")
        return

    for i, prop in enumerate(properties[:limit]):
        attom_id = prop.get("identifier", {}).get("attomId")
        if not attom_id:
            continue
        print(f"{i+1} Processing Attom ID: {attom_id}")
        process_attom_id(attom_id, propertytype)
        time.sleep(delay)

if __name__ == "__main__":
    # Uncomment on first run
    #create_tables()

    jobs = [
        ("90210", "RESIDENTIAL (NEC)"),
        #("90210", "COMMERCIAL (NEC)"),
    ]

    for zipcode, propertytype in jobs:
        process_zip_and_type(zipcode, propertytype, delay=2.0, limit=50)

    print("All jobs completed.")

    # Uncomment to run wealth estimation
    #run_batch_wealth_estimation()
