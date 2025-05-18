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

def get_properties(postalcode: str, propertytype: str = "ALL", pagesize: int = 100) -> List[Dict]:
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

    return all_properties

def get_owner_details(attom_id: int) -> Optional[Dict]:
    url = f"{BASE_URL}/property/detailowner"
    params = {"attomid": attom_id}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Owner data fetch failed: {response.status_code} → {response.text}")
        return None

    data = response.json()
    return data.get("property", [{}])[0]

def get_property_financial_details(attom_id: int) -> Optional[Dict]:
    url = f"{BASE_URL}/allevents/detail"
    params = {"id": attom_id}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Financial data fetch failed: {response.status_code} → {response.text}")
        return None

    data = response.json()
    prop = data.get("property", [{}])[0]
    addr = prop.get("address", {})
    avm = prop.get("avm", {}).get("amount", {})
    sale = prop.get("sale", {}).get("amount", {})
    assessment = prop.get("assessment", {})
    assessed = assessment.get("assessed", {})
    market = assessment.get("market", {})
    tax = assessment.get("tax", {})
    building = prop.get("building", {})
    size_info = building.get("size", {})
    summary = prop.get("summary", {})

    return {
        "attom_id": prop["identifier"]["attomId"],

        # Basic Details
        "site_address": addr.get("oneLine"),
        "address_line1": addr.get("line1"),
        "address_line2": addr.get("line2"),
        "city": addr.get("locality"),
        "state": addr.get("countrySubd"),
        "zip_code": addr.get("postal1"),
        "latitude": float(prop.get("location", {}).get("latitude", 0)),
        "longitude": float(prop.get("location", {}).get("longitude", 0)),
        "size": size_info.get("livingsize") or size_info.get("bldgsize"),
        "year_built": summary.get("yearbuilt"),

        # Sale
        "sale_amount": sale.get("saleamt"),
        "sale_date": prop.get("sale", {}).get("saleTransDate"),
        "sale_type": prop.get("sale", {}).get("saletranstype"),
        "sale_date": prop.get("sale", {}).get("saleTransDate"),

        # AVM
        "avm_value": avm.get("value"),
        "avm_low": avm.get("low"),
        "avm_high": avm.get("high"),
        "avm_score": avm.get("scr"),
        "avm_last_updated": prop.get("avm", {}).get("eventDate"),

        # Assessment
        "assessed_total_value": assessed.get("assdttlvalue"),
        "market_total_value": market.get("mktttlvalue"),
        "tax_amount": tax.get("taxamt"),
        "tax_year": tax.get("taxyear"),
    }

