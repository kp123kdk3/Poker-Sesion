from app import app, db, User
from werkzeug.security import check_password_hash

def check_temp_user():
    with app.app_context():
        user = User.query.filter_by(username='temp_user').first()
        if not user:
            print("User 'temp_user' not found in database!")
            return
        
        print(f"User found:")
        print(f"Username: {user.username}")
        print(f"Password hash: {user.password_hash}")
        
        # Test password
        test_password = 'temp123'
        if check_password_hash(user.password_hash, test_password):
            print(f"\nPassword '{test_password}' is correct!")
        else:
            print(f"\nPassword '{test_password}' is NOT correct!")

if __name__ == '__main__':
    check_temp_user() 