#!/bin/bash

# Vercel + Render Deployment Helper Script
# This script helps you deploy your AI Caregiver Chatbot

set -e

echo "🚀 AI Caregiver Chatbot - Vercel + Render Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    # Check if Python is installed
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed. Please install Python first."
        exit 1
    fi
    
    print_success "All prerequisites are installed!"
}

# Test frontend build
test_frontend_build() {
    print_status "Testing frontend build..."
    
    cd caregiver-chatbot
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    npm install
    
    # Test build
    print_status "Testing frontend build..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Frontend build successful!"
    else
        print_error "Frontend build failed!"
        exit 1
    fi
    
    cd ..
}

# Test backend startup
test_backend_startup() {
    print_status "Testing backend startup..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Test imports
    print_status "Testing backend imports..."
    python -c "
import sys
try:
    from fastapi import FastAPI
    from agents.caregiver_agent import chat_graph
    from config import Config
    print('✓ All imports successful')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "Backend startup test successful!"
    else
        print_error "Backend startup test failed!"
        exit 1
    fi
    
    cd ..
}

# Deploy backend to Render
deploy_backend() {
    print_status "Deploying backend to Render..."
    
    print_warning "Please ensure you have:"
    echo "1. A Render account (https://render.com/signup)"
    echo "2. Your repository connected to Render"
    echo "3. OPENAI_API_KEY ready to set in Render"
    echo ""
    
    read -p "Press Enter when you're ready to continue..."
    
    print_status "Steps to deploy backend:"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Click 'New +' → 'Web Service'"
    echo "3. Connect your GitHub repository"
    echo "4. Configure:"
    echo "   - Name: caregiver-chatbot-backend"
    echo "   - Environment: Docker"
    echo "   - Dockerfile Path: ./backend/Dockerfile"
    echo "   - Docker Context: ./backend"
    echo "   - Health Check Path: /health"
    echo "5. Add environment variable:"
    echo "   - Key: OPENAI_API_KEY"
    echo "   - Value: Your OpenAI API key"
    echo "   - Mark as Secret"
    echo "6. Click 'Create Web Service'"
    echo ""
    
    read -p "Enter your Render backend URL (e.g., https://caregiver-chatbot-backend.onrender.com): " BACKEND_URL
    
    if [ -z "$BACKEND_URL" ]; then
        print_error "Backend URL is required!"
        exit 1
    fi
    
    # Save backend URL for frontend deployment
    echo "$BACKEND_URL" > .backend_url
    
    print_success "Backend deployment instructions provided!"
}

# Deploy frontend to Vercel
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    # Check if backend URL is available
    if [ ! -f ".backend_url" ]; then
        print_error "Backend URL not found. Please deploy backend first."
        exit 1
    fi
    
    BACKEND_URL=$(cat .backend_url)
    
    print_warning "Please ensure you have:"
    echo "1. A Vercel account (https://vercel.com/signup)"
    echo "2. Vercel CLI installed (npm i -g vercel)"
    echo "3. Your repository connected to Vercel"
    echo ""
    
    read -p "Press Enter when you're ready to continue..."
    
    cd caregiver-chatbot
    
    # Create .env file for Vercel
    echo "VITE_API_URL=$BACKEND_URL" > .env
    
    print_status "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    # Deploy to Vercel
    print_status "Running Vercel deployment..."
    vercel --prod
    
    cd ..
    
    print_success "Frontend deployment initiated!"
}

# Main deployment flow
main() {
    echo "Choose an option:"
    echo "1. Test everything locally"
    echo "2. Deploy backend to Render"
    echo "3. Deploy frontend to Vercel"
    echo "4. Full deployment (backend + frontend)"
    echo "5. Exit"
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_prerequisites
            test_frontend_build
            test_backend_startup
            print_success "All tests passed! Ready for deployment."
            ;;
        2)
            check_prerequisites
            test_backend_startup
            deploy_backend
            ;;
        3)
            check_prerequisites
            test_frontend_build
            deploy_frontend
            ;;
        4)
            check_prerequisites
            test_frontend_build
            test_backend_startup
            deploy_backend
            deploy_frontend
            print_success "Full deployment completed!"
            ;;
        5)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please enter 1-5."
            exit 1
            ;;
    esac
}

# Run main function
main 