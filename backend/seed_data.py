import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    # Clear existing tools
    await db.tools.delete_many({})
    
    tools = [
        {
            "id": str(uuid.uuid4()),
            "name": "Perplexity",
            "description": "AI-powered search engine that provides accurate answers with citations. Get FREE 1 month Pro account at https://pplx.ai/bloomingfi18891",
            "category": "Search",
            "tags": ["AI", "Search", "Research"],
            "price_type": "Freemium",
            "website_url": "https://pplx.ai/bloomingfi18891",
            "image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=500&h=300&fit=crop",
            "is_featured": True,
            "featured_order": 1,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Comet Browser",
            "description": "Next-generation browser with built-in AI capabilities. Claim FREE 1 month Pro account at https://pplx.ai/bloomingfi18891",
            "category": "Browser",
            "tags": ["AI", "Browser", "Productivity"],
            "price_type": "Freemium",
            "website_url": "https://pplx.ai/bloomingfi18891",
            "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=500&h=300&fit=crop",
            "is_featured": True,
            "featured_order": 2,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ChatGPT",
            "description": "Advanced AI chatbot powered by GPT-4 for conversations, writing, coding, and creative tasks.",
            "category": "Chatbot",
            "tags": ["AI", "Chat", "Writing", "Coding"],
            "price_type": "Freemium",
            "website_url": "https://chat.openai.com",
            "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Midjourney",
            "description": "AI art generator creating stunning images from text descriptions using advanced diffusion models.",
            "category": "Image Generation",
            "tags": ["AI", "Art", "Design", "Image"],
            "price_type": "Paid",
            "website_url": "https://midjourney.com",
            "image_url": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Notion AI",
            "description": "AI-powered workspace that helps you write, brainstorm, edit, summarize, and translate content.",
            "category": "Productivity",
            "tags": ["AI", "Writing", "Productivity", "Notes"],
            "price_type": "Freemium",
            "website_url": "https://notion.so",
            "image_url": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "GitHub Copilot",
            "description": "AI pair programmer that helps you write code faster with intelligent code completions.",
            "category": "Coding",
            "tags": ["AI", "Coding", "Development", "Automation"],
            "price_type": "Paid",
            "website_url": "https://github.com/features/copilot",
            "image_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Jasper AI",
            "description": "AI content platform that helps teams create content 10x faster with AI-powered writing assistant.",
            "category": "Writing",
            "tags": ["AI", "Writing", "Marketing", "Content"],
            "price_type": "Paid",
            "website_url": "https://jasper.ai",
            "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Runway ML",
            "description": "AI-powered video editing and generation tool for creating professional videos with text prompts.",
            "category": "Video Generation",
            "tags": ["AI", "Video", "Editing", "Creative"],
            "price_type": "Freemium",
            "website_url": "https://runwayml.com",
            "image_url": "https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Copy.ai",
            "description": "AI copywriting tool that generates marketing copy, blog posts, and social media content in seconds.",
            "category": "Marketing",
            "tags": ["AI", "Copywriting", "Marketing", "Content"],
            "price_type": "Freemium",
            "website_url": "https://copy.ai",
            "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "DALL-E 3",
            "description": "Advanced AI image generator by OpenAI that creates detailed images from text descriptions.",
            "category": "Image Generation",
            "tags": ["AI", "Image", "Art", "Creative"],
            "price_type": "Paid",
            "website_url": "https://openai.com/dall-e-3",
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "ElevenLabs",
            "description": "AI voice generator creating realistic speech synthesis and voice cloning in multiple languages.",
            "category": "Audio",
            "tags": ["AI", "Voice", "Audio", "Speech"],
            "price_type": "Freemium",
            "website_url": "https://elevenlabs.io",
            "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Grammarly",
            "description": "AI-powered writing assistant that helps you write clear, mistake-free content with style suggestions.",
            "category": "Writing",
            "tags": ["AI", "Writing", "Grammar", "Editing"],
            "price_type": "Freemium",
            "website_url": "https://grammarly.com",
            "image_url": "https://images.unsplash.com/photo-1456324504439-367cee3b3c32?w=500&h=300&fit=crop",
            "is_featured": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Add is_active to all tools
    for tool in tools:
        if "is_active" not in tool:
            tool["is_active"] = True
    
    await db.tools.insert_many(tools)
    print(f"✅ Successfully seeded {len(tools)} tools to database")
    
    # Create default admin if not exists
    admin_exists = await db.admins.find_one({"username": "admin"})
    if not admin_exists:
        admin = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "created_at": datetime.utcnow()
        }
        await db.admins.insert_one(admin)
        print("✅ Default admin created (username: admin, password: admin123)")
    else:
        print("ℹ️  Admin already exists, skipping admin creation")
    
if __name__ == "__main__":
    asyncio.run(seed_database())
    client.close()