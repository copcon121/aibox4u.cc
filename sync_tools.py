"""
Auto Sync Tools from AIToolsDirectory.com
Scrapes tools and modifies content before saving to database
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
import uuid
import re
import random
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Configuration
SOURCE_URL = "https://aitoolsdirectory.com"
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_TOOLS_PER_RUN = 50
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]

class ContentModifier:
    """Modify scraped content to make it unique"""
    
    @staticmethod
    def modify_description(text):
        """Paraphrase and modify description"""
        if not text:
            return text
            
        # Simple modifications - you can integrate AI paraphrasing here
        modifications = [
            # Add prefix variations
            lambda t: f"Discover {t}",
            lambda t: f"Explore {t}",
            lambda t: f"Check out {t}",
            # Add suffix variations
            lambda t: f"{t} - A powerful AI tool",
            lambda t: f"{t} - Enhance your productivity",
            lambda t: f"{t} for modern workflows",
        ]
        
        # Apply random modification
        if random.random() > 0.5:
            modifier = random.choice(modifications)
            text = modifier(text)
        
        # Replace some common words
        replacements = {
            'amazing': 'excellent',
            'powerful': 'robust',
            'innovative': 'cutting-edge',
            'revolutionize': 'transform',
            'enhance': 'improve',
            'streamline': 'optimize',
        }
        
        for old, new in replacements.items():
            if random.random() > 0.5:
                text = re.sub(rf'\b{old}\b', new, text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def modify_tags(tags):
        """Add or modify tags"""
        if not tags:
            return tags
        
        # Add generic AI tags
        additional_tags = ['AI', 'Automation', 'Productivity', 'Innovation']
        
        # Randomly add 1-2 additional tags
        num_to_add = random.randint(0, 2)
        selected = random.sample(additional_tags, min(num_to_add, len(additional_tags)))
        
        return list(set(tags + selected))


class AIToolsScraper:
    """Scraper for AI Tools Directory"""
    
    def __init__(self):
        self.session = None
        self.modifier = ContentModifier()
        
    async def __aenter__(self):
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url):
        """Fetch a page with rate limiting"""
        try:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"❌ Error fetching {url}: Status {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Exception fetching {url}: {str(e)}")
            return None
    
    async def parse_tool_card(self, card_html):
        """Parse individual tool card - CUSTOMIZE BASED ON ACTUAL HTML STRUCTURE"""
        try:
            soup = BeautifulSoup(card_html, 'html.parser')
            
            # TODO: Customize these selectors based on actual HTML structure
            # You need to inspect aitoolsdirectory.com to get correct selectors
            
            tool = {
                'name': None,
                'description': None,
                'category': 'Uncategorized',
                'tags': [],
                'price_type': 'Unknown',
                'website_url': None,
                'image_url': None,
            }
            
            # Example selectors (NEED TO BE UPDATED)
            name_elem = soup.select_one('.tool-name, h3, .title')
            if name_elem:
                tool['name'] = name_elem.get_text(strip=True)
            
            desc_elem = soup.select_one('.tool-description, .description, p')
            if desc_elem:
                tool['description'] = desc_elem.get_text(strip=True)
            
            link_elem = soup.select_one('a[href]')
            if link_elem:
                tool['website_url'] = link_elem.get('href')
            
            img_elem = soup.select_one('img[src]')
            if img_elem:
                tool['image_url'] = img_elem.get('src')
            
            # Extract category from classes or data attributes
            category_elem = soup.select_one('.category, [data-category]')
            if category_elem:
                tool['category'] = category_elem.get_text(strip=True) or category_elem.get('data-category')
            
            # Extract tags
            tag_elems = soup.select('.tag, .badge, .label')
            tool['tags'] = [tag.get_text(strip=True) for tag in tag_elems]
            
            # Determine price type from text or attributes
            if any(word in str(soup).lower() for word in ['free', 'gratis']):
                tool['price_type'] = 'Free'
            elif any(word in str(soup).lower() for word in ['paid', 'premium']):
                tool['price_type'] = 'Paid'
            elif any(word in str(soup).lower() for word in ['freemium', 'trial']):
                tool['price_type'] = 'Freemium'
            
            return tool if tool['name'] else None
            
        except Exception as e:
            print(f"❌ Error parsing tool card: {str(e)}")
            return None
    
    async def scrape_tools_list(self, page_url=None):
        """Scrape tools from main listing page"""
        url = page_url or SOURCE_URL
        
        html = await self.fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # TODO: Customize this selector based on actual HTML structure
        # Find all tool cards
        tool_cards = soup.select('.tool-card, .tool-item, article, .product')
        
        print(f"📋 Found {len(tool_cards)} tool cards on page")
        
        tools = []
        for card in tool_cards[:MAX_TOOLS_PER_RUN]:
            tool = await self.parse_tool_card(str(card))
            if tool and tool['name']:
                # Modify content
                tool['description'] = self.modifier.modify_description(tool['description'])
                tool['tags'] = self.modifier.modify_tags(tool['tags'])
                tools.append(tool)
        
        return tools
    
    async def save_tool_to_db(self, tool_data):
        """Save tool to database"""
        try:
            # Check if tool already exists
            existing = await db.tools.find_one({
                '$or': [
                    {'name': tool_data['name']},
                    {'website_url': tool_data['website_url']}
                ]
            })
            
            if existing:
                print(f"⏭️  Tool already exists: {tool_data['name']}")
                return False
            
            # Create tool document
            tool = {
                'id': str(uuid.uuid4()),
                'name': tool_data['name'],
                'description': tool_data['description'] or '',
                'category': tool_data['category'] or 'Uncategorized',
                'tags': tool_data['tags'] or [],
                'price_type': tool_data['price_type'] or 'Unknown',
                'website_url': tool_data['website_url'] or '',
                'image_url': tool_data['image_url'] or '',
                'is_featured': False,
                'featured_order': None,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'synced_from': SOURCE_URL,
                'synced_at': datetime.utcnow(),
            }
            
            await db.tools.insert_one(tool)
            print(f"✅ Saved tool: {tool['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving tool {tool_data.get('name')}: {str(e)}")
            return False


async def sync_tools():
    """Main sync function"""
    print("="*60)
    print("🚀 Starting AI Tools Sync")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        async with AIToolsScraper() as scraper:
            # Scrape tools
            tools = await scraper.scrape_tools_list()
            
            print(f"\n📦 Scraped {len(tools)} tools")
            
            # Save to database
            saved_count = 0
            for tool in tools:
                if await scraper.save_tool_to_db(tool):
                    saved_count += 1
            
            print("\n" + "="*60)
            print(f"✅ Sync completed!")
            print(f"📊 New tools added: {saved_count}/{len(tools)}")
            print("="*60)
            
            return saved_count
            
    except Exception as e:
        print(f"\n❌ Sync failed: {str(e)}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(sync_tools())
