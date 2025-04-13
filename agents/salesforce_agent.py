from typing import Dict, List, Any, Optional
from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
import time
from datetime import datetime, timedelta

# Storage for Salesforce data
OPPORTUNITIES = {}
TASKS = {}

# Define request models
class SalesforceOpportunityUpdateRequest(BaseModel):
    Win_Probability__c: float
    Next_Best_Product__c: str

class SalesforceTaskRequest(BaseModel):
    WhatId: str
    Subject: str
    ActivityDate: str

# Define response models
class SalesforceOpportunityResponse(BaseModel):
    id: str
    updated: bool

class SalesforceTaskResponse(BaseModel):
    id: str
    created: bool

# Mock Salesforce service
class SalesforceAgent:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()
        
    def setup_routes(self):
        @self.router.patch("/salesforce/opportunity/{id}", response_model=SalesforceOpportunityResponse)
        async def update_opportunity(id: str, request: SalesforceOpportunityUpdateRequest):
            # Simulate processing time
            time.sleep(0.5)
            
            # Store the opportunity update
            if id not in OPPORTUNITIES:
                OPPORTUNITIES[id] = {}
                
            OPPORTUNITIES[id].update({
                "Win_Probability__c": request.Win_Probability__c,
                "Next_Best_Product__c": request.Next_Best_Product__c,
                "updated_at": datetime.now().isoformat()
            })
            
            return {"id": id, "updated": True}
        
        @self.router.post("/salesforce/task", response_model=SalesforceTaskResponse)
        async def create_task(request: SalesforceTaskRequest):
            # Simulate processing time
            time.sleep(0.3)
            
            # Generate a unique task ID
            task_id = f"task_{len(TASKS) + 1:03d}"
            
            # Store the task
            TASKS[task_id] = {
                "WhatId": request.WhatId,
                "Subject": request.Subject,
                "ActivityDate": request.ActivityDate,
                "created_at": datetime.now().isoformat()
            }
            
            return {"id": task_id, "created": True}

    def salesforce_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the user input through the Salesforce agent.
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
        """Utility function to get all updated opportunities (for testing/debugging)"""
        return OPPORTUNITIES
    
    def get_all_tasks(self):
        """Utility function to get all created tasks (for testing/debugging)"""
        return TASKS

# For direct testing
def salesforce_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function to call from the agent workflow.
    """
    agent = SalesforceAgent()
    return agent.salesforce_agent(state) 