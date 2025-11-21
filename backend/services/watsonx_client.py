"""IBM WatsonX AI client for inventory and scheduling"""
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

class WatsonXClient:
    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        
        # Require WatsonX credentials - no fallback
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY environment variable is required")
        if not self.project_id:
            raise ValueError("WATSONX_PROJECT_ID environment variable is required")
        
        print("=" * 60)
        print("🤖 WATSONX AI ENABLED")
        print("=" * 60)
        print(f"Model: meta-llama/llama-3-3-70b-instruct")
        print(f"Project ID: {self.project_id[:8]}...")
        print(f"API Key: {self.api_key[:10]}...")
        print("=" * 60)
        
        self.credentials = {
            "url": self.url,
            "apikey": self.api_key
        }
        
        self.model_id = "meta-llama/llama-3-3-70b-instruct"
        
        self.parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 1000,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.3,
            GenParams.REPETITION_PENALTY: 1.1
        }
    
    def _get_model(self):
        """Initialize WatsonX model"""
        return Model(
            model_id=self.model_id,
            params=self.parameters,
            credentials=self.credentials,
            project_id=self.project_id
        )
    
    def generate_inventory_orders(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate smart inventory orders using WatsonX.
        
        Input: [{"id": 1, "name": "Fries", "current": 5, "min": 20}]
        Output: [{"id": 1, "order_qty": 15}]
        """
        print("🤖 Calling WatsonX AI for inventory ordering...")
        print(f"   Processing {len(items)} items")
        
        prompt = f"""You are an inventory management AI. Given a list of items with current and minimum quantities, calculate how much to order for each item.

Rules:
- If current >= min: order_qty = 0 (no order needed)
- If current < min: order_qty = (min - current) + buffer
- Add a 20% buffer for items marked as low stock
- Return ONLY valid JSON, no explanations

Input items:
{json.dumps(items, indent=2)}

Return a JSON object in this exact format:
{{"orders": [{{"id": 1, "order_qty": 15}}]}}

JSON Response:"""

        model = self._get_model()
        print("   Sending request to WatsonX Llama-3.3-70B...")
        response = model.generate_text(prompt=prompt)
        print("   ✅ Received response from WatsonX AI")
        
        # Parse JSON response
        response_text = response.strip()
        
        # Try to extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        print(f"   📦 Generated {len(result.get('orders', []))} order recommendations")
        return result.get("orders", [])
    
    def generate_schedule(
        self, 
        week_start: str, 
        staffing_rules: List[Dict], 
        employees: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Generate optimal employee schedule using WatsonX.
        
        Input:
        - week_start: "2024-01-01"
        - staffing_rules: [{"day": "fri", "required": 5}]
        - employees: [{"id": 1, "strength": "strong", "availability": ["fri"]}]
        
        Output: [{"employee_id": 1, "day": "fri"}]
        """
        print("🤖 Calling WatsonX AI for schedule generation...")
        print(f"   Week starting: {week_start}")
        print(f"   {len(employees)} employees, {len(staffing_rules)} days to schedule")
        
        prompt = f"""You are a scheduling AI for a small business. Create an optimal employee schedule.

Rules:
1. ONLY schedule employees who are available that day
2. NEVER schedule the same employee twice in one day
3. Meet the required staff count for each day
4. Pair STRONG employees with NEW employees when possible
5. Distribute shifts evenly across employees
6. If not enough staff available, schedule as many as possible

Week Start: {week_start}

Staffing Requirements:
{json.dumps(staffing_rules, indent=2)}

Available Employees:
{json.dumps(employees, indent=2)}

Return ONLY valid JSON in this exact format:
{{"shifts": [{{"employee_id": 1, "day": "fri"}}]}}

JSON Response:"""

        model = self._get_model()
        print("   Sending request to WatsonX Llama-3.3-70B...")
        response = model.generate_text(prompt=prompt)
        print("   ✅ Received response from WatsonX AI")
        
        # Parse JSON response
        response_text = response.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        shifts = result.get("shifts", [])
        print(f"   📅 Generated {len(shifts)} shifts across the week")
        return shifts

# Singleton instance
watsonx_client = WatsonXClient()
