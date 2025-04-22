from app import app, db, User
from datetime import datetime

def create_temp_user():
    with app.app_context():
        # Delete existing temp user if exists
        existing_user = User.query.filter_by(username='temp_user').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("Deleted existing temporary user")
        
        # Create new user
        user = User(
            username='temp_user',
            created_at=datetime.utcnow()
        )
        # Set password using the User model's method
        user.set_password('temp123')
        
        try:
            db.session.add(user)
            db.session.commit()
            print("Temporary user created successfully")
            print("Username: temp_user")
            print("Password: temp123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {str(e)}")

if __name__ == '__main__':
    create_temp_user() 