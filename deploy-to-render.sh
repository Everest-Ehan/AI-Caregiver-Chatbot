#!/bin/bash

echo "🚀 Preparing for Render Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

echo -e "${BLUE}📋 Render Deployment Checklist${NC}"
echo "=================================="

# Check if render.yaml exists
if [ -f "render.yaml" ]; then
    print_status 0 "render.yaml configuration file found"
else
    print_status 1 "render.yaml not found"
    exit 1
fi

# Check if .env file exists (for local testing)
if [ -f ".env" ]; then
    print_status 0 ".env file found (for local testing)"
else
    echo -e "${YELLOW}⚠️  .env file not found - create one for local testing${NC}"
fi

# Check if git is initialized
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_status 0 "Git repository initialized"
else
    print_status 1 "Git repository not initialized"
    echo "Run: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Check if remote origin is set
if git remote get-url origin > /dev/null 2>&1; then
    print_status 0 "Git remote origin configured"
    echo -e "${BLUE}   Remote URL: $(git remote get-url origin)${NC}"
else
    echo -e "${YELLOW}⚠️  Git remote origin not configured${NC}"
    echo "Run: git remote add origin <your-repo-url>"
fi

# Check for uncommitted changes
if git diff-index --quiet HEAD --; then
    print_status 0 "No uncommitted changes"
else
    echo -e "${YELLOW}⚠️  You have uncommitted changes${NC}"
    echo "Run: git add . && git commit -m 'Update for deployment'"
fi

echo ""
echo -e "${BLUE}🔧 Next Steps for Render Deployment:${NC}"
echo "=========================================="
echo ""
echo "1. ${YELLOW}Push your code to GitHub/GitLab:${NC}"
echo "   git add ."
echo "   git commit -m 'Add Render deployment configuration'"
echo "   git push origin main"
echo ""
echo "2. ${YELLOW}Deploy on Render:${NC}"
echo "   - Go to https://render.com"
echo "   - Sign up/Login"
echo "   - Click 'New +' → 'Blueprint'"
echo "   - Connect your Git repository"
echo "   - Render will detect render.yaml automatically"
echo ""
echo "3. ${YELLOW}Set Environment Variables:${NC}"
echo "   - In Render dashboard, go to backend service"
echo "   - Navigate to 'Environment' tab"
echo "   - Add OPENAI_API_KEY with your actual API key"
echo ""
echo "4. ${YELLOW}Deploy:${NC}"
echo "   - Render will automatically build and deploy both services"
echo "   - Backend: https://caregiver-chatbot-backend.onrender.com"
echo "   - Frontend: https://caregiver-chatbot-frontend.onrender.com"
echo ""
echo -e "${GREEN}🎉 Your application will be live on Render!${NC}"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see: RENDER_DEPLOYMENT.md${NC}" 