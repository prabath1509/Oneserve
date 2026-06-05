"""
Script to initialize demo users in the database
"""
from sqlalchemy.orm import Session
from db.database import SessionLocal, engine
from db.models import Base, User, UserRole
from utils.hashing import hash_password

def init_demo_users():
    """Create demo users for testing"""
    db: Session = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"✅ Database already has {existing_users} users")
            return
        
        # Demo users
        demo_users = [
            {
                "email": "admin@oneserve.com",
                "password": "Admin@123",
                "full_name": "Admin User",
                "role": UserRole.ADMIN,
                "phone": "9876543210",
                "address": "Admin Office, City Center"
            },
            {
                "email": "citizen@oneserve.com",
                "password": "Citizen@123",
                "full_name": "John Citizen",
                "role": UserRole.CITIZEN,
                "phone": "9876543211",
                "address": "123 Main Street, Cityville"
            },
            {
                "email": "officer.water@oneserve.com",
                "password": "Officer@123",
                "full_name": "Water Department Officer",
                "role": UserRole.OFFICER_WATER,
                "phone": "9876543212",
                "address": "Water Department Building"
            },
            {
                "email": "officer.electricity@oneserve.com",
                "password": "Officer@123",
                "full_name": "Electricity Department Officer",
                "role": UserRole.OFFICER_ELECTRICITY,
                "phone": "9876543213",
                "address": "Electricity Board Office"
            },
            {
                "email": "officer.road@oneserve.com",
                "password": "Officer@123",
                "full_name": "Road Department Officer",
                "role": UserRole.OFFICER_ROAD,
                "phone": "9876543214",
                "address": "Public Works Department"
            },
            {
                "email": "officer.sanitation@oneserve.com",
                "password": "Officer@123",
                "full_name": "Sanitation Department Officer",
                "role": UserRole.OFFICER_SANITATION,
                "phone": "9876543215",
                "address": "Sanitation Department"
            }
        ]
        
        # Create users
        for user_data in demo_users:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                password_hash=hash_password(user_data["password"]),
                role=user_data["role"],
                phone=user_data["phone"],
                address=user_data["address"],
                is_active=True
            )
            db.add(user)
            print(f"✅ Created user: {user_data['email']} (Role: {user_data['role'].value})")
        
        db.commit()
        print("\n🎉 All demo users created successfully!")
        print("\nDemo Credentials:")
        print("=" * 50)
        for user_data in demo_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role'].value}")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_demo_users()
