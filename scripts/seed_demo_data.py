import asyncio
import os
import sys

# Add backend to path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.database import AsyncSessionLocal, Base, engine
from backend.app.models import Organization, User, JobPosting, PipelineRun
from backend.app.models.enums import Role
from backend.app.core.security import get_password_hash

async def seed_data():
    print("Initializing Database Schemas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    print("Database Initialized. Seeding Demo Data...")
    
    async with AsyncSessionLocal() as db:
        # Create Organizations
        org1 = Organization(id="org_techcorp", name="TechCorp Inc", settings={"plan": "PRO"})
        org2 = Organization(id="org_startup", name="Agile Startup LLC", settings={"plan": "FREE"})
        db.add_all([org1, org2])
        await db.commit()
        
        # Create Recruiter Users
        # Using mock hashes to bypass bcrypt/passlib incompatibilities in Python 3.12 demo environs
        user1 = User(org_id=org1.id, email="recruiter@techcorp.com", hashed_password="$2b$12$mockhash12345", role=Role.RECRUITER)
        user2 = User(org_id=org2.id, email="admin@startup.com", hashed_password="$2b$12$mockhash67890", role=Role.ORG_ADMIN)
        db.add_all([user1, user2])
        await db.commit()
        
        # Create Job Postings
        job1 = JobPosting(org_id=org1.id, title="Senior Python Developer", description="Must have 5+ years FastAPI experience.", status="OPEN")
        job2 = JobPosting(org_id=org2.id, title="React Frontend Engineer", description="Vite, Tailwind CSS, Zustand mastery.", status="OPEN")
        db.add_all([job1, job2])
        await db.commit()
        
        # Create simulated candidates
        for i in range(1, 16): # 15 candidates for Demo UI load testing
            run = PipelineRun(
                org_id=org1.id, 
                job_id=job1.id, 
                candidate_id=f"simulated-candidate-{i}",
                status="COMPLETED" if i % 2 == 0 else "STAGE_2"
            )
            db.add(run)
        
        await db.commit()
        print("✅ Seeded 2 Orgs, 2 Users, 2 Jobs, 15 Candidate Pipelines successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
