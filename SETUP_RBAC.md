# 🚀 Quick Setup Guide - RBAC System

## Step-by-Step Setup

### 1. Run Database Migration

Go to your Supabase Dashboard SQL Editor and run:

```sql
-- Copy and paste the entire contents of:
supabase/migrations/003_rbac_permissions.sql
```

This will:
- Add `role` and `custom_permissions` columns to profiles
- Create permissions tables
- Set up RLS policies
- Create audit log
- Make first user of each business an admin

### 2. Restart Backend Server

```bash
cd backend
# Stop current server (Ctrl+C)
python3 app.py
```

### 3. Test the System

#### As Admin (First Signup)
1. Go to http://localhost:5173/signup
2. Create account - you'll be **Admin** automatically
3. Notice header shows "• Admin"
4. See all nav items including "Manage Access" (purple background)

#### Manage Permissions
1. Click **"Manage Access"** in navigation
2. You'll see the permissions management interface
3. View all users in your organization
4. Click **"Edit"** next to any employee
5. Grant/revoke permissions using checkboxes
6. Changes take effect immediately

#### Create Employee Users
1. Have team members sign up
2. They'll be **Employee** by default
3. They'll have limited menu access
4. Grant them specific permissions as needed

---

## ✅ Verification Checklist

- [ ] Database migration ran successfully
- [ ] Backend started without errors
- [ ] First user shows as "Admin" in header
- [ ] "Manage Access" appears in navigation
- [ ] Can open permissions modal and see checkbox list
- [ ] Employee users have limited navigation
- [ ] Permission changes save successfully
- [ ] Audit log records changes

---

## 🎯 What You Can Do Now

### Admin Can:
- ✅ Access ALL features automatically
- ✅ View/Edit all users' permissions
- ✅ Promote users to Admin
- ✅ Grant specific permissions to employees
- ✅ Deactivate user accounts
- ✅ View audit trail of permission changes

### Employee Can:
- ✅ Access granted features only
- ✅ See only permitted navigation items
- ✅ Set own availability
- ✅ View own reminders
- ❌ Cannot access admin features
- ❌ Cannot manage other users

---

## 📋 Quick Reference

### Default Employee Permissions:
- View Dashboard
- View Inventory
- View Schedule
- Set Availability  
- View Reminders
- Set Personal Reminders

### Admin-Only Permissions:
- Manage User Permissions
- Edit Business Settings
- Full system access

### Common Permission Grants:

**Inventory Manager:**
- Edit Inventory
- Generate Orders

**Schedule Manager:**
- Edit Schedule
- Generate AI Schedule

**Financial Manager:**
- View Financials
- Edit Financials

---

## Need Help?

See `RBAC_IMPLEMENTATION.md` for complete documentation including:
- All 18 available permissions
- Security implementation details
- API endpoint reference
- Troubleshooting guide
- Developer notes for adding new permissions

---

**System is ready to use! 🎉**
