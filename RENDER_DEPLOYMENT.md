# 🚀 Deploy EmotiSense to Render.com

## Quick Start Guide

Your project is ready to deploy to Render! Follow these simple steps.

---

## ✅ Prerequisites

- ✅ GitHub repository created: https://github.com/Mallayasawini12/classproject
- ✅ Code pushed to GitHub
- ✅ Render configuration files ready
- ✅ Dockerfile configured

---

## 🎯 Deployment Steps

### Step 1: Sign Up / Log In to Render

1. Go to: **https://render.com**
2. Click **"Get Started for Free"** or **"Sign In"**
3. Sign up with GitHub (recommended) or email
4. Authorize Render to access your GitHub repositories

### Step 2: Create a New Web Service

1. From your Render Dashboard, click **"New +"** button
2. Select **"Web Service"**

### Step 3: Connect Your Repository

1. Click **"Connect a repository"**
2. If not connected, click **"Configure account"** to authorize GitHub
3. Find and select: **`Mallayasawini12/classproject`**
4. Click **"Connect"**

### Step 4: Configure Your Service

Fill in the following settings:

#### Basic Settings:
- **Name**: `emotisense` (or any name you prefer)
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `main`
- **Runtime**: `Docker`

#### Build & Deploy:
- **Docker Command**: Leave empty (uses Dockerfile CMD)
- **Root Directory**: Leave empty (uses repository root)

#### Environment Variables:
These are automatically set from `render.yaml`, but you can verify:
- `FLASK_ENV` = `production`
- `FLASK_HOST` = `0.0.0.0`
- `PYTHONUNBUFFERED` = `1`

#### Instance Type:
- **Plan**: Select **"Free"** (or upgrade if needed)

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Render will start building your Docker image
3. Wait 5-10 minutes for the build to complete
4. Once deployed, you'll get a URL like: `https://emotisense.onrender.com`

---

## 📊 Monitoring Your Deployment

### Check Build Logs
- Click on your service → **"Logs"** tab
- Watch the build process in real-time
- Look for "Build succeeded" message

### Check Deploy Status
- Dashboard shows: **"Live"** (green) when running
- Or **"Building"** (yellow) during deployment
- Or **"Failed"** (red) if errors occur

### View Application Logs
- **"Logs"** tab shows runtime logs
- Monitor for any errors or warnings
- Check Flask startup messages

---

## ⚠️ Important Notes

### Free Tier Limitations:
- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ **First request after sleep takes 30-60 seconds**
- ⚠️ **750 hours/month free** (enough for continuous running)
- ⚠️ **No webcam access on server** (see note below)

### Webcam Limitation:
**This app requires webcam access, which Render servers don't have.** 

To make this work:
1. **Option A**: Modify app to use client-side webcam (browser) with TensorFlow.js
2. **Option B**: Deploy on edge device with camera using Docker
3. **Option C**: Use for API-only deployment (remove webcam features)

---

## 🔧 Configuration Files

Your repository includes:

✅ **render.yaml** - Render service configuration  
✅ **Dockerfile** - Container build instructions  
✅ **gunicorn_config.py** - Production server settings  
✅ **wsgi.py** - WSGI entry point  
✅ **requirements.txt** - Python dependencies

---

## 🌐 Accessing Your App

Once deployed:

**Your URL**: `https://emotisense.onrender.com` (or your custom name)

**Test endpoints**:
- Home: `https://emotisense.onrender.com/`
- API: `https://emotisense.onrender.com/api/emotions`
- Dashboard: `https://emotisense.onrender.com/dashboard`

---

## 🔄 Updating Your App

To deploy changes:

```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy! 🎉

---

## 🎨 Custom Domain (Optional)

### Add Your Own Domain:

1. Go to your service settings
2. Click **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `emotisense.yourdomain.com`)
5. Add the CNAME record to your DNS provider:
   - Point to: `your-app.onrender.com`
6. Wait for DNS propagation (5-60 minutes)
7. Render automatically provisions SSL certificate

---

## 🔍 Troubleshooting

### Build Failed

**Check logs for errors:**
```
Error: Could not find requirements.txt
```
**Solution**: Ensure requirements.txt is in repository root

**Check logs for:**
```
Error: Package installation failed
```
**Solution**: Check requirements.txt for typos or incompatible versions

### Deploy Timeout

**If build takes too long:**
1. Check if dependencies are too large
2. Consider optimizing Dockerfile
3. Free tier has build time limits

### App Not Starting

**Check logs for:**
```
Error: gunicorn: command not found
```
**Solution**: Ensure gunicorn is in requirements.txt

**Check for port binding errors:**
```
Error: Address already in use
```
**Solution**: Verify gunicorn_config.py uses PORT env variable

### App Crashes

**Check runtime logs:**
- Look for Python errors
- Check camera access errors (expected without physical camera)
- Verify all dependencies installed

---

## 💰 Pricing

### Free Tier:
- ✅ 750 hours/month
- ✅ Automatic SSL
- ✅ CDN
- ✅ Auto-deploy from Git
- ⚠️ Spins down after inactivity

### Starter ($7/month):
- ✅ Always running (no spin down)
- ✅ More compute resources
- ✅ 400 build hours
- ✅ Faster performance

### Standard ($25/month):
- ✅ More resources
- ✅ Priority support
- ✅ Multiple instances

---

## 🔐 Security Settings

### Environment Variables (Secrets):
1. Go to service → **"Environment"**
2. Add sensitive variables:
   - API keys
   - Database credentials
   - Secret keys
3. These won't be visible in logs

### Auto-Deploy Settings:
- **"Settings"** → **"Build & Deploy"**
- Enable/disable auto-deploy on push
- Set branch for deployment

---

## 📈 Monitoring & Analytics

### Built-in Metrics:
- CPU usage
- Memory usage
- Request count
- Response times

### External Monitoring:
Add health check endpoint monitoring with:
- UptimeRobot (free)
- Pingdom
- StatusCake

---

## 🎯 Deployment Checklist

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Docker runtime selected
- [ ] Free plan selected
- [ ] Build completed successfully
- [ ] Service is "Live"
- [ ] Application URL accessible
- [ ] Logs checked for errors
- [ ] Auto-deploy enabled

---

## 🆘 Getting Help

### Render Support:
- **Docs**: https://render.com/docs
- **Community**: https://community.render.com
- **Status**: https://status.render.com

### Your Project Docs:
- [DEPLOYMENT.md](DEPLOYMENT.md) - General deployment guide
- [README.md](README.md) - Project documentation
- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Platform alternatives

---

## 🎉 Next Steps After Deployment

1. **Test all features** (note: camera won't work on server)
2. **Set up monitoring** for uptime tracking
3. **Configure custom domain** (optional)
4. **Set up CI/CD** (already automatic with GitHub)
5. **Monitor logs** for any issues
6. **Consider upgrading** if you need always-on service

---

## 🚀 Quick Command Reference

```bash
# Push updates
git push origin main

# View remote
git remote -v

# Check status
git status

# Create new branch
git checkout -b feature-name

# View commit history
git log --oneline
```

---

## 📝 Summary

**Your Deployment URL**: https://emotisense.onrender.com

**Deployment Method**: Automatic from GitHub (push to deploy)

**Cost**: Free (with spin-down) or $7/month (always-on)

**Build Time**: ~5-10 minutes

**Auto-Deploy**: Enabled on push to `main` branch

---

**Ready to deploy? Just follow the steps above! 🚀**

**Note**: Remember that server-side camera access won't work on Render. Consider the alternatives mentioned in [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) if you need real camera functionality.
