# 👑 Admin Access & Employee Management System

## Complete Guide to Admin Features

---

## 🎯 How Admin Access Works

### **1. First User = Automatic Admin**
When you sign up and create a business:
- ✅ You automatically become **Admin**
- ✅ Your role is set to `"admin"` in the database
- ✅ You get **all 18 permissions** immediately
- ✅ You see "• Admin" in the header after your business name

**Code Location:** `backend/app.py` line 96
```python
"role": "admin"  # First user is always admin
```

---

### **2. How to Give Employee Admin Access**

**Option A: Promote to Full Admin Role**
1. Go to **"Manage Access"** in navigation (purple background, shield icon)
2. Find the employee in the table
3. Click **"Edit"** button next to their name
4. At the top of the modal, click **"Switch to Admin Role"**
5. Confirm the change
6. ✅ Employee now has **full admin access** with all permissions

**Option B: Grant Specific Permissions** (without making them admin)
1. Go to **"Manage Access"**
2. Click **"Edit"** next to employee
3. Check/uncheck specific permission boxes:
   - ✅ Edit Inventory
   - ✅ Generate Orders
   - ✅ Edit Schedule
   - ✅ View Financials
   - etc.
4. Click **"Save Permissions"**
5. ✅ Employee gets those specific permissions only

---

## 📧 NEW: Invite Employees via Email

### **How It Works:**

1. **Admin clicks "Invite via Email"** button on Employees page
2. **Fills out invite form**:
   - Email address
   - Full name
   - Role (Employee or Admin)
3. **System creates account automatically** with:
   - ✅ Supabase Auth user
   - ✅ Profile in your business
   - ✅ Temporary password (secure, random-generated)
4. **Admin gets temporary password** to share with employee
5. **Employee logs in** with:
   - Email: (the one you entered)
   - Password: (temporary password shown)
6. **Employee changes password** on first login (recommended)

---

## 🔐 Security Features

### **Password Security:**
- Temporary passwords are **12 characters** long
- Include: letters, numbers, special characters
- Generated using `secrets` module (cryptographically secure)

### **Email Confirmation:**
- Auto-confirmed when invited by admin
- No need for email verification link
- Employee can login immediately

### **Business Isolation:**
- Employees can only be invited to **your business**
- Can't access other businesses' data
- RLS (Row Level Security) enforces this at database level

---

## 🎯 Permission System Overview

### **18 Total Permissions Across 6 Categories:**

#### **Dashboard (2)**
- `view_dashboard` - View dashboard and statistics
- `edit_dashboard` - Edit dashboard settings

#### **Inventory (3)**
- `view_inventory` - View inventory items
- `edit_inventory` - Add/edit/delete items
- `generate_orders` - AI-powered ordering

#### **Employees (3)**
- `view_employees` - View employee list
- `edit_employees` - Add/edit/delete employees
- `manage_permissions` - **Admin only** - Manage user access

#### **Schedule (4)**
- `view_schedule` - View work schedules
- `edit_schedule` - Create and edit schedules
- `generate_schedule` - AI-powered scheduling
- `set_availability` - Set own availability

#### **Financials (2)**
- `view_financials` - View financial data
- `edit_financials` - Edit transactions

#### **Reminders (3)**
- `view_reminders` - View reminders
- `edit_reminders` - Create/edit reminders
- `set_reminders` - Set personal reminders

---

## 🔄 Employee Lifecycle

### **1. Invitation**
```
Admin → Employees Page → "Invite via Email" → Fill Form → Submit
```
- Creates Supabase Auth user
- Creates profile with business_id
- Generates secure temp password
- Admin receives credentials to share

### **2. First Login**
```
Employee → Login Page → Email + Temp Password → Dashboard
```
- Employee logs in immediately
- Should change password in settings
- Gets role-based permissions

### **3. Permission Management**
```
Admin → Manage Access → Edit Employee → Grant/Revoke Permissions
```
- Real-time permission updates
- Logged in audit trail
- Employee sees changes immediately (after re-login)

### **4. Role Promotion**
```
Admin → Manage Access → Edit Employee → "Switch to Admin Role"
```
- Employee becomes admin
- Gets all permissions automatically
- Can manage other users

