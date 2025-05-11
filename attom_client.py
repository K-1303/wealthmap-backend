import os
import time
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

ATTOM_API_KEY = os.getenv("ATTOM_API_KEY")
BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

HEADERS = {
    "Accept": "application/json",
    "apikey": ATTOM_API_KEY
}

def get_properties(postalcode: str, propertytype: str, pagesize: int = 100) -> List[Dict]:
    """Fetches a list of basic properties based on postal code and property type."""
    all_properties = []
    page = 1
    while True:
        url = f"{BASE_URL}/property/address"
        params = {
            "postalcode": postalcode,
            "propertytype": propertytype,
            "page": page,
            "pagesize": pagesize
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch properties: {response.text}")
            break

        data = response.json()
        props = data.get("property", [])
        if not props:
            break

        all_properties.extend(props)

        total = data["status"]["total"]
        if len(all_properties) >= total:
            break

        page += 1
        time.sleep(0.5)
    print(f"Fetched {len(all_properties)} properties in total.")
    print(all_properties)
    return all_properties

def get_owner_details(attom_id: int) -> Optional[Dict]:
    """Fetches detailed owner information for a given Attom ID."""
    url = f"{BASE_URL}/property/detailowner"
    params = {"attomid": attom_id}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch owner data for attomid={attom_id}: {response.text}")
        return None

    data = response.json()
    return data.get("property", [{}])[0]

def get_property_financial_details(attom_id: int) -> Optional[Dict]:
    """Fetches detailed property valuation, sale, and assessment data."""
    url = f"{BASE_URL}/allevents/detail"
    params = {"id": attom_id}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch financial data for attomid={attom_id}: {response.text}")
        return None

    data = response.json()
    property_data = data.get("property", [{}])[0]

    # Extract AVM
    avm = property_data.get("avm", {})
    avm_amount = avm.get("amount", {})
    avm_details = {
        "avm_value": avm_amount.get("value"),
        "avm_low": avm_amount.get("low"),
        "avm_high": avm_amount.get("high"),
        "avm_score": avm_amount.get("scr"),
        "avm_last_updated": avm.get("eventDate")
    }

    # Extract Sale
    sale = property_data.get("sale", {})
    sale_amount = sale.get("amount", {})
    sale_details = {
        "sale_amount": sale_amount.get("saleamt"),
        "sale_date": sale.get("saleTransDate"),
        "sale_type": sale.get("saletranstype")
    }

    # Extract Assessment
    assessment = property_data.get("assessment", {})
    assessed = assessment.get("assessed", {})
    market = assessment.get("market", {})
    tax = assessment.get("tax", {})
    assessment_details = {
        "assessed_total_value": assessed.get("assdttlvalue"),
        "market_total_value": market.get("mktttlvalue"),
        "tax_amount": tax.get("taxamt"),
        "tax_year": tax.get("taxyear")
    }

    # Combine all data
    return {
        "attom_id": attom_id,
        "address": property_data.get("address", {}).get("oneLine"),
        "city": property_data.get("address", {}).get("locality"),
        "state": property_data.get("address", {}).get("countrySubd"),
        "zip_code": property_data.get("address", {}).get("postal1"),
        **avm_details,
        **sale_details,
        **assessment_details
    }
