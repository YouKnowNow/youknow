# YouKnow - Your Personal Life Analytics & AI Productivity Engine

> **Transform your digital life into actionable insights and AI-powered recommendations**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-3178c6.svg)](https://www.typescriptlang.org/)

## 🌟 Vision

**YouKnow** is not just another productivity app—it's your personal life analytics platform that understands you better than you understand yourself. By analyzing your digital footprint across multiple time services, it provides deep insights into your behavior patterns, productivity cycles, and life optimization opportunities.

### 🚀 Current Capabilities

**YouKnow** currently provides comprehensive browser analytics and productivity insights:

- **🔍 Real-time Chrome History Analysis**: Automatically reads and analyzes your browsing patterns every 5 minutes
- **📊 Smart Website Categorization**: Automatically categorizes websites (social, development, documentation, etc.)
- **⏰ Golden Hours Detection**: Identifies your most productive time periods
- **📈 Trend Analysis**: Compares current week vs. previous week metrics
- **🎯 Focus Time Tracking**: Monitors time spent on productive vs. distracting activities
- **🔗 Session Chain Analysis**: Understands your workflow patterns and context switching
- **💡 Interest Detection**: Automatically identifies your current interests based on browsing behavior

### 🚀 Future Roadmap

**YouKnow** is designed to become your comprehensive life analytics platform:

#### **Phase 1: Multi-Service Integration** (Current - Browser)
- ✅ Chrome/Edge browser history analysis
- 🔄 Firefox, Safari support
- 🔄 Mobile browser integration

#### **Phase 2: Terminal & System Analytics**
- 📱 Terminal command history analysis
- 💻 System resource usage patterns
- 🔧 Development tool usage tracking
- 📁 File system activity monitoring

#### **Phase 3: Health & Wearable Integration**
- ⌚ Smartwatch health data (Apple Watch, Fitbit, Garmin)
- 📱 Phone activity logs and app usage
- 🏃‍♂️ Fitness tracker integration
- 😴 Sleep pattern analysis

#### **Phase 4: AI-Powered Life Coach**
- 🤖 LLM integration for personalized advice
- 🎯 Predictive productivity recommendations
- 🧠 Behavioral pattern recognition
- 💬 Natural language interaction with your data
- 🎯 Life optimization suggestions based on comprehensive analytics

## 🏗️ Architecture

**YouKnow** is built with a modern, scalable architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • React 18      │◄──►│ • Flask API     │◄──►│ • InfluxDB      │
│ • TypeScript    │    │ • Python        │    │ • Time Series   │
│ • Tailwind CSS  │    │ • Data Manager  │    │ • Real-time     │
│ • shadcn/ui     │    │ • Chrome Reader │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**

- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: Flask, Python 3.8+, InfluxDB for time-series data
- **Data Processing**: Real-time analytics, automatic categorization, pattern recognition
- **Deployment**: Docker, Docker Compose, production-ready

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- Docker & Docker Compose
- Google Chrome with browsing history

### **1. Clone & Setup**
```bash
git clone https://github.com/yourusername/youknow.git
cd youknow
```

### **2. Install Dependencies**
```bash
# Frontend
cd frontend && npm install && cd ..

# Backend
cd app && pip install -r requirements.txt && cd ..
```

### **3. Start Development**
```bash
chmod +x dev.sh
./dev.sh
```

**Access your dashboard:**
- **Frontend**: http://localhost:3000 (React dev server)
- **Backend**: http://localhost:8000 (Flask API)
- **Production**: http://localhost:8000 (Flask serving built React app)

### **4. Production Deployment**
```bash
# Build frontend
./build.sh

# Start with Docker
docker-compose up --build
```

## 📊 Current Features

### **Dashboard Analytics**
- **Top Domains**: Most visited websites with time spent
- **Top Searches**: Your most common search queries
- **Focus Metrics**: Productive vs. social time breakdown
- **Golden Hours**: Hourly productivity patterns
- **Session Analysis**: Workflow patterns and context switching
- **Trend Comparison**: Week-over-week progress tracking

### **Smart Categorization**
Automatically categorizes websites into:
- 🎯 **Productivity**: Development tools, documentation, work platforms
- 📱 **Social**: Social media, communication platforms
- 📚 **Learning**: Educational content, tutorials, courses
- 🛒 **Shopping**: E-commerce, online stores
- 🎮 **Entertainment**: Video streaming, gaming, media
- 📰 **News**: Current events, information sources

### **Real-time Data Collection**
- **Automatic**: Collects data every 5 minutes in the background
- **Privacy-First**: Only reads local data, never sends to external services
- **Smart Storage**: InfluxDB for historical analysis and trends
- **Fallback Mode**: Works even without database using local processing

## 🔮 Future Vision

### **Comprehensive Life Analytics**
Imagine having a complete picture of your digital life:

```
┌─────────────────────────────────────────────────────────────┐
│                    YouKnow Life Analytics                   │
├─────────────────────────────────────────────────────────────┤
│ 🌐 Browser Activity    │ 💻 Terminal Usage                │
│ 📱 Phone Activity      │ ⌚ Health & Fitness               │
│ 🏠 Smart Home Data     │ 🚗 Location & Travel             │
│ 💼 Work Applications   │ 🎓 Learning Platforms            │
└─────────────────────────────────────────────────────────────┘
```

### **AI-Powered Life Coach**
**YouKnow** will become your personal AI assistant that:

- **Knows You**: Understands your patterns, preferences, and goals
- **Predicts**: Anticipates your needs before you realize them
- **Optimizes**: Suggests improvements to your daily routines
- **Coaches**: Provides personalized advice for productivity and well-being
- **Learns**: Continuously improves its understanding of your life

### **Cross-Service Insights**
Discover hidden connections between different aspects of your life:

- **Productivity Correlation**: How does your sleep quality affect coding productivity?
- **Health Impact**: What's the relationship between screen time and stress levels?
- **Learning Patterns**: When are you most receptive to new information?
- **Work-Life Balance**: How do your work patterns affect personal time?

## 🔧 API Reference

### **Core Endpoints**
- `GET /api/dashboard?days=N` - Get dashboard data for last N days
- `POST /api/refresh` - Force data refresh
- `GET /api/status` - Data collection status
- `GET /api/health` - System health check

### **Data Format**
```json
{
  "top_domains": [
    {"domain": "github.com", "minutes": 120, "category": "development"}
  ],
  "focus": {
    "docs_min": 180,
    "social_min": 45,
    "score": 80
  },
  "golden_hours": {
    "9": 25,
    "10": 45,
    "14": 30
  }
}
```

## 🛡️ Privacy & Security

**YouKnow** is built with privacy as a core principle:

- **🔒 Local-First**: All data processing happens on your machine
- **🚫 No External Sharing**: Your data never leaves your control
- **📊 Aggregated Insights**: Only provides insights, never raw personal data
- **🔐 Secure Storage**: Local InfluxDB with encrypted data
- **🧹 Auto-Cleanup**: Automatically removes old data (configurable retention)

## 🤝 Contributing

We welcome contributions to make **YouKnow** even more powerful:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Development Areas**
- **Data Sources**: Add support for new time services
- **Analytics**: Improve pattern recognition algorithms
- **UI/UX**: Enhance dashboard visualizations
- **AI Integration**: Implement LLM-powered insights
- **Mobile**: Create mobile companion apps

## 📈 Roadmap

### **Q1 2024** - Browser Analytics (✅ Complete)
- Chrome history integration
- Smart categorization
- Basic dashboard

### **Q2 2024** - Terminal & System Integration
- Command history analysis
- System resource tracking
- Development workflow insights

### **Q3 2024** - Health & Wearable Data
- Smartwatch integration
- Phone activity analysis
- Health correlation insights

### **Q4 2024** - AI Life Coach
- LLM integration
- Predictive analytics
- Personalized recommendations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Chrome History**: For browser data access
- **InfluxDB**: For time-series data storage
- **React & Flask**: For the modern web stack
- **shadcn/ui**: For beautiful UI components

---

## 🌟 **Join the Revolution**

**YouKnow** is more than an app—it's your journey to self-knowledge and optimization. Start understanding your digital life today, and prepare for the AI-powered future where your personal assistant knows you better than anyone else.

**Ready to know yourself better?** [Get Started](#quick-start)

---

*"The unexamined life is not worth living." - Socrates*

*"The quantified self is the examined life." - YouKnow*
