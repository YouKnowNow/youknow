# Quick Startup Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
# Frontend dependencies
cd frontend && npm install && cd ..

# Backend dependencies  
cd app && pip install -r requirements.txt && cd ..
```

### 2. Start Development Servers
```bash
chmod +x dev.sh
./dev.sh
```

### 3. Open Your Browser
- **Frontend**: http://localhost:3000 (React dev server)
- **Backend**: http://localhost:8000 (Flask API)
- **Production**: http://localhost:8000 (Flask serving built React app)

## 🔧 Development Commands

```bash
# Build frontend for production
./build.sh

# Start production with Docker
docker-compose up --build

# Run frontend only (port 3000)
cd frontend && npm run dev

# Run backend only (port 8000)
cd app && python main.py
```

## 📁 Project Structure
```
youknow/
├── app/                 # Flask backend
│   ├── main.py         # API endpoints
│   └── requirements.txt
├── frontend/           # React frontend
│   ├── src/           # Source code
│   └── package.json   # Dependencies
├── dev.sh             # Development startup script
├── build.sh           # Production build script
└── docker-compose.yml # Production deployment
```

## 🌐 API Endpoints
- `GET /api/dashboard` - Dashboard data
- `GET /api/health` - Health check

## 🐛 Troubleshooting

**Port already in use?**
- Kill existing processes: `pkill -f "python main.py"` or `pkill -f "vite"`
- Or change ports in `vite.config.ts` and `app/main.py`

**Frontend not loading?**
- Check if backend is running: `curl http://localhost:8000/api/health`
- Ensure frontend is built: `./build.sh`

**CORS issues?**
- Backend has CORS enabled for development
- In production, both run on same domain
