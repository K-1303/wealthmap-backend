from typing import List
from db import Property
from datetime import datetime

class WealthRule:
    """Base class for wealth estimation rules."""
    def applies(self, properties: List[Property]) -> bool:
        raise NotImplementedError
    def get_multiplier(self) -> float:
        raise NotImplementedError

class MinPropertiesRule(WealthRule):
    """Boost for owners with portfolio ≥ 3 properties."""
    def applies(self, properties: List[Property]) -> bool:
        return len(properties) >= 3

    def get_multiplier(self) -> float:
        return 1.15


class HighAverageAVMRule(WealthRule):
    """AVM average > $1M indicates high net worth."""
    def applies(self, properties: List[Property]) -> bool:
        avms = [p.avm_value for p in properties if p.avm_value]
        return len(avms) > 0 and (sum(avms) / len(avms)) > 1_000_000

    def get_multiplier(self) -> float:
        return 1.25


class MultiStateOwnershipRule(WealthRule):
    """Owner owns property in more than one U.S. state."""
    def applies(self, properties: List[Property]) -> bool:
        return len({p.state for p in properties if p.state}) > 1

    def get_multiplier(self) -> float:
        return 1.20


class HasCommercialPropertyRule(WealthRule):
    """Presence of any commercial-type property boosts score."""
    def applies(self, properties: List[Property]) -> bool:
        return any("COMMERCIAL" in (p.propertytype or "") for p in properties)

    def get_multiplier(self) -> float:
        return 1.30


class RecentTransactionRule(WealthRule):
    """Property sold in the last year signals activity + liquidity."""
    def applies(self, properties: List[Property]) -> bool:
        today = datetime.utcnow()
        for p in properties:
            if p.sale_date:
                try:
                    sale_dt = datetime.strptime(p.sale_date, "%Y-%m-%d")
                    if (today - sale_dt).days < 365:
                        return True
                except Exception:
                    continue
        return False

    def get_multiplier(self) -> float:
        return 1.10
    
class HighPropertyTaxRule(WealthRule):
    """Annual taxes > $15,000 indicate high-value property (common in NY, CA)."""
    def applies(self, properties: List[Property]) -> bool:
        return any((p.tax_amount or 0) > 15000 for p in properties)

    def get_multiplier(self) -> float:
        return 1.25


class LuxuryZipRule(WealthRule):
    """Owner has a property in a 'rich' ZIP code."""
    LUXURY_ZIPS = {"90210", "10007", "10065", "33109", "94027", "30327"}

    def applies(self, properties: List[Property]) -> bool:
        return any((p.zip_code or "") in self.LUXURY_ZIPS for p in properties)

    def get_multiplier(self) -> float:
        return 1.35


class LargeHomeRule(WealthRule):
    """Home size > 4000 sqft is a strong luxury signal even in low-tax states."""
    def applies(self, properties: List[Property]) -> bool:
        return any((p.size or 0) > 4000 for p in properties)

    def get_multiplier(self) -> float:
        return 1.20


class OlderLuxuryHomeRule(WealthRule):
    """Built before 1950 and still maintained means legacy wealth."""
    def applies(self, properties: List[Property]) -> bool:
        return any((p.year_built or 9999) < 1950 for p in properties)

    def get_multiplier(self) -> float:
        return 1.15


class HighConfidenceAVMRule(WealthRule):
    """AVM model score > 90 means reliable data and stable home estimate."""
    def applies(self, properties: List[Property]) -> bool:
        return any((p.avm_score or 0) >= 90 for p in properties)

    def get_multiplier(self) -> float:
        return 1.10


class LuxuryStateRule(WealthRule):
    """Certain U.S. states are disproportionately high-wealth in real estate."""
    LUX_STATES = {"CA", "NY", "FL", "NJ", "MA", "CT", "DC", "WA"}

    def applies(self, properties: List[Property]) -> bool:
        return any((p.state or "").upper() in self.LUX_STATES for p in properties)

    def get_multiplier(self) -> float:
        return 1.15

