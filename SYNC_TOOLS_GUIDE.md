# 🔄 Hướng Dẫn Đồng Bộ Tools Tự Động

## 📋 Tổng Quan

Hệ thống tự động scrape và đồng bộ AI tools từ aitoolsdirectory.com với khả năng:
- ✅ Tự động thay đổi nội dung (paraphrase)
- ✅ Kiểm tra trùng lặp
- ✅ Rate limiting để tránh spam
- ✅ Chạy thủ công hoặc tự động theo lịch
- ✅ Tích hợp vào Admin Panel

## 📁 Files Đã Tạo

```
backend/
├── sync_tools.py           # Script chính để sync tools
├── inspect_website.py      # Tool để inspect cấu trúc website
├── schedule_sync.py        # Scheduler để chạy tự động
└── server.py              # Đã thêm API endpoints
```

## 🚀 Bước 1: Inspect Website Structure

**QUAN TRỌNG**: Trước khi chạy sync, bạn cần hiểu cấu trúc HTML của aitoolsdirectory.com

```bash
cd /app/backend
python inspect_website.py
```

**Output:**
- In ra console: Cấu trúc HTML, classes, selectors
- File `/tmp/website_structure.html`: Full HTML để xem chi tiết

**Sau khi inspect:**
1. Mở file `/tmp/website_structure.html`
2. Tìm các selector cho:
   - Tool container (ví dụ: `.tool-card`, `article`)
   - Tool name
   - Tool description  
   - Tool link
   - Tool image
   - Category/tags

3. **Cập nhật file `sync_tools.py`:**

```python
# Tìm dòng này trong parse_tool_card():
tool_cards = soup.select('.tool-card, .tool-item, article, .product')

# Và cập nhật các selectors:
name_elem = soup.select_one('.tool-name, h3, .title')
desc_elem = soup.select_one('.tool-description, .description, p')
# ... etc
```

## 🔧 Bước 2: Test Sync Thủ Công

Sau khi cập nhật selectors, test sync:

```bash
cd /app/backend
python sync_tools.py
```

**Kết quả mong đợi:**
```
🚀 Starting AI Tools Sync
📅 2025-10-22 12:00:00
============================================================
📋 Found 50 tool cards on page
📦 Scraped 50 tools
✅ Saved tool: ChatGPT
✅ Saved tool: Midjourney
⏭️  Tool already exists: DALL-E
...
============================================================
✅ Sync completed!
📊 New tools added: 45/50
============================================================
```

## 📅 Bước 3: Schedule Tự Động (Optional)

Để chạy sync tự động mỗi 24 giờ:

```bash
cd /app/backend
python schedule_sync.py
```

**Hoặc dùng cron job:**

```bash
# Mở crontab
crontab -e

# Thêm dòng này để chạy mỗi ngày lúc 2AM
0 2 * * * cd /app/backend && python sync_tools.py >> /var/log/tools_sync.log 2>&1
```

## 🎛️ Bước 4: Sử Dụng Qua Admin Panel

Đã thêm 2 endpoints mới vào admin:

### 1. Trigger Sync Thủ Công
```bash
POST /api/admin/sync-tools
Headers: Authorization: Bearer <admin_token>
```

**Ví dụ với curl:**
```bash
# Login để lấy token
TOKEN=$(curl -X POST "http://localhost:8001/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Trigger sync
curl -X POST "http://localhost:8001/api/admin/sync-tools" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Xem Sync Status
```bash
GET /api/admin/sync-status
Headers: Authorization: Bearer <admin_token>
```

## ⚙️ Configuration

### Thay đổi cấu hình trong `sync_tools.py`:

```python
# Số tools tối đa mỗi lần sync
MAX_TOOLS_PER_RUN = 50

# Delay giữa các requests (seconds)
RATE_LIMIT_DELAY = 2

# Source URL
SOURCE_URL = "https://aitoolsdirectory.com"
```

### Tùy chỉnh Content Modification

Trong class `ContentModifier`, bạn có thể:

1. **Thay đổi cách paraphrase:**
```python
def modify_description(self, text):
    # Thêm logic paraphrase của bạn
    # Hoặc tích hợp AI (OpenAI, Claude) để paraphrase
    pass
```

2. **Thêm/bớt tags:**
```python
def modify_tags(self, tags):
    # Custom logic để modify tags
    pass
```

## 🎨 Tích Hợp AI Paraphrasing (Advanced)

Nếu muốn dùng AI để paraphrase nội dung:

```python
# Trong sync_tools.py, thêm:
import openai

class ContentModifier:
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
    
    async def ai_paraphrase(self, text):
        """Use AI to paraphrase content"""
        if not self.openai_key:
            return self.modify_description(text)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Paraphrase this in a unique way: {text}"
                }]
            )
            return response.choices[0].message.content
        except:
            return self.modify_description(text)
```

## 📊 Monitoring

### Xem logs của sync:
```bash
# Nếu chạy manual
python sync_tools.py

# Nếu dùng cron
tail -f /var/log/tools_sync.log
```

### Kiểm tra database:
```python
# Connect to MongoDB và xem synced tools
from pymongo import MongoClient

client = MongoClient(mongo_url)
db = client['aitools_directory']

# Count synced tools
synced_count = db.tools.count_documents({"synced_from": {"$exists": True}})
print(f"Total synced tools: {synced_count}")

# Get latest synced
latest = db.tools.find_one(
    {"synced_from": {"$exists": True}},
    sort=[("synced_at", -1)]
)
print(f"Latest sync: {latest['synced_at']}")
```

## ⚠️ Lưu Ý Quan Trọng

### 1. Legal & Ethical
- ⚠️ Scraping có thể vi phạm Terms of Service
- ⚠️ Luôn respect robots.txt
- ⚠️ Không spam với quá nhiều requests
- ✅ Content được modify để tránh duplicate

### 2. Rate Limiting
- Script có built-in delay (2 giây/request)
- Không nên giảm delay quá thấp
- Có thể bị block IP nếu spam

### 3. Maintenance
- Website structure có thể thay đổi
- Cần định kỳ kiểm tra và update selectors
- Test trước khi chạy production

## 🐛 Troubleshooting

### Lỗi: "No tools found"
```
Nguyên nhân: Selectors không đúng
Fix: Chạy lại inspect_website.py và cập nhật selectors
```

### Lỗi: "Connection timeout"
```
Nguyên nhân: Website chặn hoặc quá chậm
Fix: Tăng timeout trong fetch_page(), thử lại sau
```

### Lỗi: "All tools already exist"
```
Nguyên nhân: Tools đã được sync trước đó
Fix: Normal behavior, script skip duplicate
```

## 📈 Tối Ưu Hóa

### 1. Pagination Support
Để scrape nhiều pages:
```python
async def scrape_all_pages(self):
    all_tools = []
    for page in range(1, 11):  # Scrape 10 pages
        url = f"{SOURCE_URL}/page/{page}"
        tools = await self.scrape_tools_list(url)
        all_tools.extend(tools)
    return all_tools
```

### 2. Parallel Processing
```python
import asyncio

async def scrape_multiple_sources(self):
    sources = [url1, url2, url3]
    tasks = [self.scrape_tools_list(url) for url in sources]
    results = await asyncio.gather(*tasks)
    return [tool for result in results for tool in result]
```

## 📞 Support

Nếu có vấn đề:
1. Kiểm tra logs
2. Verify selectors với inspect_website.py
3. Test với một tool đơn lẻ trước
4. Kiểm tra MongoDB connection

---

**Created by E1 Agent**
**Last Updated: 2025-10-22**
