"""Permission checking utilities and decorators"""
from fastapi import HTTPException, Depends
from typing import List, Callable
from auth import get_current_user
from db import get_supabase
from functools import wraps

# Define all available permissions
class Permissions:
    # Dashboard
    VIEW_DASHBOARD = "view_dashboard"
    EDIT_DASHBOARD = "edit_dashboard"
    
    # Inventory
    VIEW_INVENTORY = "view_inventory"
    EDIT_INVENTORY = "edit_inventory"
    GENERATE_ORDERS = "generate_orders"
    
    # Employees
    VIEW_EMPLOYEES = "view_employees"
    EDIT_EMPLOYEES = "edit_employees"
    MANAGE_PERMISSIONS = "manage_permissions"
    
    # Schedule
    VIEW_SCHEDULE = "view_schedule"
    EDIT_SCHEDULE = "edit_schedule"
    GENERATE_SCHEDULE = "generate_schedule"
    SET_AVAILABILITY = "set_availability"
    
    # Financials
    VIEW_FINANCIALS = "view_financials"
    EDIT_FINANCIALS = "edit_financials"
    
    # Reminders
    VIEW_REMINDERS = "view_reminders"
    EDIT_REMINDERS = "edit_reminders"
    SET_REMINDERS = "set_reminders"
    
    # Business
    EDIT_BUSINESS = "edit_business"

# Default permissions for each role
ROLE_PERMISSIONS = {
    "admin": [
        # Admin has ALL permissions
        Permissions.VIEW_DASHBOARD,
        Permissions.EDIT_DASHBOARD,
        Permissions.VIEW_INVENTORY,
        Permissions.EDIT_INVENTORY,
        Permissions.GENERATE_ORDERS,
        Permissions.VIEW_EMPLOYEES,
        Permissions.EDIT_EMPLOYEES,
        Permissions.MANAGE_PERMISSIONS,
        Permissions.VIEW_SCHEDULE,
        Permissions.EDIT_SCHEDULE,
        Permissions.GENERATE_SCHEDULE,
        Permissions.SET_AVAILABILITY,
        Permissions.VIEW_FINANCIALS,
        Permissions.EDIT_FINANCIALS,
        Permissions.VIEW_REMINDERS,
        Permissions.EDIT_REMINDERS,
        Permissions.SET_REMINDERS,
        Permissions.EDIT_BUSINESS,
    ],
    "employee": [
        # Employee has limited default permissions
        Permissions.VIEW_DASHBOARD,
        Permissions.VIEW_INVENTORY,
        Permissions.VIEW_SCHEDULE,
        Permissions.SET_AVAILABILITY,
        Permissions.VIEW_REMINDERS,
        Permissions.SET_REMINDERS,
    ]
}

def get_user_permissions(user_id: str) -> List[str]:
    """Get all permissions for a user (role + custom)"""
    supabase = get_supabase()
    
    # Get user profile
    result = supabase.table("profiles")\
        .select("role, custom_permissions")\
        .eq("id", user_id)\
        .eq("is_active", True)\
        .single()\
        .execute()
    
    if not result.data:
        return []
    
    role = result.data.get("role", "employee")
    custom_permissions = result.data.get("custom_permissions", [])
    
    # Admin gets all permissions
    if role == "admin":
        return ROLE_PERMISSIONS["admin"]
    
    # Get role default permissions
    role_perms = set(ROLE_PERMISSIONS.get(role, []))
    
    # Add custom permissions
    custom_perms = set(custom_permissions) if isinstance(custom_permissions, list) else set()
    
    # Combine and return
    all_perms = role_perms.union(custom_perms)
    return list(all_perms)

def has_permission(user: dict, permission: str) -> bool:
    """Check if user has a specific permission"""
    # Admin always has permission
    if user.get("role") == "admin":
        return True
    
    # Get user's permissions
    user_permissions = get_user_permissions(user["user_id"])
    
    return permission in user_permissions

def require_permission(permission: str):
    """
    Dependency to require a specific permission for an endpoint.
    Usage: @router.get("/", dependencies=[Depends(require_permission(Permissions.VIEW_INVENTORY))])
    """
    async def check_permission(current_user: dict = Depends(get_current_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required permission: {permission}"
            )
        return current_user
    
    return check_permission

def require_any_permission(*permissions: str):
    """
    Dependency to require ANY of the listed permissions.
    Usage: dependencies=[Depends(require_any_permission(Permissions.EDIT_INVENTORY, Permissions.ADMIN))]
    """
    async def check_any_permission(current_user: dict = Depends(get_current_user)):
        user_perms = get_user_permissions(current_user["user_id"])
        
        if not any(perm in user_perms for perm in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required one of: {', '.join(permissions)}"
            )
        return current_user
    
    return check_any_permission

def require_all_permissions(*permissions: str):
    """
    Dependency to require ALL of the listed permissions.
    Usage: dependencies=[Depends(require_all_permissions(Permissions.VIEW_INVENTORY, Permissions.EDIT_INVENTORY))]
    """
    async def check_all_permissions(current_user: dict = Depends(get_current_user)):
        user_perms = get_user_permissions(current_user["user_id"])
        
        if not all(perm in user_perms for perm in permissions):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required all of: {', '.join(permissions)}"
            )
        return current_user
    
    return check_all_permissions

def require_admin():
    """Dependency to require admin role"""
    async def check_admin(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        return current_user
    
    return check_admin
