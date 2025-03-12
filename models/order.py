from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, time

@dataclass
class DeliveryWindow:
    start: time
    end: time

@dataclass
class PackageDetails:
    weight_kg: float
    dimensions: str
    fragile: bool

@dataclass
class Order:
    order_id: str
    customer_name: str
    address: str
    delivery_window: DeliveryWindow
    package_details: PackageDetails
    priority: str  # standard, express, priority
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        """Create an Order instance from a dictionary."""
        start_time = datetime.strptime(data["delivery_window"]["start"], "%H:%M").time()
        end_time = datetime.strptime(data["delivery_window"]["end"], "%H:%M").time()
        
        return cls(
            order_id=data["order_id"],
            customer_name=data["customer_name"],
            address=data["address"],
            delivery_window=DeliveryWindow(start=start_time, end=end_time),
            package_details=PackageDetails(
                weight_kg=data["package_details"]["weight_kg"],
                dimensions=data["package_details"]["dimensions"],
                fragile=data["package_details"]["fragile"]
            ),
            priority=data["priority"]
        ) 