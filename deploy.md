# 🚀 Hướng dẫn Deploy - AI Tools Directory

Hướng dẫn chi tiết để deploy website lên production cho người mới bắt đầu.

## 📋 Checklist Deploy

- [ ] Setup MongoDB Atlas Database
- [ ] Deploy Backend lên Railway
- [ ] Deploy Frontend lên Vercel
- [ ] Cấu hình Domain aibox4u.cc
- [ ] Test production site

---

## 🗄️ Bước 1: Setup MongoDB Atlas (Database)

### 1.1. Tạo Account và Cluster

1. Truy cập: https://www.mongodb.com/cloud/atlas/register
2. Đăng ký account mới (có thể dùng Google/GitHub login)
3. Sau khi đăng nhập, chọn **Create a New Cluster**

### 1.2. Cấu hình Cluster

1. **Chọn Provider & Region**:
   - Cloud Provider: AWS
   - Region: Chọn Singapore hoặc gần Việt Nam nhất (us-east-1 cũng OK)
   
2. **Cluster Tier**:
   - Chọn **M0 Sandbox (FREE)** - Đủ cho bắt đầu
   - RAM: 512MB, Storage: 5GB

3. **Cluster Name**:
   - Đặt tên: `aitools-cluster` (hoặc tên bạn thích)

4. Click **Create Cluster** (mất 3-5 phút)

### 1.3. Tạo Database User

1. Trong sidebar, click **Database Access**
2. Click **Add New Database User**
3. Chọn **Password** authentication method
4. Điền:
   - Username: `aitools_admin` (hoặc tên khác)
   - Password: Click **Autogenerate Secure Password** hoặc tự đặt
   - **LƯU LẠI USERNAME VÀ PASSWORD NÀY** - rất quan trọng!
5. Database User Privileges: Chọn **Read and write to any database**
6. Click **Add User**

### 1.4. Whitelist IP Address

1. Trong sidebar, click **Network Access**
2. Click **Add IP Address**
3. Chọn **Allow Access from Anywhere**
   - IP Address: `0.0.0.0/0`
4. Click **Confirm**

### 1.5. Lấy Connection String

1. Quay lại **Database** (sidebar)
2. Click nút **Connect** trên cluster
3. Chọn **Connect your application**
4. Driver: **Python**, Version: **3.12 or later**
5. Copy connection string:
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
6. Thay `<username>` và `<password>` bằng thông tin từ bước 1.3
7. **LƯU LẠI CONNECTION STRING NÀY**

Ví dụ:
```
mongodb+srv://aitools_admin:MySecurePass123@aitools-cluster.abc123.mongodb.net/?retryWrites=true&w=majority
```

---

## 🚂 Bước 2: Deploy Backend lên Railway

### 2.1. Chuẩn bị Repository

1. Push code lên GitHub (nếu chưa có):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### 2.2. Tạo Railway Account

1. Truy cập: https://railway.app/
2. Click **Login** → Đăng nhập bằng GitHub
3. Authorize Railway access

### 2.3. Tạo New Project

1. Click **New Project**
2. Chọn **Deploy from GitHub repo**
3. Select repository của bạn
4. Railway sẽ tự detect code

### 2.4. Cấu hình Backend Service

1. Railway sẽ tạo service tự động
2. Click vào service → **Settings** tab

3. **Root Directory** (QUAN TRỌNG):
   - Click vào **Settings** tab
   - Tìm mục **Root Directory**
   - Set: `backend`
   - Click **Save** hoặc Deploy
   - (Vì backend code nằm trong thư mục backend/)

4. **Build & Start Command** (Đã có trong file cấu hình):
   - Railway sẽ tự động dùng `railway.toml` và `Procfile`
   - Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **KHÔNG CẦN** nhập thủ công nếu đã push code với các file cấu hình

5. **Environment Variables**:
   - Click **Variables** tab
   - Add các biến:
   
   ```
   MONGO_URL=mongodb+srv://aitools_admin:MySecurePass123@cluster.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=aitools_directory
   PORT=8001
   ```
   
   (Thay MONGO_URL bằng connection string từ bước 1.5)

6. **Generate Domain**:
   - Trong **Settings** tab
   - Phần **Domains**
   - Click **Generate Domain**
   - Railway sẽ tạo URL dạng: `https://your-app.up.railway.app`
   - **LƯU LẠI URL NÀY** - sẽ dùng cho frontend

### 2.5. Deploy và Seed Data

1. Click **Deploy** (hoặc deploy tự động sau khi save settings)
2. Đợi deployment hoàn tất (2-3 phút)
3. Kiểm tra logs xem có lỗi không

