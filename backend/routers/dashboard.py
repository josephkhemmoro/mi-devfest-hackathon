from fastapi import APIRouter, Depends
from models import DashboardStats
from auth import get_current_user
from db import get_supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    business_id = current_user["business_id"]
    supabase = get_supabase()
    inventory_result = supabase.table("inventory_items")\
        .select("current_quantity, minimum_quantity")\
        .eq("business_id", business_id)\
        .execute()
    
    total_inventory = len(inventory_result.data)
    low_stock = sum(1 for item in inventory_result.data if 0 < item["current_quantity"] < item["minimum_quantity"])
    out_of_stock = sum(1 for item in inventory_result.data if item["current_quantity"] == 0)
    employees_result = supabase.table("profiles")\
        .select("is_active")\
        .eq("business_id", business_id)\
        .execute()
    
    total_employees = len(employees_result.data)
    active_employees = sum(1 for emp in employees_result.data if emp.get("is_active", True))
    today = datetime.now().date()
    week_from_now = today + timedelta(days=7)
    earliest_week_start = today - timedelta(days=7)
    
    shifts_result = supabase.table("shifts")\
        .select("week_start, day_of_week")\
        .eq("business_id", business_id)\
        .gte("week_start", earliest_week_start.isoformat())\
        .lte("week_start", week_from_now.isoformat())\
        .execute()
    
    day_offset = {
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    upcoming_shifts = 0
    for shift in shifts_result.data:
        week_start = datetime.fromisoformat(shift['week_start']).date()
        shift_date = week_start + timedelta(days=day_offset[shift['day_of_week']])
        if today <= shift_date <= week_from_now:
            upcoming_shifts += 1
    
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    today_day = day_names[today.weekday()]
    
    reminders_result = supabase.table("reminders")\
        .select("*")\
        .eq("business_id", business_id)\
        .eq("day_of_week", today_day)\
        .eq("active", True)\
        .order("time_of_day")\
        .execute()
    
    return {
        "total_inventory_items": total_inventory,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "upcoming_shifts": upcoming_shifts,
        "todays_reminders": reminders_result.data
    }
