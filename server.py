from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from models import (
    Tool, ToolCreate, SearchFilter,
    AdminLogin, Admin, Token, SiteSettings, SiteSettingsBase,
    Page, PageCreate, PageUpdate, Statistics
)
from auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "AI Tools Directory API", "version": "1.0.1"}

# Get all tools with filters
@api_router.get("/tools", response_model=List[Tool])
async def get_tools(
    search: Optional[str] = None,
    category: Optional[str] = None,
    price_type: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    query = {"is_active": True}  # Only return active tools to public
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    if category and category != "All":
        query["category"] = category
    
    if price_type and price_type != "All":
        query["price_type"] = price_type
    
    sort_direction = -1 if sort_order == "desc" else 1
    
    tools = await db.tools.find(query).sort(sort_by, sort_direction).to_list(1000)
    return [Tool(**tool) for tool in tools]

# Get featured tools
@api_router.get("/tools/featured", response_model=List[Tool])
async def get_featured_tools():
    tools = await db.tools.find({"is_featured": True, "is_active": True}).sort("featured_order", 1).to_list(10)
    return [Tool(**tool) for tool in tools]

# Get single tool by ID
@api_router.get("/tools/{tool_id}", response_model=Tool)
async def get_tool(tool_id: str):
    tool = await db.tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return Tool(**tool)

# Create new tool
@api_router.post("/tools", response_model=Tool)
async def create_tool(tool_input: ToolCreate):
    tool_dict = tool_input.dict()
    tool = Tool(**tool_dict)
    await db.tools.insert_one(tool.dict())
    return tool

# Update tool
@api_router.put("/tools/{tool_id}", response_model=Tool)
async def update_tool(tool_id: str, tool_input: ToolCreate):
    existing_tool = await db.tools.find_one({"id": tool_id})
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = tool_input.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.tools.update_one(
        {"id": tool_id},
        {"$set": update_data}
    )
    
    updated_tool = await db.tools.find_one({"id": tool_id})
    return Tool(**updated_tool)

# Delete tool
@api_router.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str):
    result = await db.tools.delete_one({"id": tool_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}

# Get all categories
@api_router.get("/categories")
async def get_categories():
    categories = await db.tools.distinct("category")
    return sorted(categories)

# Get all price types
@api_router.get("/price-types")
async def get_price_types():
    return ["All", "Free", "Paid", "Freemium"]

# ============================================
# ADMIN ROUTES
# ============================================

# Admin Login
@api_router.post("/admin/login", response_model=Token)
async def admin_login(login_data: AdminLogin):
    # Check if admin exists
    admin = await db.admins.find_one({"username": login_data.username})
    
    if not admin or not verify_password(login_data.password, admin["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Verify admin token
@api_router.get("/admin/verify")
async def verify_admin(current_admin: str = Depends(get_current_admin)):
    return {"username": current_admin, "authenticated": True}

# Create initial admin (for setup only - should be protected in production)
@api_router.post("/admin/create-initial")
async def create_initial_admin(username: str = "admin", password: str = "admin123"):
    # Check if any admin exists
    existing_admin = await db.admins.find_one({})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    admin = Admin(
        username=username,
        hashed_password=get_password_hash(password)
    )
    
    await db.admins.insert_one(admin.dict())
    return {"message": "Initial admin created successfully", "username": username}

# Get all tools for admin (including inactive ones)
@api_router.get("/admin/tools", response_model=List[Tool])
async def get_all_tools_admin(current_admin: str = Depends(get_current_admin)):
    tools = await db.tools.find({}).sort("created_at", -1).to_list(1000)
    return [Tool(**tool) for tool in tools]

# Create new tool (admin only)
@api_router.post("/admin/tools", response_model=Tool)
async def create_tool_admin(tool_input: ToolCreate, current_admin: str = Depends(get_current_admin)):
    # Create tool with default values
    tool_dict = tool_input.dict()
    tool_dict["is_active"] = True  # New tools are active by default
    tool_dict["is_featured"] = False  # New tools are not featured by default
    
    tool = Tool(**tool_dict)
    await db.tools.insert_one(tool.dict())
    return tool

# Update tool (admin only)
@api_router.put("/admin/tools/{tool_id}", response_model=Tool)
async def update_tool_admin(tool_id: str, tool_input: ToolCreate, current_admin: str = Depends(get_current_admin)):
    existing_tool = await db.tools.find_one({"id": tool_id})
    if not existing_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = tool_input.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.tools.update_one(
        {"id": tool_id},
        {"$set": update_data}
    )
    
    updated_tool = await db.tools.find_one({"id": tool_id})
    return Tool(**updated_tool)

# Delete tool (admin only)
@api_router.delete("/admin/tools/{tool_id}")
async def delete_tool_admin(tool_id: str, current_admin: str = Depends(get_current_admin)):
    result = await db.tools.delete_one({"id": tool_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"message": "Tool deleted successfully"}

# Toggle tool active status
@api_router.patch("/admin/tools/{tool_id}/toggle-active")
async def toggle_tool_active(tool_id: str, current_admin: str = Depends(get_current_admin)):
    tool = await db.tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    new_status = not tool.get("is_active", True)
    await db.tools.update_one(
        {"id": tool_id},
        {"$set": {"is_active": new_status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Tool status updated", "is_active": new_status}

# Toggle tool featured status
@api_router.patch("/admin/tools/{tool_id}/toggle-featured")
async def toggle_tool_featured(tool_id: str, current_admin: str = Depends(get_current_admin)):
    tool = await db.tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    new_status = not tool.get("is_featured", False)
    update_data = {"is_featured": new_status, "updated_at": datetime.utcnow()}
    
    # If setting as featured, set a default featured_order if not exists
    if new_status and not tool.get("featured_order"):
        max_order = await db.tools.find_one(
            {"is_featured": True},
            sort=[("featured_order", -1)]
        )
        update_data["featured_order"] = (max_order.get("featured_order", 0) + 1) if max_order else 1
    
    await db.tools.update_one(
        {"id": tool_id},
        {"$set": update_data}
    )
    
    return {"message": "Tool featured status updated", "is_featured": new_status}

# Get admin statistics
@api_router.get("/admin/stats", response_model=Statistics)
async def get_admin_statistics(current_admin: str = Depends(get_current_admin)):
    # Count totals
    total_tools = await db.tools.count_documents({})
    active_tools = await db.tools.count_documents({"is_active": True})
    featured_tools = await db.tools.count_documents({"is_featured": True})
    
    # Get categories
    categories = await db.tools.distinct("category")
    total_categories = len(categories)
    
    # Tools by category
    tools_by_category = {}
    for category in categories:
        count = await db.tools.count_documents({"category": category})
        tools_by_category[category] = count
    
    # Tools by price type
    price_types = ["Free", "Paid", "Freemium"]
    tools_by_price_type = {}
    for price_type in price_types:
        count = await db.tools.count_documents({"price_type": price_type})
        tools_by_price_type[price_type] = count
    
    return Statistics(
        total_tools=total_tools,
        active_tools=active_tools,
        featured_tools=featured_tools,
        total_categories=total_categories,
        tools_by_category=tools_by_category,
        tools_by_price_type=tools_by_price_type
    )

# Site Settings Routes
@api_router.get("/admin/site-settings", response_model=SiteSettings)
async def get_site_settings(current_admin: str = Depends(get_current_admin)):
    settings = await db.site_settings.find_one({})
    if not settings:
        # Return default settings
        default_settings = SiteSettings(
            site_name="AI Tools Directory",
            site_description="The world's best curated list of AI Tools",
            meta_title="AI Tools Directory",
            meta_description="Discover the best AI tools for your needs"
        )
        await db.site_settings.insert_one(default_settings.dict())
        return default_settings
    return SiteSettings(**settings)

@api_router.put("/admin/site-settings", response_model=SiteSettings)
async def update_site_settings(
    settings_input: SiteSettingsBase,
    current_admin: str = Depends(get_current_admin)
):
    settings = await db.site_settings.find_one({})
    
    update_data = settings_input.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    if settings:
        # Update existing
        await db.site_settings.update_one(
            {"id": settings["id"]},
            {"$set": update_data}
        )
        updated_settings = await db.site_settings.find_one({"id": settings["id"]})
    else:
        # Create new
        new_settings = SiteSettings(**update_data)
        await db.site_settings.insert_one(new_settings.dict())
        updated_settings = new_settings.dict()
    
    return SiteSettings(**updated_settings)

# Pages Management Routes
@api_router.get("/admin/pages", response_model=List[Page])
async def get_all_pages(current_admin: str = Depends(get_current_admin)):
    pages = await db.pages.find({}).sort("created_at", -1).to_list(100)
    return [Page(**page) for page in pages]

@api_router.get("/admin/pages/{page_id}", response_model=Page)
async def get_page(page_id: str, current_admin: str = Depends(get_current_admin)):
    page = await db.pages.find_one({"id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return Page(**page)

@api_router.post("/admin/pages", response_model=Page)
async def create_page(page_input: PageCreate, current_admin: str = Depends(get_current_admin)):
    # Check if slug already exists
    existing_page = await db.pages.find_one({"slug": page_input.slug})
    if existing_page:
        raise HTTPException(status_code=400, detail="Page with this slug already exists")
    
    page = Page(**page_input.dict())
    await db.pages.insert_one(page.dict())
    return page

@api_router.put("/admin/pages/{page_id}", response_model=Page)
async def update_page(
    page_id: str,
    page_input: PageUpdate,
    current_admin: str = Depends(get_current_admin)
):
    existing_page = await db.pages.find_one({"id": page_id})
    if not existing_page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Check if new slug conflicts with another page
    if page_input.slug != existing_page["slug"]:
        slug_conflict = await db.pages.find_one({
            "slug": page_input.slug,
            "id": {"$ne": page_id}
        })
        if slug_conflict:
            raise HTTPException(status_code=400, detail="Page with this slug already exists")
    
    update_data = page_input.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.pages.update_one(
        {"id": page_id},
        {"$set": update_data}
    )
    
    updated_page = await db.pages.find_one({"id": page_id})
    return Page(**updated_page)

@api_router.delete("/admin/pages/{page_id}")
async def delete_page(page_id: str, current_admin: str = Depends(get_current_admin)):
    result = await db.pages.delete_one({"id": page_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted successfully"}

# Public page endpoint (no auth required)
@api_router.get("/pages/{slug}", response_model=Page)
async def get_public_page(slug: str):
    page = await db.pages.find_one({"slug": slug, "is_published": True})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return Page(**page)

# ============================================
# SYNC TOOLS ROUTES
# ============================================

@api_router.post("/admin/sync-tools")
async def trigger_sync_tools(current_admin: str = Depends(get_current_admin)):
    """Manually trigger tools sync from external source"""
    try:
        from sync_tools_playwright import sync_tools
        
        # Run sync
        saved_count = await sync_tools()
        
        return {
            "success": True,
            "message": f"Sync completed. Added {saved_count} new tools",
            "tools_added": saved_count
        }
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )

@api_router.get("/admin/sync-status")
async def get_sync_status(current_admin: str = Depends(get_current_admin)):
    """Get last sync status"""
    try:
        # Get latest synced tool
        latest_synced = await db.tools.find_one(
            {"synced_from": {"$exists": True}},
            sort=[("synced_at", -1)]
        )
        
        if latest_synced:
            return {
                "last_sync": latest_synced.get("synced_at"),
                "synced_from": latest_synced.get("synced_from"),
                "total_synced_tools": await db.tools.count_documents({"synced_from": {"$exists": True}})
            }
        else:
            return {
                "last_sync": None,
                "message": "No synced tools found"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()