import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from db.database import SessionLocal, init_db
from db.models import User, UserRole
from utils.hashing import hash_password


def seed_users():
    """Seed initial users"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@oneserve.com").first()
        if existing_admin:
            print("Admin user already exists")
            return
        
        # Create admin
        admin = User(
            email="admin@oneserve.com",
            full_name="Admin User",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            phone="1234567890"
        )
        db.add(admin)
        
        # Create officers for each department
        officers = [
            {
                "email": "water.officer@oneserve.com",
                "full_name": "Water Department Officer",
                "password": "Officer@123",
                "role": UserRole.OFFICER_WATER,
                "phone": "1111111111"
            },
            {
                "email": "electricity.officer@oneserve.com",
                "full_name": "Electricity Department Officer",
                "password": "Officer@123",
                "role": UserRole.OFFICER_ELECTRICITY,
                "phone": "2222222222"
            },
            {
                "email": "road.officer@oneserve.com",
                "full_name": "Road Department Officer",
                "password": "Officer@123",
                "role": UserRole.OFFICER_ROAD,
                "phone": "3333333333"
            },
            {
                "email": "sanitation.officer@oneserve.com",
                "full_name": "Sanitation Department Officer",
                "password": "Officer@123",
                "role": UserRole.OFFICER_SANITATION,
                "phone": "4444444444"
            }
        ]
        
        for officer_data in officers:
            officer = User(
                email=officer_data["email"],
                full_name=officer_data["full_name"],
                password_hash=hash_password(officer_data["password"]),
                role=officer_data["role"],
                phone=officer_data["phone"]
            )
            db.add(officer)
        
        # Create sample citizen
        citizen = User(
            email="citizen@oneserve.com",
            full_name="Test Citizen",
            password_hash=hash_password("Citizen@123"),
            role=UserRole.CITIZEN,
            phone="9999999999",
            address="123 Main Street, City"
        )
        db.add(citizen)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print("\nDefault Users Created:")
        print("=" * 50)
        print("Admin:")
        print("  Email: admin@oneserve.com")
        print("  Password: Admin@123")
        print("\nOfficers:")
        print("  Water: water.officer@oneserve.com / Officer@123")
        print("  Electricity: electricity.officer@oneserve.com / Officer@123")
        print("  Road: road.officer@oneserve.com / Officer@123")
        print("  Sanitation: sanitation.officer@oneserve.com / Officer@123")
        print("\nTest Citizen:")
        print("  Email: citizen@oneserve.com")
        print("  Password: Citizen@123")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding database...")
    seed_users()