---

## 📍 Where to Find Everything

### **Frontend:**
- **Manage Access Page:** `/admin/permissions` (navigation menu)
- **Invite Employees:** Employees page → "Invite via Email" button
- **Permission Checks:** `useAuth()` hook → `hasPermission()`

### **Backend:**
- **Invite Endpoint:** `POST /api/employees/invite`
- **Permission Router:** `backend/routers/permissions_admin.py`
- **Invite Router:** `backend/routers/employee_invites.py`

### **Database:**
- **Users:** `auth.users` table (Supabase Auth)
- **Profiles:** `profiles` table (role, custom_permissions)
- **Audit Log:** `permission_audit_log` table

---

## 🎬 Quick Start Guide

### **For Admins:**

1. **Sign Up** → You're auto-admin
2. **Invite Employees:**
   - Go to Employees page
   - Click "Invite via Email"
   - Enter email, name, role
   - Copy temporary password
   - Share credentials with employee
3. **Manage Permissions:**
   - Go to "Manage Access"
   - Edit any employee
   - Grant/revoke specific permissions
   - Or promote to admin

### **For Employees:**

1. **Receive credentials** from admin
2. **Login** with email + temporary password
3. **Change password** (recommended)
4. **Access features** based on permissions

---

## 🛡️ Admin Protections

**Admins CANNOT:**
- ❌ Change their own role
- ❌ Remove their own admin permissions
- ❌ Deactivate their own account

**Why?** Prevents accidental lockout!

---

## 📊 Audit Trail

Every permission change is logged:
- **Who made the change** (admin_id)
- **Who was affected** (target_user_id)
- **What changed** (changes JSON)
- **When it happened** (created_at)

**View audit logs:** Coming soon in Manage Access page!

---

## 🚀 API Endpoints

### **Employee Invitations:**

**Invite Employee:**
```http
POST /api/employees/invite
Content-Type: application/json

{
  "email": "employee@example.com",
  "full_name": "John Doe",
  "role": "employee"
}

Response:
{
  "message": "Employee John Doe invited successfully",
  "employee_id": "uuid",
  "email": "employee@example.com",
  "temporary_password": "SecurePass123!"
}
```

**Get Pending Invites:**
```http
GET /api/employees/pending-invites

Response: [
  {
    "id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2025-11-21T..."
  }
]
```

**Revoke Invite:**
```http
DELETE /api/employees/revoke-invite/{employee_id}

Response:
{
  "message": "Invitation revoked for John Doe"
}
```

---

## 🎓 Best Practices

### **For Inviting Employees:**
1. ✅ Use work email addresses
2. ✅ Set role to "employee" by default
3. ✅ Share temp password via secure channel (not email)
4. ✅ Tell employee to change password immediately
5. ✅ Grant permissions as needed, not all at once

### **For Permission Management:**
1. ✅ Use "Manage Access" to view all user permissions
2. ✅ Grant minimum permissions needed for job role
3. ✅ Review permissions quarterly
4. ✅ Remove permissions when employee changes roles
5. ✅ Use audit log to track changes

### **For Security:**
1. ✅ Only promote trusted employees to admin
2. ✅ Regularly review who has admin access
3. ✅ Use "manage_permissions" only for HR/management
4. ✅ Deactivate accounts for departed employees
5. ✅ Don't share admin credentials

---

## 🔧 Troubleshooting

### **Employee can't login:**
- Check if account is active (`is_active = true`)
- Verify correct email
- Try resetting password in Supabase Dashboard

### **Employee doesn't see features:**
- Check their permissions in "Manage Access"
- Verify role is correct
- Ask them to logout and login again

### **Can't invite employee:**
- Check if you have `edit_employees` permission
- Verify email doesn't already exist
- Check Supabase Auth settings

---

## ✅ Summary

**Admin System Includes:**
- ✅ Role-based access (Admin/Employee)
- ✅ 18 granular permissions
- ✅ Email invitation system
- ✅ Temporary password generation
- ✅ Permission management UI
- ✅ Audit trail logging
- ✅ Security protections
- ✅ Multi-tenant isolation

**Everything is ready to use!** 🎉

Start inviting employees and managing permissions now!
