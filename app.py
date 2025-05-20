from flask import Flask, jsonify, request
from db import Session, Owner, Property, OwnerProperty
from flask_cors import CORS

app = Flask(__name__)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://wealth-map-1.onrender.com"]}})

@app.route("/properties", methods=["GET"])
def get_properties():
    session = Session()
    try:
        # Query all properties from the database
        properties = session.query(Property).all()
        # Return the data as JSON
        return jsonify([
            {
                "id": prop.id,
                "address": prop.site_address,
                "city": prop.city,
                "state": prop.state,
                "zip_code": prop.zip_code,
                "value": max(prop.avm_value or 0, prop.market_total_value or 0, prop.sale_amount or 0, prop.assessed_total_value or 0),
                "size": prop.size,
                "images": ["https://images.pexels.com/photos/1029599/pexels-photo-1029599.jpeg"],
                "coordinates": {
                    "lat": prop.latitude,
                    "lng": prop.longitude,
                },
                                "owners": [
                    {
                        "id": owner.id,
                        "name": owner.full_name,
                        "estimatedNetWorth": owner.estimated_net_worth,
                        "confidenceLevel": owner.confidence_level,
                    }
                    for owner in session.query(Owner)
                    .join(OwnerProperty, Owner.id == OwnerProperty.owner_id)
                    .filter(OwnerProperty.property_id == prop.id)
                ]
            }
            for prop in properties
        ])
    finally:
        session.close()

@app.route("/properties/<property_id>", methods=["GET"])
def get_property_by_id(property_id):
    session = Session()
    try:
        # Query the property by ID
        property = session.query(Property).filter(Property.id == property_id).first()
        if not property:
            return jsonify({"error": "Property not found"}), 404

        # Query the owners associated with the property
        owners = session.query(Owner).join(OwnerProperty, Owner.id == OwnerProperty.owner_id).filter(OwnerProperty.property_id == property_id).all()

        # Serialize the property details
        property_data = {
            "id": property.id,
            "attom_id": property.attom_id,
            "site_address": property.site_address,
            "address_line1": property.address_line1,
            "address_line2": property.address_line2,
            "city": property.city,
            "state": property.state,
            "zip_code": property.zip_code,
            "propertytype": property.propertytype,
            "year_built": property.year_built,
            "size": property.size,
            "latitude": property.latitude,
            "longitude": property.longitude,
            "sale_amount": property.sale_amount,
            "sale_date": property.sale_date,
            "sale_type": property.sale_type,
            "avm_value": property.avm_value,
            "avm_low": property.avm_low,
            "avm_high": property.avm_high,
            "avm_score": property.avm_score,
            "avm_last_updated": property.avm_last_updated,
            "assessed_total_value": max(property.assessed_total_value or 0, property.market_total_value or 0, property.sale_amount or 0, property.avm_value or 0),
            "market_total_value": property.market_total_value,
            "tax_amount": property.tax_amount,
            "tax_year": property.tax_year,
            "created_at": property.created_at,
        }

        # Serialize the owner details
        owner_data = [
            {
                "id": owner.id,
                "full_name": owner.full_name,
                "mailing_address": owner.mailing_address,
                "type": owner.type,
                "estimated_net_worth": owner.estimated_net_worth,
                "confidence_level": owner.confidence_level,
                "created_at": owner.created_at,
                "last_updated": owner.last_updated,
            }
            for owner in owners
        ]

        # Combine property and owner data
        response_data = {
            "property": property_data,
            "owners": owner_data,
        }

        return jsonify(response_data)
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
