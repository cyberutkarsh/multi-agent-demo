from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import time
import anthropic
import os
from datetime import datetime
import uvicorn

# Import the agent functions
from agents.coordinator import coordinator_agent
from agents.route_optimizer import route_optimizer_agent
from agents.fleet_monitor import fleet_monitor_agent
from agents.data_retriever import data_retriever_agent
from agents.notification import notification_agent
from utils.api_mock import load_mock_data

# Initialize Claude client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

# Define request model
class QueryRequest(BaseModel):
    input: str
    role: Optional[str] = "admin"
    session_id: Optional[str] = None

# Define response model
class QueryResponse(BaseModel):
    output: Dict[str, Any]

# Create FastAPI app
app = FastAPI(title="Supply Chain Multi-Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store session data
sessions = {}

def determine_next_agent(user_message):
    """Determine which specialized agent to call based on the message content."""
    user_message = user_message.lower()
    if "route" in user_message or "path" in user_message or "delivery" in user_message:
        return "route_optimizer"
    elif "fleet" in user_message or "vehicle" in user_message or "driver" in user_message:
        return "fleet_monitor"
    elif "weather" in user_message or "traffic" in user_message or "condition" in user_message:
        return "data_retriever"
    elif "notify" in user_message or "alert" in user_message or "send" in user_message:
        return "notification"
    return None

# Manual agent orchestration instead of using LangGraph
def process_with_agents(user_input, context):
    """Process the user input through our agent system manually without LangGraph."""
    # Initialize state
    state = {
        "input": user_input,
        "context": context,
        "next": ""
    }
    
    # Step 1: First, let coordinator determine which agent to use
    try:
        coordinator_result = coordinator_agent(state)
        next_agent = coordinator_result.get("next", "")
        state = coordinator_result  # Update state
    except Exception as e:
        print(f"Error in coordinator_agent: {str(e)}")
        return {"error": str(e), "context": context}
    
    # Step 2: Call the specialized agent determined by coordinator
    try:
        if next_agent == "route_optimizer":
            agent_result = route_optimizer_agent(state)
        elif next_agent == "fleet_monitor":
            agent_result = fleet_monitor_agent(state)
        elif next_agent == "data_retriever":
            agent_result = data_retriever_agent(state)
        elif next_agent == "notification":
            agent_result = notification_agent(state)
        else:
            # If no specific agent is identified, use route_optimizer as default
            agent_result = route_optimizer_agent(state)
        
        # Update state
        state = agent_result
    except Exception as e:
        print(f"Error in {next_agent}: {str(e)}")
        return {"error": str(e), "context": context}
    
    # Step 3: If needed, call the data retriever
    if state.get("next") == "data_retriever":
        try:
            data_result = data_retriever_agent(state)
            state = data_result
        except Exception as e:
            print(f"Error in data_retriever: {str(e)}")
            return {"error": str(e), "context": context}
    
    # Step 4: If needed, call the notification agent
    if state.get("next") == "notification":
        try:
            notif_result = notification_agent(state)
            state = notif_result
        except Exception as e:
            print(f"Error in notification_agent: {str(e)}")
            return {"error": str(e), "context": context}
    
    # Return the final state
    return {"result": state, "context": state.get("context", context)}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the multi-agent system.
    """
    # Generate a session ID if not provided
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(request.input) % 10000}"
    
    # Initialize or retrieve session context
    if session_id not in sessions:
        sessions[session_id] = {
            "role": request.role,
            "mock_data": load_mock_data(),
            "conversation_history": [],
            "messages": []
        }
    
    context = sessions[session_id]
    
    # Add user input to conversation history
    context["conversation_history"].append({"role": "user", "content": request.input})
    
    # Start request timing for metrics
    start_time = time.time()
    
    try:
        # Process with our manual agent workflow instead of LangGraph
        agent_result = process_with_agents(request.input, context)
        
        if "error" in agent_result:
            # Fall back to direct Claude API if there's an error
            try:
                fallback_response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    system=f"You are a helpful supply chain assistant for a {request.role}. You have mock data about vehicles and fleet operations to reference.",
                    messages=[{"role": "user", "content": request.input}]
                )
                response_content = fallback_response.content[0].text
                
                # Update context with fallback response
                context["conversation_history"].append({"role": "assistant", "content": response_content})
                sessions[session_id] = context
                
                # Return formatted error response
                return create_response(request.input, response_content, agent_result.get("error"), session_id)
            except Exception as inner_e:
                # If even the fallback fails, return an error message
                error_msg = f"Error processing request: {agent_result.get('error')}. Fallback also failed: {str(inner_e)}"
                return create_error_response(request.input, error_msg, session_id)
        else:
            # Get the final state and context
            final_context = agent_result.get("context", context)
            
            # Get response from messages
            response_content = "I'm sorry, there was an error processing your request."
            if "messages" in final_context and final_context["messages"]:
                response_content = final_context["messages"][-1]["content"]
            
            # Update the session context
            sessions[session_id] = final_context
            sessions[session_id]["messages"] = []  # Clear for next round
            
            # Add to conversation history
            sessions[session_id]["conversation_history"].append({"role": "assistant", "content": response_content})
            
            # Return formatted successful response
            return create_response(request.input, response_content, None, session_id)
    
    except Exception as e:
        # Log the full exception for debugging
        import traceback
        print(f"Error in process_query: {str(e)}")
        print(traceback.format_exc())
        
        # Fall back to direct Claude API
        try:
            fallback_response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                system=f"You are a helpful supply chain assistant for a {request.role}. You have mock data about vehicles and fleet operations to reference.",
                messages=[{"role": "user", "content": request.input}]
            )
            response_content = fallback_response.content[0].text
            
            # Update context with fallback response
            context["conversation_history"].append({"role": "assistant", "content": response_content})
            sessions[session_id] = context
            
            # Return formatted error response
            return create_response(request.input, response_content, str(e), session_id)
        except Exception as inner_e:
            # If even the fallback fails, return an error message
            error_msg = f"Error processing request: {str(e)}. Fallback also failed: {str(inner_e)}"
            return create_error_response(request.input, error_msg, session_id)

def create_response(input_text, content, error=None, session_id=None):
    """Create a standardized response object."""
    # Calculate approximate token counts
    input_tokens = len(input_text.split()) * 1.3
    output_tokens = len(content.split()) * 1.3
    
    # Determine which agent was used
    agent_used = determine_next_agent(input_text) or "coordinator"
    
    # Create response with the required format
    response = {
        "output": {
            "content": content,
            "additional_kwargs": {} if not error else {"error": error},
            "response_metadata": {
                "token_usage": {
                    "completion_tokens": int(output_tokens),
                    "prompt_tokens": int(input_tokens),
                    "total_tokens": int(input_tokens + output_tokens)
                },
                "model_name": "claude-3-sonnet-20240229",
                "finish_reason": "stop" if not error else "error",
                "content_filter_results": {
                    "hate": {"filtered": False, "severity": "safe"},
                    "self_harm": {"filtered": False, "severity": "safe"},
                    "sexual": {"filtered": False, "severity": "safe"},
                    "violence": {"filtered": False, "severity": "safe"}
                }
            },
            "type": "ai",
            "id": f"run-{session_id}-{int(time.time())}",
            "example": False,
            "tool_calls": [],
            "invalid_tool_calls": [],
            "usage_metadata": {
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "total_tokens": int(input_tokens + output_tokens),
                "input_token_details": {},
                "output_token_details": {}
            },
            "agent_used": agent_used
        }
    }
    
    if error:
        response["output"]["error"] = error
    
    return response

def create_error_response(input_text, error_message, session_id=None):
    """Create a standardized error response."""
    return {
        "output": {
            "content": error_message,
            "additional_kwargs": {"error": error_message},
            "response_metadata": {
                "token_usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": int(len(input_text.split()) * 1.3),
                    "total_tokens": int(len(input_text.split()) * 1.3)
                },
                "model_name": "claude-3-sonnet-20240229",
                "finish_reason": "error"
            },
            "type": "error",
            "id": f"error-{session_id or 'unknown'}-{int(time.time())}",
            "example": False
        }
    }

# Run the API server when the script is executed directly
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 