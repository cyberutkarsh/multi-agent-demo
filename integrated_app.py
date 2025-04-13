import streamlit as st
import os
import json
import time
import random
from typing import Dict, List, Any, Tuple, Generator
import anthropic
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import aiohttp
from langgraph.graph import StateGraph, END, START
from typing import TypedDict
import matplotlib.pyplot as plt
import html
import numpy as np
import uuid
import logging

# Import components for supply chain system
from components.agent_visualizer import visualize_agent_workflow
from agents.coordinator import coordinator_agent
from agents.route_optimizer import route_optimizer_agent
from agents.fleet_monitor import fleet_monitor_agent
from agents.data_retriever import data_retriever_agent
from agents.notification import notification_agent
from utils.api_mock import load_mock_data

# Import components for Q2 deal prioritization system
from agents.deal_orchestrator_agent import OrchestratorAgent
from agents.snowflake_agent import SnowflakeAgent
from agents.databricks_agent import DatabricksAgent
from agents.salesforce_agent import SalesforceAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Claude client (using environment variable for API key)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key"))

# Define the state schema for supply chain system
class AgentState(TypedDict):
    input: str
    context: Dict[str, Any]
    next: str

# Set page configuration
st.set_page_config(
    page_title="Multi-Agent Systems Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom styling
st.markdown("""
<style>
    /* Dark theme background */
    .stApp {
        background-color: #262730;
    }
    
    /* Text elements */
    h1, h2, h3, h4, h5, h6, p, .stMarkdown, .stText {
        color: auto !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        color: black !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
        font-weight: bold;
        border: 1px solid gray;
    }
    
    /* Custom chat styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .chat-message.user {
        background-color: #4c8bf5;
        color: white;
    }
    .chat-message.assistant {
        background-color: #343a40;
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1oe6o3n {
        background-color: #1e2129;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #4c8bf5 !important;
    }
    .stAlert > div {
        color: white !important;
    }
    
    /* API detail styling */
    .api-detail {
        padding: 4px 8px;
        margin: 4px 0;
        font-family: monospace;
        font-size: 0.9em;
        border-radius: 4px;
        background-color: rgba(0, 0, 0, 0.2);
    }
    
    .api-endpoint {
        color: #1E88E5;
    }
    
    .api-request {
        color: #FF5722;
    }
    
    .api-purpose {
        color: #00897B;
    }
    
    .api-analysis {
        color: #FFC107;
        font-weight: bold;
    }
    
    /* Agent thinking status */
    .agent-thinking {
        padding: 1rem;
        background-color: #3c4043;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #ffd166;
    }
    
    /* Status message container */
    .chat-message.status {
        background-color: #2b3035;
        border-left: 5px solid #ffd166;
        color: #e0e0e0;
        padding: 0.8rem;
        font-size: 0.9em;
        margin-bottom: 0.5rem;
    }
    
    /* Fix for agent header */
    .agent-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .agent-icon {
        background-color: #ffd166;
        color: #333;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 8px;
        font-weight: bold;
        text-align: center;
    }
    
    .agent-name {
        font-weight: bold;
        color: #ffd166;
    }
    
    /* Status steps */
    .status-step {
        margin: 5px 0;
        display: flex;
        align-items: center;
    }
    
    .status-icon {
        margin-right: 8px;
        color: #00AA66;
        display: inline-block;
    }
    
    .status-icon.processing {
        color: #ffd166;
    }
    
    .status-text {
        flex: 1;
    }
    
    /* Pending step styling */
    .status-step.pending {
        opacity: 0.7;
    }
    
    .status-icon.pending {
        color: #8c8c8c;
    }
    
    /* Dashboard specific styles */
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #4c8bf5;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }
    .metric-card {
        background-color: #343a40;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4c8bf5;
    }
    .metric-label {
        font-size: 1rem;
        color: #e0e0e0;
    }
    .priority-high {
        color: #00AA66;
        font-weight: bold;
    }
    .priority-medium {
        color: #FFA500;
        font-weight: bold;
    }
    .priority-low {
        color: #888888;
        font-weight: bold;
    }
    .comment-text {
        font-size: 0.8em;
        color: #e0e0e0;
    }
    .system-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 6px;
    }
    .system-snowflake {
        background-color: #1E88E5;
        color: white;
    }
    .system-databricks {
        background-color: #FF5722;
        color: white;
    }
    .system-salesforce {
        background-color: #00897B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

#----------------------------------------------------
# Supply Chain System Functions
#----------------------------------------------------

def build_agent_network():
    """Build the network of agents for the Supply Chain system using LangGraph."""
    # Create the graph with defined state type
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_agent)
    workflow.add_node("route_optimizer", route_optimizer_agent)
    workflow.add_node("fleet_monitor", fleet_monitor_agent)
    workflow.add_node("data_retriever", data_retriever_agent)
    workflow.add_node("notification", notification_agent)
    
    # Define the routing function
    def router(state: AgentState) -> str:
        return state["next"]
    
    # Add the START edge to the coordinator (fixing the entrypoint error)
    workflow.add_edge("START", "coordinator")
    
    # Add conditional edges based on the router function
    workflow.add_conditional_edges(
        "coordinator",
        router,
        {
            "route_optimizer": "route_optimizer",
            "fleet_monitor": "fleet_monitor",
            "data_retriever": "data_retriever",
            "notification": "notification"
        }
    )
    
    # Add edges from specialized agents back to coordinator for final response
    workflow.add_edge("route_optimizer", "coordinator")
    workflow.add_edge("fleet_monitor", "coordinator")
    workflow.add_edge("data_retriever", "coordinator")
    workflow.add_edge("notification", "coordinator")
    
    # Add terminal state
    workflow.add_edge("coordinator", END)
    
    # Compile the graph
    return workflow.compile()

def get_demo_scenarios(role: str) -> Dict[str, str]:
    """Get demo scenarios based on the user's role."""
    scenarios = {
        "logistics_coordinator": {
            "Route Optimization": "I need to optimize delivery routes for tomorrow. We have 12 deliveries across the city.",
            "Weather Impact": "How will the current weather affect our delivery routes?",
            "Fleet Status": "Show me the status of all delivery vehicles in the southwest region."
        },
        "driver": {
            "Next Delivery": "What's my next delivery stop?",
            "Route Change": "I'm stuck in traffic on Highway 101. What's an alternative route?",
            "Weather Alert": "Is there any weather I should be aware of on my route?"
        },
        "admin": {
            "Fleet Overview": "Show me a summary of our entire fleet status",
            "Maintenance": "Which vehicles are due for maintenance this week?",
            "Performance": "Show me driver performance metrics for the past week"
        }
    }
    return scenarios.get(role, {})

def get_agent_details(agent_name):
    """Get icon and description for a specific agent."""
    agent_details = {
        "coordinator": {
            "icon": "C",
            "description": "Analyzes your request and routes it to the appropriate specialized agent."
        },
        "route_optimizer": {
            "icon": "R",
            "description": "Specializes in finding the most efficient delivery routes."
        },
        "fleet_monitor": {
            "icon": "F",
            "description": "Tracks vehicle status, maintenance needs, and driver performance."
        },
        "data_retriever": {
            "icon": "D",
            "description": "Gathers external data like weather and traffic conditions."
        },
        "notification": {
            "icon": "N",
            "description": "Sends alerts and updates to relevant parties."
        }
    }
    return agent_details.get(agent_name, {"icon": "?", "description": "Unknown agent"})

def simulate_agent_progress(agent_name, step_container):
    """Simulate agent processing with a visual indicator."""
    agent_details = get_agent_details(agent_name)
    
    with step_container:
        st.markdown(f"""
        <div class="agent-thinking">
            <div class="agent-header">
                <div class="agent-icon">{agent_details["icon"]}</div>
                <div class="agent-name">{agent_name.replace('_', ' ').title()} Agent</div>
            </div>
            <p>{agent_details["description"]}</p>
            <div class="progress-indicator">
                <p>Processing... <span id="thinking-dots"></span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Simulate processing time
    time.sleep(random.uniform(1.5, 3.0))

def update_with_thinking(msg, agent):
    """Update the display with agent thinking status."""
    status_placeholder = st.empty()
    with status_placeholder:
        st.markdown(f"""
        <div class="chat-message status">
            <div class="agent-header">
                <div class="agent-icon">{get_agent_details(agent)["icon"]}</div>
                <div class="agent-name">{agent.replace('_', ' ').title()} Agent</div>
            </div>
            <div class="agent-message">
                {msg}
            </div>
        </div>
        """, unsafe_allow_html=True)
    return status_placeholder

def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent_network" not in st.session_state:
        st.session_state.agent_network = build_agent_network()
    
    if "context" not in st.session_state:
        st.session_state.context = load_mock_data()
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "user_role" not in st.session_state:
        st.session_state.user_role = "logistics_coordinator"
    
    if "status_messages" not in st.session_state:
        st.session_state.status_messages = []

def add_status_message(agent_name, status_type="info", content=""):
    """Add a status message to the conversation display."""
    agent_details = get_agent_details(agent_name)
    status_message = {
        "type": status_type,
        "agent": agent_name,
        "icon": agent_details["icon"],
        "content": content or agent_details["description"],
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    
    st.session_state.status_messages.append(status_message)
    return status_message

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

def process_user_message(user_message: str, agent_status_placeholder=None):
    """Process a user message through the multi-agent system."""
    # Add user message to conversation history
    st.session_state.conversation_history.append({"role": "user", "content": user_message})
    
    try:
        # First step: determine which agent should handle this
        hint_agent = determine_next_agent(user_message)
        
        # Initialize state
        input_state = {
            "input": user_message,
            "context": st.session_state.context,
            "next": ""
        }
        
        # If we have a hint, add it to help the coordinator
        if hint_agent:
            hint_status = add_status_message(
                "coordinator", 
                "info", 
                f"Request appears to be about {hint_agent.replace('_', ' ')}. Routing appropriately."
            )
        
        # First call the coordinator agent to determine routing
        add_status_message("coordinator", "info", "Analyzing your request...")
        simulate_agent_progress("coordinator", agent_status_placeholder)
        
        coord_result = coordinator_agent(input_state)
        next_agent = coord_result.get("next", "")
        
        # Call the specialized agent
        if next_agent and next_agent != "END":
            routing_message = f"Routing to {next_agent.replace('_', ' ')} agent..."
            update_with_thinking(routing_message, "coordinator")
            
            add_status_message(next_agent, "info")
            simulate_agent_progress(next_agent, agent_status_placeholder)
            
            # Call the specialized agent
            if next_agent == "route_optimizer":
                agent_result = route_optimizer_agent(coord_result)
            elif next_agent == "fleet_monitor":
                agent_result = fleet_monitor_agent(coord_result)
            elif next_agent == "data_retriever":
                agent_result = data_retriever_agent(coord_result)
            elif next_agent == "notification":
                agent_result = notification_agent(coord_result)
            else:
                agent_result = coord_result
            
            # Final coordinator pass
            add_status_message("coordinator", "info", "Preparing final response...")
            simulate_agent_progress("coordinator", agent_status_placeholder)
            
            final_result = coordinator_agent(agent_result)
            context = final_result.get("context", {})
            
            # Extract the message from context
            if context and "messages" in context and context["messages"]:
                response_msg = context["messages"][-1]["content"]
                # Add to conversation history
                st.session_state.conversation_history.append({"role": "assistant", "content": response_msg})
                return response_msg, next_agent
            else:
                fallback_msg = "I processed your request but couldn't generate a proper response."
                st.session_state.conversation_history.append({"role": "assistant", "content": fallback_msg})
                return fallback_msg, next_agent
        else:
            # Direct coordinator response
            context = coord_result.get("context", {})
            if context and "messages" in context and context["messages"]:
                response_msg = context["messages"][-1]["content"]
                st.session_state.conversation_history.append({"role": "assistant", "content": response_msg})
                return response_msg, "coordinator"
            else:
                fallback_msg = "I couldn't determine how to process your request."
                st.session_state.conversation_history.append({"role": "assistant", "content": fallback_msg})
                return fallback_msg, "coordinator"
    
    except Exception as e:
        error_msg = f"Error processing your request: {str(e)}"
        st.session_state.conversation_history.append({"role": "assistant", "content": error_msg})
        return error_msg, "error"

#----------------------------------------------------
# Q2 Deal Prioritization Functions
#----------------------------------------------------

def get_system_tag(step_text):
    """Get the appropriate system tag based on the step text"""
    if "Snowflake" in step_text:
        return '<span class="system-tag system-snowflake">SNOWFLAKE</span>'
    elif "Databricks" in step_text:
        return '<span class="system-tag system-databricks">DATABRICKS</span>'
    elif "Salesforce" in step_text or "follow-up" in step_text:
        return '<span class="system-tag system-salesforce">SALESFORCE</span>'
    else:
        return ''

def get_system_name(step_text):
    """Get the appropriate system name based on the step text"""
    if "Snowflake" in step_text:
        return "SNOWFLAKE"
    elif "Databricks" in step_text:
        return "DATABRICKS"
    elif "Salesforce" in step_text or "follow-up" in step_text:
        return "SALESFORCE"
    else:
        return None

# Map workflow stages to step indices
STAGE_TO_STEP = {
    "start": -1,  # Not started yet
    "snowflake_query": 0,
    "snowflake_query_done": 0,
    "databricks_score": 1,
    "databricks_score_done": 1,
    "salesforce_update": 2,
    "salesforce_update_done": 2,
    "salesforce_tasks": 3,
    "salesforce_tasks_done": 3,
    "snowflake_insert": 4,
    "snowflake_insert_done": 4,
    "error": -1  # Error state
}

def update_progress_display(step_container, steps, current_stage):
    """Update the progress display based on the current stage"""
    # Map the current stage to a step index
    current_step = STAGE_TO_STEP.get(current_stage, -1)
    
    with step_container.container():
        # Display completed steps
        for i in range(len(steps)):
            col1, col2 = st.columns([1, 10])
            with col1:
                # Show checkmark for completed steps
                if i < current_step or (i == current_step and current_stage.endswith("_done")):
                    st.write("✅")
                # Show processing icon for current step
                elif i == current_step:
                    st.write("⟳")
                # Show pending icon for future steps
                else:
                    st.write("○")
            
            with col2:
                system = get_system_name(steps[i])
                if system:
                    st.markdown(f"<span class='system-tag system-{system.lower()}'>{system}</span> {steps[i]}", unsafe_allow_html=True)
                else:
                    st.write(steps[i])

def simulate_step_progress(step_container, steps, delay=0.5):
    """Simulate workflow steps with progress indicators."""
    # Display initial state with all steps pending
    with step_container:
        for step in steps:
            step_content = f"""
            <div class="status-step pending">
                <span class="status-icon pending">⌛</span>
                {get_system_tag(step)}
                <span class="status-text">{step}</span>
            </div>
            """
            st.markdown(step_content, unsafe_allow_html=True)
    
    # Update steps to show progress
    for i, step in enumerate(steps):
        time.sleep(delay)  # Simulate processing time for this step
        
        # Mark this step as completed
        with step_container:
            step_content = ""
            
            # Create step indicators
            for j, s in enumerate(steps):
                if j < i:  # Previous steps are done
                    step_content += f"""
                    <div class="status-step">
                        <span class="status-icon">✅</span>
                        {get_system_tag(s)}
                        <span class="status-text">{s}</span>
                    </div>
                    """
                elif j == i:  # Current step is processing
                    system_tag = get_system_tag(s)
                    if "Databricks" in s:
                        # Update the step text for Databricks to show Llama 4
                        s = "Scoring deals with Databricks Llama 4 endpoint"
                    
                    step_content += f"""
                    <div class="status-step">
                        <span class="status-icon processing">🔄</span>
                        {system_tag}
                        <span class="status-text">{s}</span>
                    </div>
                    """
                else:  # Future steps are pending
                    step_content += f"""
                    <div class="status-step pending">
                        <span class="status-icon pending">⌛</span>
                        {get_system_tag(s)}
                        <span class="status-text">{s}</span>
                    </div>
                    """
            
            st.markdown(step_content, unsafe_allow_html=True)
            
        # Wait again for "processing" effect
        time.sleep(delay)
        
        # Mark the step as completed
        with step_container:
            step_content = ""
            
            # Update all steps with current status
            for j, s in enumerate(steps):
                if j <= i:  # Steps up to current are done
                    system_tag = get_system_tag(s)
                    if j == i and "Databricks" in s:
                        # Update the step text for Databricks to show Llama 4
                        s = "Scoring deals with Databricks Llama 4 endpoint"
                    
                    step_content += f"""
                    <div class="status-step">
                        <span class="status-icon">✅</span>
                        {system_tag}
                        <span class="status-text">{s}</span>
                    </div>
                    """
                else:  # Future steps are pending
                    step_content += f"""
                    <div class="status-step pending">
                        <span class="status-icon pending">⌛</span>
                        {get_system_tag(s)}
                        <span class="status-text">{s}</span>
                    </div>
                    """
            
            st.markdown(step_content, unsafe_allow_html=True)

async def run_workflow(status_callback=None, progress_callback=None):
    """Run the Q2 deal prioritization workflow with status updates"""
    # Use mock data instead of trying to connect to backend
    
    # Initialize the Databricks agent directly for Llama 4 endpoint
    databricks_agent = DatabricksAgent()
    
    # If no callback is provided, create a dummy one
    if status_callback is None:
        status_callback = lambda stage, message: None
    
    if progress_callback is None:
        progress_callback = lambda stage: None
        
    # Generate mock opportunities
    def generate_mock_opportunities(count=4):
        opps = []
        industries = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing"]
        products = ["Enterprise Software", "Cloud Services", "Security Suite", "Analytics Platform", "IoT Solution"]
        regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        sizes = ["Small", "Medium", "Large", "Enterprise"]
        
        # Generate standard opportunities
        for i in range(count):
            opps.append({
                "id": f"OPP-{1000+i}",
                "name": f"Opportunity {1000+i}",
                "amount": random.uniform(10000, 500000),
                "industry": random.choice(industries),
                "product": random.choice(products),
                "region": random.choice(regions),
                "customer_size": random.choice(sizes),
                "existing_customer": random.choice([True, False]),
                "days_in_current_stage": random.randint(1, 90)
            })
        
        # Ensure at least one high-priority deal (modify the first opportunity to have high win probability factors)
        opps[0]["industry"] = "Technology"  # Technology has highest industry bonus
        opps[0]["amount"] = random.uniform(10000, 50000)  # Lower amount means higher win probability
        opps[0]["existing_customer"] = True  # Existing customers are more likely to close
        opps[0]["days_in_current_stage"] = random.randint(1, 30)  # Shorter time in stage
        
        return opps
    
    # Function to extract key insights from Llama response
    def extract_insights(response_text, opp_id):
        insights = []
        
        # Look for specific patterns
        if "win probability" in response_text.lower():
            insights.append("Analyzing win factors...")
        
        if "existing customer" in response_text.lower():
            if "existing customer: yes" in response_text.lower():
                insights.append("✓ Existing relationship detected")
            else:
                insights.append("⚠ New customer - higher risk")
                
        if "high-value" in response_text.lower() or "high value" in response_text.lower():
            insights.append("⚠ High-value deal - complex approval likely")
            
        if "days in" in response_text.lower() and "stage" in response_text.lower():
            if any(x in response_text.lower() for x in ["long time", "significant", "concerning"]):
                insights.append("⚠ Deal may be stalled")
                
        # Add a summary if we found insights
        if insights:
            return f"🔍 {opp_id}: " + " | ".join(insights)
        else:
            return f"🔍 Analyzing {opp_id}..."
    
    try:
        status_callback("start", "Starting Q2 deal prioritization workflow")
        
        # Step 1: Generate mock Snowflake data
        status_callback("snowflake_query", "🔄 SNOWFLAKE API: Fetching opportunity data from Snowflake\n"
                       "→ Endpoint: /snowflake/query\n"
                       "→ Request: SELECT * FROM opportunity WHERE stage = 'Proposal'\n"
                       "→ Purpose: Retrieve opportunities for scoring and prioritization")
        progress_callback("snowflake_query")
        
        time.sleep(1)  # Simulate API call
        opportunities = generate_mock_opportunities(4)
        
        status_callback("snowflake_query_done", f"✅ SNOWFLAKE API: Retrieved opportunities\n"
                      f"→ Found: {len(opportunities)} opportunities\n"
                      f"→ Pipeline Total: ${sum(opp['amount'] for opp in opportunities):,.2f}\n"
                      f"→ Analysis: {len(opportunities)} deals ready for scoring")
        progress_callback("snowflake_query_done")
        
        # Step 2: Score deals using Databricks Llama 4 endpoint
        status_callback("databricks_score", "🔄 DATABRICKS API: Scoring opportunities with Llama 4 model\n"
                       "→ Endpoint: /api/serving-endpoints/llama4-maverick/invocations\n"
                       "→ Total Records: 4\n"
                       "→ Purpose: Score deals for win probability and next best product")
        progress_callback("databricks_score")
        
        # Process opportunities one by one to show progress
        scored_opportunities = []
        high_priority = 0
        sum_probability = 0
        
        for i, opp in enumerate(opportunities):
            # Update status to show which opportunity is being processed
            status_callback("databricks_score", f"🔄 DATABRICKS API: Scoring opportunity {i+1} of {len(opportunities)}\n"
                           f"→ Endpoint: /api/serving-endpoints/llama4-maverick/invocations\n"
                           f"→ Processing: {opp['id']} - {opp['name']}\n"
                           f"→ Industry: {opp['industry']}\n"
                           f"→ Amount: ${opp['amount']:,.2f}")
            
            # Call the agent to score this opportunity
            result = databricks_agent.score_opportunity(opp)
            
            # Show result for this opportunity
            status_callback("databricks_score", f"🔄 DATABRICKS API: Scored opportunity {i+1} of {len(opportunities)}\n"
                           f"→ Opportunity: {opp['id']} - {opp['name']}\n"
                           f"→ Win Probability: {result.get('winProbability', 0):.2f}\n"
                           f"→ Next Best Product: {result.get('nextBestProduct', 'Unknown')}")
            
            # Add a small delay to see the updates
            time.sleep(0.5)
            
            # Count high priority deals
            if result.get("winProbability", 0) > 0.7:
                high_priority += 1
                
            # Add to sum for average calculation
            sum_probability += result.get("winProbability", 0)
            
            # Add the scored opportunity to our list
            scored_opportunities.append(result)
        
        # Calculate average probability
        avg_probability = sum_probability / len(scored_opportunities) if scored_opportunities else 0
        
        # Sample for display
        sample_scored = scored_opportunities[0] if scored_opportunities else {}
        
        status_callback("databricks_score_done", f"✅ DATABRICKS API: Scoring complete\n"
                       f"→ Scored: {len(scored_opportunities)} opportunities\n"
                       f"→ High Priority: {high_priority} deals (win prob > 70%)\n"
                       f"→ Avg Win Probability: {avg_probability:.2f}\n"
                       f"→ Sample Output: ID={sample_scored.get('id', 'N/A')}, Win Prob={sample_scored.get('winProbability', 0):.2f}, Next Product={sample_scored.get('nextBestProduct', 'Unknown')}\n"
                       f"→ Analysis: {high_priority} deals need immediate follow-up")
        progress_callback("databricks_score_done")
        
        # Step 3: Mock Salesforce updates
        sample_sf_input = {
            "Win_Probability__c": sample_scored.get('winProbability', 0),
            "Next_Best_Product__c": sample_scored.get('nextBestProduct', 'Unknown')
        }
        
        status_callback("salesforce_update", f"🔄 SALESFORCE API: Updating opportunities\n"
                       f"→ Endpoint: /salesforce/opportunity/{{id}}\n"
                       f"→ Total Updates: {len(scored_opportunities)}\n"
                       f"→ Sample Request: {json.dumps(sample_sf_input)}\n"
                       f"→ Purpose: Update Salesforce with ML predictions for sales team")
        progress_callback("salesforce_update")
        
        # Show progress for each opportunity update
        for i, opp in enumerate(scored_opportunities):
            status_callback("salesforce_update", f"🔄 SALESFORCE API: Updating opportunity {i+1} of {len(scored_opportunities)}\n"
                           f"→ Opportunity: {opp['id']} - Amount: ${opp.get('amount', 0):,.2f}\n"
                           f"→ Win Probability: {opp.get('winProbability', 0):.2f}\n"
                           f"→ Next Best Product: {opp.get('nextBestProduct', 'Unknown')}")
            time.sleep(0.3)  # Simulate API call for each update
        
        time.sleep(0.5)  # Final delay before completion
        
        # Create mock Salesforce results
        sf_results = {
            "updated_records": [{"id": opp["id"]} for opp in scored_opportunities],
            "created_tasks": [{"id": f"TASK-{1000+i}"} for i, opp in enumerate(scored_opportunities) if opp.get("winProbability", 0) > 0.5],
            "high_priority_count": high_priority,
            "total_pipeline_value": sum(opp.get("amount", 0) for opp in scored_opportunities),
            "error_records": []
        }
        
        status_callback("salesforce_update_done", f"✅ SALESFORCE API: Updates complete\n"
                       f"→ Updated: {len(sf_results['updated_records'])} opportunities\n"
                       f"→ High Priority Count: {sf_results['high_priority_count']}\n"
                       f"→ Total Pipeline Value: ${sf_results['total_pipeline_value']:,.2f}\n"
                       f"→ Analysis: {sf_results['high_priority_count']} high-priority opportunities flagged for immediate attention")
        progress_callback("salesforce_update_done")
        
        # Sample task data
        sample_task = {
            "subject": "Follow up on high-priority deal",
            "priority": "High" if sample_scored.get('winProbability', 0) > 0.7 else "Normal",
            "opportunityId": sample_scored.get('id', 'Unknown'),
            "dueDate": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "ownerId": "0051a000000FLOdAAO"  # Sample owner ID
        }
        
        status_callback("salesforce_tasks", f"🔄 SALESFORCE API: Creating follow-up tasks\n"
                       f"→ Endpoint: /salesforce/task\n"
                       f"→ Total Tasks: {len(scored_opportunities)}\n"
                       f"→ Sample Request: {json.dumps(sample_task)}\n"
                       f"→ Purpose: Auto-generate follow-up tasks for sales representatives")
        progress_callback("salesforce_tasks")
        
        # Show progress for each task creation
        for i, opp in enumerate(scored_opportunities):
            if opp.get("winProbability", 0) > 0.5:  # Only create tasks for higher probability opps
                task_priority = "High" if opp.get("winProbability", 0) > 0.7 else "Normal"
                status_callback("salesforce_tasks", f"🔄 SALESFORCE API: Creating task {i+1}\n"
                               f"→ Opportunity: {opp['id']}\n"
                               f"→ Priority: {task_priority}\n"
                               f"→ Subject: Follow up on {task_priority.lower()}-priority deal\n"
                               f"→ Due Date: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}")
                time.sleep(0.3)  # Simulate API call
        
        time.sleep(0.5)  # Final delay before completion
        
        status_callback("salesforce_tasks_done", f"✅ SALESFORCE API: Tasks created\n"
                       f"→ Created: {len(sf_results['created_tasks'])} tasks\n"
                       f"→ High Priority Tasks: {sf_results['high_priority_count']}\n"
                       f"→ Assigned To: Sales team members\n"
                       f"→ Analysis: All high-priority opportunities have follow-up tasks assigned")
        progress_callback("salesforce_tasks_done")
        
        # Step 4: Mock Snowflake write
        status_callback("snowflake_insert", f"🔄 SNOWFLAKE API: Writing summary to Snowflake\n"
                       f"→ Endpoint: /snowflake/insert\n"
                       f"→ Table: deal_prioritization_summary\n"
                       f"→ Purpose: Store scoring results for reporting and analytics")
        progress_callback("snowflake_insert")
        
        # Show detailed steps for Snowflake writing
        phases = [
            "Preparing data schema...",
            "Validating opportunity records...",
            "Generating summary statistics...",
            "Uploading to Snowflake warehouse...",
            "Committing transaction..."
        ]
        
        for phase in phases:
            status_callback("snowflake_insert", f"🔄 SNOWFLAKE API: {phase}\n"
                           f"→ Operation: Writing summary data\n"
                           f"→ Records: {len(scored_opportunities)} opportunities + 1 summary")
            time.sleep(0.4)  # Simulate each phase
        
        time.sleep(0.5)  # Final delay before completion
        
        status_callback("snowflake_insert_done", f"✅ SNOWFLAKE API: Summary written successfully\n"
                       f"→ Records Written: 1 summary record\n"
                       f"→ Opportunities Updated: {len(scored_opportunities)}\n"
                       f"→ Analysis: Q2 Deal Prioritization workflow completed successfully")
        progress_callback("snowflake_insert_done")
        
        # Return the result
        return {
            "status": "success",
            "opportunities": scored_opportunities,
            "tasks": sf_results["created_tasks"],
            "summary": {
                "runDate": datetime.now().strftime("%Y-%m-%d"),
                "highPriorityCount": sf_results["high_priority_count"],
                "totalPipelineValue": sf_results["total_pipeline_value"],
                "avgWinProbability": avg_probability
            },
            "errors": sf_results["error_records"]
        }
        
    except Exception as e:
        status_callback("error", f"Workflow failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def format_currency(value):
    """Format a number as currency"""
    return f"${value:,.2f}"

def get_probability_comment(value):
    """Generate a comment explaining the win probability"""
    if value > 0.8:
        return "High likelihood to close. Premium Advisory recommended."
    elif value > 0.5:
        return "Moderate conversion potential. Standard Package offering appropriate."
    else:
        return "Lower conversion probability. Start with Intro Offer to build relationship."

def display_opportunities(opportunities):
    """Display opportunities in a formatted table with comments"""
    if not opportunities:
        st.info("No opportunities available")
        return
    
    # Add probability comments
    opportunities_with_comments = []
    for opp in opportunities:
        opp_copy = opp.copy()
        opp_copy["comment"] = get_probability_comment(opp["winProbability"])
        opportunities_with_comments.append(opp_copy)
    
    # Convert opportunities to DataFrame
    df = pd.DataFrame(opportunities_with_comments)
    
    # Add styling based on win probability
    def highlight_probability(value):
        if value > 0.8:
            return "priority-high"
        elif value > 0.5:
            return "priority-medium"
        else:
            return "priority-low"
    
    # Format currencies
    df['amount'] = df['amount'].apply(format_currency)
    
    # Style the table
    styled_df = pd.DataFrame()
    styled_df['ID'] = df['id']
    styled_df['Amount'] = df['amount']
    styled_df['Win Probability'] = df.apply(
        lambda row: f'<span class="{highlight_probability(row.winProbability)}">{row.winProbability:.2f}</span><br>' + 
                   f'<span class="comment-text">{row.comment}</span>',
        axis=1
    )
    styled_df['Next Best Product'] = df['nextBestProduct']
    styled_df['Data Source'] = '<span class="system-tag system-databricks">DATABRICKS</span>'
    
    # Display the styled table
    st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)

def display_tasks(tasks):
    """Display tasks in a formatted table with more details"""
    if not tasks:
        st.info("No tasks created")
        return
    
    # Create a table of tasks with assigned owners
    task_data = []
    for idx, task in enumerate(tasks):
        # Assign owners in a round-robin fashion from a list of 3 sales reps
        owners = ["Sarah Johnson", "Michael Chen", "Priya Patel"]
        owner = owners[idx % len(owners)]
        
        # Calculate due date (tomorrow)
        due_date = (datetime.now() + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        
        task_data.append({
            "Task ID": task.get("id", "Unknown"),
            "Subject": "Follow up on high-priority deal",
            "Owner": owner,
            "Due Date": due_date,
            "Status": "Not Started",
            "Data Source": '<span class="system-tag system-salesforce">SALESFORCE</span>'
        })
    
    # Convert to DataFrame for display
    task_df = pd.DataFrame(task_data)
    
    # Display the styled table
    st.write(task_df.to_html(escape=False, index=False), unsafe_allow_html=True)

#----------------------------------------------------
# Main Application
#----------------------------------------------------

def show_supply_chain_ui():
    """Display the Supply Chain system UI."""
    st.title("Supply Chain Multi-Agent System")
    
    # Initialize session state for supply chain system
    initialize_session_state()
    
    # Sidebar user role selection
    st.sidebar.title("User Settings")
    role_options = {
        "logistics_coordinator": "Logistics Coordinator",
        "driver": "Driver",
        "admin": "Administrator"
    }
    
    selected_role = st.sidebar.selectbox(
        "Select your role:",
        list(role_options.keys()),
        format_func=lambda x: role_options[x],
        index=list(role_options.keys()).index(st.session_state.user_role)
    )
    
    # Update user role if changed
    if selected_role != st.session_state.user_role:
        st.session_state.user_role = selected_role
        st.session_state.status_messages = []
    
    # Display user role and demo scenarios
    st.sidebar.markdown(f"### Welcome, {role_options[selected_role]}")
    
    # Display demo scenarios in sidebar
    st.sidebar.markdown("### Demo Scenarios")
    demo_scenarios = get_demo_scenarios(selected_role)
    
    for title, scenario in demo_scenarios.items():
        if st.sidebar.button(title):
            st.session_state.messages.append({"role": "user", "content": scenario})
    
    # Display visualization of the multi-agent architecture
    st.sidebar.markdown("### System Architecture")
    with st.sidebar.expander("View Agent Network", expanded=False):
        fig = visualize_agent_workflow()
        st.pyplot(fig)
    
    # Main conversation interface
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    # User input
    if prompt := st.chat_input("Ask about supply chain operations..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            agent_status = st.empty()
            response, agent_used = process_user_message(prompt, agent_status)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Also display agent processing flow
        for status in st.session_state.status_messages[-5:]:  # Show last 5 messages to avoid clutter
            st.sidebar.markdown(f"""
            <div class="status-message">
                <span style="color: #ffd166; font-weight: bold;">[{status['timestamp']}]</span> 
                <span style="color: #e0e0e0;"><b>{status['agent'].replace('_', ' ').title()}</b>: {status['content']}</span>
            </div>
            """, unsafe_allow_html=True)

def show_q2_deal_prioritization_ui():
    """Display the Q2 Deal Prioritization system UI."""
    st.title("Q2 Deal Prioritization Dashboard")
    
    # Sidebar
    st.sidebar.markdown("## Q2 Deal Prioritization")
    st.sidebar.markdown("This dashboard controls the Q2 deal prioritization workflow.")
    
    # Add option to select data source
    data_source = st.sidebar.selectbox("Data Source", ["Production", "Staging", "Development"], index=2)
    st.sidebar.markdown(f"Connected to: **{data_source}**")
    
    # Add info about Databricks Llama 4 integration
    st.sidebar.markdown("## Databricks Integration")
    st.sidebar.markdown("Using Databricks Llama 4 model for win probability prediction and next best product recommendations.")
    
    with st.sidebar.expander("Databricks Endpoint Details"):
        st.markdown("""
        **Endpoint:** databricks-llama-4-maverick
        
        **Model:** Meta-Llama-4-Maverick
        
        **Features:**
        - Win probability prediction
        - Next best product recommendations
        - Natural language analysis
        """)
    
    # Run workflow button and progress section
    st.markdown('<div class="section-header">Deal Scoring Workflow</div>', unsafe_allow_html=True)
    
    # Run workflow button
    if st.button("Run Q2 Deal Prioritization with Llama 4"):
        # Initialize workflow result in session state
        if 'workflow_result' not in st.session_state:
            st.session_state.workflow_result = None
        
        # Create single blue status box for updates
        status_box = st.empty()
        
        # Create placeholders for progress and status
        progress_container = st.empty()
        step_container = st.empty()
        
        # Show progress message
        progress_message = progress_container.info("Running Q2 Deal Prioritization workflow...")
        
        # Define workflow steps
        steps = [
            "Fetching opportunity data from Snowflake",
            "Scoring deals in Databricks",
            "Updating opportunities in Salesforce",
            "Creating follow-up tasks in Salesforce",
            "Writing summary to Snowflake"
        ]
        
        # Current workflow stage for step display
        if 'current_stage' not in st.session_state:
            st.session_state.current_stage = "start"
            
        # Update progress display with current stage
        update_progress_display(step_container, steps, st.session_state.current_stage)
        
        def update_status(stage, message):
            """Updates the status display with the current processing information"""
            # Display in a single status box that replaces itself with each update
            with status_box.container():
                if "\n" in message:
                    # For multi-line messages, create a more detailed display
                    lines = message.split("\n")
                    header = lines[0]
                    
                    # Create a styled box for the header
                    st.info(header)
                    
                    # Display each detail line with proper formatting
                    for line in lines[1:]:
                        if not line.strip():  # Skip empty lines
                            continue
                        
                        # Apply custom styling based on line content
                        if line.startswith("→ Endpoint:"):
                            st.markdown(f'<div class="api-detail api-endpoint">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Processing:") or line.startswith("→ Opportunity:"):
                            st.markdown(f'<div class="api-detail api-request">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Win Probability:"):
                            st.markdown(f'<div class="api-detail api-analysis">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Next Best Product:"):
                            st.markdown(f'<div class="api-detail api-purpose">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Request:") or line.startswith("→ Sample"):
                            st.markdown(f'<div class="api-detail api-request">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Purpose:"):
                            st.markdown(f'<div class="api-detail api-purpose">{line}</div>', unsafe_allow_html=True)
                        elif line.startswith("→ Analysis:"):
                            st.markdown(f'<div class="api-detail api-analysis">{line}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="api-detail">{line}</div>', unsafe_allow_html=True)
                else:
                    # For simple messages, use the standard info message
                    st.info(message)
        
        # Progress callback to update step display
        def update_progress(stage):
            st.session_state.current_stage = stage
            update_progress_display(step_container, steps, stage)
        
        try:
            # Run the workflow with status updates
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(run_workflow(update_status, update_progress))
            loop.close()
            
            # Store the results in session state
            st.session_state.workflow_result = result
            st.session_state.last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Display success message
            if result['status'] == 'success':
                progress_message.success("Workflow completed successfully using Databricks Llama 4!")
                
                # Display summary metrics
                st.markdown('<div class="section-header">Processing Results</div>', unsafe_allow_html=True)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("<span class='system-tag system-salesforce'>SALESFORCE</span> High Priority Deals", unsafe_allow_html=True)
                    st.metric("High Priority Deals", result['summary']['highPriorityCount'])
                
                with col2:
                    st.markdown("<span class='system-tag system-snowflake'>SNOWFLAKE</span> Total Pipeline Value", unsafe_allow_html=True)
                    st.metric("Total Pipeline Value", format_currency(result['summary']['totalPipelineValue']))
                
                with col3:
                    st.markdown("<span class='system-tag system-databricks'>DATABRICKS</span> Avg Win Probability", unsafe_allow_html=True)
                    st.metric("Avg Win Probability", f"{result['summary']['avgWinProbability']:.2f}")
                
                with col4:
                    st.markdown("<span class='system-tag system-salesforce'>SALESFORCE</span> Tasks Created", unsafe_allow_html=True)
                    st.metric("Tasks Created", len(result['tasks']))
            else:
                progress_message.error(f"Workflow failed: {result['message']}")
                
        except Exception as e:
            progress_message.error(f"Error running workflow: {str(e)}")
    
    # Only show results if we have them
    if 'workflow_result' in st.session_state and st.session_state.workflow_result:
        result = st.session_state.workflow_result
        
        # Display the scored opportunities
        st.markdown('<div class="section-header">Scored Opportunities</div>', unsafe_allow_html=True)
        st.markdown("Opportunities scored by the Databricks Llama 4 model with win probability and next best product recommendations.")
        display_opportunities(result.get('opportunities', []))
        
        # Display the created tasks
        st.markdown('<div class="section-header">Sales Follow-up Tasks</div>', unsafe_allow_html=True)
        st.markdown("Tasks automatically created in Salesforce for sales representatives to follow up on opportunities.")
        display_tasks(result.get('tasks', []))
        
        # Display errors if any
        if result.get('errors', []):
            st.markdown('<div class="section-header">Processing Errors</div>', unsafe_allow_html=True)
            st.error(f"Errors occurred with these records: {', '.join(result['errors'])}")
        
        # Option to export results as JSON
        st.markdown('<div class="section-header">Export Data</div>', unsafe_allow_html=True)
        if st.button("Export Results as JSON"):
            # Create a downloadable link
            result_json = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=result_json,
                file_name=f"q2_deal_prioritization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def main():
    """Main application with tabs for different systems."""
    st.sidebar.title("Multi-Agent Systems")
    
    # Create tabs for the different systems - MODIFIED to show only Q2 prioritization
    tabs = st.tabs(["Q2 Deal Prioritization"])
    
    # Show only the Q2 prioritization UI to avoid langgraph errors
    with tabs[0]:
        show_q2_deal_prioritization_ui()

if __name__ == "__main__":
    main() 