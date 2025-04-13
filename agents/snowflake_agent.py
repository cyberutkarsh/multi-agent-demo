from typing import Dict, List, Any
from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
import json
import time
from datetime import datetime, timedelta
import random

# Sample opportunity data
SAMPLE_OPPORTUNITIES = [
    {"id": "opp_001", "amount": 250000, "accountId": "acct_A", "stage": "Proposal", "industry": "Finance", "monthlyVolume": 120000, "marketTrendScore": 0.8, "region": "East", "contactName": "Sarah Johnson", "lastActivity": "2023-05-15", "expectedCloseDate": "2023-06-30", "product": "Enterprise Analytics"},
    {"id": "opp_002", "amount": 75000, "accountId": "acct_B", "stage": "Negotiation", "industry": "Tech", "monthlyVolume": 50000, "marketTrendScore": 0.6, "region": "West", "contactName": "Michael Chen", "lastActivity": "2023-05-10", "expectedCloseDate": "2023-07-15", "product": "Data Integration"},
    {"id": "opp_003", "amount": 150000, "accountId": "acct_C", "stage": "Prospecting", "industry": "Retail", "monthlyVolume": 30000, "marketTrendScore": 0.4, "region": "Central", "contactName": "Jessica Smith", "lastActivity": "2023-05-12", "expectedCloseDate": "2023-08-01", "product": "Customer Analytics"},
    {"id": "opp_004", "amount": 320000, "accountId": "acct_D", "stage": "Discovery", "industry": "Healthcare", "monthlyVolume": 85000, "marketTrendScore": 0.75, "region": "Northeast", "contactName": "Robert Williams", "lastActivity": "2023-05-08", "expectedCloseDate": "2023-07-10", "product": "Healthcare Analytics Suite"},
    {"id": "opp_005", "amount": 95000, "accountId": "acct_E", "stage": "Qualification", "industry": "Manufacturing", "monthlyVolume": 42000, "marketTrendScore": 0.55, "region": "South", "contactName": "Amanda Garcia", "lastActivity": "2023-05-11", "expectedCloseDate": "2023-06-25", "product": "Supply Chain Insights"}
]

# Storage for summary rows
SUMMARY_ROWS = []

# Define request models
class SnowflakeQueryRequest(BaseModel):
    sql: str

class SnowflakeInsertRequest(BaseModel):
    table: str
    row: Dict[str, Any]

# Define response models
class SnowflakeQueryResponse(BaseModel):
    rows: List[Dict[str, Any]]

class SnowflakeInsertResponse(BaseModel):
    status: str

# Mock Snowflake service
class SnowflakeAgent:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()
        
    def setup_routes(self):
        @self.router.post("/snowflake/query", response_model=SnowflakeQueryResponse)
        async def query(request: SnowflakeQueryRequest):
            # Simulate query processing time
            time.sleep(0.5)
            
            # Mock SQL parsing - in a real app we'd actually parse the SQL
            if "opportunities" in request.sql.lower():
                return {"rows": SAMPLE_OPPORTUNITIES}
            else:
                return {"rows": []}
        
        @self.router.post("/snowflake/insert", response_model=SnowflakeInsertResponse)
        async def insert(request: SnowflakeInsertRequest):
            # Simulate insert processing time
            time.sleep(0.5)
            
            # Process the insert request
            if request.table == "analytics.fin_sales_priority_summary":
                SUMMARY_ROWS.append(request.row)
                return {"status": "ok"}
            else:
                raise HTTPException(status_code=400, detail=f"Table {request.table} not found")

    def snowflake_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the user input through the Snowflake agent.
        This function interfaces with the HTTP endpoints but is called directly in the agent workflow.
        """
        input_text = state.get("input", "")
        context = state.get("context", {})
        
        response = {
            "input": input_text,
            "context": context,
            "next": "END"
        }
        
        # Add agent-specific processing logic here if needed
        
        return response
    
    def get_all_opportunities(self):
        """Utility function to get all opportunities (for testing/debugging)"""
        return SAMPLE_OPPORTUNITIES
    
    def get_all_summary_rows(self):
        """Utility function to get all summary rows (for testing/debugging)"""
        return SUMMARY_ROWS

# For direct testing
def snowflake_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function to call from the agent workflow.
    """
    agent = SnowflakeAgent()
    return agent.snowflake_agent(state) 