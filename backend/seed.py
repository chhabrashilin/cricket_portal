"""
Seed script to create test data for development
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

# Try to import from shared models, fallback to local
try:
    from shared.models import User, Session as SessionModel, Delivery, Pose, WeaknessSummary
    from shared.types.enums import (
        UserRole, Handedness, ExperienceLevel, PlayStyle, ProcessingStatus,
        DeliveryType, Line, ShotType, Outcome, BowlerType, Surface
    )
    from auth import get_password_hash
    USING_SHARED = True
except ImportError:
    from models import User, Session as SessionModel, Delivery, Pose, WeaknessSummary
    from models import (
        Handedness, ProcessingStatus, DeliveryType, Line, ShotType, Outcome, BowlerType, Surface
    )
    # Create a simple UserRole enum for compatibility
    from enum import Enum
    class UserRole(str, Enum):
        PLAYER = "player"
        COACH = "coach"
        ADMIN = "admin"
    from auth import get_password_hash
    USING_SHARED = False

import random
from datetime import datetime, timedelta

def seed_database():
    """Seed the database with test data"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            # Create user with role
            if USING_SHARED:
                test_user = User(
                    email="test@example.com",
                    name="Test User",
                    password_hash=get_password_hash("password123"),
                    role=UserRole.PLAYER,
                    handedness=Handedness.RIGHT,
                    experience_level=ExperienceLevel.INTERMEDIATE,
                    play_style=PlayStyle.BALANCED
                )
            else:
                # Fallback for old model structure
                test_user = User(
                    email="test@example.com",
                    name="Test User",
                    password_hash=get_password_hash("password123"),
                    handedness=Handedness.RIGHT
                )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"Created test user: {test_user.email}")
        else:
            print(f"Test user already exists: {test_user.email}")
        
        # Create test sessions
        for i in range(3):
            session = SessionModel(
                user_id=test_user.id,
                title=f"Practice Session {i+1}",
                location="Local Cricket Ground",
                notes=f"Test session {i+1}",
                batting_hand=Handedness.RIGHT,
                bowler_type=BowlerType.PACE,
                surface=Surface.TURF,
                raw_video_url=f"s3://test-videos/session_{i+1}.mp4",
                processing_status=ProcessingStatus.COMPLETED
            )
            db.add(session)
            db.flush()
            
            # Create deliveries
            delivery_types = list(DeliveryType)
            shot_types = list(ShotType)
            outcomes = list(Outcome)
            lines = list(Line)
            
            for j in range(random.randint(15, 25)):
                delivery = Delivery(
                    session_id=session.id,
                    timestamp_in_video=j * 2.5 + random.uniform(0, 1),
                    inferred_delivery_type=random.choice(delivery_types).value,
                    line=random.choice(lines).value,
                    shot_type=random.choice(shot_types).value,
                    outcome=random.choice(outcomes).value,
                    ball_speed_estimate=random.uniform(120, 150),
                    bat_speed_estimate=random.uniform(30, 70),
                    score_zone=random.choice(["cover", "mid_off", "mid_on", "square_leg", "point"]),
                    rating=random.uniform(3, 9)
                )
                db.add(delivery)
            
            db.flush()
            
            # Create weakness summary
            weakness_summary = WeaknessSummary(
                user_id=test_user.id,
                session_id=session.id,
                summary_text=f"Analyzed {random.randint(15, 25)} deliveries. Success rate: {random.randint(40, 70)}%. Main areas for improvement: short ball pull shots, full deliveries outside off.",
                strengths_text="Strong timing on good length deliveries. Excellent defense technique.",
                key_weakness_tags=["short_ball_pull", "full_off_stump"],
                metric_breakdown={
                    "total_deliveries": random.randint(15, 25),
                    "by_outcome": {
                        "middled": random.randint(5, 10),
                        "edge": random.randint(2, 5),
                        "mishit": random.randint(3, 6),
                        "miss": random.randint(1, 3)
                    },
                    "combinations": {
                        "short_pull": {
                            "attempts": random.randint(8, 15),
                            "middled": random.randint(2, 5),
                            "edges": random.randint(2, 4),
                            "mishits": random.randint(2, 4),
                            "misses": random.randint(1, 3)
                        }
                    }
                },
                recommendations={
                    "drills": [
                        "Short ball pull-shot practice (20 minutes)",
                        "Full-length driving practice (20 minutes)"
                    ],
                    "focus_points": [
                        "Prioritize improving timing on short balls",
                        "Work on head position and balance"
                    ]
                }
            )
            db.add(weakness_summary)
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

