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
        
        # Validate credentials
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY is required")
        if not self.project_id:
            raise ValueError("WATSONX_PROJECT_ID is required")
        if self.api_key.startswith("ApiKey-"):
            raise ValueError(
                "Invalid API key format! You provided the Key ID instead of the actual key.\n"
                "Go to https://cloud.ibm.com/iam/apikeys and create a NEW key.\n"
                "Copy the LONG string shown (NOT the Key ID)."
            )
        
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
        print(f"   📝 Raw response: {response[:500]}...")
        
        # Parse JSON response - be very robust
        response_text = response.strip()
        
        # Try to extract JSON from markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Find ALL JSON objects and pick the best one (non-empty)
        try:
            all_json_objects = []
            i = 0
            while i < len(response_text):
                if response_text[i] == '{':
                    # Found start of a JSON object
                    start = i
                    brace_count = 0
                    end = start
                    for j in range(start, len(response_text)):
                        if response_text[j] == '{':
                            brace_count += 1
                        elif response_text[j] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = j + 1
                                break
                    
                    # Extract this JSON object
                    json_text = response_text[start:end]
                    try:
                        parsed = json.loads(json_text)
                        all_json_objects.append(parsed)
                        print(f"   🔍 Found JSON object: {json_text}")
                    except json.JSONDecodeError:
                        pass  # Skip invalid JSON
                    
                    i = end
                else:
                    i += 1
            
            # Filter to only objects with 'orders' key (ignore example data)
            valid_results = [obj for obj in all_json_objects if 'orders' in obj]
            print(f"   📊 Found {len(valid_results)} valid order objects (out of {len(all_json_objects)} total JSON)")
            
            # Pick the best result: prefer non-empty orders array
            best_result = None
            for obj in valid_results:
                if len(obj['orders']) > 0:
                    best_result = obj
                    break
            
            # If no non-empty found, use the last valid one
            if not best_result and valid_results:
                best_result = valid_results[-1]
            
            if best_result:
                print(f"   ✅ Selected result: {best_result}")
                print(f"   📦 Generated {len(best_result.get('orders', []))} order recommendations")
                return best_result.get("orders", [])
            else:
                print("   ❌ No valid JSON found")
                return []
        except (ValueError, json.JSONDecodeError) as e:
            print(f"   ❌ Failed to parse JSON: {e}")
            print(f"   Response text: {response_text[:200]}...")
            return []
    
    def generate_schedule(
        self, 
        week_start: str, 
        shift_slots: List[Dict], 
        employees: List[Dict],
        preferences: str = "",
        current_schedule: List[Dict] = None,
        store_hours: Dict = None
    ) -> List[Dict[str, Any]]:
        """
        Generate optimal employee schedule using WatsonX based on shift slots.
        
        Input:
        - week_start: "2024-01-01"
        - shift_slots: [{"day_of_week": "fri", "slot_name": "morning", "start_time": "09:00", "end_time": "13:00", "required_count": 2}]
        - employees: [{"id": 1, "strength": "shiftleader", "availability": ["fri"]}]
        
        Output: [{"employee_id": 1, "day": "fri", "start_time": "09:00", "end_time": "13:00"}]
        """
        print("🤖 Calling WatsonX AI for schedule generation...")
        print(f"   Week starting: {week_start}")
        print(f"   {len(employees)} employees, {len(shift_slots)} shift slots to fill")
        print(f"   📊 Shift Slots: {json.dumps(shift_slots, indent=2)}")
        
        if preferences.strip():
            preferences_section = f"""

🚨 CRITICAL USER REQUIREMENTS (HIGHEST PRIORITY - MUST FOLLOW):
{preferences}

YOU MUST STRICTLY FOLLOW THESE REQUIREMENTS WHEN SELECTING EMPLOYEES.
For example:
- If it says "shift leader only on weekends", ONLY assign employees with strength="shiftleader" on Saturday and Sunday
- If it says "no new employees on busy days", do NOT assign employees with strength="new" on those days
- These preferences override all other rules

"""
        else:
            preferences_section = ""
        
        if preferences.strip():
            print(f"\n   💬 AI Preferences provided by user:")
            print(f"      \"{preferences}\"")
            print(f"   ⚠️  AI MUST follow these preferences when selecting employees!")
        else:
            print(f"   💬 No AI preferences provided - using default rules only")
        
        current_schedule_section = ""
        if current_schedule:
            current_schedule_section = f"\n\nCurrent Schedule (you can modify/improve this):\n{json.dumps(current_schedule, indent=2)}\n"
        
        store_hours_section = ""
        if store_hours:
            store_hours_section = f"\n\nStore Hours (schedule shifts within these times):\n{json.dumps(store_hours, indent=2)}\n"
        
        prompt = f"""You are a scheduling AI for a small business. Create an optimal employee schedule based on shift slots.

🎯 YOUR PRIMARY GOAL: For each shift slot below, create EXACTLY "required_count" shifts with different employees.
{preferences_section}
EMPLOYEE ROLES (CRITICAL - READ THE "strength" FIELD):
Each employee has a "strength" field that defines their role:
- "shiftleader" = SHIFT LEADER (experienced, can supervise)
- "normal" = REGULAR EMPLOYEE (standard worker)
- "new" = NEW EMPLOYEE (needs supervision)

IMPORTANT: Weekends = Saturday (sat) and Sunday (sun) ONLY

CRITICAL RULES - SHIFT SLOT SCHEDULING:
1. For EVERY shift slot listed below, create exactly "required_count" number of shifts
2. Each shift MUST use the EXACT "start_time" and "end_time" from the slot - DO NOT modify times
3. Example: If Monday has a slot "morning" with required_count: 1, start_time: "09:00", end_time: "13:00"
   → Create 1 shift: {{"employee_id": "...", "day": "mon", "start_time": "09:00", "end_time": "13:00"}}
4. Example: If Friday has a slot "evening" with required_count: 3, start_time: "18:00", end_time: "22:00"
   → Create 3 shifts with 3 DIFFERENT employees, all with same times: "18:00" to "22:00"
5. The "day_of_week" in slots uses 3-letter codes (mon, tue, wed, thu, fri, sat, sun) - use these exact codes in your output

Other Rules:
1. ONLY schedule employees who are available on that day (check their "availability" array)
2. NEVER schedule the same employee for multiple overlapping time slots
3. ONLY schedule shifts during store operating hours (skip days marked as "closed": true)
4. When selecting employees, CHECK THE "strength" FIELD - employees with "shiftleader" are shift leaders
5. Distribute shifts evenly across employees throughout the week
6. If not enough staff available for a slot, assign as many as possible (but try to meet required_count)

Week Start: {week_start}

Shift Slots to Fill (create "required_count" shifts for EACH slot below):
{json.dumps(shift_slots, indent=2)}{store_hours_section}

Available Employees:
{json.dumps(employees, indent=2)}{current_schedule_section}

Return ONLY valid JSON in this exact format:
{{"shifts": [{{"employee_id": "uuid-here", "day": "fri", "start_time": "09:00", "end_time": "17:00"}}]}}

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