4. **Seed database** (tạo dữ liệu mẫu):
   - Railway có thể tự chạy seed_data.py
   - Hoặc chạy manual qua local:
   ```bash
   # Trong terminal local
   cd backend
   # Set MONGO_URL trong .env thành MongoDB Atlas URL
   python seed_data.py
   ```

5. Test API:
   - Truy cập: `https://your-app.up.railway.app/api/tools`
   - Nếu thấy JSON data → Thành công! ✅

---

## ▲ Bước 3: Deploy Frontend lên Vercel

### 3.1. Tạo Vercel Account

1. Truy cập: https://vercel.com/signup
2. Đăng nhập bằng GitHub
3. Authorize Vercel access

### 3.2. Import Project

1. Click **Add New...** → **Project**
2. Import Git Repository
3. Chọn repository của bạn
4. Click **Import**

### 3.3. Cấu hình Project

1. **Framework Preset**: Create React App (auto-detect)

2. **Root Directory**: 
   - Click **Edit** 
   - Chọn `frontend`

3. **Build Settings**:
   - Build Command: `yarn build`
   - Output Directory: `build`
   - Install Command: `yarn install`

4. **Environment Variables**:
   Click **Environment Variables** → Add:
   
   ```
   REACT_APP_BACKEND_URL=https://your-app.up.railway.app
   ```
   
   (Thay bằng Railway URL từ bước 2.4)

5. Click **Deploy**

### 3.4. Deployment

1. Vercel sẽ build và deploy (2-3 phút)
2. Sau khi xong, Vercel cung cấp URL:
   - Production: `https://your-project.vercel.app`
   - **LƯU LẠI URL NÀY**

3. Test website:
   - Truy cập URL
   - Kiểm tra tools hiển thị đúng
   - Test search, filter
   - Test click vào tool details

---

## 🌐 Bước 4: Cấu hình Domain aibox4u.cc

### 4.1. Nếu đã có Domain

#### Cấu hình cho Vercel (Frontend)

1. Vào Vercel Dashboard → Project Settings
2. Tab **Domains**
3. Add domain: `aibox4u.cc`
4. Vercel sẽ yêu cầu cấu hình DNS

5. Vào nhà cung cấp domain (ví dụ: Namecheap, GoDaddy)
6. Thêm DNS records:

**Type A Record:**
```
Type: A
Host: @
Value: 76.76.21.21
TTL: Automatic
```

**Type CNAME Record:**
```
Type: CNAME
Host: www
Value: cname.vercel-dns.com
TTL: Automatic
```

7. Đợi DNS propagate (5-30 phút)
8. Vercel tự động cấp SSL certificate

#### Cấu hình API Subdomain cho Railway (Backend)

1. Tạo subdomain cho backend: `api.aibox4u.cc`
2. Trong DNS settings, thêm:

```
Type: CNAME
Host: api
Value: your-app.up.railway.app
TTL: Automatic
```

3. Trong Railway:
   - Settings → Domains
   - Add custom domain: `api.aibox4u.cc`

4. Update frontend environment variable trong Vercel:
   ```
   REACT_APP_BACKEND_URL=https://api.aibox4u.cc
   ```

5. Redeploy frontend trên Vercel

### 4.2. Nếu chưa có Domain

Có thể dùng URLs miễn phí từ Vercel và Railway:
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-app.up.railway.app`

Mua domain sau tại:
- Namecheap: https://www.namecheap.com/
- GoDaddy: https://www.godaddy.com/
- Google Domains: https://domains.google/

---

## ✅ Bước 5: Testing Production

### 5.1. Checklist Test

- [ ] Truy cập `https://aibox4u.cc` (hoặc Vercel URL)
- [ ] Kiểm tra Featured Tools hiển thị (Perplexity & Comet)
- [ ] Test search bar
- [ ] Test category filter
- [ ] Test price filter
- [ ] Click vào tool xem details
- [ ] Click "Visit Website" link
- [ ] Test trên mobile
- [ ] Kiểm tra loading speed

### 5.2. Monitoring

**Vercel Analytics**:
- Vercel Dashboard → Analytics
- Xem traffic, performance

**Railway Logs**:
- Railway Dashboard → Service → Logs
- Monitor API errors

**MongoDB Monitoring**:
- MongoDB Atlas → Clusters → Metrics
- Xem database performance

---

## 🔧 Troubleshooting

### Frontend không load được data

**Nguyên nhân**: CORS hoặc wrong backend URL

**Giải pháp**:
1. Kiểm tra `REACT_APP_BACKEND_URL` trong Vercel environment variables
2. Kiểm tra backend có running không (Railway logs)
3. Test API trực tiếp: `https://your-app.up.railway.app/api/tools`
4. Kiểm tra CORS settings trong `backend/server.py`

### Railway deployment fail

**Nguyên nhân**: Thiếu dependencies hoặc wrong start command

