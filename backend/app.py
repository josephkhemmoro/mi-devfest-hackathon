"""
MainStreet Copilot - Multi-Tenant SaaS Backend
FastAPI application with Supabase, WatsonX AI
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import Optional

from models import SignUpRequest, LoginRequest, AuthResponse, BusinessResponse
from pydantic import BaseModel
from auth import get_current_user
from fastapi import Depends
from db import get_supabase
from routers import inventory, employees, schedule, money, reminders, dashboard, permissions_admin, employee_invites

load_dotenv()

app = FastAPI(
    title="MainStreet Copilot API",
    description="Multi-tenant SaaS for small business operations",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(inventory.router)
app.include_router(employees.router)
app.include_router(employee_invites.router)
app.include_router(schedule.router)
app.include_router(money.router)
app.include_router(reminders.router)
app.include_router(dashboard.router)
app.include_router(permissions_admin.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "MainStreet Copilot API",
        "status": "running",
        "version": "1.0.0"
    }

# ==================== AUTHENTICATION ====================

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(signup_data: SignUpRequest):
    """
    Sign up new user and create business.
    
    Flow:
    1. Create business record
    2. Sign up user with Supabase Auth
    3. Store business_id in user metadata
    4. Return auth tokens + business info
    """
    supabase = get_supabase()
    
    try:
        # 1. Create business
        business_result = supabase.table("businesses").insert({
            "name": signup_data.business_name,
            "logo_url": None  # Will be updated after logo upload
        }).execute()
        
        business = business_result.data[0]
        business_id = business["id"]
        
        # 2. Sign up user with business_id in metadata
        auth_result = supabase.auth.sign_up({
            "email": signup_data.email,
            "password": signup_data.password,
            "options": {
                "data": {
                    "business_id": business_id,
                    "business_name": signup_data.business_name
                }
            }
        })
        
        if not auth_result.user:
            # Rollback: delete business if user creation failed
            supabase.table("businesses").delete().eq("id", business_id).execute()
            raise HTTPException(status_code=400, detail="User signup failed")
        
        # 3. Create profile record (first user is admin)
        supabase.table("profiles").insert({
            "id": auth_result.user.id,
            "business_id": business_id,
            "email": signup_data.email,
            "full_name": signup_data.business_name,  # Use business name as fallback
            "role": "admin"  # First user is always admin
        }).execute()
        
        # Check if session exists (it won't if email confirmation is required)
        if not auth_result.session:
            raise HTTPException(
                status_code=400, 
                detail="Please check your email to confirm your account, or disable email confirmation in Supabase Settings > Authentication > Email Auth"
            )
        
        # Get permissions for admin role
        from permissions import get_user_permissions
        user_permissions = get_user_permissions(auth_result.user.id)
        
        return {
            "access_token": auth_result.session.access_token,
            "refresh_token": auth_result.session.refresh_token,
            "user_id": auth_result.user.id,
            "business_id": business_id,
            "business_name": signup_data.business_name,
            "logo_url": None,
            "role": "admin",
            "permissions": user_permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(login_data: LoginRequest):
    """
    Login user and retrieve business info.
    
    Returns JWT token and business details for white-labeling.
    """
    supabase = get_supabase()
    
    try:
        # Sign in user
        print(f"[LOGIN] Attempting login for: {login_data.email}")
        auth_result = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })
        
        if not auth_result.user:
            print(f"[LOGIN] Auth failed - no user returned")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print(f"[LOGIN] Auth successful for user: {auth_result.user.id}")
        
        # Get business_id from user metadata
        business_id = auth_result.user.user_metadata.get("business_id")
        print(f"[LOGIN] Business ID from metadata: {business_id}")
        
        if not business_id:
            raise HTTPException(
                status_code=403,
                detail="No business associated with this account"
            )
        
        # Get business details
        print(f"[LOGIN] Fetching business details...")
        business_result = supabase.table("businesses")\
            .select("*")\
            .eq("id", business_id)\
            .execute()
        
        if not business_result.data:
            print(f"[LOGIN] Business not found for ID: {business_id}")
            raise HTTPException(status_code=404, detail="Business not found")
        
        business = business_result.data[0]
        print(f"[LOGIN] Business found: {business['name']}")
        
        # Get user profile with role and permissions
        print(f"[LOGIN] Fetching user profile...")
        profile_result = supabase.table("profiles")\
            .select("role, custom_permissions")\
            .eq("id", auth_result.user.id)\
            .single()\
            .execute()
        
        print(f"[LOGIN] Profile data: {profile_result.data}")
        role = profile_result.data.get("role", "employee") if profile_result.data else "employee"
        
        # Get all permissions for user
        print(f"[LOGIN] Getting permissions for role: {role}")
        from permissions import get_user_permissions
        user_permissions = get_user_permissions(auth_result.user.id)
        print(f"[LOGIN] Permissions: {user_permissions}")
        
        print(f"[LOGIN] Login successful!")
        return {
            "access_token": auth_result.session.access_token,
            "refresh_token": auth_result.session.refresh_token,
            "user_id": auth_result.user.id,
            "business_id": business_id,
            "business_name": business["name"],
            "logo_url": business.get("logo_url"),
            "role": role,
            "permissions": user_permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN ERROR] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")

@app.post("/api/auth/logout")
async def logout():
    """Logout user (client should delete tokens)"""
    return {"message": "Logged out successfully"}

# ==================== BUSINESS / LOGO UPLOAD ====================

@app.post("/api/business/upload-logo")
async def upload_logo(
    business_id: str,
    file: UploadFile = File(...)
):
    """
    Upload business logo to Supabase Storage.
    
    NOTE: In production, add authentication middleware to verify user owns this business.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PNG and JPEG allowed."
        )
    
    # Validate file size (3MB max)
    content = await file.read()
    if len(content) > 3 * 1024 * 1024:  # 3MB in bytes
        raise HTTPException(status_code=400, detail="File too large. Max 3MB.")
    
    supabase = get_supabase()
    
    try:
        # Upload to storage
        file_path = f"{business_id}/{file.filename}"
        
        storage_result = supabase.storage.from_("business-logos").upload(
            file_path,
            content,
            {"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_("business-logos").get_public_url(file_path)
        
        # Update business record
        supabase.table("businesses")\
            .update({"logo_url": public_url})\
            .eq("id", business_id)\
            .execute()
        
        return {"logo_url": public_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logo upload failed: {str(e)}")

@app.get("/api/business/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str):
    """Get business details"""
    supabase = get_supabase()
    
    result = supabase.table("businesses")\
        .select("*")\
        .eq("id", business_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return result.data[0]

# ==================== STORE HOURS ====================

class DayHours(BaseModel):
    open_time: str = "09:00"
    close_time: str = "17:00"
    closed: bool = False

class StoreHours(BaseModel):
    monday: DayHours = DayHours()
    tuesday: DayHours = DayHours()
    wednesday: DayHours = DayHours()
    thursday: DayHours = DayHours()
    friday: DayHours = DayHours()
    saturday: DayHours = DayHours()
    sunday: DayHours = DayHours()

@app.get("/api/business/store-hours")
async def get_store_hours(current_user: dict = Depends(get_current_user)):
    """Get business store hours by day"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    result = supabase.table("businesses")\
        .select("store_hours")\
        .eq("id", business_id)\
        .execute()
    
    if result.data and result.data[0] and result.data[0].get("store_hours"):
        return result.data[0]["store_hours"]
    
    # Default hours if not set (9 AM - 5 PM, closed Sunday)
    default_hours = {
        "monday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "tuesday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "wednesday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "thursday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "friday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "saturday": {"open_time": "09:00", "close_time": "17:00", "closed": False},
        "sunday": {"open_time": "09:00", "close_time": "17:00", "closed": True}
    }
    return default_hours

@app.put("/api/business/store-hours")
async def update_store_hours(
    hours: StoreHours,
    current_user: dict = Depends(get_current_user)
):
    """Update business store hours by day"""
    business_id = current_user["business_id"]
    supabase = get_supabase()
    
    # Convert Pydantic model to dict
    hours_dict = hours.model_dump()
    
    result = supabase.table("businesses")\
        .update({"store_hours": hours_dict})\
        .eq("id", business_id)\
        .execute()
    
    return {
        "message": "Store hours updated successfully!",
        "hours": hours_dict
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
