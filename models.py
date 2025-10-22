from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

# Tool Models
class ToolBase(BaseModel):
    name: str
    description: str
    category: str
    tags: List[str]
    price_type: str  # Free, Paid, Freemium
    website_url: str
    image_url: Optional[str] = None
    is_featured: bool = False
    featured_order: Optional[int] = None
    is_active: bool = True  # New field for enabling/disabling tools

class ToolCreate(ToolBase):
    pass

class Tool(ToolBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ChatGPT",
                "description": "AI-powered chatbot for conversations",
                "category": "Chatbot",
                "tags": ["AI", "Chat", "NLP"],
                "price_type": "Freemium",
                "website_url": "https://chat.openai.com",
                "image_url": "https://example.com/image.jpg",
                "is_featured": False,
                "is_active": True
            }
        }

class CategoryModel(BaseModel):
    name: str
    description: Optional[str] = None

class SearchFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    price_type: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"

# Admin Models
class AdminLogin(BaseModel):
    username: str
    password: str

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Site Settings Models
class SiteSettingsBase(BaseModel):
    site_name: str
    site_logo_url: Optional[str] = None
    site_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None

class SiteSettings(SiteSettingsBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Page Models
class PageBase(BaseModel):
    title: str
    slug: str
    content: str
    is_published: bool = True

class PageCreate(PageBase):
    pass

class PageUpdate(PageBase):
    pass

class Page(PageBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Statistics Models
class Statistics(BaseModel):
    total_tools: int
    active_tools: int
    featured_tools: int
    total_categories: int
    tools_by_category: dict
    tools_by_price_type: dict