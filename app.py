from flask import Flask, jsonify, request
from db import Session, Owner, Property, OwnerProperty
from serialization import serialize_owner

app = Flask(__name__)

@app.route("/owners", methods=["GET"])
def get_owners():
    session = Session()
    try:
        name = request.args.get("name")
        state = request.args.get("state")
        min_net_worth = request.args.get("min_net_worth", type=float)

        query = session.query(Owner)

        if name:
            query = query.filter(Owner.full_name.ilike(f"%{name}%"))
        if state:
            query = query.filter(Owner.mailing_address.ilike(f"%{state}%"))
        if min_net_worth:
            query = query.filter(Owner.estimated_net_worth >= min_net_worth)

        owners = query.all()

        response = []
        for owner in owners:
            # Join on properties
            property_ids = session.query(OwnerProperty.property_id).filter_by(owner_id=owner.id)
            props = session.query(Property).filter(Property.id.in_(property_ids)).all()
            response.append(serialize_owner(owner, props))

        return jsonify(response)
    finally:
        session.close()

@app.route("/owners/<owner_id>")
def get_owner(owner_id):
    session = Session()
    try:
        owner = session.query(Owner).get(owner_id)
        if not owner:
            return jsonify({"error": "Not found"}), 404

        property_ids = session.query(OwnerProperty.property_id).filter_by(owner_id=owner.id)
        props = session.query(Property).filter(Property.id.in_(property_ids)).all()

        return jsonify(serialize_owner(owner, props))
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
