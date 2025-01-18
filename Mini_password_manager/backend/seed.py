from app import app, db, User, Password
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
import random

def generate_creative_passwords():
    return [
        {
            'account': 'Hogwarts Portal',
            'username': 'harry.potter',
            'password': 'Alohomora123!'
        },
        {
            'account': 'Stark Industries',
            'username': 'tony.stark',
            'password': 'IamIronMan3000!'
        },
        {
            'account': 'SHIELD Database',
            'username': 'nick.fury',
            'password': 'ItsAllConnected#42'
        },
        {
            'account': 'Wayne Enterprises',
            'username': 'bruce.wayne',
            'password': 'IamBatman!2024'
        },
        {
            'account': 'Daily Planet',
            'username': 'clark.kent',
            'password': 'Kr7pt0n1te!'
        },
        {
            'account': 'Jurassic World',
            'username': 'owen.grady',
            'password': 'RaptorSquad#2024'
        },
        {
            'account': 'Matrix Access',
            'username': 'neo.anderson',
            'password': 'FollowTheWhiteRabbit!'
        },
        {
            'account': 'Millennium Falcon',
            'username': 'han.solo',
            'password': 'NeverTellMeTheOdds#1'
        }
    ]

def create_test_users():
    return [
        {
            'username': 'superhero@avengers.com',
            'password': 'AssembleNow2024!',
            'passwords': generate_creative_passwords()[:3]
        },
        {
            'username': 'wizard@hogwarts.edu',
            'password': 'Lumos123!',
            'passwords': generate_creative_passwords()[3:6]
        },
        {
            'username': 'jedi@resistance.org',
            'password': 'UseTheForce2024!',
            'passwords': generate_creative_passwords()[6:]
        }
    ]

def seed_database():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("🌱 Starting the magical seeding process...")
        
        for user_data in create_test_users():
            # Create user with encryption key
            encryption_key = Fernet.generate_key().decode()
            user = User(
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                encryption_key=encryption_key
            )
            db.session.add(user)
            db.session.commit()
            
            # Create Fernet instance for password encryption
            f = Fernet(user.encryption_key.encode())
            
            # Add passwords for user
            for pwd in user_data['passwords']:
                encrypted_password = f.encrypt(pwd['password'].encode()).decode()
                password = Password(
                    account=pwd['account'],
                    username=pwd['username'],
                    encrypted_password=encrypted_password,
                    user_id=user.id
                )
                db.session.add(password)
            
            print(f"🚀 Created user: {user.username} with {len(user_data['passwords'])} secure passwords")
        
        db.session.commit()
        print("\n✨ Database seeding completed successfully! ✨")
        print("\nTest User Credentials:")
        print("------------------------")
        for user in create_test_users():
            print(f"Username: {user['username']}")
            print(f"Password: {user['password']}")
            print("------------------------")

if __name__ == '__main__':
    seed_database() 