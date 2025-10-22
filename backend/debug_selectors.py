"""
Debug script to find correct selectors for aitoolsdirectory.com
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

URL = "https://aitoolsdirectory.com"

async def debug_selectors():
    print("🔍 DEBUGGING SELECTORS FOR AITOOLSDIRECTORY.COM")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"🌐 Loading {URL}...")
        await page.goto(URL, wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        # Get HTML
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Save HTML
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("💾 Saved HTML to: debug_page.html")
        
        # Try different selectors
        selectors_to_try = [
            'div[class*="tool"]',
            'article',
            'div[class*="card"]',
            'div[class*="item"]',
            'a[class*="tool"]',
            'li[class*="tool"]',
        ]
        
        print("\n📋 TRYING DIFFERENT SELECTORS:")
        print("-"*60)
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements and len(elements) > 3:
                print(f"\n✅ Selector: {selector}")
                print(f"   Found: {len(elements)} elements")
                
                # Show first element
                first = elements[0]
                print(f"   Classes: {first.get('class', [])}")
                
                # Try to find name
                name = None
                for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'strong']:
                    elem = first.find(tag)
                    if elem:
                        name = elem.get_text(strip=True)
                        break
                
                # Try to find link
                link = first.find('a', href=True)
                link_url = link.get('href') if link else None
                
                # Try to find description
                desc = first.find('p')
                description = desc.get_text(strip=True)[:100] if desc else None
                
                print(f"   Sample name: {name}")
                print(f"   Sample URL: {link_url}")
                print(f"   Sample desc: {description}")
                print(f"   HTML preview: {str(first)[:200]}...")
        
        # Check for specific patterns
        print("\n\n🔎 CHECKING COMMON PATTERNS:")
        print("-"*60)
        
        # Look for data attributes
        data_attrs = soup.find_all(attrs={'data-tool': True})
        if data_attrs:
            print(f"✅ Found elements with data-tool: {len(data_attrs)}")
        
        # Look for grid/list containers
        containers = soup.find_all(['div', 'section'], class_=lambda x: x and ('grid' in str(x).lower() or 'list' in str(x).lower()))
        if containers:
            print(f"✅ Found grid/list containers: {len(containers)}")
            for c in containers[:3]:
                print(f"   Container classes: {c.get('class', [])}")
        
        print("\n"+"="*60)
        print("✅ Debug complete! Check debug_page.html for details")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_selectors())
