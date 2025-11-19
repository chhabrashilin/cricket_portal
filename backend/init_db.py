"""
Initialize database - creates tables and seeds data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base

print("🗄️  Initializing database...")

# Try to import shared models, fallback to local
try:
    from shared.models import User, Session, Delivery, Pose, WeaknessSummary
    print("✅ Using shared models")
except ImportError:
    try:
        from models import User, Session, Delivery, Pose, WeaknessSummary
        print("✅ Using local models")
    except ImportError as e:
        print(f"❌ Error importing models: {e}")
        sys.exit(1)

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    sys.exit(1)

# Seed database
print("🌱 Seeding database...")
try:
    from seed import seed_database
    seed_database()
    print("✅ Database seeded successfully")
except Exception as e:
    print(f"⚠️  Seed failed (may already be seeded): {e}")

print("✅ Database initialization complete!")

