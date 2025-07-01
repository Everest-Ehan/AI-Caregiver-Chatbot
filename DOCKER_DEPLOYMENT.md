# Docker Deployment Guide

This guide explains how to deploy the AI Caregiver Chatbot using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- OpenAI API key

## Quick Start

### 1. Set up Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Health Check**: http://localhost:8000/health

## Docker Architecture

### Services

1. **Backend** (`caregiver-chatbot-backend`)
   - Python FastAPI application
   - Runs on port 8000
   - Uses Python 3.11 slim image
   - Includes health checks

2. **Frontend** (`caregiver-chatbot-frontend`)
   - React application served by Nginx
   - Runs on port 3000 (mapped to container port 80)
   - Multi-stage build for optimization
   - Includes health checks

### Network

Both services communicate through a custom bridge network (`caregiver-network`).

## Development vs Production

### Development Mode

For development, you can mount volumes to enable hot reloading:

```yaml
# In docker-compose.yml, add volumes to backend service:
volumes:
  - ./backend:/app
```

### Production Mode

For production deployment:

1. Remove volume mounts
2. Set environment variables properly
3. Use proper secrets management
4. Configure reverse proxy if needed

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

## Health Checks

Both services include health checks:

- **Backend**: Checks `/health` endpoint
- **Frontend**: Checks if nginx is responding

## Useful Commands

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Check service status
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **API key missing**: Set the `OPENAI_API_KEY` environment variable
3. **Build failures**: Check Docker logs for specific error messages
4. **Network issues**: Ensure Docker network is properly configured

### Debug Commands

```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check network connectivity
docker-compose exec frontend ping backend

# Check backend health
curl http://localhost:8000/health
```

## Production Deployment

### Security Considerations

1. **API Keys**: Use Docker secrets or environment variables
2. **HTTPS**: Configure SSL/TLS certificates
3. **Firewall**: Restrict access to necessary ports only
4. **Updates**: Regularly update base images

### Scaling

To scale the application:

```bash
# Scale backend service
docker-compose up --scale backend=3

# Scale frontend service
docker-compose up --scale frontend=2
```

### Monitoring

Consider adding monitoring tools:

- Prometheus for metrics
- Grafana for visualization
- ELK stack for logging

## Customization

### Changing Ports

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # Change 8080 to your preferred port
  frontend:
    ports:
      - "3001:80"    # Change 3001 to your preferred port
```

### Adding Environment Variables

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
      - LOG_LEVEL=info
```

## Support

For issues or questions:

1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Check network connectivity
4. Review this documentation 