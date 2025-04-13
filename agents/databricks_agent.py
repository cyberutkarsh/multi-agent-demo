"""
Databricks Agent for deal scoring using Llama 4 serving endpoint
"""

import os
import json
import requests
import logging
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabricksAgent:
    """Agent for interacting with Databricks Llama 4 serving endpoint"""
    
    def __init__(self):
        """Initialize the Databricks agent"""
        self.host = os.getenv("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com")
        self.token = os.getenv("DATABRICKS_TOKEN")
        self.endpoint_name = "databricks-llama-4-maverick"
        self.endpoint_url = f"{self.host}/serving-endpoints/{self.endpoint_name}/invocations"
        self.last_response = None  # Store the last model response for UI display
        
        # Check if we have the token
        if not self.token:
            logger.warning("DATABRICKS_TOKEN not set, using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    def score_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single opportunity using Databricks Llama 4 model
        
        Args:
            opportunity: The opportunity to score
            
        Returns:
            Scored opportunity with win probability and next best product
        """
        if self.mock_mode:
            return self._mock_score_opportunity(opportunity)
        
        try:
            # Format request for the Llama 4 model
            prompt = self._create_scoring_prompt(opportunity)
            
            # Prepare the request data for Llama 4
            request_data = {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Set up headers
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Make API call
            logger.info(f"Calling Databricks Llama 4 endpoint: {self.endpoint_name}")
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract the model's response text
            if "choices" in result and len(result["choices"]) > 0 and "message" in result["choices"][0]:
                model_response = result["choices"][0]["message"]["content"]
                logger.info(f"Model response: {model_response}")
                
                # Store the last response for UI display
                self.last_response = model_response
                
                # Extract win probability and next best product from response
                win_probability, next_best_product = self._parse_llm_response(model_response, opportunity)
                
                # Return scored opportunity
                scored_opp = opportunity.copy()
                scored_opp["winProbability"] = win_probability
                scored_opp["nextBestProduct"] = next_best_product
                return scored_opp
            else:
                # Fallback if response format is unexpected
                logger.error(f"Unexpected response format: {result}")
                self.last_response = "Error: Unexpected response format from model"
                scored_opp = opportunity.copy()
                scored_opp["winProbability"] = 0.5
                scored_opp["nextBestProduct"] = "Unknown"
                return scored_opp
            
        except Exception as e:
            logger.error(f"Error scoring opportunity {opportunity.get('id', 'unknown')}: {str(e)}")
            self.last_response = f"Error: {str(e)}"
            # Apply default score for this opportunity
            scored_opp = opportunity.copy()
            scored_opp["winProbability"] = 0.5
            scored_opp["nextBestProduct"] = "Unknown"
            return scored_opp
    
    def score_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Score multiple opportunities using Databricks Llama 4 model
        
        Args:
            opportunities: List of opportunities to score
            
        Returns:
            Dictionary with scored opportunities
        """
        if self.mock_mode:
            return self._mock_score_opportunities(opportunities)
        
        scored_opportunities = []
        
        for opp in opportunities:
            scored_opp = self.score_opportunity(opp)
            scored_opportunities.append(scored_opp)
        
        return {"scored": scored_opportunities}
    
    def _create_scoring_prompt(self, opportunity: Dict[str, Any]) -> str:
        """
        Create a prompt for the Llama 4 model to score an opportunity
        
        Args:
            opportunity: The opportunity to score
            
        Returns:
            Prompt for the model
        """
        # Extract key opportunity details
        opp_id = opportunity.get("id", "unknown")
        amount = opportunity.get("amount", 0)
        industry = opportunity.get("industry", "Unknown")
        product = opportunity.get("product", "Unknown")
        region = opportunity.get("region", "Unknown")
        customer_size = opportunity.get("customer_size", "Unknown")
        existing_customer = opportunity.get("existing_customer", False)
        days_in_current_stage = opportunity.get("days_in_current_stage", 0)
        
        # Create a detailed prompt
        prompt = f"""As an expert sales analyst, evaluate the win probability of this sales opportunity and suggest the next best product to offer:

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

Consider that higher amounts typically have lower win rates, existing customers are more likely to close, and longer time in stage may indicate stalled deals.
"""
        return prompt
    
    def _parse_llm_response(self, response_text: str, opportunity: Dict[str, Any]) -> tuple:
        """
        Parse the LLM response to extract win probability and next best product
        
        Args:
            response_text: The response from the Llama 4 model
            opportunity: The original opportunity data for context
            
        Returns:
            Tuple of (win_probability, next_best_product)
        """
        try:
            # Extract win probability using regex
            import re
            
            # Look for the win probability
            prob_match = re.search(r"Win Probability:\s*(0\.\d+|1\.0|1)", response_text)
            if prob_match:
                win_probability = float(prob_match.group(1))
                # Ensure it's in the valid range
                win_probability = max(0.0, min(1.0, win_probability))
            else:
                # Fallback
                win_probability = 0.5
            
            # Look for next best product
            product_match = re.search(r"Next Best Product:\s*(.+?)(?:$|\n)", response_text)
            if product_match:
                next_best_product = product_match.group(1).strip()
            else:
                # Fallback based on industry
                industry = opportunity.get("industry", "").lower()
                if "tech" in industry:
                    next_best_product = "Cloud Security Suite"
                elif "health" in industry:
                    next_best_product = "Healthcare Analytics Platform"
                elif "finance" in industry:
                    next_best_product = "Financial Risk Assessment Tool"
                else:
                    next_best_product = "Enterprise Support Package"
            
            return win_probability, next_best_product
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return 0.5, "Unknown"
    
    def _mock_score_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock score for a single opportunity
        
        Args:
            opportunity: The opportunity to score
            
        Returns:
            Scored opportunity
        """
        scored_opp = opportunity.copy()
        
        # Generate mock win probability based on amount (higher amounts = lower probability)
        amount = float(opportunity.get("amount", 50000))
        industry = opportunity.get("industry", "Technology")
        
        # Base probability
        base_prob = 0.5
        
        # Adjust for amount
        amount_factor = max(0, min(0.3, 1 - (amount / 1000000)))
        
        # Adjust for industry
        industry_bonus = {
            "Technology": 0.2,
            "Healthcare": 0.15,
            "Finance": 0.1,
            "Retail": 0.05
        }.get(industry, 0)
        
        # Calculate win probability with some randomness
        win_prob = base_prob + amount_factor + industry_bonus + random.uniform(-0.1, 0.1)
        win_prob = max(0.1, min(0.9, win_prob))
        
        # Determine next best product based on industry and win probability
        if industry == "Technology":
            products = ["Cloud Security", "API Manager", "Data Warehouse"]
        elif industry == "Healthcare":
            products = ["Patient Portal", "Analytics Platform", "Compliance Suite"]
        elif industry == "Finance":
            products = ["Trading Platform", "Risk Assessment", "Fraud Detection"]
        else:
            products = ["CRM Enterprise", "Analytics Suite", "Support Package"]
            
        # Select product based on win probability
        if win_prob > 0.7:
            next_product = products[0]  # High-value product for high-probability deals
        elif win_prob > 0.4:
            next_product = products[1]  # Mid-tier product
        else:
            next_product = products[2]  # Entry-level product
        
        # Create mock Llama response for UI display
        self.last_response = f"""Analyzing opportunity {opportunity.get('id', 'unknown')}:
        
This is a {'high-value' if amount > 100000 else 'standard'} deal in the {industry} industry.
The customer is {'an existing' if opportunity.get('existing_customer', False) else 'a new'} customer.
They have been in the current stage for {opportunity.get('days_in_current_stage', 0)} days.

Based on these factors, I estimate:
Win Probability: {win_prob:.2f}
Next Best Product: {next_product}
"""
        
        scored_opp["winProbability"] = round(win_prob, 2)
        scored_opp["nextBestProduct"] = next_product
        return scored_opp
    
    def _mock_score_opportunities(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate mock scores for testing
        
        Args:
            opportunities: List of opportunities to score
            
        Returns:
            Dictionary with mock-scored opportunities
        """
        logger.info("Using mock scoring mode")
        
        scored_opportunities = []
        for opp in opportunities:
            scored_opp = self._mock_score_opportunity(opp)
            scored_opportunities.append(scored_opp)
        
        return {"scored": scored_opportunities}
