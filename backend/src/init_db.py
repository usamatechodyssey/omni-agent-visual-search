import asyncio
from backend.src.shared.db.session import engine
from backend.src.shared.db.base import Base

# Import only Visual Search + Shared models
from backend.src.shared.models.user import User
from backend.src.shared.models.integration import UserIntegration
from backend.src.modules.visual_search.models.ingestion import IngestionJob

# Reference them so linters don't flag as unused
ALL_MODELS = [User, UserIntegration, IngestionJob]


async def init_database():
    print("🚀 Connecting to the database...")
    async with engine.begin() as conn:
        print("🗑️ Dropping old tables to apply new Schema...")
        await conn.run_sync(Base.metadata.drop_all)

        print("⚙️ Creating new tables (Users, Integrations, Jobs)...")
        await conn.run_sync(Base.metadata.create_all)
        print(f"✅ Database tables created successfully! Models: {len(ALL_MODELS)}")


if __name__ == "__main__":
    print("Starting database initialization...")
    asyncio.run(init_database())