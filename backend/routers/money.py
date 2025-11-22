"""Financial tracking routes"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import FinancialsCreate, FinancialsResponse
from auth import get_current_user
from db import get_supabase
from services.watsonx_client import watsonx_client
import json

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

@router.get("/summary")
async def get_financial_summary(
    current_user: dict = Depends(get_current_user),
    month: str = None  # Format: YYYY-MM
):
    """Get financial summary (totals) for current business, optionally filtered by month"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    query = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)
    
    # Filter by month if provided
    if month:
        # Get records where week_start is in the specified month
        start_date = f"{month}-01"
        # Calculate last day of month
        year, mon = month.split("-")
        if mon == "12":
            end_date = f"{int(year)+1}-01-01"
        else:
            end_date = f"{year}-{int(mon)+1:02d}-01"
        
        query = query.gte("week_start", start_date).lt("week_start", end_date)
    
    result = query.execute()
    
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
        "record_count": len(result.data),
        "month": month
    }

@router.get("/by-month")
async def get_financials_by_month(current_user: dict = Depends(get_current_user)):
    """Get financials grouped by month"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    result = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .order("week_start", desc=False)\
        .execute()
    
    # Group by month
    monthly_data = {}
    for record in result.data:
        month = record["week_start"][:7]  # Extract YYYY-MM
        
        if month not in monthly_data:
            monthly_data[month] = {
                "month": month,
                "total_revenue": 0,
                "total_expenses": 0,
                "total_profit": 0,
                "weeks": []
            }
        
        monthly_data[month]["total_revenue"] += record.get("gross_sales", 0)
        monthly_data[month]["total_expenses"] += record.get("total_expenses", 0)
        monthly_data[month]["total_profit"] += record.get("net_profit", 0)
        monthly_data[month]["weeks"].append(record)
    
    # Calculate profit margins
    monthly_list = []
    for month, data in monthly_data.items():
        data["profit_margin"] = round((data["total_profit"] / data["total_revenue"] * 100), 1) if data["total_revenue"] > 0 else 0
        data["total_revenue"] = round(data["total_revenue"], 2)
        data["total_expenses"] = round(data["total_expenses"], 2)
        data["total_profit"] = round(data["total_profit"], 2)
        monthly_list.append(data)
    
    return sorted(monthly_list, key=lambda x: x["month"], reverse=True)

@router.post("/analyze")
async def analyze_financials_with_ai(
    current_user: dict = Depends(get_current_user),
    month: str = None  # Optional: analyze specific month
):
    """Use Watson AI to analyze financial data and provide insights"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Get financial data
    query = supabase.table("weekly_financials")\
        .select("*")\
        .eq("business_id", business_id)\
        .order("week_start", desc=True)
    
    if month:
        start_date = f"{month}-01"
        year, mon = month.split("-")
        if mon == "12":
            end_date = f"{int(year)+1}-01-01"
        else:
            end_date = f"{year}-{int(mon)+1:02d}-01"
        query = query.gte("week_start", start_date).lt("week_start", end_date)
    
    result = query.execute()
    
    if not result.data:
        return {"error": "No financial data available for analysis"}
    
    # Prepare summary for AI
    total_revenue = sum(r.get("gross_sales", 0) for r in result.data)
    total_expenses = sum(r.get("total_expenses", 0) for r in result.data)
    
    # Aggregate expenses by category
    expense_categories = {
        "Cost of Goods Sold": sum(r.get("cogs", 0) for r in result.data),
        "Payroll": sum(r.get("payroll", 0) for r in result.data),
        "Rent": sum(r.get("rent", 0) for r in result.data),
        "Utilities": sum(r.get("utilities", 0) for r in result.data),
        "Supplies": sum(r.get("supplies", 0) for r in result.data),
        "Marketing": sum(r.get("marketing", 0) for r in result.data),
        "Maintenance": sum(r.get("maintenance", 0) for r in result.data),
        "Insurance": sum(r.get("insurance", 0) for r in result.data),
        "Processing Fees": sum(r.get("processing_fees", 0) for r in result.data),
        "Other": sum(r.get("other_expenses", 0) for r in result.data)
    }
    
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Find best and worst performing weeks for comparison
    weeks_sorted = sorted(result.data, key=lambda x: x.get('profit_margin', 0), reverse=True)
    best_week = weeks_sorted[0] if weeks_sorted else None
    worst_week = weeks_sorted[-1] if len(weeks_sorted) > 1 else None
    recent_week = result.data[0] if result.data else None  # Most recent (already desc sorted)
    
    # Calculate averages for comparison
    avg_revenue = total_revenue / len(result.data) if result.data else 0
    avg_profit_margin = sum(r.get('profit_margin', 0) for r in result.data) / len(result.data) if result.data else 0
    
    # Determine if current situation is critical
    is_critical = profit_margin < 10 or (recent_week and recent_week.get('profit_margin', 0) < 10)
    
    comparison_data = ""
    if best_week and recent_week:
        comparison_data = f"""
BEST WEEK: Week of {best_week.get('week_start')} - {best_week.get('profit_margin', 0):.1f}% margin, ${best_week.get('net_profit', 0):,.0f} profit
RECENT WEEK: Week of {recent_week.get('week_start')} - {recent_week.get('profit_margin', 0):.1f}% margin, ${recent_week.get('net_profit', 0):,.0f} profit
AVERAGE: {avg_profit_margin:.1f}% margin, ${avg_revenue:,.0f} weekly revenue"""
    
    # Create enhanced prompt for Watson
    prompt = f"""You are a financial analyst for a small business. Analyze this data and provide actionable insights.

CURRENT PERFORMANCE:
Revenue: ${total_revenue:,.2f} | Expenses: ${total_expenses:,.2f} | Profit: ${net_profit:,.2f} ({profit_margin:.1f}%)
Status: {"🚨 CRITICAL - Under 10% margin" if is_critical else "⚠️ Warning - Below 20% target" if profit_margin < 20 else "✅ Healthy"}

TOP EXPENSE CATEGORIES:
{chr(10).join([f'{cat}: ${amt:,.2f} ({amt/total_expenses*100:.1f}% of expenses)' for cat, amt in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:3] if amt > 0])}
{comparison_data}

{"🚨 CRITICAL SITUATION DETECTED - Focus on immediate cost reduction!" if is_critical else ""}

Return ONLY this format:

{"CRITICAL ISSUES (address immediately)" if is_critical else "KEY INSIGHTS"}
• {f"Profit margin at {profit_margin:.1f}% - need immediate action" if is_critical else "[insight about revenue or efficiency]"}
• {f"Compare to best week: {best_week.get('profit_margin', 0):.1f}% vs current {recent_week.get('profit_margin', 0) if recent_week else 0:.1f}%" if best_week and recent_week else "[comparison or trend insight]"}
• [Third insight about expenses or opportunities]

WHAT'S DIFFERENT FROM GOOD WEEKS
• {f"Best week had ${best_week.get('gross_sales', 0) - (recent_week.get('gross_sales', 0) if recent_week else 0):,.0f} more revenue" if best_week and recent_week else "[revenue difference]"}
• {f"Expenses {abs(best_week.get('total_expenses', 0)/(best_week.get('gross_sales', 1) or 1)*100 - (recent_week.get('total_expenses', 0)/(recent_week.get('gross_sales', 1) or 1)*100)) if recent_week else 0:.1f}% higher than best performing week" if best_week and recent_week else "[expense difference]"}

IMMEDIATE COST SAVINGS (with $ amounts)
• [Specific expense to cut with dollar amount]
• [Another cost reduction opportunity with amount]

RECOMMENDATIONS TO MATCH BEST PERFORMANCE
1. [Specific action to increase revenue]
2. [Specific action to reduce largest expense]
3. [Specific action to improve efficiency]

Keep responses concise and actionable. Focus on comparing current to best performance."""

    try:
        # Call Watson AI using the existing client
        model = watsonx_client._get_model()
        print("   🤖 Analyzing financial data with WatsonX AI...")
        response = model.generate_text(prompt=prompt)
        print("   ✅ Received AI analysis")
        
        # Clean up response - remove any extra text before/after the format
        analysis = response.strip()
        
        # If Watson added extra text, extract only the formatted section
        # Look for either "KEY INSIGHTS" or "CRITICAL ISSUES"
        start_markers = ["CRITICAL ISSUES", "KEY INSIGHTS"]
        start_idx = -1
        for marker in start_markers:
            if marker in analysis:
                start_idx = analysis.find(marker)
                break
        
        if start_idx >= 0:
            # Find end (after 3rd recommendation)
            lines = analysis[start_idx:].split('\n')
            rec_count = 0
            end_idx = start_idx
            for i, line in enumerate(lines):
                if line.strip().startswith(('1.', '2.', '3.')):
                    rec_count += 1
                    if rec_count == 3:
                        # Found the 3rd recommendation, include next line break
                        end_idx = start_idx + len('\n'.join(lines[:i+1]))
                        break
            
            if end_idx > start_idx:
                analysis = analysis[start_idx:end_idx].strip()
        
        # Add performance comparison data
        performance_comparison = None
        if best_week and recent_week:
            performance_comparison = {
                "best_week": {
                    "week_start": best_week.get('week_start'),
                    "profit_margin": round(best_week.get('profit_margin', 0), 1),
                    "net_profit": round(best_week.get('net_profit', 0), 2),
                    "gross_sales": round(best_week.get('gross_sales', 0), 2)
                },
                "recent_week": {
                    "week_start": recent_week.get('week_start'),
                    "profit_margin": round(recent_week.get('profit_margin', 0), 1),
                    "net_profit": round(recent_week.get('net_profit', 0), 2),
                    "gross_sales": round(recent_week.get('gross_sales', 0), 2)
                },
                "average": {
                    "profit_margin": round(avg_profit_margin, 1),
                    "weekly_revenue": round(avg_revenue, 2)
                }
            }
        
        return {
            "month": month,
            "period_weeks": len(result.data),
            "is_critical": is_critical,
            "summary": {
                "revenue": round(total_revenue, 2),
                "expenses": round(total_expenses, 2),
                "profit": round(net_profit, 2),
                "profit_margin": round(profit_margin, 1)
            },
            "performance_comparison": performance_comparison,
            "expense_breakdown": {k: round(v, 2) for k, v in expense_categories.items() if v > 0},
            "ai_analysis": analysis
        }
        
    except Exception as e:
        print(f"[WATSON ERROR] {str(e)}")
        return {
            "error": "AI analysis temporarily unavailable",
            "summary": {
                "revenue": round(total_revenue, 2),
                "expenses": round(total_expenses, 2),
                "profit": round(net_profit, 2),
                "profit_margin": round(profit_margin, 1)
            }
        }

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
