# 🚀 Railway Deployment Setup (5 minutes)

## Step 1: Create Railway Account & Project

1. Visit: https://railway.app
2. **Sign up with GitHub** (easier)
3. Click **"New Project"**
4. Select **"Deploy from GitHub"**
5. GitHub will ask for permission → **Allow**
6. Search for repo: `shl-assessment-recommender`
7. Click **"Deploy Now"**

✅ Railway project created!

---

## Step 2: Get Railway Token

1. Visit: https://railway.app/account/tokens
2. Click **"Create New Token"**
3. Name it: `GITHUB_DEPLOY`
4. Copy the token (looks like: `railway_xxx...`)

✅ Token copied!

---

## Step 3: Add Token to GitHub Secrets

1. Go to your GitHub repo:
   https://github.com/Hadar01/shl-assessment-recommender

2. Click **Settings** (top menu)

3. Click **Secrets and variables** → **Actions** (left sidebar)

4. Click **"New repository secret"**

5. Name: `RAILWAY_TOKEN`
   Value: (paste the token from Step 2)

6. Click **"Add secret"**

✅ Secret added to GitHub!

---

## Step 4: Done! 🎉

Now every time you push to GitHub:
```bash
git push origin main
```

GitHub Actions automatically:
1. ✅ Checks out your code
2. ✅ Installs Railway CLI
3. ✅ Deploys to Railway
4. ✅ Your app updates live!

---

## 📊 What Happens

```
You push to GitHub
        ↓
GitHub Actions triggers
        ↓
Runs deploy-railway.yml
        ↓
Railway CLI deploys
        ↓
Your app updates live! 🚀
```

---

## 🔍 Monitor Deployment

1. Push to GitHub:
   ```bash
   git push origin main
   ```

2. Watch deployment:
   - GitHub: Go to **Actions** tab → See workflow running
   - Railway: https://railway.app → See deployment progress

3. View live app:
   - Go to Railway dashboard
   - Click your project
   - Copy the deployed URL

---

## ✅ Verify It Works

Once deployed to Railway:

```bash
# Test the API (replace with your Railway URL)
curl https://your-railway-app.up.railway.app/docs

# Try a recommendation
curl -X POST "https://your-railway-app.up.railway.app/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "skills": "Python, Machine Learning"
  }'
```

---

## 🆘 Troubleshooting

### GitHub Actions showing error?
- Check you copied the token correctly
- Token has no extra spaces

### Railway not deploying?
- Check Railway logs: https://railway.app
- Make sure Dockerfile exists (✅ it does)
- Make sure you connected the repo to Railway

### Need to view logs?
- Railway dashboard → Project → Deployments
- GitHub Actions → Actions tab

---

## 🎉 You're Done!

Your app now:
- ✅ Deploys automatically on every push
- ✅ Runs on Railway (not GitHub)
- ✅ Has its own URL
- ✅ Scales automatically
- ✅ Updates with each commit

---

**Next: Push a change to GitHub to test it!**

```bash
# Make a small change
git add .
git commit -m "test: trigger auto-deployment"
git push origin main

# Watch it deploy in Actions tab!
```

**Questions?** Check Railway docs: https://docs.railway.app
