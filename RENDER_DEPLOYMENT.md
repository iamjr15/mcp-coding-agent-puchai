# 🚀 Render Deployment Guide

Deploy your MCP Code Generator to Render in minutes!

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push this code to GitHub
3. **API Keys**: Gather required environment variables

## 🔑 Required Environment Variables

Set these in Render Dashboard > Environment:

### **🔴 Required Variables:**
```bash
# MCP Authentication (Required)
AUTH_TOKEN=your_secure_token_here
MY_NUMBER=919876543210

# OpenAI (Required for code generation)
OPENAI_API_KEY=sk-your-openai-api-key

# Download URL (Set to your Render app URL)
DOWNLOAD_BASE_URL=https://your-app.onrender.com
```

### **🟡 Optional Variables (Legacy Blaxel features):**
```bash
# Only needed if using legacy Blaxel features
BL_WORKSPACE=your_workspace_name
BL_API_KEY=your_blaxel_api_key
MORPH_API_KEY=your_morph_api_key
MORPH_MODEL=morph-v2
```

**Note**: The generator now runs entirely on OpenAI, so Blaxel variables are optional.

## 🚀 Quick Deploy

### Method 1: Render Dashboard (Recommended)
1. **Create Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**:
   - **Name**: `mcp-code-generator`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_start.py`
   - **Plan**: `Starter` (recommended for production)

3. **Set Environment Variables**:
   - Add all variables from above
   - Set `DOWNLOAD_BASE_URL` to your Render URL (e.g., `https://mcp-code-generator.onrender.com`)

4. **Deploy**: Click "Create Web Service"

### Method 2: render.yaml (Auto-deploy)
1. **Push to GitHub** with the included `render.yaml`
2. **Import to Render** - it will auto-configure
3. **Set Environment Variables** in dashboard
4. **Deploy** automatically

## 🔧 Configuration Details

### Health Check
- **Path**: `/health`
- **Expected Response**: `{"status": "healthy"}`

### Persistent Storage
- **Mount Path**: `/app/static/downloads`
- **Size**: 1GB
- **Purpose**: Store generated MCP zip files

### Scaling
- **Min Instances**: 1 (keeps service warm)
- **Max Instances**: 1 (sufficient for our use case)

## 🎯 Testing Your Deployment

1. **Health Check**:
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **MCP Connection**:
   ```
   wss://your-app.onrender.com/mcp/
   ```

3. **Puch AI Connection**:
   ```
   /mcp connect https://your-app.onrender.com/mcp/ your_auth_token
   ```

## 📊 Performance

- **Generation Time**: ~24 seconds (well under timeout)
- **Cold Start**: ~10-15 seconds (first request)
- **Warm Requests**: Instant response
- **File Storage**: Persistent across deployments

## 💰 Cost

**Render Starter Plan** (Recommended):
- $7/month for web services
- Always-on (no sleeping)
- 512MB RAM, persistent disk included
- Better for production use

**Alternative - Free Tier**:
- 750 hours/month (sleeps after 15min idle)
- Good for testing, but may timeout on generation
- Upgrade to Starter recommended for production

## 🐛 Troubleshooting

### Common Issues:

1. **Build Failed**:
   - Check `requirements.txt` is present
   - Verify Python 3.11+ compatibility

2. **Environment Variables**:
   - Ensure `OPENAI_API_KEY` is set
   - Verify `DOWNLOAD_BASE_URL` matches your domain

3. **Health Check Failed**:
   - Check logs for startup errors
   - Verify port 8086 is accessible

### Logs Access:
- **Render Dashboard** → Your Service → "Logs" tab
- Real-time log streaming available

## 🔄 Updates

**Auto-Deploy**: Push to `main` branch → Render auto-deploys

**Manual Deploy**: Render Dashboard → "Manual Deploy"

## 🎉 Success!

Once deployed, your MCP Code Generator will be available at:
- **MCP Endpoint**: `wss://your-app.onrender.com/mcp/`
- **Health Check**: `https://your-app.onrender.com/health`
- **Downloads**: `https://your-app.onrender.com/download/`

Connect it to Puch AI and start generating MCPs! 🚀
