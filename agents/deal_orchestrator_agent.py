from typing import Dict, List, Any, Optional
from fastapi import FastAPI, APIRouter, Request, HTTPException
from pydantic import BaseModel
import json
import time
import requests
from datetime import datetime, timedelta
import aiohttp
import asyncio

class OrchestratorAgent:
    def __init__(self, base_url="http://localhost:8000"):
        """
        Initialize the orchestrator with the base URL for API calls.
        Default is localhost:8000, but can be changed for testing.
        """
        self.base_url = base_url
        self.retry_config = {
            "max_retries": 2,
            "backoff_factor": 1.5
        }
    
    async def fetch_opportunities(self, session):
        """Fetch raw opportunity data from Snowflake"""
        snowflake_query_url = f"{self.base_url}/snowflake/query"
        query_payload = {
            "sql": "SELECT * FROM sales.opportunities WHERE close_date > CURRENT_DATE"
        }
        
        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                async with session.post(snowflake_query_url, json=query_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["rows"]
                    elif 500 <= response.status < 600:
                        if attempt < self.retry_config["max_retries"]:
                            # Calculate backoff time
                            backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                            print(f"Snowflake query failed with status {response.status}. Retrying in {backoff_time}s...")
                            await asyncio.sleep(backoff_time)
                            continue
                    # Non-retriable error
                    response.raise_for_status()
            except Exception as e:
                if attempt < self.retry_config["max_retries"]:
                    backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                    print(f"Error fetching from Snowflake: {str(e)}. Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"Failed to fetch from Snowflake after {self.retry_config['max_retries']} retries: {str(e)}")
                    raise
        
        raise Exception("Failed to fetch opportunities from Snowflake")
    
    async def score_opportunities(self, session, opportunities):
        """Score the opportunities using Databricks"""
        if not opportunities:
            return []
            
        databricks_score_url = f"{self.base_url}/databricks/score"
        score_payload = {
            "model": "prod_fin_sales_v2",
            "data": opportunities
        }
        
        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                async with session.post(databricks_score_url, json=score_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["scored"]
                    elif 500 <= response.status < 600:
                        if attempt < self.retry_config["max_retries"]:
                            backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                            print(f"Databricks scoring failed with status {response.status}. Retrying in {backoff_time}s...")
                            await asyncio.sleep(backoff_time)
                            continue
                    # For Databricks, we abort the entire flow for any failure as per requirements
                    print(f"Databricks scoring failed with status {response.status}")
                    raise Exception(f"Critical error: Databricks scoring failed with status {response.status}")
            except Exception as e:
                if attempt < self.retry_config["max_retries"]:
                    backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                    print(f"Error scoring opportunities: {str(e)}. Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"Critical error: Failed to score opportunities after {self.retry_config['max_retries']} retries")
                    raise Exception(f"Critical error in Databricks: {str(e)}")
        
        raise Exception("Failed to score opportunities in Databricks")
    
    async def update_salesforce(self, session, scored_opportunities):
        """Update Salesforce with scores and create follow-up tasks"""
        if not scored_opportunities:
            return []
            
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        high_priority_count = 0
        total_pipeline_value = 0
        error_records = []
        updated_records = []
        created_tasks = []
        
        for opp in scored_opportunities:
            # Update the opportunity
            sf_update_url = f"{self.base_url}/salesforce/opportunity/{opp['id']}"
            update_payload = {
                "Win_Probability__c": opp["winProbability"],
                "Next_Best_Product__c": opp["nextBestProduct"]
            }
            
            try:
                async with session.patch(sf_update_url, json=update_payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        updated_records.append(result)
                        
                        # Create follow-up task
                        sf_task_url = f"{self.base_url}/salesforce/task"
                        task_payload = {
                            "WhatId": opp["id"],
                            "Subject": "Follow up on high-priority deal",
                            "ActivityDate": tomorrow
                        }
                        
                        async with session.post(sf_task_url, json=task_payload) as task_response:
                            if task_response.status == 200:
                                task_result = await task_response.json()
                                created_tasks.append(task_result)
                            else:
                                print(f"Failed to create task for opportunity {opp['id']}: {task_response.status}")
                        
                        # Track high priority deals
                        if opp["winProbability"] > 0.8:
                            high_priority_count += 1
                            total_pipeline_value += opp["amount"]
                    elif 400 <= response.status < 500:
                        # For 4xx errors, log and continue
                        error_records.append(opp["id"])
                        print(f"Non-critical error updating Salesforce for {opp['id']}: {response.status}")
                    elif 500 <= response.status < 600:
                        # For 5xx errors, retry
                        retry_success = False
                        for retry in range(self.retry_config["max_retries"]):
                            backoff_time = self.retry_config["backoff_factor"] * (2 ** retry)
                            await asyncio.sleep(backoff_time)
                            print(f"Retrying Salesforce update for {opp['id']} after {backoff_time}s...")
                            
                            async with session.patch(sf_update_url, json=update_payload) as retry_response:
                                if retry_response.status == 200:
                                    retry_result = await retry_response.json()
                                    updated_records.append(retry_result)
                                    retry_success = True
                                    break
                        
                        if not retry_success:
                            error_records.append(opp["id"])
                            print(f"Failed to update Salesforce for {opp['id']} after {self.retry_config['max_retries']} retries")
            except Exception as e:
                error_records.append(opp["id"])
                print(f"Error updating Salesforce for opportunity {opp['id']}: {str(e)}")
        
        return {
            "high_priority_count": high_priority_count,
            "total_pipeline_value": total_pipeline_value,
            "updated_records": updated_records,
            "created_tasks": created_tasks,
            "error_records": error_records
        }
    
    async def write_summary(self, session, summary_data):
        """Write summary data back to Snowflake"""
        snowflake_insert_url = f"{self.base_url}/snowflake/insert"
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary_payload = {
            "table": "analytics.fin_sales_priority_summary",
            "row": {
                "runDate": today,
                "highPriorityCount": summary_data["high_priority_count"],
                "totalPipelineValue": summary_data["total_pipeline_value"]
            }
        }
        
        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                async with session.post(snowflake_insert_url, json=summary_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif 500 <= response.status < 600:
                        if attempt < self.retry_config["max_retries"]:
                            backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                            print(f"Snowflake insert failed with status {response.status}. Retrying in {backoff_time}s...")
                            await asyncio.sleep(backoff_time)
                            continue
                    response.raise_for_status()
            except Exception as e:
                if attempt < self.retry_config["max_retries"]:
                    backoff_time = self.retry_config["backoff_factor"] * (2 ** attempt)
                    print(f"Error inserting to Snowflake: {str(e)}. Retrying in {backoff_time}s...")
                    await asyncio.sleep(backoff_time)
                else:
                    print(f"Failed to insert summary to Snowflake after {self.retry_config['max_retries']} retries: {str(e)}")
                    raise
        
        raise Exception("Failed to write summary to Snowflake")
    
    async def run_workflow(self):
        """Run the entire Q2 deal prioritization workflow"""
        async with aiohttp.ClientSession() as session:
            try:
                print("Starting Q2 deal prioritization workflow")
                
                # Step 1: Fetch raw data from Snowflake
                print("Step 1: Fetching opportunities from Snowflake")
                opportunities = await self.fetch_opportunities(session)
                print(f"Retrieved {len(opportunities)} opportunities")
                
                # Step 2: Score deals in Databricks
                print("Step 2: Scoring opportunities in Databricks")
                scored_opportunities = await self.score_opportunities(session, opportunities)
                print(f"Scored {len(scored_opportunities)} opportunities")
                
                # Step 3: Update Salesforce
                print("Step 3: Updating Salesforce")
                sf_results = await self.update_salesforce(session, scored_opportunities)
                print(f"Updated {len(sf_results['updated_records'])} opportunities in Salesforce")
                print(f"Created {len(sf_results['created_tasks'])} follow-up tasks")
                if sf_results["error_records"]:
                    print(f"Failed to update {len(sf_results['error_records'])} records: {sf_results['error_records']}")
                
                # Step 4: Write summary to Snowflake
                print("Step 4: Writing summary to Snowflake")
                summary_result = await self.write_summary(session, sf_results)
                print("Summary written successfully")
                
                # Step 5: Return final state
                return {
                    "status": "success",
                    "opportunities": scored_opportunities,
                    "tasks": sf_results["created_tasks"],
                    "summary": {
                        "runDate": datetime.now().strftime("%Y-%m-%d"),
                        "highPriorityCount": sf_results["high_priority_count"],
                        "totalPipelineValue": sf_results["total_pipeline_value"]
                    },
                    "errors": sf_results["error_records"]
                }
                
            except Exception as e:
                print(f"Workflow failed: {str(e)}")
                return {
                    "status": "error",
                    "message": str(e)
                }
    
    async def orchestrator_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the user input through the Orchestrator agent.
        This runs the workflow asynchronously and returns results.
        """
        input_text = state.get("input", "")
        context = state.get("context", {})
        
        # Run the workflow if the input contains the trigger phrase
        if "run q2 prioritization" in input_text.lower():
            try:
                # Run the workflow using the current event loop
                result = await self.run_workflow()
                
                # Update context with the results
                context["deal_workflow_result"] = result
                
                # Prepare response message
                response_message = "Q2 deal prioritization workflow completed successfully."
                if result["status"] == "error":
                    response_message = f"Q2 deal prioritization workflow failed: {result['message']}"
                
                return {
                    "input": input_text,
                    "context": context,
                    "next": "END",
                    "message": response_message
                }
            except Exception as e:
                return {
                    "input": input_text,
                    "context": context,
                    "next": "END",
                    "message": f"Error in Q2 deal prioritization workflow: {str(e)}"
                }
        else:
            return {
                "input": input_text,
                "context": context,
                "next": "END",
                "message": "I didn't recognize that command. Try 'run Q2 prioritization' to start the deal scoring workflow."
            }

# For direct testing
def deal_orchestrator_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function to call from the agent workflow.
    """
    agent = OrchestratorAgent()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(agent.orchestrator_agent(state))
    loop.close()
    return result 