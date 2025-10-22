# Tạo file: backend/clear_tools.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def clear_tools():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    result = await db.tools.delete_many({})
    print(f"🗑️  Deleted {result.deleted_count} tools")
    client.close()

asyncio.run(clear_tools())