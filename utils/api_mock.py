import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

def load_mock_data() -> Dict[str, Any]:
    """Load mock data for various APIs and systems."""
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # If data directory doesn't exist, generate mock data
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        return generate_mock_data(data_path)
    
    # Try to load existing data, generate if files don't exist
    try:
        orders = json.load(open(os.path.join(data_path, "mock_orders.json")))
        vehicles = json.load(open(os.path.join(data_path, "mock_vehicles.json")))
        weather = json.load(open(os.path.join(data_path, "mock_weather.json")))
        traffic = json.load(open(os.path.join(data_path, "mock_traffic.json")))
        
        return {
            "orders": orders,
            "vehicles": vehicles,
            "weather": weather,
            "traffic": traffic
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return generate_mock_data(data_path)

def generate_mock_data(data_path: str) -> Dict[str, Any]:
    """Generate mock data for the system."""
    # Generate mock orders
    orders = []
    addresses = [
        "123 Main St, Springfield, IL", 
        "456 Elm Ave, Riverdale, NY", 
        "789 Oak Dr, Lakeside, CA",
        "321 Pine Rd, Mountainview, CO",
        "654 Maple Ln, Oceanside, FL",
        "987 Cedar Ct, Hillside, TX",
        "741 Birch Way, Valleytown, PA",
        "852 Spruce Blvd, Desertville, AZ",
        "963 Walnut St, Forestcity, OR",
        "159 Cherry Ave, Plainsville, OH"
    ]
    
    for i in range(10):
        order_time = datetime.now() + timedelta(hours=random.randint(1, 8))
        orders.append({
            "order_id": f"ORD-{1000+i}",
            "customer_name": f"Customer {i+1}",
            "address": random.choice(addresses),
            "delivery_window": {
                "start": (order_time - timedelta(hours=1)).strftime("%H:%M"),
                "end": (order_time + timedelta(hours=1)).strftime("%H:%M")
            },
            "package_details": {
                "weight_kg": round(random.uniform(0.5, 20.0), 1),
                "dimensions": f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(10, 30)} cm",
                "fragile": random.choice([True, False])
            },
            "priority": random.choice(["standard", "express", "priority"])
        })
    
    # Generate mock vehicles
    vehicles = []
    for i in range(5):
        maintenance_due = random.choice([True, False])
        vehicles.append({
            "vehicle_id": f"VEH-{100+i}",
            "type": random.choice(["van", "truck", "delivery car"]),
            "driver_name": f"Driver {i+1}",
            "current_location": {
                "latitude": round(random.uniform(40.0, 42.0), 6),
                "longitude": round(random.uniform(-74.0, -72.0), 6),
                "address": "En route" if random.choice([True, False]) else "At depot"
            },
            "status": random.choice(["active", "loading", "maintenance", "returning"]),
            "fuel_level": random.randint(20, 100),
            "maintenance": {
                "last_service": (datetime.now() - timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d"),
                "next_service_due": (datetime.now() + timedelta(days=random.randint(-10, 30) if maintenance_due else random.randint(30, 90))).strftime("%Y-%m-%d"),
                "issues": ["Engine check light on", "Brake pads worn"] if maintenance_due and random.choice([True, False]) else []
            },
            "capacity": {
                "weight_kg": random.randint(500, 2000),
                "volume_m3": random.randint(5, 20)
            }
        })
    
    # Generate mock weather data
    cities = ["Springfield", "Riverdale", "Lakeside", "Mountainview", "Oceanside"]
    weather_conditions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Foggy", "Partly Cloudy", "Clear"]
    weather = {city: {
        "condition": random.choice(weather_conditions),
        "temperature_c": random.randint(5, 35),
        "wind_speed_kmh": random.randint(0, 50),
        "precipitation_mm": round(random.uniform(0, 25), 1) if "Rain" in weather_conditions else 0,
        "forecast": [
            {
                "time": (datetime.now() + timedelta(hours=i)).strftime("%H:%M"),
                "condition": random.choice(weather_conditions),
                "temperature_c": random.randint(5, 35)
            } for i in range(1, 13, 3)
        ]
    } for city in cities}
    
    # Generate mock traffic data
    roads = ["Main Highway", "Route 66", "Interstate 95", "Central Expressway", "Coastal Road"]
    traffic = {road: {
        "congestion_level": random.randint(1, 10),
        "average_speed_kmh": random.randint(20, 110),
        "incidents": [
            {
                "type": random.choice(["accident", "construction", "road closure"]),
                "location": f"Km {random.randint(10, 50)}",
                "impact": random.choice(["minor", "moderate", "severe"])
            }
        ] if random.random() < 0.3 else [],
        "estimated_delay_minutes": random.randint(0, 45)
    } for road in roads}
    
    # Save generated data
    with open(os.path.join(data_path, "mock_orders.json"), "w") as f:
        json.dump(orders, f, indent=2)
    
    with open(os.path.join(data_path, "mock_vehicles.json"), "w") as f:
        json.dump(vehicles, f, indent=2)
    
    with open(os.path.join(data_path, "mock_weather.json"), "w") as f:
        json.dump(weather, f, indent=2)
    
    with open(os.path.join(data_path, "mock_traffic.json"), "w") as f:
        json.dump(traffic, f, indent=2)
    
    return {
        "orders": orders,
        "vehicles": vehicles,
        "weather": weather,
        "traffic": traffic
    } 