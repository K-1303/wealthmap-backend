from flask import Flask, jsonify, request
from db import Session, Owner, Property, OwnerProperty
from serialization import serialize_owner
from flask_cors import CORS

app = Flask(__name__)


app = Flask(__name__)
CORS(app, resources={r"/properties": {"origins": "http://localhost:5173"}})

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
                "value": prop.avm_value,
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

#@app.route("/properties/<property_id>", methods=["GET"])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
