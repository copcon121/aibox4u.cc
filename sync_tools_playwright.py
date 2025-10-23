"""
Auto Sync Tools using Playwright (for JavaScript-rendered sites)
Works with SPA sites like aitoolsdirectory.com
Enhanced version: Visits detail pages to get accurate category, price, and description
"""
import asyncio
from playwright.async_api import async_playwright
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
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
MAX_TOOLS_PER_RUN = 10  # Reduced because we visit detail pages
SCROLL_PAUSE = 2  # seconds to wait after scrolling
DETAIL_PAGE_DELAY = 2  # seconds between detail page visits

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
    
    async def extract_tool_details(self, tool_url):
        """Visit tool detail page and extract full information"""
        try:
            print(f"   🔍 Visiting: {tool_url}")
            await self.page.goto(tool_url, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_timeout(2000)
            
            details = await self.page.evaluate('''() => {
                // Extract category from breadcrumbs or category badges
                const categorySelectors = [
                    '.breadcrumb a[href*="/category/"]',
                    'a[href*="/category/"]',
                    '.category-badge',
                    '.sv-breadcrumb a',
                    '[class*="category"]',
                    '[class*="breadcrumb"] a'
                ];
                
                let category = 'AI Tools';
                for (const selector of categorySelectors) {
                    const elem = document.querySelector(selector);
                    if (elem && elem.textContent.trim() && !elem.textContent.toLowerCase().includes('home')) {
                        category = elem.textContent.trim();
                        break;
                    }
                }
                
                // Extract price type from badges or page content
                let priceType = 'Unknown';
                
                // Look for pricing badges/labels
                const pricingElements = document.querySelectorAll('.badge, .tag, .label, [class*="price"], [class*="pricing"]');
                for (const elem of pricingElements) {
                    const text = elem.textContent.toLowerCase();
                    if (text.includes('free') && !text.includes('trial')) {
                        priceType = 'Free';
                        break;
                    } else if (text.includes('freemium') || text.includes('free trial')) {
                        priceType = 'Freemium';
                        break;
                    } else if (text.includes('paid') || text.includes('premium')) {
                        priceType = 'Paid';
                        break;
                    }
                }
                
                // Fallback: search in page content
                if (priceType === 'Unknown') {
                    const bodyText = document.body.textContent.toLowerCase();
                    if (bodyText.includes('100% free') || bodyText.includes('completely free') || bodyText.includes('free to use')) {
                        priceType = 'Free';
                    } else if (bodyText.includes('freemium') || bodyText.includes('free trial') || bodyText.includes('free plan')) {
                        priceType = 'Freemium';
                    } else if (bodyText.includes('paid plan') || bodyText.includes('subscription') || bodyText.includes('premium')) {
                        priceType = 'Paid';
                    }
                }
                
                // Extract full description
                const descSelectors = [
                    '.tool-description',
                    '.sv-tool__description',
                    '[class*="description"]',
                    'article p',
                    'main p',
                    '.content p'
                ];
                
                let description = '';
                for (const selector of descSelectors) {
                    const elem = document.querySelector(selector);
                    if (elem && elem.textContent.trim().length > 50) {
                        description = elem.textContent.trim();
                        break;
                    }
                }
                
                // If no description found, collect paragraphs
                if (!description) {
                    const paragraphs = Array.from(document.querySelectorAll('main p, article p, .content p, [class*="description"] p'))
                        .map(p => p.textContent.trim())
                        .filter(text => text.length > 30 && !text.toLowerCase().includes('cookie') && !text.toLowerCase().includes('submit'));
                    description = paragraphs.slice(0, 2).join(' ');
                }
                
                return {
                    category: category,
                    price_type: priceType,
                    description: description || 'No description available'
                };
            }''')
            
            print(f"      ✅ Category: {details['category']}, Price: {details['price_type']}")
            return details
            
        except Exception as e:
            print(f"      ⚠️  Could not extract details: {str(e)}")
            return {
                'category': 'AI Tools',
                'price_type': 'Unknown',
                'description': 'No description available'
            }
    
    async def extract_tools_from_page(self):
        """Extract tools from the loaded page"""
        try:
            # Wait for content to load
            print("⏳ Waiting for content to load...")
            await self.page.wait_for_timeout(5000)  # Wait 5 seconds for JS to render
            
            # Scroll slowly to load ALL content and trigger lazy loading
            print("📜 Scrolling to load more content...")
            total_height = await self.page.evaluate('document.body.scrollHeight')
            viewport_height = await self.page.evaluate('window.innerHeight')
            current_position = 0
            
            while current_position < total_height:
                current_position += viewport_height
                await self.page.evaluate(f'window.scrollTo(0, {current_position})')
                await self.page.wait_for_timeout(1500)  # Wait 1.5s per scroll
                # Update total height as page may load more content
                total_height = await self.page.evaluate('document.body.scrollHeight')
            
            print(f"   ✅ Scrolled to bottom ({total_height}px)")
            
            # Trigger lazy loading for images - scroll to each element individually
            print("🖼️  Triggering lazy image loading...")
            image_count = await self.page.evaluate('''() => {
                const elements = document.querySelectorAll('div[role="img"], .sv-tile__image');
                return elements.length;
            }''')
            print(f"   Found {image_count} images to load...")
            
            # Scroll to each image element to trigger lazy loading
            batch_size = 10
            for i in range(0, image_count, batch_size):
                await self.page.evaluate(f'''() => {{
                    const elements = document.querySelectorAll('div[role="img"], .sv-tile__image');
                    for (let i = {i}; i < Math.min({i + batch_size}, elements.length); i++) {{
                        elements[i].scrollIntoView({{behavior: 'instant', block: 'center'}});
                        void elements[i].offsetHeight;
                    }}
                }}''')
                await self.page.wait_for_timeout(1000)
                print(f"   Loading batch {i//batch_size + 1}/{(image_count + batch_size - 1)//batch_size}...")
            
            print("   ✅ All images triggered, waiting for load...")
            await self.page.wait_for_timeout(3000)
            
            # Get all tool links
            tools_data = await self.page.evaluate(r'''() => {
                const tools = [];
                
                const selectors = [
                    '.sv-tiles-list a[href*="/tool/"]',
                    'div[class*="sv-tiles"] a[href*="/tool/"]',
                    'a[href^="/tool/"]'
                ];
                
                const foundLinks = new Set();
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(link => {
                        const href = link.href;
                        
                        if (!href || foundLinks.has(href) || 
                            href.includes('#') || 
                            href === window.location.href ||
                            !href.includes('/tool/')) {
                            return;
                        }
                        
                        foundLinks.add(href);
                        
                        let container = link.closest('article, .card, .tool, .item, .sv-tile, [class*="card"]');
                        if (!container) container = link.parentElement;
                        
                        const heading = container?.querySelector('h1, h2, h3, h4, h5, [class*="title"], [class*="name"]');
                        const name = heading?.textContent?.trim() || 
                                   link.textContent?.trim() ||
                                   link.getAttribute('title') ||
                                   link.getAttribute('aria-label') ||
                                   'Unknown Tool';
                        
                        // Extract image from div with role="img" and background-image
                        let imageUrl = '';
                        
                        const imgDiv = container?.querySelector('div[role="img"]') || 
                                       container?.querySelector('.sv-tile__image') ||
                                       container?.querySelector('div[class*="image"]');
                        
                        if (imgDiv) {
                            const style = window.getComputedStyle(imgDiv);
                            const bgImage = style.backgroundImage;
                            
                            if (bgImage && bgImage !== 'none') {
                                const match = bgImage.match(/url\(["']?([^"')]+)["']?\)/);
                                if (match) {
                                    imageUrl = match[1];
                                }
                            }
                        }
                        
                        if (!imageUrl) {
                            const img = container?.querySelector('img');
                            imageUrl = img?.src || img?.getAttribute('data-src') || '';
                        }
                        
                        const finalImageUrl = imageUrl && !imageUrl.startsWith('http') 
                            ? new URL(imageUrl, window.location.origin).href 
                            : imageUrl;
                        
                        const tagElements = container?.querySelectorAll('.tag, .badge, .label, [class*="tag"]') || [];
                        const tags = Array.from(tagElements).map(t => t.textContent?.trim()).filter(Boolean);
                        
                        tools.push({
                            name: name,
                            website_url: href,
                            image_url: finalImageUrl,
                            tags: tags
                        });
                    });
                });
                
                return tools;
            }''')
            
            print(f"📦 Extracted {len(tools_data)} potential tools")
            
            if tools_data:
                tools_with_images = sum(1 for t in tools_data if t.get('image_url'))
                print(f"   📊 {tools_with_images}/{len(tools_data)} tools have images")
            
            return tools_data[:MAX_TOOLS_PER_RUN]
            
        except Exception as e:
            print(f"❌ Error extracting tools: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_tools(self):
        """Main scraping function"""
        try:
            print(f"🌐 Navigating to {SOURCE_URL}...")
            await self.page.goto(SOURCE_URL, wait_until='networkidle', timeout=60000)
            
            print("✅ Page loaded")
            
            # Extract tool list
            tools = await self.extract_tools_from_page()
            
            if not tools:
                return []
            
            # Visit each tool's detail page to get full info
            print(f"\n🔎 Extracting details from {len(tools)} tool pages...")
            
            processed_tools = []
            for i, tool in enumerate(tools, 1):
                print(f"\n📄 [{i}/{len(tools)}] {tool['name']}")
                
                # Get details from tool page
                details = await self.extract_tool_details(tool['website_url'])
                
                # Merge data
                tool.update(details)
                
                # Modify content for uniqueness
                tool['description'] = self.modifier.modify_description(tool['description'])
                tool['tags'] = self.modifier.modify_tags(tool['tags'])
                
                processed_tools.append(tool)
                
                # Rate limiting
                if i < len(tools):
                    await asyncio.sleep(DETAIL_PAGE_DELAY)
            
            return processed_tools
            
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
                'name': tool_data['name'][:100],
                'description': tool_data['description'][:500] or 'No description available',
                'category': tool_data.get('category', 'AI Tools'),
                'tags': tool_data.get('tags', [])[:10],
                'price_type': tool_data.get('price_type', 'Unknown'),
                'website_url': tool_data['website_url'],
                'image_url': tool_data.get('image_url', ''),
                'is_featured': False,
                'featured_order': None,
                'is_active': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
                'synced_from': SOURCE_URL,
                'synced_at': datetime.now(timezone.utc),
            }
            
            await db.tools.insert_one(tool)
            print(f"✅ Saved: {tool['name']} | {tool['category']} | {tool['price_type']}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving tool {tool_data.get('name')}: {str(e)}")
            return False


async def sync_tools():
    """Main sync function"""
    print("="*60)
    print("🚀 Starting AI Tools Sync (Enhanced with Detail Pages)")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Source: {SOURCE_URL}")
    print(f"📊 Max tools per run: {MAX_TOOLS_PER_RUN}")
    print("="*60)
    
    try:
        async with PlaywrightScraper() as scraper:
            # Scrape tools
            tools = await scraper.scrape_tools()
            
            print(f"\n📦 Scraped {len(tools)} tools with full details")
            
            if not tools:
                print("⚠️  No tools found. The website structure may have changed.")
                return 0
            
            # Show sample
            if tools:
                print("\n📋 Sample tool:")
                sample = tools[0]
                print(f"   Name: {sample['name']}")
                print(f"   Category: {sample.get('category', 'N/A')}")
                print(f"   Price: {sample.get('price_type', 'N/A')}")
                print(f"   URL: {sample['website_url'][:60]}...")
                print(f"   Description: {sample['description'][:100]}...")
                print(f"   Image: {sample.get('image_url', 'N/A')[:60]}...")
                print()
            
            # Save to database
            saved_count = 0
            for tool in tools:
                if await scraper.save_tool_to_db(tool):
                    saved_count += 1
                await asyncio.sleep(0.1)
            
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