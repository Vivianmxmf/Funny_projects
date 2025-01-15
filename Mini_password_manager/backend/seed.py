from app import app, db, User, Password
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

def seed_database():
    with app.app_context():
        # Create tables
        db.create_all()

        # Create test user
        test_user = User(
            username='test@example.com',
            password_hash=generate_password_hash('test123'),
            encryption_key=Fernet.generate_key().decode()
        )
        db.session.add(test_user)
        db.session.commit()

        # Create test passwords
        f = Fernet(test_user.encryption_key.encode())
        test_passwords = [
            {
                'account': 'Gmail',
                'username': 'test.user@gmail.com',
                'password': 'gmail123'
            },
            {
                'account': 'Facebook',
                'username': 'test.user',
                'password': 'facebook123'
            },
            {
                'account': 'Twitter',
                'username': 'test_user',
                'password': 'twitter123'
            }
        ]

        for pwd in test_passwords:
            encrypted_password = f.encrypt(pwd['password'].encode()).decode()
            password = Password(
                account=pwd['account'],
                username=pwd['username'],
                encrypted_password=encrypted_password,
                user_id=test_user.id
            )
            db.session.add(password)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database() 