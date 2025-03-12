from typing import Dict, Any, List
import anthropic
import os
import json
import random
from datetime import datetime, timedelta
from langgraph.graph import END

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

def route_optimizer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent specialized in optimizing delivery routes based on orders,
    traffic conditions, and weather data.
    """
    input_text = state["input"]
    context = state["context"]
    role = context.get("role", "unknown")
    history = context.get("conversation_history", [])
    mock_data = context.get("mock_data", {})
    
    # Create system message content
    system_message = """You are an advanced route optimization agent for a supply chain system.
    
    Your capabilities include:
    - Analyzing delivery orders and generating optimal routes
    - Considering traffic conditions, weather, and time windows
    - Providing ETAs and turn-by-turn directions
    - Adjusting routes based on real-time conditions
    
    You have access to vehicle data, order information, and external APIs.
    Respond as if you're actively processing and optimizing routes.
    
    When generating routes, include realistic stops with addresses, ETAs, and any relevant details.
    """
    
    # Prepare the messages for Claude (without system message)
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
        - Orders: {len(mock_data.get('orders', []))} delivery orders
        - Vehicles: {len(mock_data.get('vehicles', []))} vehicles in fleet
        - Weather: Current conditions available
        - Traffic: Real-time traffic data available
        
        Please respond with optimized routes or relevant information.
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
    
    # Determine next step - data retriever, notification, or end
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