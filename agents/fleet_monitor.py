from typing import Dict, Any, List
import anthropic
import os
import json
import random
from datetime import datetime, timedelta
from langgraph.graph import END

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

def fleet_monitor_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent specialized in monitoring fleet status, vehicle maintenance,
    and driver performance.
    """
    input_text = state["input"]
    context = state["context"]
    role = context.get("role", "unknown")
    history = context.get("conversation_history", [])
    mock_data = context.get("mock_data", {})
    
    # Extract vehicle data from mock data
    vehicles = mock_data.get("vehicles", [])
    
    # Create detailed fleet summary if requested
    if "summary" in input_text.lower() or "status" in input_text.lower() or "overview" in input_text.lower():
        fleet_summary = create_fleet_summary(vehicles)
        input_text = f"{input_text}\n\nHere's the current fleet data:\n{fleet_summary}"
    
    # Create system message content
    system_message = """You are an intelligent fleet monitoring agent for a supply chain system.
    
    Your capabilities include:
    - Tracking real-time location and status of all vehicles
    - Monitoring maintenance needs and scheduling service
    - Analyzing driver performance and compliance
    - Generating reports on fleet operations
    
    You have access to telematics data, maintenance records, and driver logs.
    Use the mock fleet data provided to give specific and detailed responses.
    """
    
    # Prepare messages array (without system message)
    messages = []
    
    # Add conversation history
    for entry in history[-5:]:  # Last 5 exchanges for context
        messages.append({
            "role": "user" if entry["role"] == "user" else "assistant",
            "content": entry["content"]
        })
    
    # Add current request with context
    messages.append({
        "role": "user", 
        "content": f"""User role: {role}
        User request: {input_text}
        
        Available mock data:
        - Vehicles: {len(mock_data.get('vehicles', []))} vehicles in fleet
        - Maintenance records: Available for all vehicles
        - Real-time locations: GPS tracking active
        - Driver logs: Performance metrics available
        
        Please respond with fleet status or relevant information.
        """
    })
    
    # Get response from Claude
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        system=system_message,
        messages=messages
    )
    
    content = response.content[0].text
    
    # Determine if we need to fetch additional data or send notifications
    if "weather" in input_text.lower() or "traffic" in input_text.lower():
        next_agent = "data_retriever"
    elif "notify" in input_text.lower() or "alert" in input_text.lower() or "send" in input_text.lower():
        next_agent = "notification"
    else:
        next_agent = END
    
    # Set output or pass input to next agent
    if next_agent == END:
        # Store output in context for the main app to retrieve
        context["messages"] = context.get("messages", []) + [{"role": "assistant", "content": content}]
    
    return {
        "input": content if next_agent != END else input_text,
        "context": context,
        "next": next_agent
    }

def create_fleet_summary(vehicles):
    """Create a text summary of fleet status from mock vehicle data."""
    if not vehicles:
        return "No vehicle data available"
    
    # Count vehicles by status
    status_counts = {}
    for vehicle in vehicles:
        status = vehicle.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Count vehicles by type
    type_counts = {}
    for vehicle in vehicles:
        v_type = vehicle.get("type", "unknown")
        type_counts[v_type] = type_counts.get(v_type, 0) + 1
    
    # Count maintenance issues
    maintenance_needed = 0
    for vehicle in vehicles:
        if vehicle.get("maintenance", {}).get("issues", []):
            maintenance_needed += 1
    
    # Generate summary
    summary = f"""
    Fleet Summary:
    - Total vehicles: {len(vehicles)}
    - Status breakdown: {', '.join([f"{k}: {v}" for k, v in status_counts.items()])}
    - Vehicle types: {', '.join([f"{k}: {v}" for k, v in type_counts.items()])}
    - Vehicles needing maintenance: {maintenance_needed}
    
    Individual vehicle details:
    """
    
    # Add individual vehicle details
    for i, vehicle in enumerate(vehicles):
        if i >= 5:  # Limit to first 5 vehicles to avoid long text
            summary += f"- ... and {len(vehicles) - 5} more vehicles"
            break
            
        v_id = vehicle.get("vehicle_id", "unknown")
        v_type = vehicle.get("type", "unknown")
        v_status = vehicle.get("status", "unknown")
        v_driver = vehicle.get("driver_name", "unknown")
        v_location = vehicle.get("current_location", {}).get("address", "unknown")
        v_issues = vehicle.get("maintenance", {}).get("issues", [])
        
        summary += f"""
    - {v_id} ({v_type}): 
      Driver: {v_driver}
      Status: {v_status}
      Location: {v_location}
      Issues: {', '.join(v_issues) if v_issues else "None"}
        """
    
    return summary 