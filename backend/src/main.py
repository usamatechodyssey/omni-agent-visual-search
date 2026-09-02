import os
import sys
import asyncio
import random
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.src.core.config import settings

# --- API Route Imports ---
from backend.src.shared.api.routes import auth
from backend.src.shared.api.routes import settings as settings_route
from backend.src.shared.api.routes import ingestion
from backend.src.modules.visual_search.api.routes import visual

# Pakistan Timezone
PKT = ZoneInfo("Asia/Karachi")

# 1. App Initialize
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="OmniAgent Core API - The Intelligent Employee"
)

# 2. CORS Setup (Configurable via .env)
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Static Files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- 🔥 SMART KEEP-ALIVE WITH PKT SLEEP MODE ---
async def keep_alive_loop():
    """
    Space ko 24/7 active rakhne ke liye random ping karega.
    Lekin Pakistan Time (PKT) raat 3:30 AM se 8:00 AM tak Space ko sleep hone dega.
    """
    space_url = os.getenv("SPACE_URL", "http://127.0.0.1:8000/")
    print(f"✅ Keep-Alive Loop Shuru: Target {space_url}")

    while True:
        try:
            # 1. Current Pakistan Time check karein
            now_pkt = datetime.now(PKT)
            hour = now_pkt.hour
            minute = now_pkt.minute

            # 2. Sleep Mode Logic (PKT 03:30 se 08:00 tak)
            # Condition: (3:30 se 4:00) YA (4:00 se 8:00)
            is_sleep_time = (hour == 3 and minute >= 30) or (4 <= hour < 8)

            if is_sleep_time:
                print(f"🛌 Sleep Mode (PKT {now_pkt.strftime('%H:%M')}). Ping skip kar rahe hain...")
                # 10 minute (600 seconds) wait karke dobara check karenge
                await asyncio.sleep(600)
                continue

            # 3. Random Ping (Agar sleep mode nahi hai)
            wait_time = random.uniform(240, 480)  # 4 se 8 minute random gap
            await asyncio.sleep(wait_time)

            # Ping karein (Async, user requests block nahi hongi)
            async with httpx.AsyncClient(timeout=10) as client:
                await client.get(space_url)
                print(f"✅ Ping successful (waited {int(wait_time)}s)")

        except Exception as e:
            print(f"⚠️ Keep-Alive Ping Failed: {e}")
            await asyncio.sleep(60)  # Error par 1 minute baad retry

# --- 🔥 STARTUP EVENT (Keep-Alive + Model Pre-load) ---
@app.on_event("startup")
async def startup_event():
    # Background task start karein (Non-blocking)
    asyncio.create_task(keep_alive_loop())
    print("🚀 Keep-Alive Background Task Started!")

    # Model Pre-load (Taake subah 8 baje model jaldi ready ho)
    try:
        from backend.src.modules.visual_search.services.visual.engine import get_visual_model
        get_visual_model()
        print("✅ CLIP Model Pre-loaded on startup")
    except Exception as e:
        print(f"⚠️ Model preload failed: {e}")

# 4. Health Check Route
@app.get("/")
async def root():
    return {
        "message": "Welcome to OmniAgent Core 🚀",
        "status": "active",
        "widget_url": "/static/widget.js"
    }

# 5. API Router Includes
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(settings_route.router, prefix=settings.API_V1_STR, tags=["User Settings"])
app.include_router(ingestion.router, prefix=settings.API_V1_STR, tags=["Ingestion"])
app.include_router(visual.router, prefix=settings.API_V1_STR, tags=["Visual Search"])

# ==========================================
# UNIVERSAL START LOGIC
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Server on Port: {port}")
    uvicorn.run("backend.src.main:app", host="0.0.0.0", port=port, reload=True)