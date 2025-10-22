"""
Inspect AIToolsDirectory.com structure
Run this first to understand the HTML structure for scraping
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

URL = "https://aitoolsdirectory.com"

async def inspect_website():
    """Inspect the website structure"""
    print("🔍 Inspecting website structure...")
    print(f"URL: {URL}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(URL, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ Error: Status {response.status}")
                    return
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                print("="*60)
                print("📋 PAGE STRUCTURE ANALYSIS")
                print("="*60)
                
                # Find potential tool containers
                print("\n1️⃣  POTENTIAL TOOL CONTAINERS:")
                print("-" * 40)
                
                container_selectors = [
                    'article', '.card', '.tool', '.item', '.product',
                    '[class*="tool"]', '[class*="card"]', '[class*="item"]'
                ]
                
                for selector in container_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        # Show first element structure
                        if len(elements) > 0:
                            first = elements[0]
                            print(f"   Sample classes: {first.get('class', [])}")
                            print(f"   Sample HTML (first 200 chars):")
                            print(f"   {str(first)[:200]}...")
                            print()
                
                # Find all unique classes
                print("\n2️⃣  ALL UNIQUE CLASSES (top 30):")
                print("-" * 40)
                all_classes = set()
                for elem in soup.find_all(class_=True):
                    all_classes.update(elem.get('class', []))
                
                sorted_classes = sorted(all_classes)[:30]
                for i, cls in enumerate(sorted_classes, 1):
                    print(f"{i}. {cls}")
                
                # Find links
                print("\n3️⃣  LINKS STRUCTURE:")
                print("-" * 40)
                links = soup.find_all('a', href=True)
                print(f"Total links found: {len(links)}")
                
                # Categorize links
                external_links = [l for l in links if l['href'].startswith('http')]
                internal_links = [l for l in links if l['href'].startswith('/')]
                
                print(f"External links: {len(external_links)}")
                print(f"Internal links: {len(internal_links)}")
                
                # Sample external links (potential tool links)
                print("\nSample external links (first 5):")
                for link in external_links[:5]:
                    print(f"  - {link['href']}")
                    print(f"    Text: {link.get_text(strip=True)[:50]}")
                    print(f"    Classes: {link.get('class', [])}")
                    print()
                
                # Find images
                print("\n4️⃣  IMAGES STRUCTURE:")
                print("-" * 40)
                images = soup.find_all('img', src=True)
                print(f"Total images found: {len(images)}")
                
                if images:
                    print("\nSample images (first 3):")
                    for img in images[:3]:
                        print(f"  - src: {img['src'][:60]}...")
                        print(f"    alt: {img.get('alt', 'N/A')}")
                        print(f"    classes: {img.get('class', [])}")
                        print()
                
                # Find common text patterns
                print("\n5️⃣  TEXT PATTERNS:")
                print("-" * 40)
                
                # Find headings
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
                print(f"Headings found: {len(headings)}")
                if headings:
                    print("Sample headings (first 5):")
                    for h in headings[:5]:
                        print(f"  {h.name}: {h.get_text(strip=True)[:50]}")
                
                # Save full HTML for manual inspection
                with open('/tmp/website_structure.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                
                print("\n" + "="*60)
                print("✅ Inspection complete!")
                print("📄 Full HTML saved to: /tmp/website_structure.html")
                print("="*60)
                
                print("\n📝 NEXT STEPS:")
                print("1. Open /tmp/website_structure.html to see full HTML")
                print("2. Identify the correct selectors for:")
                print("   - Tool container (e.g., .tool-card, article)")
                print("   - Tool name")
                print("   - Tool description")
                print("   - Tool link")
                print("   - Tool image")
                print("   - Tool category/tags")
                print("3. Update sync_tools.py with correct selectors")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(inspect_website())
