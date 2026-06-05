from sqlalchemy.orm import Session
from db.models import User, UserRole, ComplaintCategory
from typing import Optional
import random


KEYWORD_MAPPING = {
    "WATER": ["water", "leakage", "leak", "pipe", "tank", "tap", "supply", "drainage"],
    "ELECTRICITY": ["power", "light", "current", "electricity", "electric", "bulb", "wire", "transformer"],
    "ROAD": ["road", "pothole", "street", "path", "highway", "bridge", "footpath"],
    "SANITATION": ["garbage", "waste", "drain", "sewer", "clean", "dustbin", "trash", "sanitation"]
}


def assign_category_from_text(title: str = "", description: str = "") -> str:
    """
    Assign complaint category based on keyword matching
    """
    combined_text = f"{title or ''} {description or ''}".lower()
    
    if not combined_text.strip():
        return "GENERAL"
    
    # Count keyword matches for each category
    category_scores = {}
    for category, keywords in KEYWORD_MAPPING.items():
        score = sum(1 for keyword in keywords if keyword in combined_text)
        category_scores[category] = score
    
    # Get category with highest score
    max_score = max(category_scores.values())
    if max_score == 0:
        return "GENERAL"
    
    # Return category with highest score
    best_category = max(category_scores, key=category_scores.get)
    return best_category


def assign_officer_to_complaint(db: Session, category: str) -> Optional[int]:
    """
    Assign an officer to a complaint based on category
    Returns officer_id or None if no officer available
    """
    # Map category to officer role
    role_mapping = {
        "WATER": UserRole.OFFICER_WATER,
        "ELECTRICITY": UserRole.OFFICER_ELECTRICITY,
        "ROAD": UserRole.OFFICER_ROAD,
        "SANITATION": UserRole.OFFICER_SANITATION,
    }
    
    officer_role = role_mapping.get(category)
    if not officer_role:
        return None
    
    # Find officers with this role
    officers = db.query(User).filter(
        User.role == officer_role,
        User.is_active == True
    ).all()
    
    if not officers:
        return None
    
    # Simple round-robin: pick random officer
    # In production, implement load balancing
    selected_officer = random.choice(officers)
    return selected_officer.id
