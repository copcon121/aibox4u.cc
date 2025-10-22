"""
Auto-inspect website and update sync_tools.py with correct selectors
Combined script for ease of use
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re
from collections import Counter
from pathlib import Path

URL = "https://aitoolsdirectory.com"
TEST_URLS = [
    "https://aitoolsdirectory.com",
    "https://aitoolsdirectory.com/tools",
]

async def inspect_website():
    """Inspect website and detect selectors"""
    print("="*60)
    print("🔍 AUTO-DETECTING SELECTORS")
    print("="*60)
    
    for test_url in TEST_URLS:
        print(f"\n🌐 Trying: {test_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(test_url, timeout=30) as response:
                    if response.status != 200:
                        print(f"❌ Status {response.status}")
                        continue
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Save HTML for manual check
                    with open('/tmp/website_structure.html', 'w', encoding='utf-8') as f:
                        f.write(soup.prettify())
                    
                    # Detect selectors
                    selectors = detect_selectors(soup)
                    
                    if selectors['container']:
                        print(f"\n✅ Found valid selectors!")
                        save_config(selectors)
                        return selectors
                        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue
    
    return None

def detect_selectors(soup):
    """Auto-detect tool selectors"""
    
    result = {
        'container': None,
        'name': None,
        'description': None,
        'link': None,
        'image': None,
        'tags': None
    }
    
    # Find repeated elements (tool cards)
    all_divs = soup.find_all(['div', 'article', 'li'])
    
    class_counter = Counter()
    for elem in all_divs:
        classes = elem.get('class', [])
        text = elem.get_text(strip=True)
        
        # Must have substantial content
        if len(text) > 100 and len(text) < 1000:
            for cls in classes:
                class_counter[cls] += 1
    
    # Find most repeated class (likely tool container)
    repeated = [(cls, cnt) for cls, cnt in class_counter.items() if 5 <= cnt <= 50]
    
    if repeated:
        repeated.sort(key=lambda x: x[1], reverse=True)
        best_class = repeated[0][0]
        result['container'] = f'.{best_class}'
        
        print(f"\n🎯 Found container: .{best_class} ({repeated[0][1]} items)")
        
        # Analyze first container
        first = soup.find(class_=best_class)
        if first:
            # Find name (heading or strong text)
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                elem = first.find(tag)
                if elem:
                    if elem.get('class'):
                        result['name'] = f"{tag}.{elem['class'][0]}"
                    else:
                        result['name'] = tag
                    break
            
            # Find description
            p = first.find('p')
            if p and len(p.get_text(strip=True)) > 20:
                if p.get('class'):
                    result['description'] = f"p.{p['class'][0]}"
                else:
                    result['description'] = 'p'
            
            # Find link
            a = first.find('a', href=True)
            if a:
                if a.get('class'):
                    result['link'] = f"a.{a['class'][0]}"
                else:
                    result['link'] = 'a[href]'
            
            # Find image
            img = first.find('img')
            if img:
                if img.get('class'):
                    result['image'] = f"img.{img['class'][0]}"
                else:
                    result['image'] = 'img[src]'
            
            # Find tags/badges
            for cls_pattern in ['tag', 'badge', 'label', 'category']:
                elems = first.find_all(class_=lambda x: x and cls_pattern in str(x).lower())
                if elems:
                    cls = elems[0].get('class', [''])[0]
                    result['tags'] = f".{cls}"
                    break
    
    return result

def save_config(selectors):
    """Save detected selectors"""
    with open('/tmp/selectors_config.json', 'w') as f:
        json.dump(selectors, f, indent=2)
    
    print("\n📋 Detected selectors:")
    for key, value in selectors.items():
        if value:
            print(f"  {key}: {value}")

def update_sync_tools(selectors):
    """Update sync_tools.py with detected selectors"""
    
    if not selectors['container']:
        print("❌ No container selector found!")
        return False
    
    sync_file = Path(__file__).parent / 'sync_tools.py'
    
    # Backup
    backup = Path(__file__).parent / 'sync_tools.py.backup'
    with open(sync_file, 'r') as f:
        content = f.read()
    with open(backup, 'w') as f:
        f.write(content)
    
    print(f"\n💾 Backed up to: {backup.name}")
    
    # Update container selector
    content = re.sub(
        r"tool_cards = soup\.select\('(\.tool-card, \.tool-item, article, \.product)\'\)",
        f"tool_cards = soup.select('{selectors['container']}')",
        content
    )
    
    # Update name selector
    if selectors['name']:
        content = re.sub(
            r"name_elem = soup\.select_one\('(\.tool-name, h3, \.title)\'\)",
            f"name_elem = soup.select_one('{selectors['name']}')",
            content
        )
    
    # Update description
    if selectors['description']:
        content = re.sub(
            r"desc_elem = soup\.select_one\('(\.tool-description, \.description, p)\'\)",
            f"desc_elem = soup.select_one('{selectors['description']}')",
            content
        )
    
    # Update link
    if selectors['link']:
        content = re.sub(
            r"link_elem = soup\.select_one\('a\[href\]'\)",
            f"link_elem = soup.select_one('{selectors['link']}')",
            content
        )
    
    # Update image
    if selectors['image']:
        content = re.sub(
            r"img_elem = soup\.select_one\('img\[src\]'\)",
            f"img_elem = soup.select_one('{selectors['image']}')",
            content
        )
    
    # Update tags
    if selectors['tags']:
        content = re.sub(
            r"tag_elems = soup\.select\('(\.tag, \.badge, \.label)'\)",
            f"tag_elems = soup.select('{selectors['tags']}')",
            content
        )
    
    # Save
    with open(sync_file, 'w') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("✅ UPDATED sync_tools.py!")
    print("="*60)
    
    return True

async def main():
    """Main function"""
    print("\n🚀 AUTO-INSPECT AND UPDATE TOOL\n")
    
    # Step 1: Inspect
    selectors = await inspect_website()
    
    if not selectors:
        print("\n❌ Could not detect selectors!")
        print("💡 The site may use JavaScript rendering")
        print("💡 Try using sync_tools_playwright.py instead")
        return
    
    # Step 2: Update
    success = update_sync_tools(selectors)
    
    if success:
        print("\n📝 Files created:")
        print("  /tmp/selectors_config.json")
        print("  /tmp/website_structure.html")
        print("  backend/sync_tools.py.backup")
        print("\n🚀 Now run: python sync_tools.py")
    else:
        print("\n❌ Failed to update sync_tools.py")

if __name__ == "__main__":
    asyncio.run(main())
