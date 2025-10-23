"""
Clear all tools from database
Use this to test sync from scratch
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


async def clear_tools():
    """Clear all tools from database"""
    print("="*60)
    print("🗑️  Clear All Tools from Database")
    print("="*60)
    
    try:
        # Count current tools
        count = await db.tools.count_documents({})
        print(f"\n📊 Current tools in database: {count}")
        
        if count == 0:
            print("✅ Database is already empty!")
            return
        
        # Ask for confirmation
        print("\n⚠️  WARNING: This will delete ALL tools!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return
        
        # Delete all tools
        result = await db.tools.delete_many({})
        print(f"\n✅ Deleted {result.deleted_count} tools")
        
        # Verify
        remaining = await db.tools.count_documents({})
        print(f"📊 Remaining tools: {remaining}")
        
        print("\n" + "="*60)
        print("✅ Database cleared successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(clear_tools())