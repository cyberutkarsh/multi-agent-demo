from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Location:
    latitude: float
    longitude: float
    address: str

@dataclass
class MaintenanceInfo:
    last_service: datetime
    next_service_due: datetime
    issues: List[str]

@dataclass
class Capacity:
    weight_kg: float
    volume_m3: float

@dataclass
class Vehicle:
    vehicle_id: str
    type: str
    driver_name: str
    current_location: Location
    status: str  # active, loading, maintenance, returning
    fuel_level: int  # percentage
    maintenance: MaintenanceInfo
    capacity: Capacity
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Vehicle':
        """Create a Vehicle instance from a dictionary."""
        return cls(
            vehicle_id=data["vehicle_id"],
            type=data["type"],
            driver_name=data["driver_name"],
            current_location=Location(
                latitude=data["current_location"]["latitude"],
                longitude=data["current_location"]["longitude"],
                address=data["current_location"]["address"]
            ),
            status=data["status"],
            fuel_level=data["fuel_level"],
            maintenance=MaintenanceInfo(
                last_service=datetime.strptime(data["maintenance"]["last_service"], "%Y-%m-%d"),
                next_service_due=datetime.strptime(data["maintenance"]["next_service_due"], "%Y-%m-%d"),
                issues=data["maintenance"]["issues"]
            ),
            capacity=Capacity(
                weight_kg=data["capacity"]["weight_kg"],
                volume_m3=data["capacity"]["volume_m3"]
            )
        ) 