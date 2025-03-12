# Supply Chain Multi-Agent System
A comprehensive multi-agent system for supply chain management, powered by Anthropic Claude and LangGraph. This system provides specialized agents for route optimization, fleet monitoring, data retrieval, and notifications through both a web interface and an API.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Architecture](#architecture)
7. [Multi-turn Conversations](#multi-turn-conversations)
8. [Response Format](#response-format)
9. [Error Handling](#error-handling)
10. [Development](#development)

## Overview

This Supply Chain Multi-Agent System demonstrates the power of specialized AI agents working together to solve complex supply chain management tasks. The system features:

- A conversational Streamlit web interface
- A RESTful API for integration with external systems
- Specialized agents with different capabilities
- Multi-turn conversation support
- Visual tracking of agent processing

## Features

- **Route Optimization**: Calculate optimal delivery routes considering traffic and weather
- **Fleet Monitoring**: Track vehicle status, maintenance needs, and driver performance
- **Data Retrieval**: Access weather forecasts, traffic conditions, and other external data
- **Notification System**: Send alerts and updates to relevant stakeholders
- **Role-Based Interface**: Different views for logistics coordinators, drivers, and administrators
- **API Integration**: Connect with external orchestrator agents and systems

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/supply-chain-multi-agent.git
   cd supply-chain-multi-agent
   ```

2. Install dependencies:
   ```bash
   pip install streamlit anthropic langgraph matplotlib networkx fastapi uvicorn pydantic
   ```

3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Streamlit Web Interface

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser to [http://localhost:8501](http://localhost:8501)

3. Select your role (Logistics Coordinator, Driver, or Administrator)

4. Start interacting with the agents through the chat interface

### API Server

1. Run the API server:
   ```bash
   python api.py
   ```

2. The API will be available at [http://localhost:8000](http://localhost:8000)

3. Access the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t supply-chain-multi-agent .
   ```

2. Run the Docker container:
   ```bash
   docker run -d -p 8501:8501 -p 8000:8000 -e ANTHROPIC_API_KEY=your_api_key_here --name supply-chain-container supply-chain-multi-agent
   ```

3. Access the Streamlit UI at [http://localhost:8501](http://localhost:8501) and the API at [http://localhost:8000](http://localhost:8000)

4. Stop the running container:
   ```bash
   docker stop supply-chain-container
   ```

5. Remove the container (after stopping):
   ```bash
   docker rm supply-chain-container
   ```

6. Build and run in a single command (for development):
   ```bash
   docker build -t supply-chain-multi-agent . && docker run -d -p 8501:8501 -p 8000:8000 -e ANTHROPIC_API_KEY=your_api_key_here --name supply-chain-container supply-chain-multi-agent
   ```

7. Remove the container if it exists, then build and run (for clean restart):
   ```bash
   docker rm -f supply-chain-container 2>/dev/null || true && docker build -t supply-chain-multi-agent . && docker run -d -p 8501:8501 -p 8000:8000 -e ANTHROPIC_API_KEY=your_api_key_here --name supply-chain-container supply-chain-multi-agent
   ```

## API Documentation

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST   | Process a query through the supply chain multi-agent system |

### Integration Guide for Orchestrator Agents

If you're calling this API from another orchestrator agent, here are suggested prompts and instructions:

#### Suggested Prompt for Your Orchestrator Agent

Notifications

Sample API Calls

#### Basic Query

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Show me a summary of our entire fleet status",
    "role": "admin"
}'
```

#### Role-Specific Query

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "What's my next delivery stop?",
    "role": "driver"
}'
```

#### Fleet Monitoring Example

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Which vehicles are due for maintenance this week?",
    "role": "admin"
}'
```

#### Route Optimization Example

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "I need to optimize delivery routes for tomorrow. We have 12 deliveries across the city.",
    "role": "logistics_coordinator"
}'
```

## Architecture

The system consists of several components:

1. **Coordinator Agent**: Central router that analyzes requests and directs them to specialized agents
2. **Route Optimizer Agent**: Specializes in delivery route planning and optimization
3. **Fleet Monitor Agent**: Tracks vehicle status, maintenance, and driver performance
4. **Data Retriever Agent**: Gets external data like weather forecasts and traffic conditions
5. **Notification Agent**: Sends alerts and notifications to relevant parties
6. **Web Interface**: Streamlit app providing chat interface with agent processing visualization
7. **API Server**: FastAPI service allowing external systems to use the agent capabilities

## Multi-turn Conversations

To maintain conversation context across multiple interactions, use the `session_id` parameter. The API will automatically track conversation history for that session.

### Example Multi-turn Conversation

**Turn 1: Initial query**

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Show me our fleet status",
    "role": "admin",
    "session_id": "session-123"
}'
```

**Turn 2: Follow-up query (using same session_id)**

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Which of those vehicles needs maintenance?",
    "role": "admin",
    "session_id": "session-123"
}'
```

**Turn 3: Another follow-up**

```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Schedule maintenance for VEH-101 for next Monday",
    "role": "admin",
    "session_id": "session-123"
}'
```

## Response Format

The API returns responses in a standardized format:

```json
{
  "output": {
    "content": "The answer to your query...",
    "additional_kwargs": {},
    "response_metadata": {
      "token_usage": {
        "completion_tokens": 123,
        "prompt_tokens": 456,
        "total_tokens": 579
      },
      "model_name": "claude-3-sonnet-20240229",
      "finish_reason": "stop",
      "content_filter_results": {
        "hate": {"filtered": false, "severity": "safe"},
        "self_harm": {"filtered": false, "severity": "safe"},
        "sexual": {"filtered": false, "severity": "safe"},
        "violence": {"filtered": false, "severity": "safe"}
      }
    },
    "type": "ai",
    "id": "run-session-123-1738528940",
    "example": false,
    "tool_calls": [],
    "invalid_tool_calls": [],
    "usage_metadata": {
      "input_tokens": 456,
      "output_tokens": 123,
      "total_tokens": 579,
      "input_token_details": {},
      "output_token_details": {}
    },
    "agent_used": "fleet_monitor"
  }
}
```

The main content is in the `output.content` field. The `agent_used` field indicates which specialized agent handled the query.

## Error Handling

If an error occurs, the response will include error information in the `additional_kwargs` field:

```json
{
  "output": {
    "content": "I apologize, but I encountered an error processing your request...",
    "additional_kwargs": {
      "error": "Error description here"
    },
    "response_metadata": {
      "token_usage": {
        "completion_tokens": 123,
        "prompt_tokens": 456,
        "total_tokens": 579
      },
      "model_name": "claude-3-sonnet-20240229",
      "finish_reason": "error",
      "content_filter_results": {
        "hate": {"filtered": false, "severity": "safe"},
        "self_harm": {"filtered": false, "severity": "safe"},
        "sexual": {"filtered": false, "severity": "safe"},
        "violence": {"filtered": false, "severity": "safe"}
      }
    },
    "type": "ai",
    "id": "error-session-123-1738528940",
    "example": false
  }
}
```

## Example Conversation Scenarios

### Supply Chain Planning Scenario

**User → Orchestrator:** "I need to plan delivery routes for tomorrow"

**Orchestrator → Supply Chain API:**
```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "I need to plan delivery routes for tomorrow",
    "role": "logistics_coordinator",
    "session_id": "planning-123"
}'
```

**API → Orchestrator:** Response with optimized routes

**User → Orchestrator:** "Will the weather affect these routes?"

**Orchestrator → Supply Chain API:**
```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Will the weather affect these routes?",
    "role": "logistics_coordinator",
    "session_id": "planning-123"
}'
```

**API → Orchestrator:** Response with weather impact analysis

### Fleet Management Scenario

**User → Orchestrator:** "Show me all vehicles that need maintenance"

**Orchestrator → Supply Chain API:**
```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Show me all vehicles that need maintenance",
    "role": "admin",
    "session_id": "fleet-456"
}'
```

**API → Orchestrator:** Response with maintenance needs

**User → Orchestrator:** "Schedule service for VEH-103"

**Orchestrator → Supply Chain API:**
```bash
curl --location 'http://localhost:8000/query' \
--header 'Content-Type: application/json' \
--data '{
    "input": "Schedule service for VEH-103",
    "role": "admin",
    "session_id": "fleet-456"
}'
```

**API → Orchestrator:** Response confirming service scheduling

## Development

### Project Structure

```
supply_chain_agents/
├── main.py                # CLI interface (alternative to web UI)
├── app.py                 # Streamlit web interface
├── api.py                 # FastAPI REST API
├── agents/
│   ├── __init__.py
│   ├── coordinator.py     # Central agent for routing requests
│   ├── route_optimizer.py # Route optimization specialist
│   ├── fleet_monitor.py   # Vehicle tracking and maintenance
│   ├── data_retriever.py  # Weather and traffic data fetching
│   └── notification.py    # Communication with drivers/admins
├── components/
│   └── agent_visualizer.py # Visualization of agent workflow
├── models/
│   ├── __init__.py
│   ├── vehicle.py         # Vehicle data models
│   ├── order.py           # Order and delivery models
│   └── user.py            # User profiles (driver, admin)
├── data/
│   ├── mock_orders.json   # Sample order data
│   ├── mock_vehicles.json # Sample vehicle data
│   └── mock_weather.json  # Sample weather conditions
└── utils/
    ├── __init__.py
    ├── cli.py             # CLI utilities
    └── api_mock.py        # Mocked API responses
```

### Extending the System

To add new agent capabilities:

1. Create a new agent file in the `agents/` directory
2. Update the coordinator agent to route appropriate requests to your new agent
3. Add the new agent to the agent network in both `app.py` and `api.py`
4. Update the UI and documentation to reflect the new capabilities

---

This project demonstrates how specialized AI agents can collaborate to provide comprehensive supply chain management solutions through both interactive and programmatic interfaces.