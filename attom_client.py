import os
import time
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

ATTOM_API_KEY = os.getenv("ATTOM_API_KEY")
BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"

HEADERS = {
    "Accept": "application/json",
    "apikey": ATTOM_API_KEY
}


def get_properties(postalcode: str, propertytype: str, pagesize: int = 100) -> List[Dict]:
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


def get_owner_details(attom_id: int) -> Dict:
    url = f"{BASE_URL}/property/detailowner"
    params = {"attomid": attom_id}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch owner data for attomid={attom_id}: {response.text}")
        return {}

    data = response.json()
    if "property" not in data or not data["property"]:
        return {}

    return data["property"][0]
