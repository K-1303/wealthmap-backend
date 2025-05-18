from typing import List
from db import Property, Owner, OwnerProperty, Session
from datetime import datetime
from rules import (
    MinPropertiesRule, HighAverageAVMRule,
    HasCommercialPropertyRule, MultiStateOwnershipRule,
    RecentTransactionRule
)

RULES = [
    MinPropertiesRule(),
    HighAverageAVMRule(),
    MultiStateOwnershipRule(),
    HasCommercialPropertyRule(),
    RecentTransactionRule(),
]

def estimate_property_value(p: Property):
    return max(
        p.avm_value or 0,
        p.market_total_value or 0,
        p.sale_amount or 0,
        p.assessed_total_value or 0
    )

def compute_owner_wealth(owner_id: str):
    session = Session()
    try:
        owner = session.query(Owner).get(owner_id)
        if not owner:
            return

        property_links = session.query(OwnerProperty).filter_by(owner_id=owner_id).all()
        property_ids = [pl.property_id for pl in property_links]
        properties = session.query(Property).filter(Property.id.in_(property_ids)).all()

        base_value = sum(estimate_property_value(p) for p in properties)
        multiplier = 1.0

        active_rules = []
        for rule in RULES:
            if rule.applies(properties):
                multiplier *= rule.get_multiplier()
                active_rules.append(rule.__class__.__name__)

        inferred_real_estate_wealth = base_value * multiplier
        estimated_net_worth = inferred_real_estate_wealth * 2.0  # Conservative boost for non-RE wealth

        # Confidence based on rule count
        confidence = (
            "high" if len(active_rules) >= 4 else
            "medium" if len(active_rules) >= 2 else
            "low"
        )

        # Update DB
        owner.estimated_net_worth = estimated_net_worth
        owner.confidence_level = confidence
        owner.last_updated = datetime.utcnow()
        session.commit()

        return {
            "owner_id": owner_id,
            "estimated_net_worth": estimated_net_worth,
            "confidence_level": confidence,
            "base_value": base_value,
            "multiplier": multiplier,
            "rules_triggered": active_rules
        }

    finally:
        session.close()
