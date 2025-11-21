"""Admin routes for managing user permissions"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import (
    PermissionResponse,
    UserPermissionsResponse,
    UpdateUserPermissions,
    UpdateUserRole
)
from auth import get_current_user
from db import get_supabase
from permissions import require_permission, Permissions, get_user_permissions, ROLE_PERMISSIONS

router = APIRouter(prefix="/api/admin/permissions", tags=["admin-permissions"])

@router.get("/all", response_model=List[PermissionResponse])
async def get_all_permissions(current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))):
    """Get list of all available permissions"""
    supabase = get_supabase()
    
    result = supabase.table("permissions")\
        .select("*")\
        .order("category, name")\
        .execute()
    
    return result.data

@router.get("/users", response_model=List[UserPermissionsResponse])
async def get_all_users_permissions(current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))):
    """Get all users in the business with their permissions"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Get all users in business with emails
    users_result = supabase.table("profiles")\
        .select("id, email, full_name, role, custom_permissions, is_active")\
        .eq("business_id", business_id)\
        .order("full_name")\
        .execute()
    
    users_with_permissions = []
    for user in users_result.data:
        user_id = user["id"]
        role = user.get("role", "employee")
        custom_perms = user.get("custom_permissions", [])
        
        # Get email from profiles
        email = user.get("email", "No email")
        
        # Get all permissions for this user
        all_perms = get_user_permissions(user_id)
        
        users_with_permissions.append({
            "user_id": user_id,
            "full_name": user["full_name"],
            "email": email,
            "role": role,
            "custom_permissions": custom_perms,
            "all_permissions": all_perms,
            "is_active": user.get("is_active", True)
        })
    
    return users_with_permissions

@router.get("/users/{user_id}", response_model=UserPermissionsResponse)
async def get_user_permissions_detail(
    user_id: str,
    current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))
):
    """Get detailed permissions for a specific user"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Get user profile
    user_result = supabase.table("profiles")\
        .select("id, full_name, email, role, custom_permissions, is_active, business_id")\
        .eq("id", user_id)\
        .single()\
        .execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify user belongs to same business
    if user_result.data["business_id"] != business_id:
        raise HTTPException(status_code=403, detail="User belongs to different business")
    
    user = user_result.data
    role = user.get("role", "employee")
    custom_perms = user.get("custom_permissions", [])
    all_perms = get_user_permissions(user_id)
    
    return {
        "user_id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "role": role,
        "custom_permissions": custom_perms,
        "all_permissions": all_perms,
        "is_active": user.get("is_active", True)
    }

@router.put("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def update_user_custom_permissions(
    user_id: str,
    permissions_update: UpdateUserPermissions,
    current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))
):
    """Update custom permissions for a user"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Verify user exists and belongs to same business
    user_result = supabase.table("profiles")\
        .select("id, business_id, role")\
        .eq("id", user_id)\
        .single()\
        .execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_result.data["business_id"] != business_id:
        raise HTTPException(status_code=403, detail="User belongs to different business")
    
    # Prevent admin from removing their own admin permissions
    if user_id == current_user["user_id"] and user_result.data["role"] == "admin":
        raise HTTPException(
            status_code=403,
            detail="Cannot modify your own admin permissions"
        )
    
    # Update custom permissions
    update_result = supabase.table("profiles")\
        .update({"custom_permissions": permissions_update.custom_permissions})\
        .eq("id", user_id)\
        .execute()
    
    # Log the change
    supabase.table("permission_audit_log").insert({
        "business_id": business_id,
        "admin_id": current_user["user_id"],
        "target_user_id": user_id,
        "action": "update_permissions",
        "changes": {
            "custom_permissions": permissions_update.custom_permissions
        }
    }).execute()
    
    # Return updated user permissions
    return await get_user_permissions_detail(user_id, current_user)

@router.put("/users/{user_id}/role", response_model=UserPermissionsResponse)
async def update_user_role(
    user_id: str,
    role_update: UpdateUserRole,
    current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))
):
    """Update role for a user"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Verify user exists and belongs to same business
    user_result = supabase.table("profiles")\
        .select("id, business_id, role")\
        .eq("id", user_id)\
        .single()\
        .execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_result.data["business_id"] != business_id:
        raise HTTPException(status_code=403, detail="User belongs to different business")
    
    # Prevent admin from changing their own role
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Cannot change your own role"
        )
    
    # Update role
    old_role = user_result.data["role"]
    update_result = supabase.table("profiles")\
        .update({"role": role_update.role})\
        .eq("id", user_id)\
        .execute()
    
    # Log the change
    supabase.table("permission_audit_log").insert({
        "business_id": business_id,
        "admin_id": current_user["user_id"],
        "target_user_id": user_id,
        "action": "update_role",
        "changes": {
            "old_role": old_role,
            "new_role": role_update.role
        }
    }).execute()
    
    # Return updated user permissions
    return await get_user_permissions_detail(user_id, current_user)

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))
):
    """Deactivate a user account"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Verify user exists and belongs to same business
    user_result = supabase.table("profiles")\
        .select("id, business_id")\
        .eq("id", user_id)\
        .single()\
        .execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_result.data["business_id"] != business_id:
        raise HTTPException(status_code=403, detail="User belongs to different business")
    
    # Prevent admin from deactivating themselves
    if user_id == current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="Cannot deactivate your own account"
        )
    
    # Deactivate user
    supabase.table("profiles")\
        .update({"is_active": False})\
        .eq("id", user_id)\
        .execute()
    
    # Log the change
    supabase.table("permission_audit_log").insert({
        "business_id": business_id,
        "admin_id": current_user["user_id"],
        "target_user_id": user_id,
        "action": "deactivate_user",
        "changes": {"is_active": False}
    }).execute()
    
    return {"message": "User deactivated successfully"}

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: dict = Depends(require_permission(Permissions.MANAGE_PERMISSIONS))
):
    """Reactivate a user account"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Verify user exists and belongs to same business
    user_result = supabase.table("profiles")\
        .select("id, business_id")\
        .eq("id", user_id)\
        .single()\
        .execute()
    
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_result.data["business_id"] != business_id:
        raise HTTPException(status_code=403, detail="User belongs to different business")
    
    # Activate user
    supabase.table("profiles")\
        .update({"is_active": True})\
        .eq("id", user_id)\
        .execute()
    
    # Log the change
    supabase.table("permission_audit_log").insert({
        "business_id": business_id,
        "admin_id": current_user["user_id"],
        "target_user_id": user_id,
        "action": "activate_user",
        "changes": {"is_active": True}
    }).execute()
    
    return {"message": "User activated successfully"}
