# Supply Chain Multi-Agent System
A comprehensive multi-agent system for supply chain management, powered by Anthropic Claude and LangGraph. This system provides specialized agents for route optimization, fleet monitoring, data retrieval, and notifications through both a web interface and an API.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [API Documentation](#api-documentation)
6. [Architecture](#architecture)
7. [Q2 Deal Prioritization System](#q2-deal-prioritization-system)
8. [Multi-turn Conversations](#multi-turn-conversations)
9. [Response Format](#response-format)
10. [Error Handling](#error-handling)
11. [Development](#development)

## Overview

This Supply Chain Multi-Agent System demonstrates the power of specialized AI agents working together to solve complex supply chain management tasks. The system features:

- A conversational Streamlit web interface
- A RESTful API for integration with external systems
- Specialized agents with different capabilities
- Multi-turn conversation support
- Visual tracking of agent processing
- Q2 Deal Prioritization workflow (new!)

## Features

- **Route Optimization**: Calculate optimal delivery routes considering traffic and weather
- **Fleet Monitoring**: Track vehicle status, maintenance needs, and driver performance
- **Data Retrieval**: Access weather forecasts, traffic conditions, and other external data
- **Notification System**: Send alerts and updates to relevant stakeholders
- **Role-Based Interface**: Different views for logistics coordinators, drivers, and administrators
- **API Integration**: Connect with external orchestrator agents and systems
- **Q2 Deal Prioritization**: Multi-agent workflow for scoring sales opportunities (new!)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/supply-chain-multi-agent.git
   cd supply-chain-multi-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

### Integrated Application

1. Run the integrated application (combines both Supply Chain System and Q2 Deal Prioritization):
   ```bash
   streamlit run integrated_app.py
   ```

2. Open your browser to [http://localhost:8501](http://localhost:8501)

3. Use the tabs at the top to switch between the Supply Chain System and Q2 Deal Prioritization dashboard

4. For the Supply Chain System:
   - Select your role (Logistics Coordinator, Driver, or Administrator)
   - Start interacting with the agents through the chat interface

5. For Q2 Deal Prioritization:
   - Click "Run Q2 Deal Prioritization with Llama 4" to start the workflow
   - View the real-time status updates and final results

### Streamlit Web Interface (Supply Chain Only)

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

### Q2 Deal Prioritization System

1. Run the Q2 Deal Prioritization API:
   ```bash
   python q2_deal_prioritization.py
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
| `/run-workflow` | POST | Run the Q2 deal prioritization workflow |
| `/snowflake/query` | POST | Query data from Snowflake |
| `/snowflake/insert` | POST | Insert data into Snowflake |
| `/databricks/score` | POST | Score opportunities using Databricks |
| `/salesforce/opportunity/{id}` | PATCH | Update an opportunity in Salesforce |
| `/salesforce/task` | POST | Create a task in Salesforce |

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

## Q2 Deal Prioritization System

The Q2 Deal Prioritization system is a Multi-Agent workflow that:

1. Pulls raw opportunity data from Snowflake
2. Scores each deal in Databricks
3. Writes scores and follow-up tasks back into Salesforce
4. Inserts a summary row back into Snowflake for dashboards

### Components

1. **OrchestratorAgent**: Central coordinator that drives the entire flow by calling each service in sequence
2. **SnowflakeAgent**: Handles data queries and inserts for Snowflake
3. **DatabricksAgent**: Scores opportunities based on defined criteria
4. **SalesforceAgent**: Updates opportunities and creates follow-up tasks

### Data Models

- **Opportunity**: Basic sales opportunity data with amount, industry, etc.
- **ScoredOpportunity**: Opportunity with win probability and next best product
- **SummaryRow**: Aggregated data about high-priority deals for dashboards

### Workflow Sequence

1. Trigger the system with a "run Q2 prioritization" command
2. Fetch raw opportunity data from Snowflake
3. Score deals using the Databricks model
4. Update Salesforce with scores and create follow-up tasks
5. Write summary data back to Snowflake
6. Return a comprehensive results report

### Using the Q2 Deal Prioritization API

```bash
# Run the Q2 Deal Prioritization workflow
curl --location 'http://localhost:8000/run-workflow' \
--header 'Content-Type: application/json' \
--data '{
    "command": "run Q2 prioritization"
}'

# Query opportunities from Snowflake
curl --location 'http://localhost:8000/snowflake/query' \
--header 'Content-Type: application/json' \
--data '{
    "sql": "SELECT * FROM sales.opportunities"
}'

# Score opportunities with Databricks
curl --location 'http://localhost:8000/databricks/score' \
--header 'Content-Type: application/json' \
--data '{
    "model": "prod_fin_sales_v2",
    "data": [
        {"id":"opp_001","amount":250000,"accountId":"acct_A","stage":"Proposal","industry":"Finance","monthlyVolume":120000,"marketTrendScore":0.8}
    ]
}'
```

### Error Handling

The system implements the following error handling strategies:
- **5xx responses** from any agent: retry up to 2× with exponential backoff
- **DatabricksAgent failure**: abort the entire flow and report an error
- **SalesforceAgent 4xx** on a particular record: log that record's ID and continue with the rest

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
├── integrated_app.py      # Combined app with Supply Chain & Q2 Deal Prioritization
├── agents/
│   ├── __init__.py
│   ├── coordinator.py     # Central agent for routing requests
│   ├── route_optimizer.py # Route optimization specialist
│   ├── fleet_monitor.py   # Vehicle tracking and maintenance
│   ├── data_retriever.py  # Weather and traffic data fetching
│   ├── notification.py    # Communication with drivers/admins
│   ├── databricks_agent.py # Deal scoring with Llama 4
│   ├── salesforce_agent.py # CRM updates and task creation
│   └── snowflake_agent.py  # Data warehouse interaction
├── components/
│   └── agent_visualizer.py # Visualization of agent workflow
├── models/
│   ├── __init__.py
│   ├── vehicle.py         # Vehicle data models
│   ├── order.py           # Order and delivery models
│   └── user.py            # User profiles (driver, admin)
├── databricks/
│   └── DATABRICKS_AGENT_README.md # Documentation for Databricks integration
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