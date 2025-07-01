# Render Deployment Guide

This guide explains how to deploy the AI Caregiver Chatbot on Render.

## Prerequisites

- Render account (free tier available)
- OpenAI API key
- Git repository with your code

## Quick Deployment

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub/GitLab**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Sign up/Login
   - Click "New +" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   - In the Render dashboard, go to your backend service
   - Navigate to "Environment" tab
   - Add `OPENAI_API_KEY` with your actual API key

4. **Deploy**
   - Render will automatically build and deploy both services
   - Backend: `https://caregiver-chatbot-backend.onrender.com`
   - Frontend: `https://caregiver-chatbot-frontend.onrender.com`

### Option 2: Manual Deployment

#### Deploy Backend First

1. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Set build command: `docker build -t backend ./backend`
   - Set start command: `docker run -p $PORT:8000 backend`
   - Set Dockerfile path: `./backend/Dockerfile`
   - Set Docker context: `./backend`

2. **Configure Environment**
   - Add environment variable: `OPENAI_API_KEY`
   - Set health check path: `/health`

3. **Deploy Backend**
   - Click "Create Web Service"
   - Note the backend URL (e.g., `https://your-backend-name.onrender.com`)

#### Deploy Frontend

1. **Create Another Web Service**
   - Click "New +" → "Web Service"
   - Connect the same Git repository
   - Set build command: `docker build -t frontend ./caregiver-chatbot`
   - Set start command: `docker run -p $PORT:80 frontend`
   - Set Dockerfile path: `./caregiver-chatbot/Dockerfile`
   - Set Docker context: `./caregiver-chatbot`

2. **Configure Environment**
   - Add environment variable: `REACT_APP_API_URL`
   - Set value to your backend URL: `https://your-backend-name.onrender.com`
   - Set health check path: `/`

3. **Deploy Frontend**
   - Click "Create Web Service"

## Environment Variables

### Backend Service
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Frontend Service
| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_API_URL` | Backend service URL | Yes |

## Render Configuration Details

### Backend Service
- **Type**: Web Service
- **Environment**: Docker
- **Region**: Oregon (or your preferred region)
- **Plan**: Starter (free tier)
- **Health Check**: `/health`
- **Port**: 8000 (internal)

### Frontend Service
- **Type**: Web Service
- **Environment**: Docker
- **Region**: Oregon (or your preferred region)
- **Plan**: Starter (free tier)
- **Health Check**: `/`
- **Port**: 80 (internal)

## Testing Deployment

### 1. Health Checks
```bash
# Test backend health
curl https://your-backend-name.onrender.com/health

# Test frontend
curl https://your-frontend-name.onrender.com
```

### 2. API Endpoints
```bash
# Test scenarios endpoint
curl https://your-backend-name.onrender.com/scenarios

# Test session creation
curl -X POST https://your-backend-name.onrender.com/start-session \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "general_chat"}'
```

### 3. Frontend Integration
- Visit your frontend URL
- Select a scenario
- Test the chatbot functionality
- Verify context management

## Local Testing with Render Configuration

Test the production configuration locally:

```bash
# Use the Render-specific compose file
docker-compose -f render-docker-compose.yml up --build

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:3000
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check build logs in Render dashboard
   - Verify Dockerfile paths are correct
   - Ensure all dependencies are in requirements.txt/package.json

2. **Environment Variables**
   - Verify `OPENAI_API_KEY` is set correctly
   - Check `REACT_APP_API_URL` points to correct backend URL
   - Ensure variable names match exactly

3. **Health Check Failures**
   - Verify health check paths are correct
   - Check if services are starting properly
   - Review service logs

4. **CORS Issues**
   - Backend includes CORS middleware for all origins
   - If issues persist, check frontend API URL configuration

### Debug Commands

```bash
# Check service status
curl https://your-backend-name.onrender.com/health

# Test API endpoints
curl https://your-backend-name.onrender.com/scenarios

# Check frontend
curl -I https://your-frontend-name.onrender.com
```

## Performance Optimization

### Backend
- Consider upgrading to paid plan for better performance
- Monitor memory usage in Render dashboard
- Optimize Python dependencies if needed

### Frontend
- Static files are served by Nginx with compression
- Consider CDN for better global performance
- Monitor bundle size and optimize if needed

## Security Considerations

1. **API Keys**: Never commit API keys to Git
2. **Environment Variables**: Use Render's secure environment variable system
3. **HTTPS**: Render provides automatic HTTPS
4. **CORS**: Backend is configured for production CORS

## Monitoring

### Render Dashboard
- Monitor service health
- Check build logs
- View deployment history
- Monitor resource usage

### Application Logs
- Access logs through Render dashboard
- Monitor for errors and performance issues
- Set up alerts for critical failures

## Scaling

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- Limited CPU and memory resources
- Cold starts may cause delays

### Paid Plans
- Always-on services
- Better performance
- More resources
- Custom domains

## Custom Domains

1. **Add Custom Domain**
   - Go to service settings
   - Click "Custom Domains"
   - Add your domain

2. **Configure DNS**
   - Point your domain to Render's servers
   - Wait for DNS propagation

## Backup and Recovery

### Code Backup
- Keep your Git repository updated
- Use version control for all changes

### Environment Variables
- Document all environment variables
- Keep backups of configuration

## Support

For Render-specific issues:
- Check Render documentation
- Contact Render support
- Review service logs

For application issues:
- Check application logs
- Verify environment variables
- Test locally first 