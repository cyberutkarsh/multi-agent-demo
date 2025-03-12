from typing import Dict, Any, List
import anthropic
import os

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

def coordinator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Central coordinator agent that directs requests to specialized agents.
    """
    input_text = state["input"]
    context = state["context"]
    role = context.get("role", "unknown")
    history = context.get("conversation_history", [])
    
    # Create system message content
    system_message = """You are an intelligent supply chain coordination assistant.
    Your job is to understand the user's request and determine which specialized agent should handle it.
    
    Options:
    - route_optimizer: For questions about delivery routes, schedules, and optimization
    - fleet_monitor: For questions about vehicle status, maintenance, and tracking
    - data_retriever: For specific requests about traffic, weather, or external data
    - notification: For sending alerts, updates, or communications
    
    Respond with which agent should handle this request and why.
    """
    
    # Prepare messages array (without system message)
    messages = []
    
    # Add conversation history
    for entry in history[-5:]:  # Last 5 exchanges for context
        messages.append({
            "role": "user" if entry["role"] == "user" else "assistant",
            "content": entry["content"]
        })
    
    # Add current request
    messages.append({
        "role": "user", 
        "content": f"User role: {role}\nUser request: {input_text}\n\nWhich agent should handle this and why?"
    })
    
    # Get response from Claude with system message as parameter
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        system=system_message,
        messages=messages
    )
    
    # Parse the response to determine which agent to route to
    content = response.content[0].text
    
    # Simple routing logic
    if "route_optimizer" in content.lower():
        next_agent = "route_optimizer"
    elif "fleet_monitor" in content.lower():
        next_agent = "fleet_monitor"
    elif "data_retriever" in content.lower():
        next_agent = "data_retriever"
    elif "notification" in content.lower():
        next_agent = "notification"
    else:
        # Default to route optimizer if unclear
        next_agent = "route_optimizer"
    
    # Update context with reasoning
    context["routing_reason"] = content
    context["next_agent"] = next_agent
    
    # Return updated state
    return {"input": input_text, "context": context, "next": next_agent} 