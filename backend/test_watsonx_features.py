"""Test WatsonX AI features for inventory and scheduling"""
from services.watsonx_client import watsonx_client
import json

def test_inventory_ordering():
    """Test AI-powered inventory order generation"""
    print("\n" + "=" * 60)
    print("TEST 1: INVENTORY ORDERING")
    print("=" * 60)
    
    # Sample inventory data
    items = [
        {"id": 1, "name": "French Fries", "current": 5, "min": 20},
        {"id": 2, "name": "Burger Buns", "current": 15, "min": 50},
        {"id": 3, "name": "Cheese", "current": 30, "min": 25},
        {"id": 4, "name": "Lettuce", "current": 2, "min": 15},
    ]
    
    print("\nInput Inventory:")
    for item in items:
        status = "📉 LOW" if item["current"] < item["min"] else "✅ OK"
        print(f"  {status} {item['name']}: {item['current']}/{item['min']}")
    
    print("\nGenerating order recommendations...")
    try:
        orders = watsonx_client.generate_inventory_orders(items)
        
        print("\n✅ ORDER GENERATED:")
        total_items = 0
        for order in orders:
            item = next(i for i in items if i["id"] == order["id"])
            print(f"  📦 {item['name']}: Order {order['order_qty']} units")
            total_items += order['order_qty']
        
        print(f"\nTotal items to order: {total_items}")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_employee_scheduling():
    """Test AI-powered employee scheduling"""
    print("\n" + "=" * 60)
    print("TEST 2: EMPLOYEE SCHEDULING")
    print("=" * 60)
    
    # Sample staffing rules
    staffing_rules = [
        {"day": "mon", "required": 3},
        {"day": "tue", "required": 3},
        {"day": "wed", "required": 4},
        {"day": "thu", "required": 4},
        {"day": "fri", "required": 5},
    ]
    
    # Sample employees
    employees = [
        {"id": 1, "name": "John", "strength": "strong", "availability": ["mon", "tue", "wed", "thu", "fri"]},
        {"id": 2, "name": "Sarah", "strength": "normal", "availability": ["mon", "wed", "fri"]},
        {"id": 3, "name": "Mike", "strength": "new", "availability": ["tue", "thu", "fri"]},
        {"id": 4, "name": "Lisa", "strength": "strong", "availability": ["mon", "tue", "wed"]},
        {"id": 5, "name": "Tom", "strength": "new", "availability": ["wed", "thu", "fri"]},
    ]
    
    print("\nStaffing Requirements:")
    for rule in staffing_rules:
        print(f"  {rule['day'].upper()}: {rule['required']} employees needed")
    
    print("\nAvailable Employees:")
    for emp in employees:
        days = ", ".join([d.upper() for d in emp["availability"]])
        print(f"  [{emp['strength'].upper()}] {emp['name']}: {days}")
    
    print("\nGenerating schedule...")
    try:
        shifts = watsonx_client.generate_schedule(
            week_start="2024-12-02",
            staffing_rules=staffing_rules,
            employees=employees
        )
        
        print("\n✅ SCHEDULE GENERATED:")
        
        # Group by day
        schedule_by_day = {}
        for shift in shifts:
            day = shift["day"]
            if day not in schedule_by_day:
                schedule_by_day[day] = []
            emp = next(e for e in employees if e["id"] == shift["employee_id"])
            schedule_by_day[day].append(emp)
        
        for day in ["mon", "tue", "wed", "thu", "fri"]:
            required = next(r["required"] for r in staffing_rules if r["day"] == day)
            assigned = schedule_by_day.get(day, [])
            status = "✅" if len(assigned) >= required else "⚠️"
            
            print(f"\n  {status} {day.upper()} (need {required}, have {len(assigned)}):")
            for emp in assigned:
                print(f"     - {emp['name']} ({emp['strength']})")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all WatsonX feature tests"""
    print("\n" + "=" * 60)
    print("WATSONX AI FEATURE TESTS")
    print("=" * 60)
    
    results = []
    
    # Test inventory
    results.append(("Inventory Ordering", test_inventory_ordering()))
    
    # Test scheduling  
    results.append(("Employee Scheduling", test_employee_scheduling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - WATSONX AI FULLY INTEGRATED!")
    else:
        print("⚠️ SOME TESTS FAILED - CHECK ERRORS ABOVE")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
