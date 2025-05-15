def serialize_property(prop):
    return {
        "id": prop.id,
        "address": prop.site_address,
        "city": prop.city,
        "state": prop.state,
        "zipCode": prop.zip_code,
        "coordinates": {
            "lat": prop.latitude,
            "lng": prop.longitude
        },
        "value": prop.avm_value or prop.market_total_value or 0,
        "size": None,  # Fill in if you store sqft or lot size
        "images": [],  # Optional: extend later
    }

def serialize_owner(owner, properties=None):
    return {
        "id": owner.id,
        "name": owner.full_name,
        # "type": owner.type or "individual",
        # "estimatedNetWorth": owner.estimated_net_worth or 0,
        # "confidenceLevel": owner.confidence_level or "low",
        # "wealthComposition": owner.wealth_composition or {
        #     "realEstate": 0,
        #     "stocks": 0,
        #     "cash": 0,
        #     "other": 0,
        # },
        "properties": [serialize_property(p) for p in properties] if properties else []
        # "lastUpdated": owner.last_updated.isoformat() if owner.last_updated else None
    }