**Giải pháp**:
1. Kiểm tra `requirements.txt` có đầy đủ
2. Kiểm tra Start Command:
   ```
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```

---

## 🔧 Troubleshooting: Fix Railway Build Errors

### Lỗi: "Railpack could not determine how to build the app"

**Nguyên nhân**: Railway không tự nhận diện được project structure

**Giải pháp 1: Kiểm tra Files Cấu Hình**

Đảm bảo các file này có trong thư mục `backend/`:
- ✅ `railway.toml` - Cấu hình Railway
- ✅ `Procfile` - Start command
- ✅ `runtime.txt` - Python version
- ✅ `nixpacks.toml` - Build configuration
- ✅ `requirements.txt` - Dependencies

**Giải pháp 2: Cấu hình thủ công trong Railway**

1. Vào Railway Dashboard → Select Service
2. Click **Settings** tab
3. **Root Directory**: Nhập `backend` và save
4. **Build Command**: Để trống (Railway tự detect)
5. **Start Command**: 
   ```
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
6. Click **Deploy** để thử lại

**Giải pháp 3: Xóa và Deploy lại**

1. Trong Railway, xóa service hiện tại
2. Tạo service mới
3. Chọn GitHub repository
4. Trong **Settings**:
   - **Root Directory**: `backend`
   - **Environment Variables**: Add MONGO_URL và DB_NAME
5. Railway sẽ tự động build

**Giải pháp 4: Kiểm tra Branch**

Đảm bảo code đã push lên đúng branch mà Railway đang theo dõi (thường là `main` hoặc `master`)

```bash
# Kiểm tra branch hiện tại
git branch

# Push lên main
git add .
git commit -m "Add Railway config files"
git push origin main
```

**Kiểm tra Deploy Logs**

1. Trong Railway, click vào **Deployments** tab
2. Click vào deployment đang fail
3. Xem **Build Logs** để tìm lỗi cụ thể
4. **Common errors**:
   - Missing `requirements.txt` → Add file
   - Wrong Python version → Check `runtime.txt`
   - Port binding error → Ensure using `$PORT` variable


3. Xem logs để tìm error cụ thể

### MongoDB connection error

**Nguyên nhân**: Wrong connection string hoặc IP not whitelisted

**Giải pháp**:
1. Kiểm tra MONGO_URL trong Railway environment variables
2. Kiểm tra MongoDB Atlas Network Access (0.0.0.0/0 whitelisted)
3. Kiểm tra username/password trong connection string

### Domain không kết nối

**Nguyên nhân**: DNS chưa propagate

**Giải pháp**:
1. Đợi 30 phút - 24 giờ để DNS propagate
2. Kiểm tra DNS config: https://dnschecker.org/
3. Xóa browser cache và thử lại

---

## 🔄 CI/CD - Auto Deploy

### Vercel
- Tự động deploy khi push lên `main` branch
- Vercel tự build và deploy

### Railway  
- Tự động deploy khi push code mới
- Railway tự build và restart service

### Update Code:
```bash
git add .
git commit -m "Update features"
git push origin main
```

Cả Vercel và Railway sẽ tự động deploy sau vài phút!

---

## 📊 Monitoring & Maintenance

### Daily Checks
- Kiểm tra website hoạt động bình thường
- Xem Railway logs có error không
- Monitor MongoDB storage usage

### Weekly
- Backup database (MongoDB Atlas có auto backup)
- Review analytics (Vercel)
- Check for updates

### Monthly
- Review và optimize database
- Update dependencies nếu cần
- Check SSL certificates

---

## 💰 Cost Estimates

### Free Tier (Đủ để bắt đầu)
- **MongoDB Atlas**: FREE (512MB)
- **Railway**: $5 credit/month (đủ cho small app)
- **Vercel**: FREE (unlimited deployments)
- **Domain**: ~$10-15/năm

### Khi traffic tăng
- MongoDB Atlas: Upgrade lên M10 (~$57/tháng)
- Railway: ~$10-20/tháng tùy usage
- Vercel: FREE hoặc Pro $20/tháng

---

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

## 🆘 Support

Nếu gặp vấn đề:
1. Kiểm tra logs (Vercel, Railway)
2. Google error message
3. Check Stack Overflow
4. MongoDB Community Forums
5. Vercel/Railway Discord

---

## ✨ Next Steps

Sau khi deploy thành công:

1. **Add more tools**: Sử dụng API POST `/api/tools`
2. **SEO optimization**: Add meta tags, sitemap
3. **Analytics**: Google Analytics, Vercel Analytics
4. **Performance**: Optimize images, lazy loading
5. **Features**: User accounts, ratings, comments
6. **Marketing**: Social media, SEO, ads

---

**Chúc bạn deploy thành công! 🎉**