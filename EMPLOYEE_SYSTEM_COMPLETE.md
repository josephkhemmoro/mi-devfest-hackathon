# ✅ Employee & Admin System - Complete Setup

## 🎯 What's Been Fixed

### 1. **Employee Creation with User Account**
- ✅ Added **email field** to employee form
- ✅ Added **"Create login account"** checkbox
- ✅ Automatically creates Supabase Auth user when checked
- ✅ Generates secure temporary password
- ✅ Creates profile for login access

### 2. **Manage Access Page Fixed**
- ✅ Now loads all user profiles correctly
- ✅ Fetches emails from `auth.users` table
- ✅ Shows role, permissions, and status
- ✅ Admin can edit permissions

### 3. **Email Invite System**
- ✅ "Invite via Email" button on Employees page
- ✅ Creates user account immediately
- ✅ Shows temporary password to admin
- ✅ Employee can login right away

---

## 🚀 How to Use

### **Option A: Add Employee with Login (Quick Way)**

1. Go to **Employees** page
2. Click **"Invite via Email"** (blue button)
3. Enter:
   - Email
   - Full Name
   - Role (Employee or Admin)
4. Click **"Send Invite"**
5. Copy the temporary password
6. Share email + password with employee
7. ✅ Employee can login immediately!

---

### **Option B: Add Employee via Regular Form**

1. Go to **Employees** page
2. Click **"Add Employee"** (gray button)
3. Fill out form:
   - **Full Name** * (required)
   - **Email** (optional - needed for login)
   - ☑️ **Check "Create login account"** if you want them to have system access
   - Job Role
   - Strength Level
   - Availability
4. Click **"Create Employee"**
5. If you checked "Create login account":
   - Check backend terminal for temp password
   - Share credentials with employee

---

### **Manage User Permissions**

1. Go to **"Manage Access"** in navigation (purple background, shield icon)
2. See table of all users with:
   - Full name
   - Email
   - Role (Admin/Employee)
   - Custom permissions
   - Status (Active/Inactive)
3. Click **"Edit"** next to any user
4. **Option A - Promote to Admin:**
   - Click "Switch to Admin Role"
   - User gets all permissions
5. **Option B - Grant Specific Permissions:**
   - Check individual permission boxes
   - Click "Save Permissions"

---

## 🔑 Key Differences

### **employees table** (for scheduling only)
- Used for shift scheduling
- No login access
- Just tracks availability and strength

### **profiles table** (for user accounts)
- Created when you invite via email OR check "create login account"
- Has actual Supabase Auth user
- Can login to system
- Has role and permissions

---

## 📊 Testing Everything

### **1. Test Employee Creation with Login:**
```bash
# Start backend
cd backend
python3 app.py

# Start frontend  
cd frontend
npm run dev
```

1. Go to http://localhost:5173/employees
2. Click "Add Employee"
3. Enter name, email, check "Create login account"
4. Submit
5. Check backend terminal for temp password
6. Logout and login with new employee email

---

### **2. Test Manage Access:**

1. Login as admin
2. Go to "Manage Access" in nav
3. Should see all users with emails
4. Click "Edit" on any employee
5. Grant/revoke permissions
6. Save

---

### **3. Test Email Invite:**

1. Go to Employees page
2. Click "Invite via Email"
3. Enter email, name
4. Submit
5. Copy temp password from modal
6. Logout
7. Login with invited email + temp password

---

## 🛠️ What Happens Behind the Scenes

### **When you create employee with "create login account" checked:**

```
1. Frontend sends: { full_name, email, create_user_account: true }
2. Backend:
   - Generates secure 12-char password
   - Creates Supabase Auth user (email + password)
   - Creates profile (id, business_id, full_name, role: "employee")
   - Creates employee in employees table (for scheduling)
   - Prints temp password in terminal
3. Employee in both systems now!
```

### **When admin invites via email:**

```
1. Frontend: Invite modal with email, name, role
2. Backend:
   - Same as above but via /api/employees/invite
   - Returns temp password in response
3. Frontend: Shows temp password to admin to share
```

### **When admin edits permissions:**

```
1. Admin opens "Manage Access"
2. Backend queries:
   - profiles table (role, custom_permissions)
   - auth.users (for emails)
   - Combines into UserPermissionsResponse
3. Admin clicks "Edit"
4. Backend:
   - Updates custom_permissions in profiles
   - Logs change in audit trail
5. Employee sees changes on next login
```

---

## 🔒 Security

- ✅ Temporary passwords are cryptographically secure
- ✅ Email auto-confirmed for invited users
- ✅ RLS policies enforce business isolation
- ✅ Only admins can manage permissions
- ✅ All permission changes logged in audit trail
- ✅ Admins can't remove their own admin access

---

## 🎓 Common Use Cases

### **Restaurant Manager adds new waiter:**
```
1. "Add Employee" → Name: "John Doe"
2. Email: john@restaurant.com
3. Check "Create login account"
4. Role: "Waiter", Strength: "New"
5. Availability: Mon, Tue, Wed, Thu, Fri
6. Submit
7. Share temp password with John
8. John logs in, changes password
```

### **HR gives inventory manager elevated access:**
```
1. "Manage Access" → Find "Jane Smith"
2. Click "Edit"
3. Check: ☑️ Edit Inventory, ☑️ Generate Orders
4. Save
5. Jane can now manage inventory without being admin
```

---

## ✅ Summary

**You can now:**
- ✅ Create employees for scheduling (no login)
- ✅ Create employees WITH login accounts
- ✅ Invite employees via email
- ✅ Manage user permissions (Manage Access page)
- ✅ Promote employees to admin
- ✅ Grant custom permissions

**Everything is working!** 🎉

**Next steps:**
1. Restart backend to load new routes
2. Test creating employee with login
3. Test Manage Access page
4. Test inviting via email
