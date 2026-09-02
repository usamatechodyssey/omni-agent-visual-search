import asyncio
from sqlalchemy import text
from backend.src.shared.db.session import engine, AsyncSessionLocal
from backend.src.shared.models.user import User
from backend.src.shared.utils.auth import generate_api_key
from sqlalchemy.future import select

async def upgrade_database():
    print("⚙️ Updating Database Schema (Without Deleting Data)...")
    
    async with engine.begin() as conn:
        # --- Add all columns using IF NOT EXISTS (idempotent) ---
        print("   -> Ensuring columns exist...")
        
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key VARCHAR;"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS allowed_domains VARCHAR DEFAULT '*';"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS bot_name VARCHAR DEFAULT 'Support Agent';"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS bot_instruction TEXT DEFAULT 'You are a helpful customer support agent.';"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS selected_vector_provider VARCHAR DEFAULT '';"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS selected_collection_name VARCHAR DEFAULT '';"))
        
        await conn.execute(text("ALTER TABLE user_integrations ADD COLUMN IF NOT EXISTS profile_description TEXT;"))

    print("✅ Database Schema Updated!")

    # --- 2. Generate API Keys for existing users (if missing) ---
    print("🔑 Generating API Keys for existing users...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        count = 0
        for user in users:
            if not user.api_key:
                user.api_key = generate_api_key()
                user.allowed_domains = "*"
                db.add(user)
                count += 1
                print(f"   -> Key generated for: {user.email}")
        await db.commit()
        print(f"✅ {count} Users updated with new API Keys.")

if __name__ == "__main__":
    asyncio.run(upgrade_database())