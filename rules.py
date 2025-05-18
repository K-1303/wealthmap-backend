from typing import List
from db import Property
from datetime import datetime

class WealthRule:
    """Abstract base class."""
    def applies(self, properties: List[Property]) -> bool:
        raise NotImplementedError

    def get_multiplier(self) -> float:
        raise NotImplementedError


class MinPropertiesRule(WealthRule):
    def applies(self, properties: List[Property]) -> bool:
        return len(properties) >= 3

    def get_multiplier(self) -> float:
        return 1.15


class HighAverageAVMRule(WealthRule):
    def applies(self, properties: List[Property]) -> bool:
        avms = [p.avm_value for p in properties if p.avm_value]
        return len(avms) > 0 and (sum(avms) / len(avms)) > 1_000_000

    def get_multiplier(self) -> float:
        return 1.2


class MultiStateOwnershipRule(WealthRule):
    def applies(self, properties: List[Property]) -> bool:
        return len({p.state for p in properties if p.state}) > 1

    def get_multiplier(self) -> float:
        return 1.25


class HasCommercialPropertyRule(WealthRule):
    def applies(self, properties: List[Property]) -> bool:
        return any("COMMERCIAL" in (p.propertytype or "").upper() for p in properties)

    def get_multiplier(self) -> float:
        return 1.3


class RecentTransactionRule(WealthRule):
    def applies(self, properties: List[Property]) -> bool:
        today = datetime.utcnow()
        for p in properties:
            if p.sale_date:
                try:
                    date = datetime.strptime(p.sale_date, "%Y-%m-%d")
                    if (today - date).days < 365:
                        return True
                except Exception:
                    continue
        return False

    def get_multiplier(self) -> float:
        return 1.1
