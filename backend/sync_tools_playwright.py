"""
Auto Sync Tools using Playwright (for JavaScript-rendered sites)
Works with SPA sites like aitoolsdirectory.com
"""
import asyncio
from playwright.async_api import async_playwright
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
RATE_LIMIT_DELAY = 3  # seconds between requests
MAX_TOOLS_PER_RUN = 30
SCROLL_PAUSE = 2  # seconds to wait after scrolling

class ContentModifier:
    """Modify scraped content to make it unique"""
    
    @staticmethod
    def modify_description(text):
        """Paraphrase and modify description"""
        if not text:
            return text
        
        # Simple text modifications
        replacements = {
            'amazing': 'excellent',
            'powerful': 'robust',
            'innovative': 'cutting-edge',
            'revolutionize': 'transform',
            'enhance': 'improve',
            'streamline': 'optimize',
            'state-of-the-art': 'advanced',
            'cutting edge': 'innovative',
        }
        
        modified = text
        for old, new in replacements.items():
            if random.random() > 0.6:  # 40% chance to replace
                modified = re.sub(rf'\b{old}\b', new, modified, flags=re.IGNORECASE)
        
        # Add prefix/suffix variations
        prefixes = ['Discover', 'Explore', 'Try', 'Experience', 'Check out']
        if random.random() > 0.7 and len(modified) < 200:
            modified = f"{random.choice(prefixes)} {modified}"
        
        return modified
    
    @staticmethod
    def modify_tags(tags):
        """Add or modify tags"""
        if not tags:
            return tags
        
        additional_tags = ['AI', 'Automation', 'Productivity', 'Innovation', 'Technology']
        num_to_add = random.randint(0, 2)
        selected = random.sample(additional_tags, min(num_to_add, len(additional_tags)))
        
        return list(set(tags + selected))


class PlaywrightScraper:
    """Scraper using Playwright for JavaScript-rendered sites"""
    
    def __init__(self):
        self.modifier = ContentModifier()
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def extract_tools_from_page(self):
        """Extract tools from the loaded page"""
        try:
            # Wait for content to load
            print("⏳ Waiting for content to load...")
            await self.page.wait_for_timeout(5000)  # Wait 5 seconds for JS to render
            
            # Try to scroll to load more content
            print("📜 Scrolling to load more content...")
            for i in range(3):  # Scroll 3 times
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await self.page.wait_for_timeout(SCROLL_PAUSE * 1000)
            
            # Get all links that might be tool links
            tools_data = await self.page.evaluate('''() => {
                const tools = [];
                
                // Strategy 1: Find cards/items with links
                const selectors = [
                    'article a[href]',
                    '.card a[href]', 
                    '.tool a[href]',
                    '.item a[href]',
                    '[class*="tool"] a[href]',
                    '[class*="card"] a[href]',
                    'a[href*="tool"]'
                ];
                
                const foundLinks = new Set();
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(link => {
                        const href = link.href;
                        
                        // Skip internal links and duplicates
                        if (!href || foundLinks.has(href) || 
                            href.includes('#') || 
                            href === window.location.href) {
                            return;
                        }
                        
                        foundLinks.add(href);
                        
                        // Try to get parent container
                        let container = link.closest('article, .card, .tool, .item, [class*="card"]');
                        if (!container) container = link.parentElement;
                        
                        // Extract data
                        const name = link.textContent?.trim() || 
                                   link.querySelector('h1, h2, h3, h4, .title, [class*="title"]')?.textContent?.trim() ||
                                   'Unknown Tool';
                        
                        const description = container?.querySelector('p, .description, [class*="desc"]')?.textContent?.trim() || '';
                        
                        const img = container?.querySelector('img');
                        const imageUrl = img?.src || img?.getAttribute('data-src') || '';
                        
                        // Get tags from badges/labels
                        const tagElements = container?.querySelectorAll('.tag, .badge, .label, [class*="tag"]') || [];
                        const tags = Array.from(tagElements).map(t => t.textContent?.trim()).filter(Boolean);
                        
                        tools.push({
                            name: name,
                            description: description,
                            website_url: href,
                            image_url: imageUrl,
                            tags: tags
                        });
                    });
                });
                
                return tools;
            }''')
            
            print(f"📦 Extracted {len(tools_data)} potential tools")
            
            # Filter and process
            processed_tools = []
            for tool in tools_data[:MAX_TOOLS_PER_RUN]:
                if not tool['name'] or tool['name'] == 'Unknown Tool':
                    continue
                
                # Modify content
                tool['description'] = self.modifier.modify_description(tool['description'])
                tool['tags'] = self.modifier.modify_tags(tool['tags'])
                
                # Set defaults
                tool['category'] = 'AI Tools'
                tool['price_type'] = 'Unknown'
                
                # Try to detect price type from description
                desc_lower = tool['description'].lower()
                if any(word in desc_lower for word in ['free', 'gratis', 'no cost']):
                    tool['price_type'] = 'Free'
                elif any(word in desc_lower for word in ['paid', 'premium', 'subscription']):
                    tool['price_type'] = 'Paid'
                elif any(word in desc_lower for word in ['freemium', 'trial', 'free trial']):
                    tool['price_type'] = 'Freemium'
                
                processed_tools.append(tool)
            
            return processed_tools
            
        except Exception as e:
            print(f"❌ Error extracting tools: {str(e)}")
            return []
    
    async def scrape_tools(self):
        """Main scraping function"""
        try:
            print(f"🌐 Navigating to {SOURCE_URL}...")
            await self.page.goto(SOURCE_URL, wait_until='networkidle', timeout=60000)
            
            print("✅ Page loaded")
            
            # Extract tools
            tools = await self.extract_tools_from_page()
            
            return tools
            
        except Exception as e:
            print(f"❌ Error scraping: {str(e)}")
            return []
    
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
                'name': tool_data['name'][:100],  # Limit length
                'description': tool_data['description'][:500] or 'No description available',
                'category': tool_data.get('category', 'AI Tools'),
                'tags': tool_data.get('tags', [])[:10],  # Max 10 tags
                'price_type': tool_data.get('price_type', 'Unknown'),
                'website_url': tool_data['website_url'],
                'image_url': tool_data.get('image_url', ''),
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
    print("🚀 Starting AI Tools Sync (Playwright)")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Source: {SOURCE_URL}")
    print("="*60)
    
    try:
        async with PlaywrightScraper() as scraper:
            # Scrape tools
            tools = await scraper.scrape_tools()
            
            print(f"\n📦 Scraped {len(tools)} tools")
            
            if not tools:
                print("⚠️  No tools found. The website structure may have changed.")
                print("💡 Try manually inspecting the site and updating selectors")
                return 0
            
            # Show sample
            if tools:
                print("\n📋 Sample tool:")
                sample = tools[0]
                print(f"   Name: {sample['name']}")
                print(f"   URL: {sample['website_url'][:60]}...")
                print(f"   Description: {sample['description'][:100]}...")
                print()
            
            # Save to database
            saved_count = 0
            for tool in tools:
                if await scraper.save_tool_to_db(tool):
                    saved_count += 1
                await asyncio.sleep(0.1)  # Small delay
            
            print("\n" + "="*60)
            print(f"✅ Sync completed!")
            print(f"📊 New tools added: {saved_count}/{len(tools)}")
            print("="*60)
            
            return saved_count
            
    except Exception as e:
        print(f"\n❌ Sync failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(sync_tools())
