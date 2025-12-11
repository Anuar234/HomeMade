"""
Bot Configuration
Loads environment variables and validates settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token from BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin IDs (comma-separated)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables!")

if not ADMIN_IDS:
    print("⚠️ Warning: No ADMIN_IDS configured. Admin features will not work.")

print(f"✅ Bot configuration loaded")
print(f"   Database: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")
print(f"   Admins: {len(ADMIN_IDS)} configured")
