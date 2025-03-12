from typing import Dict, Any, List
import anthropic
import os
import json
import random
from datetime import datetime
from langgraph.graph import END

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

def data_retriever_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent specialized in retrieving external data like weather conditions,
    traffic information, and other relevant environmental factors.
    """
    input_text = state["input"]
    context = state["context"]
    mock_data = context.get("mock_data", {})
    
    # Extract weather and traffic data from mock data
    weather_data = mock_data.get("weather", {})
    traffic_data = mock_data.get("traffic", {})
    
    # Create system message content
    system_message = """You are a data retrieval agent that specializes in getting real-time weather,
    traffic, and other environmental data relevant to delivery routes.
    
    When presented with a request, you should:
    1. Identify what data is being requested
    2. Access the relevant mock APIs
    3. Format the data in a useful way for route optimization or fleet monitoring
    
    Respond as if you're actively fetching this data from real APIs.
    """
    
    # Prepare messages array (without system message)
    messages = [
        {
            "role": "user",
            "content": f"""I need the following data based on this request: {input_text}
            
            Available mock data:
            - Weather: {json.dumps(weather_data, indent=2)}
            - Traffic: {json.dumps(traffic_data, indent=2)}
            
            Please retrieve and format the relevant information.
            """
        }
    ]
    
    # Get response from Claude
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        system=system_message,
        messages=messages
    )
    
    content = response.content[0].text
    
    # Update context with the retrieved data
    context["retrieved_data"] = {
        "timestamp": datetime.now().isoformat(),
        "content": content,
        "type": "weather" if "weather" in input_text.lower() else "traffic" if "traffic" in input_text.lower() else "general"
    }
    
    # Store output in context for the main app to retrieve
    context["messages"] = context.get("messages", []) + [{"role": "assistant", "content": content}]
    
    # Determine next agent based on request origin
    from_agent = context.get("next_agent", "")
    next_agent = END  # Default to END
    
    return {
        "input": content,
        "context": context,
        "next": next_agent
    } 