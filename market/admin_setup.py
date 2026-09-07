from market import app, db
from market.models import User

def setup_admin():  # Creating logic to set the first registered user as admin if no admin exists
    
    with app.app_context():
        # Checking if any admin exist
        admin_exists = User.query.filter_by(is_admin = True).first()
        
        if not admin_exists:
            # Geting the first user in the system
            first_user = User.query.first()
            if first_user: # Making first user as an admin
                first_user.is_admin = True
                db.session.commit()
                print(f"User '{first_user.username}' has been set as an admin")
            else:
                print("No users found. Please register first")
        else:
            print(f"Admin already exists: {admin_exists.username}")

    pass

if __name__ == "__main__":
    setup_admin()

    