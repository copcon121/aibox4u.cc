# 🎯 Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Files kiểm tra trong `backend/`
- [ ] `server.py` - Main FastAPI application
- [ ] `models.py` - Pydantic models
- [ ] `seed_data.py` - Database seeding script
- [ ] `requirements.txt` - Python dependencies
- [ ] `railway.toml` - Railway configuration **[MỚI THÊM]**
- [ ] `Procfile` - Start command **[MỚI THÊM]**
- [ ] `runtime.txt` - Python version **[MỚI THÊM]**
- [ ] `nixpacks.toml` - Build configuration **[MỚI THÊM]**

### 2. MongoDB Atlas Setup
- [ ] Tạo account tại mongodb.com
- [ ] Tạo FREE cluster (M0)
- [ ] Tạo database user (username + password)
- [ ] Whitelist IP: 0.0.0.0/0 (Network Access)
- [ ] Copy connection string
- [ ] Thay `<username>` và `<password>` trong connection string

### 3. GitHub Repository
- [ ] Code đã push lên GitHub
- [ ] Repository có thể public hoặc private
- [ ] Đã commit các file cấu hình Railway mới

---

## 🚀 Railway Deployment Steps

### Step 1: Login Railway
- [ ] Vào https://railway.app/
- [ ] Login bằng GitHub account
- [ ] Authorize Railway access

### Step 2: Create New Project
- [ ] Click **New Project**
- [ ] Chọn **Deploy from GitHub repo**
- [ ] Select repository của bạn
- [ ] Railway bắt đầu tạo service

### Step 3: Configure Service Settings
- [ ] Click vào service vừa tạo
- [ ] Vào tab **Settings**
- [ ] Set **Root Directory** = `backend`
- [ ] **Start Command** để trống (Railway dùng Procfile tự động)
- [ ] Click **Save** hoặc **Deploy**

### Step 4: Add Environment Variables
- [ ] Vào tab **Variables**
- [ ] Click **New Variable** và thêm:

```
Variable: MONGO_URL
Value: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

```
Variable: DB_NAME
Value: aitools_directory
```

- [ ] Click **Add** để lưu

### Step 5: Generate Domain
- [ ] Vào tab **Settings**
- [ ] Scroll xuống mục **Domains**
- [ ] Click **Generate Domain**
- [ ] Copy URL: `https://your-app-name.up.railway.app`
- [ ] Lưu lại URL này để dùng cho frontend

### Step 6: Monitor Deployment
- [ ] Vào tab **Deployments**
- [ ] Xem deployment mới nhất
- [ ] Check **Build Logs** - Phải thấy "Building..."
- [ ] Check **Deploy Logs** - Phải thấy "Uvicorn running..."
- [ ] Status phải là **Success** (màu xanh)

### Step 7: Test API
Mở browser hoặc dùng curl:

- [ ] Test root: `https://your-app.up.railway.app/api/`
  - Expected: `{"message": "AI Tools Directory API", "version": "1.0.0"}`

- [ ] Test tools: `https://your-app.up.railway.app/api/tools`
  - Expected: Array of tools (hoặc [] nếu chưa seed)

- [ ] Test docs: `https://your-app.up.railway.app/docs`
  - Expected: Swagger UI page

### Step 8: Seed Database
Chạy từ máy local (sau khi test API thành công):

```bash
cd backend
# Update .env với MongoDB Atlas URL
python seed_data.py
```

- [ ] Seed script chạy thành công
- [ ] Test lại `https://your-app.up.railway.app/api/tools`
- [ ] Phải thấy 12 tools trong response

---

## 🐛 Common Issues & Fixes

### Issue 1: "Railpack could not determine how to build"
**Status**: ❌ Build Failed

**Fixes to try**:
- [ ] Kiểm tra Root Directory = `backend` trong Settings
- [ ] Kiểm tra có đủ 4 files: railway.toml, Procfile, runtime.txt, nixpacks.toml
- [ ] Push lại code với đầy đủ config files
- [ ] Redeploy trong Railway

### Issue 2: "Application startup failed"
**Status**: ⚠️ Deploy Failed

**Fixes to try**:
- [ ] Kiểm tra MONGO_URL trong Variables tab
- [ ] Kiểm tra MongoDB Network Access (phải có 0.0.0.0/0)
- [ ] Kiểm tra username/password trong connection string
- [ ] Test MongoDB connection từ local trước

### Issue 3: "502 Bad Gateway" khi truy cập URL
**Status**: ⚠️ Service Not Running

**Fixes to try**:
- [ ] Xem Deploy Logs trong Railway
- [ ] Kiểm tra service có đang chạy không (Deployments tab)
- [ ] Kiểm tra start command đúng format: `uvicorn server:app --host 0.0.0.0 --port $PORT`
- [ ] Redeploy service

### Issue 4: "Module not found" error
**Status**: ❌ Build Failed

**Fixes to try**:
- [ ] Kiểm tra requirements.txt có đầy đủ packages
- [ ] Từ local, chạy: `pip freeze > requirements.txt`
- [ ] Push lại code
- [ ] Redeploy

### Issue 5: API trả về empty array `[]`
**Status**: ✅ Working, nhưng no data

**Fix**:
- [ ] Chưa seed database
- [ ] Chạy `python seed_data.py` từ local
- [ ] Test lại API

---

## 📋 Post-Deployment Checklist

### Backend Verification
- [ ] API root endpoint working
- [ ] GET /api/tools returns data (12 tools)
- [ ] GET /api/tools/featured returns 2 tools (Perplexity & Comet)
- [ ] GET /api/categories returns array of categories
- [ ] Swagger docs accessible at /docs

### Frontend Integration
- [ ] Copy Railway URL
- [ ] Update frontend/.env: `REACT_APP_BACKEND_URL=https://your-app.up.railway.app`
- [ ] Redeploy frontend on Vercel
- [ ] Test frontend can fetch data from backend

### Final Tests
- [ ] Search functionality working
- [ ] Category filter working
- [ ] Price filter working
- [ ] Tool details page working
- [ ] No CORS errors in browser console

---

## 💰 Cost Tracking

Railway Free Tier:
- ✅ $5 free credit per month
- ✅ Đủ cho small app với moderate traffic
- ✅ Sleep after 30 minutes inactive (có thể config)

Monitor usage:
- [ ] Check Railway Dashboard → Usage
- [ ] Set up alerts nếu gần hết credit

---

## 🎉 Success Criteria

✅ Backend deployed successfully khi:
1. Railway deployment status = **Success**
2. API root endpoint trả về JSON response
3. GET /api/tools trả về 12 AI tools
4. GET /api/tools/featured trả về Perplexity & Comet Browser
5. Swagger docs (/docs) accessible
6. No errors in Railway logs

---

## 📞 Need Help?

- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app/
- Check `/app/backend/README.md` for detailed guide
- Check `/app/deploy.md` for full deployment guide

---

**Ready to deploy?** Follow checklist từ trên xuống! ✨
