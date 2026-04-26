# Railway Deployment Guide

This guide will walk you through deploying CampingBot to Railway.app for 24/7 monitoring.

## Step 1: Create Railway Account & Project

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (easiest option)
3. Create a new project → "Start from Scratch"

## Step 2: Push Code to GitHub

1. Create a new GitHub repository (e.g., `campingbot`)
2. In your local project folder:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/campingbot.git
   git branch -M main
   git push -u origin main
   ```

## Step 3: Set Up PostgreSQL Database on Railway

1. In Railway project dashboard:
   - Click "+ New" → "Database" → PostgreSQL
   - Wait for it to provision (2-3 minutes)
   - Railway will automatically create a `DATABASE_URL` environment variable

2. No manual setup needed! Railway handles everything.

## Step 4: Deploy Backend

1. In Railway project dashboard:
   - Click "+ New" → "GitHub Repo"
   - Select your `campingbot` repository
   - Railway automatically detects Python
   - Set these environment variables:
     ```
     DATABASE_URL=your-postgres-url (auto-set from PostgreSQL service)
     PORT=8000
     ```

2. Railway will build and deploy automatically from main branch

3. Get your production URL:
   - Railway gives you a URL like `https://campingbot-prod.up.railway.app`
   - This is your 24/7 service URL!

## Step 5: Verify Deployment

Test your API:
```bash
curl https://your-railway-url.up.railway.app/api/campgrounds/
```

Open in browser:
```
https://your-railway-url.up.railway.app
```

## Environment Variables

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Port to run on (usually 8000)

You can add more in Railway dashboard → Variables

## Monitoring & Logs

1. In Railway dashboard, click your backend service
2. Go to "Logs" tab to see real-time output
3. Check deployment status in "Deployments" tab

## Auto-Deploy

Once connected to GitHub:
- Every push to `main` automatically redeploys
- No manual steps needed
- Takes ~2-3 minutes per deployment

## Updating Your Service

To make changes:
1. Edit files locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
3. Railway automatically redeploys in ~2 minutes

## Next Steps (Phase 2)

Once deployed, we'll add:
1. **Ontario Parks Scraper** - Fetch real availability data
2. **Scheduled Jobs** - Check availability automatically every hour
3. **SMS Notifications** - Get alerted when sites open up

## Cost

Railway free tier includes:
- 500 hours/month (plenty for 24/7 service)
- 5GB PostgreSQL storage
- 1 production deployment

**Cost: $0 with free tier**

Pay-as-you-go: ~$5-10/month if you exceed free tier

## Troubleshooting

**App won't start:**
- Check Logs tab
- Verify DATABASE_URL is set
- Check Procfile syntax

**Database connection error:**
- Ensure PostgreSQL service is running in Railway
- Check DATABASE_URL environment variable

**Need help:**
- Railway has excellent docs: https://docs.railway.app
- Check GitHub Issues in your repo
