# Databricks Agent Documentation

This document provides comprehensive information about the `DatabricksAgent` class in the multi-agent demo system and how it integrates with the overall application.

## Overview

The `DatabricksAgent` is a specialized component responsible for scoring sales opportunities using the Databricks Llama 4 model serving endpoint. It analyzes opportunity data and returns win probability predictions and next best product recommendations.

## How the Databricks Agent Works

### Key Features

- **Opportunity Scoring**: Uses Databricks Llama 4 model to analyze sales opportunities and predict win probability
- **Next Best Product Recommendations**: Suggests the optimal next product to offer each customer
- **Mock Mode**: Falls back to simulated scoring if Databricks credentials are not available
- **Error Handling**: Gracefully handles API failures and connectivity issues

### Integration Points

The `DatabricksAgent` is primarily used in the Q2 Deal Prioritization workflow of the integrated application, where it:

1. Receives opportunity data from the Snowflake agent
2. Scores each opportunity using the Llama 4 model
3. Provides results to the Salesforce agent for updates and task creation

## Technical Implementation

### Authentication

The agent uses the following environment variables for authentication:
- `DATABRICKS_HOST`: The URL of your Databricks workspace (default: "https://your-workspace.cloud.databricks.com")
- `DATABRICKS_TOKEN`: Personal access token for API authentication

### API Interaction

When scoring opportunities, the agent:
1. Creates a prompt containing opportunity details
2. Sends the prompt to the Llama 4 serving endpoint
3. Parses the natural language response to extract structured data
4. Returns the scored opportunity with win probability and next best product

### Key Methods

- `score_opportunity()`: Scores a single opportunity
- `score_opportunities()`: Processes a batch of opportunities
- `_create_scoring_prompt()`: Formats opportunity data into a prompt for the LLM
- `_parse_llm_response()`: Extracts structured data from the LLM's response
- `_mock_score_opportunity()`: Provides simulated scoring when Databricks access is unavailable

## Status Message Streaming

The DatabricksAgent facilitates real-time feedback to users by storing and streaming status updates during API calls:

### How Status Messages Work

1. **LLM Response Storage**: The agent stores the full natural language response from Llama 4 in the `last_response` instance variable:
   ```python
   self.last_response = model_response
   ```

2. **Status Callbacks**: In `integrated_app.py`, status callbacks are used to display progress:
   ```python
   status_callback("databricks_score", f"🔄 DATABRICKS API: Scoring opportunity {i+1} of {len(opportunities)}\n"
                  f"→ Endpoint: /api/serving-endpoints/llama4-maverick/invocations\n"
                  f"→ Processing: {opp['id']} - {opp['name']}")
   ```

3. **UI Updates**: The status messages are displayed in the Streamlit UI through a container system:
   ```python
   # Create single blue status box for updates
   status_box = st.empty()
   
   def update_status(stage, message):
       with status_box.container():
           if "\n" in message:
               # For multi-line messages, create a more detailed display
               lines = message.split("\n")
               header = lines[0]
               st.info(header)
               
               # Display each detail line with proper formatting
               for line in lines[1:]:
                   if line.startswith("→ Win Probability:"):
                       st.markdown(f'<div class="api-detail api-analysis">{line}</div>', 
                                  unsafe_allow_html=True)
                   # Other formatting rules...
   ```

4. **Progress Tracking**: As each opportunity is processed, the UI updates to show:
   - Current progress (which opportunity is being processed)
   - The Databricks endpoint being called
   - Real-time scoring results
   - Summary statistics

5. **Rich Response Visualization**: For each scored opportunity, the UI displays:
   - Win probability with color-coded indicators (red/yellow/green)
   - Next best product recommendations
   - Analysis comments based on the Llama 4 response

### Streaming Implementation

The actual data flow works as follows:

1. **Databricks API Call**:
   ```python
   response = requests.post(
       self.endpoint_url,
       headers=headers,
       json=request_data,
       timeout=30
   )
   ```

2. **Response Parsing and Storage**:
   ```python
   model_response = result["choices"][0]["message"]["content"]
   self.last_response = model_response
   ```

3. **Real-time UI Updates**:
   ```python
   # For each opportunity
   for i, opp in enumerate(opportunities):
       # Update status to show current progress
       status_callback("databricks_score", f"🔄 DATABRICKS API: Scoring opportunity {i+1}...")
       
       # Call the agent to score this opportunity
       result = databricks_agent.score_opportunity(opp)
       
       # Show result for this opportunity with extracted insights
       insights = extract_insights(databricks_agent.last_response, opp['id'])
       status_callback("databricks_score", f"📊 {insights}")
   ```

4. **Progress Indicators**: The application uses a step container with progress tracking:
   ```python
   # Update progress display with current stage
   update_progress_display(step_container, steps, st.session_state.current_stage)
   ```

This streaming architecture provides users with a responsive experience and visibility into the scoring process, making the "black box" of ML model predictions more transparent and interpretable.

## Usage in Integrated App

In `integrated_app.py`, the `DatabricksAgent` is used during the Q2 Deal Prioritization workflow:

```python
# Initialize the Databricks agent
databricks_agent = DatabricksAgent()

# Score opportunities
status_callback("databricks_score", "Scoring opportunities with Llama 4 model...")
result = databricks_agent.score_opportunity(opp)
```

The workflow:
1. Fetches opportunity data from Snowflake
2. Passes each opportunity to the Databricks agent for scoring
3. Updates Salesforce with win probabilities and next best products
4. Creates follow-up tasks for high-probability opportunities
5. Stores summary data back in Snowflake

## LLM Prompt Engineering

The agent uses a carefully engineered prompt to guide the Llama 4 model:

```
As an expert sales analyst, evaluate the win probability of this sales opportunity and suggest the next best product to offer:

Opportunity Details:
- ID: {opp_id}
- Deal Amount: ${amount:,.2f}
- Industry: {industry}
- Current Product: {product}
- Region: {region}
- Customer Size: {customer_size}
- Existing Customer: {"Yes" if existing_customer else "No"}
- Days in Current Stage: {days_in_current_stage}

Based on these details, please provide:
1. The win probability as a decimal between 0.0 and 1.0
2. The recommended next best product to offer this customer

Format your response as:
Win Probability: [probability]
Next Best Product: [product name]
```

## Mock Mode

The agent includes a mock mode that simulates Llama 4 responses when DATABRICKS_TOKEN is not set. Mock scoring:

1. Generates realistic win probabilities based on opportunity attributes
2. Considers factors like industry and deal amount
3. Recommends appropriate next products based on win probability
4. Creates realistic LLM-like responses for UI display

## Error Handling

The agent includes robust error handling:
- API connection failures
- Response format errors
- Parsing issues

When errors occur, it falls back to a default probability (0.5) and generic product recommendation.

## Setup Requirements

To use the live Databricks Llama 4 endpoint:

1. Set up a Databricks workspace with the Llama 4 model serving endpoint
2. Configure environment variables in your `.env` file:
   ```
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=your-access-token
   ```

## Conclusion

The `DatabricksAgent` is a critical component in the Q2 Deal Prioritization workflow, using advanced LLM capabilities to score opportunities and provide intelligent recommendations to sales teams. 