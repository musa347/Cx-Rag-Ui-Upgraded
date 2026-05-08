import streamlit as st
import requests
import json
import time

# Page config must be first
st.set_page_config(
    page_title="CP-DIP - Developer Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_URL = st.secrets.get("API_URL", "https://developer-intelligence-platform-xivl.onrender.com")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "history" not in st.session_state:
    st.session_state.history = []
if "last_query_result" not in st.session_state:
    st.session_state.last_query_result = None
if "last_ingestion_message" not in st.session_state:
    st.session_state.last_ingestion_message = None

if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False
if "reset_token_sent" not in st.session_state:
    st.session_state.reset_token_sent = False
if "direct_reset_token" not in st.session_state:
    st.session_state.direct_reset_token = None

# Check for direct reset token in URL parameters
query_params = st.query_params
if "token" in query_params and not st.session_state.authenticated:
    st.session_state.direct_reset_token = query_params["token"][0]
    st.session_state.show_forgot_password = True
    st.session_state.reset_token_sent = True


# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-bottom: 4px solid #5a67d8;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse-bg 4s ease-in-out infinite;
    }
    @keyframes pulse-bg {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    .main-header h1 {
        color: white;
        font-size: 2.8rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.15rem;
        margin: 0.8rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    .query-box {
        background: white;
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    .user-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .admin-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.3rem;
    }
    .user-role-badge {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== AUTHENTICATION FUNCTIONS ====================

def login_user(username, password):
    """Authenticate user with backend"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.username = data.get("username")
            st.session_state.role = data.get("role")
            return True, "Login successful"
        else:
            error = response.json()
            return False, error.get("error", "Invalid credentials")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def signup_user(username, email, password):
    """Register new user with backend"""
    try:
        response = requests.post(
            f"{API_URL}/api/registration/signup",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get("message", "Account created successfully")
        else:
            error = response.json()
            return False, error.get("error", "Failed to create account")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.history = []
    st.rerun()

def forgot_password(email):
    """Request password reset email"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/forgot-password",
            json={"email": email},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json().get("message", "Reset email sent")
        return False, response.json().get("error", "Failed to send reset email")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def reset_password(token, new_password):
    """Reset password using token"""
    try:
        response = requests.post(
            f"{API_URL}/api/auth/reset-password",
            json={"token": token, "newPassword": new_password},
            timeout=10
        )
        if response.status_code == 200:
            return True, response.json().get("message", "Password reset successfully")
        return False, response.json().get("error", "Failed to reset password")
    except Exception as e:
        return False, f"Connection error: {str(e)}"



def create_user_admin(username, password, role):
    """Create new user (admin only)"""
    try:
        response = requests.post(
            f"{API_URL}/api/users",
            json={"username": username, "password": password, "role": role},
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "User created successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to create user")
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_users():
    """Get all users (admin only)"""
    try:
        response = requests.get(
            f"{API_URL}/api/users",
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def create_user_admin(username, email, password, role):
    """Create new user (admin only)"""
    try:
        response = requests.post(
            f"{API_URL}/api/users",
            json={"username": username, "email": email, "password": password, "role": role},
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "User created successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to create user")
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_user_admin(user_id, username, email, role):
    """Update user (admin only)"""
    try:
        response = requests.put(
            f"{API_URL}/api/users/{user_id}",
            json={"username": username, "email": email, "role": role},
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "User updated successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to update user")
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_user_admin(user_id):
    """Delete user (admin only)"""
    try:
        response = requests.delete(
            f"{API_URL}/api/users/{user_id}",
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "User deleted successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to delete user")
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_services():
    """Get all services (admin only)"""
    try:
        response = requests.get(
            f"{API_URL}/api/services",
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def create_service_admin(service_code, name, domain, owning_team, owner_id, status):
    """Create new service (admin only)"""
    try:
        payload = {
            "serviceCode": service_code,
            "name": name,
            "domain": domain,
            "owningTeam": owning_team,
            "status": status
        }
        if owner_id:
            payload["ownerId"] = owner_id
        
        # Use the new endpoint with owner support
        endpoint = f"{API_URL}/api/services/with-owner" if owner_id else f"{API_URL}/api/services"
        response = requests.post(
            endpoint,
            json=payload,
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "Service created successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to create service")
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_service_admin(service_code, name, domain, owning_team, status):
    """Update service (admin only)"""
    try:
        response = requests.put(
            f"{API_URL}/api/services/{service_code}",
            json={
                "name": name,
                "domain": domain,
                "owningTeam": owning_team,
                "status": status
            },
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "Service updated successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to update service")
    except Exception as e:
        return False, f"Error: {str(e)}"

def delete_service_admin(service_code):
    """Delete service (admin only)"""
    try:
        response = requests.delete(
            f"{API_URL}/api/services/{service_code}",
            headers={"X-User": st.session_state.username},
            timeout=10
        )
        if response.status_code == 200:
            return True, "Service deleted successfully"
        else:
            error = response.json()
            return False, error.get("error", "Failed to delete service")
    except Exception as e:
        return False, f"Error: {str(e)}"

def upload_document_admin(file, service_code, document_type, version):
    """Upload document (admin only)"""
    try:
        files = {"file": file}
        data = {
            "serviceCode": service_code,
            "documentType": document_type,
            "version": version
        }
        response = requests.post(
            f"{API_URL}/api/documents/upload",
            files=files,
            data=data,
            headers={"X-User": st.session_state.username},
            timeout=10  # Reduced timeout since response is immediate
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "PROCESSING":
                return True, result
            else:
                return True, result
        else:
            error = response.json()
            return False, error.get("error", "Failed to upload document")
    except Exception as e:
        return False, f"Error: {str(e)}"

# ==================== LOGIN/SIGNUP PAGE ====================

def show_auth_page():
    """Display login/signup page"""
    st.markdown("""
    <div class="main-header">
        <h1>CP-DIP</h1>
        <p>Core Payments Developer Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for Sign In and Sign Up
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        st.markdown("### Welcome Back!")
        st.markdown("Sign in to access the Developer Intelligence Platform")

        if not st.session_state.show_forgot_password:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter your username", key="login_username")
                password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
                submit = st.form_submit_button("Sign In", use_container_width=True)

                if submit:
                    if username and password:
                        with st.spinner("Signing in..."):
                            success, message = login_user(username, password)
                            if success:
                                st.success(message)
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Please enter username and password")

            if st.button("Forgot Password?", use_container_width=False):
                st.session_state.show_forgot_password = True
                st.rerun()

        elif not st.session_state.reset_token_sent:
            st.markdown("### Forgot Password")
            st.markdown("Enter your email and we'll send you a reset link.")

            with st.form("forgot_password_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                col1, col2 = st.columns(2)
                with col1:
                    send_btn = st.form_submit_button("Send Reset Email", use_container_width=True)
                with col2:
                    back_btn = st.form_submit_button("Back to Login", use_container_width=True)

                if send_btn:
                    if email:
                        with st.spinner("Sending reset email..."):
                            success, message = forgot_password(email)
                            if success:
                                st.success(message)
                                st.session_state.reset_token_sent = True
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Please enter your email")

                if back_btn:
                    st.session_state.show_forgot_password = False
                    st.rerun()

        else:
            st.markdown("### Reset Your Password")
            
            with st.form("reset_password_form"):
                # Check if we have a direct token from URL
                if st.session_state.direct_reset_token:
                    st.markdown("Reset your password using the token from your email.")
                    st.info("Token automatically loaded from email link")
                    # Don't show token field when we have direct token
                    token = st.session_state.direct_reset_token
                else:
                    st.markdown("Enter the token from your email and your new password.")
                    token = st.text_input("Reset Token", placeholder="Paste token from email")
                new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter new password")
                col1, col2 = st.columns(2)
                with col1:
                    reset_btn = st.form_submit_button("Reset Password", use_container_width=True)
                with col2:
                    back_btn = st.form_submit_button("Back to Login", use_container_width=True)

                if reset_btn:
                    # Use direct token if available, otherwise use form input
                    reset_token = st.session_state.direct_reset_token if st.session_state.direct_reset_token else token
                    
                    if not reset_token or not new_password:
                        st.warning("Please fill all fields")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        with st.spinner("Resetting password..."):
                            success, message = reset_password(reset_token, new_password)
                            if success:
                                st.success(f"{message}. Redirecting to login...")
                                # Clear the direct token and reset states
                                st.session_state.direct_reset_token = None
                                st.session_state.show_forgot_password = False
                                st.session_state.reset_token_sent = False
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"{message}")

                if back_btn:
                    st.session_state.direct_reset_token = None
                    st.session_state.show_forgot_password = False
                    st.session_state.reset_token_sent = False
                    st.rerun()

    # Sign Up Tab
    with tab2:
        st.markdown("### Create Your Account")
        st.markdown("Join the Developer Intelligence Platform")
        
        with st.form("signup_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                signup_username = st.text_input("Username", placeholder="Choose a username", key="signup_username")
            with col2:
                signup_email = st.text_input("Email", placeholder="your.email@example.com", key="signup_email")
            
            signup_password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm")
            
            signup_submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if signup_submit:
                # Validation
                if not signup_username or not signup_email or not signup_password:
                    st.error("Username, email, and password are required")
                elif len(signup_username) < 3:
                    st.error("Username must be at least 3 characters")
                elif "@" not in signup_email or "." not in signup_email:
                    st.error("Please enter a valid email address")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Creating account..."):
                        success, message = signup_user(signup_username, signup_email, signup_password)
                        if success:
                            st.success(f"{message}")
                            st.info("Please switch to the Sign In tab to login with your new account")
                            time.sleep(2)
                        else:
                            st.error(f"{message}")
        
        st.markdown("---")
        st.caption("By signing up, you agree to our Terms of Service and Privacy Policy")

# ==================== USER MANAGEMENT PAGE ====================

def show_user_management():
    """Display user management interface (admin only)"""
    if st.session_state.role != "ADMIN":
        st.error("Access denied. Admin privileges required.")
        return
    
    st.markdown("### User Management")
    
    # Create user form
    with st.expander("Create New User", expanded=True):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username *")
                new_email = st.text_input("Email *")
                new_password = st.text_input("Password *", type="password")
            with col2:
                new_role = st.selectbox("Role *", ["USER", "ADMIN"])
                st.write("")  # Spacing
                create_btn = st.form_submit_button("Create User", use_container_width=True)
            
            if create_btn:
                if new_username and new_email and new_password:
                    if "@" not in new_email or "." not in new_email:
                        st.error("Please enter a valid email address")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = create_user_admin(new_username, new_email, new_password, new_role)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please fill all fields")
    
    # List existing users
    st.markdown("### Existing Users")
    users = get_all_users()
    
    if users:
        for user in users:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**{user.get('username')}**")
                    st.caption(f"Email: {user.get('email', 'N/A')}")
                with col2:
                    role = user.get('role')
                    badge_class = "admin-badge" if role == 'ADMIN' else "user-role-badge"
                    st.markdown(f'<span class="{badge_class}">{role}</span>', unsafe_allow_html=True)
                with col3:
                    created = user.get('createdAt', 'N/A')
                    if created and created != 'N/A':
                        created = str(created)[:10]
                    st.caption(f"Created: {created}")
                with col4:
                    edit_btn = st.button("Edit", key=f"edit_{user.get('id')}", help="Edit User")
                    delete_btn = st.button("Delete", key=f"delete_{user.get('id')}", help="Delete User")
                
                # Edit user dialog
                if edit_btn:
                    with st.expander(f"Edit User: {user.get('username')}", expanded=True):
                        with st.form(f"edit_user_form_{user.get('id')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_username = st.text_input("Username", value=user.get('username'))
                                edit_email = st.text_input("Email", value=user.get('email'))
                            with col2:
                                edit_role = st.selectbox("Role", ["USER", "ADMIN"], 
                                                         index=0 if user.get('role') == 'USER' else 1)
                                update_btn = st.form_submit_button("Update User", use_container_width=True)
                            
                            if update_btn:
                                if edit_username and edit_email:
                                    if "@" not in edit_email or "." not in edit_email:
                                        st.error("Please enter a valid email address")
                                    else:
                                        success, message = update_user_admin(user.get('id'), edit_username, edit_email, edit_role)
                                        if success:
                                            st.success(message)
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.error(message)
                                else:
                                    st.warning("Please fill all fields")
                
                # Delete user confirmation
                if delete_btn:
                    st.warning(f"Are you sure you want to delete user '{user.get('username')}'?")
                    col1, col2 = st.columns(2)
                    with col1:
                        confirm_delete = st.button("Yes, Delete", key=f"confirm_{user.get('id')}", type="primary")
                    with col2:
                        cancel_delete = st.button("Cancel", key=f"cancel_{user.get('id')}")
                    
                    if confirm_delete:
                        success, message = delete_user_admin(user.get('id'))
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                    
                    if cancel_delete:
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No users found or unable to fetch users")

def show_service_management():
    """Display service management interface (admin only)"""
    if st.session_state.role != "ADMIN":
        st.error("Access denied. Admin privileges required.")
        return
    
    st.markdown("### Service Management")
    
    # Create service form
    with st.expander("Create New Service", expanded=True):
        with st.form("create_service_form"):
            col1, col2 = st.columns(2)
            with col1:
                service_code = st.text_input("Service Code *")
                service_name = st.text_input("Service Name *")
                service_domain = st.text_input("Domain")
            with col2:
                owning_team = st.text_input("Owning Team")
                users = get_all_users()
                if users:
                    user_options = [""] + [f"{user.get('username')} ({user.get('email')})" for user in users]
                    selected_user = st.selectbox("Owner", user_options)
                    owner_id = None
                    if selected_user:
                        # Extract username from the selection
                        selected_username = selected_user.split(" (")[0]
                        for user in users:
                            if user.get('username') == selected_username:
                                owner_id = user.get('id')
                                break
                else:
                    st.warning("No users available for selection")
                    owner_id = None
                service_status = st.selectbox("Status *", ["ACTIVE", "INACTIVE", "DEPRECATED"])
                create_btn = st.form_submit_button("Create Service", use_container_width=True)
            
            if create_btn:
                if service_code and service_name and service_status:
                    success, message = create_service_admin(service_code, service_name, service_domain, owning_team, owner_id, service_status)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill all required fields")
    
    # List existing services
    st.markdown("### Existing Services")
    services = get_all_services()
    
    if services:
        for service in services:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**{service.get('name')}**")
                    st.caption(f"Code: {service.get('serviceCode')}")
                    if service.get('domain'):
                        st.caption(f"Domain: {service.get('domain')}")
                    if service.get('owningTeam'):
                        st.caption(f"Team: {service.get('owningTeam')}")
                    if service.get('owner'):
                        owner_name = service.get('owner', {}).get('username', 'Unknown')
                        st.caption(f"Owner: {owner_name}")
                with col2:
                    status = service.get('status', 'UNKNOWN')
                    status_class = "active-badge" if status == 'ACTIVE' else "inactive-badge"
                    st.markdown(f'<span class="{status_class}">{status}</span>', unsafe_allow_html=True)
                with col3:
                    updated = service.get('updatedAt', service.get('createdAt', 'N/A'))
                    if updated and updated != 'N/A':
                        updated = str(updated)[:10]
                    st.caption(f"Updated: {updated}")
                with col4:
                    edit_btn = st.button("Edit", key=f"edit_service_{service.get('serviceCode')}", help="Edit Service")
                    delete_btn = st.button("Delete", key=f"delete_service_{service.get('serviceCode')}", help="Delete Service")
                
                # Edit service dialog
                if edit_btn:
                    with st.expander(f"Edit Service: {service.get('name')}", expanded=True):
                        with st.form(f"edit_service_form_{service.get('serviceCode')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_name = st.text_input("Service Name", value=service.get('name'))
                                edit_domain = st.text_input("Domain", value=service.get('domain'))
                            with col2:
                                edit_team = st.text_input("Owning Team", value=service.get('owningTeam'))
                                edit_status = st.selectbox("Status", ["ACTIVE", "INACTIVE", "DEPRECATED"], 
                                                        index=0 if service.get('status') == 'ACTIVE' else 
                                                        (1 if service.get('status') == 'INACTIVE' else 2))
                                update_btn = st.form_submit_button("Update Service", use_container_width=True)
                            
                            if update_btn:
                                if edit_name:
                                    success, message = update_service_admin(service.get('serviceCode'), edit_name, edit_domain, edit_team, edit_status)
                                    if success:
                                        st.success(message)
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(message)
                                else:
                                    st.warning("Service name is required")
                
                # Delete service confirmation
                if delete_btn:
                    st.warning(f"Are you sure you want to delete service '{service.get('name')}'?")
                    col1, col2 = st.columns(2)
                    with col1:
                        confirm_delete = st.button("Yes, Delete", key=f"confirm_service_{service.get('serviceCode')}", type="primary")
                    with col2:
                        cancel_delete = st.button("Cancel", key=f"cancel_service_{service.get('serviceCode')}")
                    
                    if confirm_delete:
                        success, message = delete_service_admin(service.get('serviceCode'))
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                    
                    if cancel_delete:
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No services found or unable to fetch services")

def show_document_upload():
    """Display document upload interface (admin only)"""
    if st.session_state.role != "ADMIN":
        st.error("Access denied. Admin privileges required.")
        return
    
    st.markdown("### Document Upload")
    st.markdown("Upload documents to make them searchable in the RAG system.")
    st.caption("Uploads are asynchronous. A successful upload response means ingestion started, not that the document is already queryable.")

    if st.session_state.last_ingestion_message:
        st.info(st.session_state.last_ingestion_message)
    
    # PDF to Markdown Converter
    with st.expander("🔄 PDF to Markdown Converter (with Diagram Descriptions)", expanded=False):
        st.markdown("""
        **Convert PDFs with diagrams to markdown automatically!**
        
        This tool will:
        - Extract all text from your PDF
        - Detect diagrams and images
        - Generate text descriptions of diagrams using AI (free)
        - Output a markdown file ready for upload
        """)
        
        pdf_file = st.file_uploader("Upload PDF to Convert", type=['pdf'], key="pdf_converter")
        convert_btn = st.button("Convert to Markdown", use_container_width=True, key="convert_pdf_btn")
        
        if convert_btn and pdf_file:
            with st.spinner("Converting PDF to Markdown... This may take a minute for PDFs with many diagrams."):
                try:
                    # Import the converter
                    from pdf_converter import convert_pdf_to_markdown
                    
                    # Read PDF bytes
                    pdf_bytes = pdf_file.read()
                    
                    # Convert
                    markdown_content, diagram_count = convert_pdf_to_markdown(pdf_bytes)
                    
                    # Show success
                    st.success(f"✅ Conversion complete! Found and described {diagram_count} diagrams.")
                    
                    # Show preview
                    st.markdown("#### Preview (first 500 characters):")
                    st.text(markdown_content[:500] + "...")
                    
                    # Download button (now outside form)
                    st.download_button(
                        label="📥 Download Markdown File",
                        data=markdown_content,
                        file_name=pdf_file.name.replace('.pdf', '_with_diagrams.md'),
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    st.info("💡 Download the markdown file and upload it below using 'Upload Document' section.")
                    
                except ImportError:
                    st.error("PDF converter not available. Please install: pip install pdfplumber")
                except Exception as e:
                    st.error(f"Conversion failed: {str(e)}")
    
    # Document upload form
    with st.expander("Upload Document", expanded=True):
        with st.form("upload_document_form"):
            uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'doc', 'docx', 'md'])
            
            col1, col2 = st.columns(2)
            with col1:
                service_code = st.text_input("Service Code *", placeholder="e.g., PAPSS-001")
                document_type = st.selectbox("Document Type *", ["MANUAL", "API_SPEC", "USER_GUIDE", "POLICY", "TECHNICAL", "OTHER"])
            with col2:
                version = st.text_input("Version *", placeholder="e.g., 1.0.0")
                st.write("")  # Spacing
                upload_btn = st.form_submit_button("Upload Document", use_container_width=True)
            
            if upload_btn:
                if uploaded_file and service_code and version:
                    with st.spinner("Uploading document..."):
                        success, result = upload_document_admin(uploaded_file, service_code, document_type, version)
                        if success:
                            message = result.get("message", "Document upload started successfully")
                            filename = result.get("filename", uploaded_file.name)
                            status = result.get("status", "PROCESSING")
                            st.session_state.last_ingestion_message = (
                                f"{message} Status: {status}. Service: {service_code}. "
                                f"Document: {filename}. Wait for background ingestion to finish before querying."
                            )
                            st.success(st.session_state.last_ingestion_message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(result)
                else:
                    st.warning("Please fill all required fields")
    
    # Instructions
    with st.expander("Upload Instructions", expanded=False):
        st.markdown("""
        **Supported File Types:**
        - Text files (.txt)
        - PDF files (.pdf)
        - Word documents (.doc, .docx)
        - Markdown files (.md)
        
        **Document Types:**
        - **MANUAL**: Technical manuals and documentation
        - **API_SPEC**: API specifications and technical docs
        - **USER_GUIDE**: User manuals and guides
        - **POLICY**: Policy documents and compliance
        - **TECHNICAL**: Technical documentation
        - **OTHER**: Miscellaneous documents
        
        **Best Practices:**
        - For PDFs with diagrams, use the PDF to Markdown converter first
        - Use clear, descriptive service codes
        - Follow semantic versioning (e.g., 1.0.0, 1.1.0, 2.0.0)
        - Choose the most appropriate document type
        - Ensure documents are well-structured and readable
        """)

# ==================== MAIN APPLICATION ====================

def show_main_app():
    """Display main application interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>CP-DIP</h1>
        <p>Core Payments Developer Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
            <div style="font-size: 0.85rem; opacity: 0.9;">Logged in as</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin-top: 0.2rem;">{st.session_state.username}</div>
            <div style="margin-top: 0.5rem;">
                <span class="{'admin-badge' if st.session_state.role == 'ADMIN' else 'user-role-badge'}">{st.session_state.role}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        pages = ["Query Documentation"]
        if st.session_state.role == "ADMIN":
            pages.extend(["User Management", "Service Management", "Document Upload"])
        
        page = st.radio("Navigation", pages, label_visibility="collapsed")
        
        st.markdown("---")
        st.caption(f"Backend: `{API_URL}`")
        
        if st.button("Logout", use_container_width=True):
            logout()
    
    # Show selected page
    if page == "User Management":
        show_user_management()
    elif page == "Service Management":
        show_service_management()
    elif page == "Document Upload":
        show_document_upload()
    else:
        show_query_interface()

def show_query_interface():
    """Display the main query interface"""
    # Mode selection
    mode = st.sidebar.radio(
        "Select Intelligence Mode",
        ["NIBSS Policy Intelligence", "Technical Documentation"],
        help="NIBSS Policy: Customer service policies | Technical: Developer documentation"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if mode == "NIBSS Policy Intelligence":
            st.info("**NIBSS Policy Intelligence** - Query NIBSS customer service policies and compliance guidelines.")
        else:
            st.info("**Technical Documentation** - Access technical documentation and API specifications.")
        
        # Service selection for Technical Documentation
        if mode == "Technical Documentation":
            try:
                services_response = requests.get(f"{API_URL}/api/services", timeout=5)
                if services_response.status_code == 200:
                    services = services_response.json()
                    if services:
                        # Create a list of "Service Name (Service Code)" for display
                        service_display_options = []
                        service_code_map = {}
                        for service in services:
                            display_name = f"{service.get('name', 'Unknown')} ({service.get('serviceCode', 'N/A')})"
                            service_display_options.append(display_name)
                            service_code_map[display_name] = service.get('serviceCode')
                        
                        selected_display = st.selectbox("Select Service *", options=service_display_options)
                        service_code = service_code_map.get(selected_display)
                    else:
                        service_code = st.text_input("Service Code *", placeholder="e.g., PAPSS-001")
                else:
                    service_code = st.text_input("Service Code *", placeholder="e.g., PAPSS-001")
            except:
                service_code = st.text_input("Service Code *", placeholder="e.g., PAPSS-001")
        
        # Query input
        query = st.text_area(
            "Your Question",
            placeholder="Ask a question about the service...",
            height=100
        )
        
        if st.button("Submit Query", type="primary", use_container_width=True):
            if query:
                if mode == "Technical Documentation" and not service_code:
                    st.error("Service code is required")
                else:
                    # Process query
                    with st.spinner("Processing query..."):
                        try:
                            endpoint = "/api/query"
                            payload = {"query": query, "userId": st.session_state.username}
                            if mode == "Technical Documentation":
                                payload["serviceCode"] = service_code
                            
                            response = requests.post(
                                f"{API_URL}{endpoint}",
                                json=payload,
                                headers={"X-User": st.session_state.username},
                                timeout=60
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.session_state.last_query_result = result
                                
                                st.markdown("### Response")
                                st.write(result.get("answer", "No answer"))
                                
                                confidence = result.get("confidence", "UNKNOWN")
                                st.markdown(f"**Confidence:** `{confidence}`")
                                if mode == "Technical Documentation" and service_code:
                                    st.caption(f"Service: {service_code}")
                                
                                # Sources
                                sources = result.get("sources", [])
                                if sources:
                                    st.markdown("### Sources")
                                    for index, source in enumerate(sources, start=1):
                                        with st.expander(
                                            f"{index}. {source.get('section', 'Unknown Section')} "
                                            f"[{source.get('documentType', 'Unknown')}, v{source.get('version', '?')}]",
                                            expanded=(index == 1)
                                        ):
                                            st.markdown(f"**Document Type:** `{source.get('documentType', 'Unknown')}`")
                                            st.markdown(f"**Version:** `{source.get('version', '?')}`")
                                            st.markdown(f"**Section:** `{source.get('section', 'Unknown Section')}`")
                                            st.code(source.get('excerpt', ''), language="text")
                                else:
                                    st.warning("No sources were returned. That usually means retrieval was weak or ingestion is still processing.")

                                with st.expander("Debug Response", expanded=False):
                                    st.json(result)
                                
                                # Add to history
                                st.session_state.history.append({
                                    "mode": mode,
                                    "service_code": service_code if mode == "Technical Documentation" else None,
                                    "query": query,
                                    "answer": result.get("answer", ""),
                                    "confidence": confidence,
                                    "timestamp": time.strftime("%H:%M")
                                })
                            else:
                                st.error(f"Error: {response.text}")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a question")
    
    with col2:
        st.markdown("### Control Panel")
        
        # System status
        if st.button("Check System Status", use_container_width=True):
            try:
                response = requests.get(f"{API_URL}/api/health", timeout=10)
                if response.status_code == 200:
                    st.success("System Online")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.caption("Health endpoint responded without JSON body.")
                else:
                    st.error("System Offline")
            except:
                st.error("Connection Failed")
        
        # Query history
        if st.session_state.history:
            st.markdown("### Recent Queries")
            if st.button("Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()
            
            for item in reversed(st.session_state.history[-5:]):
                with st.expander(f"{item['timestamp']} - {item['query'][:20]}..."):
                    st.write(f"**Mode:** {item.get('mode', 'Unknown')}")
                    if item.get("service_code"):
                        st.write(f"**Service:** `{item['service_code']}`")
                    st.write(f"**Answer:** {item['answer'][:80]}...")
                    st.write(f"**Confidence:** `{item['confidence']}`")

# ==================== MAIN ENTRY POINT ====================

def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
