"""Financial tracking routes"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import FinancialsCreate, FinancialsResponse
from auth import get_current_user
from db import get_supabase

router = APIRouter(prefix="/api/financials", tags=["financials"])

def calculate_financials(financials: dict) -> dict:
    """Calculate total expenses, net profit, and margins"""
    # Calculate total expenses
    total_expenses = sum([
        financials.get('payroll', 0),
        financials.get('cogs', 0),
        financials.get('rent', 0),
        financials.get('utilities', 0),
        financials.get('supplies', 0),
        financials.get('marketing', 0),
        financials.get('maintenance', 0),
        financials.get('insurance', 0),
        financials.get('processing_fees', 0),
        financials.get('other_expenses', 0)
    ])
    
    gross_sales = financials.get('gross_sales', 0)
    payroll = financials.get('payroll', 0)
    
    # Calculate net profit
    net_profit = gross_sales - total_expenses
    
    # Calculate profit margin percentage
    profit_margin = round((net_profit / gross_sales * 100), 1) if gross_sales > 0 else 0.0
    
    # Calculate payroll percentage
    payroll_pct = round((payroll / gross_sales * 100), 1) if gross_sales > 0 else 0.0
    
    return {
        'total_expenses': round(total_expenses, 2),
        'net_profit': round(net_profit, 2),
        'profit_margin': profit_margin,
        'payroll_pct': payroll_pct
    }

def get_financial_status(profit_margin: float) -> str:
    """Determine status color based on profit margin"""
    if profit_margin >= 20:
        return "green"
    elif profit_margin >= 10:
        return "yellow"
    else:
        return "red"

@router.get("/", response_model=List[FinancialsResponse])
async def get_financials(current_user: dict = Depends(get_current_user)):
    """Get all financial records for current business"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    result = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .order("week_start", desc=True)\
        .execute()
    
    # Add status based on profit margin
    financials_with_status = []
    for record in result.data:
        record["status"] = get_financial_status(record.get("profit_margin", 0))
        financials_with_status.append(record)
    
    return financials_with_status

@router.post("/", response_model=FinancialsResponse)
async def create_financial_record(
    financials: FinancialsCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new financial record"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Check for duplicate week
    week_start_str = financials.week_start.isoformat()
    
    existing = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .eq("week_start", week_start_str)\
        .execute()
    
    if existing.data:
        raise HTTPException(
            status_code=400,
            detail=f"Financial record already exists for week starting {week_start_str}. Use PUT to update."
        )
    
    # Build financial data with all expense categories
    financial_data = {
        "business_id": business_id,
        "week_start": week_start_str,
        "gross_sales": financials.gross_sales,
        "payroll": financials.payroll,
        "cogs": financials.cogs,
        "rent": financials.rent,
        "utilities": financials.utilities,
        "supplies": financials.supplies,
        "marketing": financials.marketing,
        "maintenance": financials.maintenance,
        "insurance": financials.insurance,
        "processing_fees": financials.processing_fees,
        "other_expenses": financials.other_expenses
    }
    
    # Calculate derived fields
    calculated = calculate_financials(financial_data)
    financial_data.update(calculated)
    
    result = supabase.table("weekly_financials").insert(financial_data).execute()
    
    record = result.data[0]
    record["status"] = get_financial_status(calculated['profit_margin'])
    
    return record

@router.put("/{week_start}", response_model=FinancialsResponse)
async def update_financial_record(
    week_start: str,
    financials: FinancialsCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update financial record for a specific week"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Verify record exists
    existing = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .eq("week_start", week_start)\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Financial record not found")
    
    # Build update data with all expense categories
    update_data = {
        "gross_sales": financials.gross_sales,
        "payroll": financials.payroll,
        "cogs": financials.cogs,
        "rent": financials.rent,
        "utilities": financials.utilities,
        "supplies": financials.supplies,
        "marketing": financials.marketing,
        "maintenance": financials.maintenance,
        "insurance": financials.insurance,
        "processing_fees": financials.processing_fees,
        "other_expenses": financials.other_expenses
    }
    
    # Calculate derived fields
    calculated = calculate_financials(update_data)
    update_data.update(calculated)
    
    result = supabase.table("weekly_financials")\
        .update(update_data)\
        .eq("business_id", business_id)\
        .eq("week_start", week_start)\
        .execute()
    
    record = result.data[0]
    record["status"] = get_financial_status(calculated['profit_margin'])
    
    return record

@router.get("/summary")
async def get_financial_summary(current_user: dict = Depends(get_current_user)):
    """Get financial summary (totals) for current business"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    result = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .execute()
    
    if not result.data:
        return {
            "total_revenue": 0,
            "total_expenses": 0,
            "total_profit": 0,
            "avg_profit_margin": 0,
            "record_count": 0
        }
    
    # Calculate totals
    total_revenue = sum(r.get("gross_sales", 0) for r in result.data)
    total_expenses = sum(r.get("total_expenses", 0) for r in result.data)
    total_profit = sum(r.get("net_profit", 0) for r in result.data)
    avg_profit_margin = sum(r.get("profit_margin", 0) for r in result.data) / len(result.data)
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "total_profit": round(total_profit, 2),
        "avg_profit_margin": round(avg_profit_margin, 1),
        "record_count": len(result.data)
    }

@router.delete("/{week_start}")
async def delete_financial_record(
    week_start: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete financial record"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    supabase.table("weekly_financials")\
        .delete()\
        .eq("business_id", business_id)\
        .eq("week_start", week_start)\
        .execute()
    
    return {"message": "Financial record deleted"}
