# 🚀 Quick Deploy to Railway (5 Minutes)

## Copy-Paste Setup

### 1️⃣ Get Railway Token
```
Visit: https://railway.app/account/tokens
Create new token → Copy it
```

### 2️⃣ Add to GitHub Secrets
```
Repo: https://github.com/Hadar01/shl-assessment-recommender
Settings → Secrets and variables → Actions
New repository secret:
  Name: RAILWAY_TOKEN
  Value: (paste token)
```

### 3️⃣ Create Railway Project
```
Visit: https://railway.app
New Project → Deploy from GitHub
Select: shl-assessment-recommender
Click: Deploy Now
```

### 4️⃣ Test Auto-Deployment
```bash
# Make a tiny change
echo "# Deployed!" >> README.md

# Push to GitHub
git add README.md
git commit -m "test: deployment"
git push origin main

# Watch it deploy:
# - GitHub: Actions tab
# - Railway: Dashboard
```

---

## 📊 Result

| Item | Status |
|------|--------|
| Code | 📍 GitHub (https://github.com/Hadar01/shl-assessment-recommender) |
| Running App | 🚀 Railway (auto-deployed) |
| Auto-Deploy | ✅ Enabled (on every push) |
| URL | Will get from Railway dashboard |

---

## ✅ You Now Have

✅ Code on GitHub
✅ App running on Railway  
✅ Auto-deployment on every push
✅ Professional CI/CD setup

**That's production-grade deployment!** 🎉

---

## 🔗 Links

- **GitHub Repo:** https://github.com/Hadar01/shl-assessment-recommender
- **Railway:** https://railway.app
- **Setup Guide:** .github/RAILWAY_SETUP.md (in your repo)
- **GitHub Actions:** View in repo "Actions" tab

---

**All done! Your code auto-deploys to Railway on every push.** 🚀
