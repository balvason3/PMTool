# --- BEDROCK: AUTHENTICATION MODULE ---
from werkzeug.security import generate_password_hash, check_password_hash
from database import User, Role, get_session

def initialize_roles():
    """Ensures basic default roles exist in the database on first boot."""
    for db in get_session():
        admin_role = db.query(Role).filter_by(name="Admin").first()
        if not admin_role:
            # Placeholder for future customizable permissions JSON
            db.add(Role(name="Admin", permissions='["all"]')) 
            
        user_role = db.query(Role).filter_by(name="User").first()
        if not user_role:
            db.add(Role(name="User", permissions='["view_projects", "log_hours", "receive_materials"]'))
            
        db.commit()

def check_first_boot():
    """Checks if there are any users in the system yet."""
    for db in get_session():
        user_count = db.query(User).count()
        return user_count == 0

def create_user(username, password, role_name="User"):
    """Creates a new user with a cryptographically hashed password."""
    for db in get_session():
        # Check if user already exists
        if db.query(User).filter_by(username=username).first():
            return False, "!! Username already exists."
            
        role = db.query(Role).filter_by(name=role_name).first()
        if not role:
            return False, f"!! Role '{role_name}' does not exist in the database."
            
        # Hash the password so it's unreadable in the bedrock.db file
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw, role_id=role.id)
        
        db.add(new_user)
        db.commit()
        return True, f">> User '{username}' created successfully as {role_name}."

def authenticate_user(username, password):
    """Verifies credentials. Returns True and the User's Role if successful."""
    for db in get_session():
        user = db.query(User).filter_by(username=username).first()
        
        # check_password_hash securely compares the typed password to the stored hash
        if user and check_password_hash(user.password_hash, password):
            return True, user.role.name
            
        return False, None