# YouKnow - Productivity Dashboard

A productivity dashboard application with a React frontend and Flask backend.

## Project Structure

- `app/` - Flask backend application
- `frontend/` - React frontend application
- `docker-compose.yml` - Docker configuration for production deployment

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Docker (optional, for production)

### Quick Start

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

2. **Install backend dependencies:**
   ```bash
   cd app
   pip install -r requirements.txt
   cd ..
   ```

3. **Start development servers:**
   ```bash
   chmod +x dev.sh
   ./dev.sh
   ```

   This will start:
   - Flask backend on http://localhost:8000
   - React frontend on http://localhost:3000
   - API endpoint on http://localhost:8000/api/dashboard

### Development Workflow

- **Frontend development**: The React app runs on port 3000 with hot reload
- **Backend development**: Flask runs on port 8000 with auto-reload
- **API calls**: Frontend proxies `/api/*` requests to Flask backend
- **Build**: Use `./build.sh` to build the frontend for production

## Production Deployment

1. **Build the frontend:**
   ```bash
   ./build.sh
   ```

2. **Start with Docker:**
   ```bash
   docker-compose up --build
   ```

   The Flask app will serve the built React frontend on port 8000.

## API Endpoints

- `GET /api/dashboard` - Dashboard data
- `GET /api/health` - Health check

## Features

- **Productivity Dashboard**: Track focus time, social media usage, and browsing patterns
- **Golden Hours Analysis**: Identify your most productive time periods
- **Session Tracking**: Monitor browsing sessions and patterns
- **Trend Analysis**: Compare current week vs. previous week metrics
- **Interest Detection**: Automatically identify your current interests based on browsing

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: Flask, Python
- **Build Tools**: Vite, TypeScript compiler
- **Deployment**: Docker, Docker Compose
