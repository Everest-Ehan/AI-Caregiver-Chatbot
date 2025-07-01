# Vercel + Render Deployment Guide

This guide will help you deploy your AI Caregiver Chatbot with the frontend on Vercel and backend on Render.

## 🚀 Frontend Deployment (Vercel)

### Prerequisites
- [Vercel account](https://vercel.com/signup)
- [GitHub account](https://github.com)

### Step 1: Prepare Frontend for Vercel

1. **Environment Variables**: Create a `.env` file in the `caregiver-chatbot` directory:
   ```bash
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

2. **Build Test**: Test the build locally:
   ```bash
   cd caregiver-chatbot
   npm install
   npm run build
   ```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI
1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy from the frontend directory:
   ```bash
   cd caregiver-chatbot
   vercel
   ```

3. Follow the prompts:
   - Link to existing project or create new
   - Set environment variables when prompted

#### Option B: Using Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `caregiver-chatbot`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Add Environment Variables:
   - Go to Project Settings → Environment Variables
   - Add `VITE_API_URL` with your Render backend URL

### Step 3: Configure Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

## 🔧 Backend Deployment (Render)

### Prerequisites
- [Render account](https://render.com/signup)
- OpenAI API key

### Step 1: Deploy Backend on Render

1. **Create New Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the Service**:
   - **Name**: `caregiver-chatbot-backend`
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend` (this is the key setting!)

3. **Environment Variables**:
   - Go to Environment → Environment Variables
   - Add `OPENAI_API_KEY` (set as Secret)
   - Add any other required environment variables

4. **Health Check**:
   - **Health Check Path**: `/health`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for the build to complete

### Step 2: Update Frontend API URL

Once your backend is deployed, update the frontend's environment variable:

1. **In Vercel Dashboard**:
   - Go to your frontend project settings
   - Environment Variables
   - Update `VITE_API_URL` to your Render backend URL

2. **Redeploy Frontend**:
   - Trigger a new deployment in Vercel

## 🔗 Connecting Frontend and Backend

### CORS Configuration
The backend is already configured to allow all origins in development. For production, you may want to restrict CORS to your Vercel domain:

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:5173"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables Summary

#### Frontend (Vercel)
- `VITE_API_URL`: Your Render backend URL (e.g., `https://caregiver-chatbot-backend.onrender.com`)

#### Backend (Render)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `HOST`: `0.0.0.0` (default)
- `PORT`: `8000` (default)
- `DEBUG`: `False` (for production)

## 🧪 Testing the Deployment

1. **Test Backend Health**:
   ```bash
   curl https://your-backend-url.onrender.com/health
   ```

2. **Test Frontend**:
   - Visit your Vercel URL
   - Try starting a chat session
   - Verify API calls work

3. **Check Logs**:
   - Vercel: Project → Functions → View Function Logs
   - Render: Service → Logs

## 🔄 Continuous Deployment

Both platforms support automatic deployments:

- **Vercel**: Automatically deploys on every push to your main branch
- **Render**: Automatically deploys on every push to your main branch

## 🚨 Troubleshooting

### Common Issues

1. **502 Bad Gateway (Backend)**:
   - Check if `OPENAI_API_KEY` is set in Render
   - Check Render logs for startup errors
   - Verify the Dockerfile builds correctly

2. **CORS Errors (Frontend)**:
   - Ensure backend CORS allows your Vercel domain
   - Check that `VITE_API_URL` is correct

3. **Build Failures**:
   - Check package.json for correct scripts
   - Verify all dependencies are installed
   - Check for TypeScript/ESLint errors

### Debug Commands

```bash
# Test backend locally
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Test frontend locally
cd caregiver-chatbot
npm run dev

# Test API connection
curl http://localhost:8000/health
```

## 📊 Monitoring

- **Vercel Analytics**: Built-in performance monitoring
- **Render Metrics**: CPU, memory, and request metrics
- **Custom Logging**: Add logging to your backend for debugging

## 🔐 Security Considerations

1. **Environment Variables**: Never commit API keys to Git
2. **CORS**: Restrict to specific domains in production
3. **Rate Limiting**: Consider adding rate limiting to your backend
4. **HTTPS**: Both platforms provide HTTPS by default

## 📝 Next Steps

1. Set up monitoring and alerting
2. Configure custom domains
3. Set up staging environments
4. Implement CI/CD pipelines
5. Add error tracking (Sentry, etc.)

Your chatbot should now be live and accessible via your Vercel URL! 🎉 