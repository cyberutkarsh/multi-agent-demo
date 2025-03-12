from typing import Dict, Any, List
import anthropic
import os
from datetime import datetime
from langgraph.graph import END

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

def notification_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent specialized in sending notifications and alerts to drivers,
    admins, and other stakeholders.
    """
    input_text = state["input"]
    context = state["context"]
    role = context.get("role", "unknown")
    
    # Create system message content
    system_message = """You are a notification agent that specializes in communicating with drivers,
    logistics coordinators, and system administrators.
    
    Your capabilities include:
    - Sending route updates to drivers
    - Alerting administrators about maintenance needs
    - Notifying logistics coordinators about delivery status
    - Providing confirmation of message delivery
    
    Format your response as if you've actually sent the notification to the relevant parties.
    """
    
    # Prepare messages array (without system message)
    messages = [
        {
            "role": "user",
            "content": f"""Based on this information, prepare and send appropriate notifications:
            
            User role: {role}
            Message content: {input_text}
            
            Please describe what notifications were sent and to whom.
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
    
    # Log the notification
    notification_log = {
        "timestamp": datetime.now().isoformat(),
        "content": content,
        "recipient_role": "driver" if "driver" in content.lower() else "admin" if "admin" in content.lower() else "coordinator"
    }
    
    # Update context with notification record
    if "notifications" not in context:
        context["notifications"] = []
    context["notifications"].append(notification_log)
    
    # Store output in context for the main app to retrieve
    context["messages"] = context.get("messages", []) + [{"role": "assistant", "content": content}]
    
    return {
        "input": content,
        "context": context,
        "next": END
    } 