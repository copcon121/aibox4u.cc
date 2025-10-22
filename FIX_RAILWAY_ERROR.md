"# 🔧 Fix Railway \"pip: command not found\" Error

## ❌ Lỗi gặp phải:
```
/bin/bash: line 1: pip: command not found
ERROR: failed to build: failed to solve
```

---

## ✅ Giải pháp (Chọn 1 trong 3)

### 🎯 Giải Pháp 1: Đơn giản hóa Config (KHUYẾN NGHỊ)

**Bước 1**: Xóa các file config phức tạp (nếu có):
```bash
# Trong local machine
cd backend
rm nixpacks.toml  # Đã xóa
```

**Bước 2**: Chỉ giữ lại các file cần thiết:
- ✅ `requirements.txt` hoặc `requirements.min.txt`
- ✅ `Procfile` 
- ✅ `railway.json` (MỚI - đơn giản hơn railway.toml)
- ⚠️ `runtime.txt` (optional)

**Bước 3**: Railway Settings:
1. Vào Railway Dashboard → Service Settings
2. **Root Directory**: `backend`
3. **Build Command**: Để trống
4. **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Save và Redeploy

---

### 🎯 Giải Pháp 2: Dùng requirements tối giản

Nếu build vẫn lỗi, dùng `requirements.min.txt` thay vì `requirements.txt`:

**Bước 1**: Rename file:
```bash
cd backend
mv requirements.txt requirements.full.txt
mv requirements.min.txt requirements.txt
```

**Bước 2**: Push code:
```bash
git add .
git commit -m \"Use minimal requirements\"
git push origin main
```

**Bước 3**: Railway sẽ tự động redeploy với requirements nhẹ hơn

---

### 🎯 Giải Pháp 3: Dockerfile Custom (Nếu 2 cách trên không work)

**Tạo file `Dockerfile` trong `backend/`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.min.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.min.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Start command
CMD [\"uvicorn\", \"server:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8001\"]
```

**Push lên GitHub và Railway sẽ tự detect Dockerfile**

---

## 📋 Railway Settings - Cấu hình Đúng

### Option A: Không dùng Dockerfile
```
Root Directory: backend
Build Command: (empty)
Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Option B: Dùng Dockerfile
```
Root Directory: backend
Build Command: (empty - Railway tự detect Dockerfile)
Start Command: (empty - dùng CMD trong Dockerfile)
```

---

## 🧪 Test Local Trước Khi Deploy

```bash
cd backend

# Test với requirements.min.txt
pip install -r requirements.min.txt

# Start server
uvicorn server:app --reload --port 8001

# Test API
curl http://localhost:8001/api/
```

Nếu local chạy OK → Deploy lên Railway sẽ OK

---

## 🔍 Debug Railway Build

### Xem Logs:
1. Railway Dashboard → Deployments
2. Click vào deployment đang fail
3. Xem **Build Logs** tab
4. Tìm dòng lỗi cụ thể

### Common Issues:

**Issue**: `pip: command not found`
- Fix: Xóa `nixpacks.toml`, để Railway tự detect

**Issue**: `python: command not found`  
- Fix: Đảm bảo `runtime.txt` có `python-3.11.*`

**Issue**: `requirements.txt not found`
- Fix: Check Root Directory = `backend` trong Settings

**Issue**: Package installation failed
- Fix: Dùng `requirements.min.txt` (ít packages hơn)

---

## ✨ Quick Fix Commands

```bash
# 1. Xóa config files phức tạp
cd backend
rm nixpacks.toml

# 2. Dùng requirements tối giản
mv requirements.txt requirements.full.txt
mv requirements.min.txt requirements.txt

# 3. Commit và push
git add .
git commit -m \"Simplify Railway config\"
git push origin main

# 4. Railway sẽ tự động redeploy
```

---

## 📞 Vẫn Lỗi?

### Check Railway Logs chi tiết:
1. Build logs có dòng: \"Detected Python app\"?
2. Build logs có cài pip thành công không?
3. Build logs có lỗi gì khác?

### Last Resort - Contact Railway:
- Railway Discord: https://discord.gg/railway
- Railway GitHub Issues: https://github.com/railwayapp/nixpacks/issues

---

## ✅ Success Indicators

Deploy thành công khi thấy:
```
✓ Building...
✓ Installing Python 3.11
✓ Installing requirements
✓ Starting uvicorn
✓ Application startup complete
✓ Deployment successful
```

---

**Push code mới lên GitHub và Railway sẽ tự động redeploy!** 🚀
"
