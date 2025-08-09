# Chrome History Integration

This application now reads real Chrome browser history data and provides insights into your browsing patterns.

## Features

- **Real-time Data**: Automatically reads Chrome history every 5 minutes
- **Smart Categorization**: Automatically categorizes websites (social, development, documentation, etc.)
- **InfluxDB Storage**: Stores data in InfluxDB for historical analysis
- **Fallback Mode**: Works even without InfluxDB using local data processing
- **Privacy-First**: Only reads your local Chrome history, no data sent to external services

## How It Works

### 1. Chrome History Reading
- Reads Chrome's SQLite history database from `~/.config/google-chrome/Default/History`
- Creates a temporary copy to avoid locking issues
- Extracts URLs, titles, visit times, and visit counts
- Categorizes websites automatically

### 2. Data Processing
- Groups visits by domain
- Extracts search queries from Google/Bing URLs
- Calculates time spent on different categories
- Generates hourly activity patterns

### 3. Data Storage
- **Primary**: InfluxDB for long-term storage and analytics
- **Fallback**: Local processing if InfluxDB is unavailable

## Setup

### Prerequisites
- Google Chrome installed with browsing history
- Docker and Docker Compose

### 1. Test Chrome History Access
Before starting the full application, test if Chrome history can be read:

```bash
python3 test_chrome_history.py
```

### 2. Start the Application
```bash
docker-compose up --build
```

This will:
- Start InfluxDB with pre-configured credentials
- Start the Flask backend with Chrome history integration
- Mount your Chrome history directory (read-only)

### 3. Access the Application
- Frontend: http://localhost:8000
- InfluxDB: http://localhost:8086 (admin/adminpassword123)

## Configuration

### Environment Variables
The following environment variables can be set in `docker-compose.yml`:

```yaml
INFLUXDB_URL: http://influxdb:8086
INFLUXDB_TOKEN: your-super-secret-auth-token
INFLUXDB_ORG: youknow
INFLUXDB_BUCKET: chrome_history
```

### Chrome History Path
The default Chrome history path is `~/.config/google-chrome/Default/History`. 
If your Chrome is installed elsewhere, update the volume mount in `docker-compose.yml`.

## Data Collection

### Automatic Collection
- Data is collected every 5 minutes in the background
- Reads history from the last 7 days by default
- Automatically cleans up data older than 30 days

### Manual Refresh
You can force a data refresh via the API:

```bash
curl http://localhost:8000/api/refresh
```

### Data Status
Check the status of data collection:

```bash
curl http://localhost:8000/api/status
```

## API Endpoints

- `GET /api/dashboard` - Get dashboard data (supports `?days=N` parameter)
- `POST /api/refresh` - Force data refresh
- `GET /api/status` - Get data collection status
- `GET /api/health` - Health check

## Data Categories

The system automatically categorizes websites:

- **social**: Facebook, Twitter, Reddit, Instagram, TikTok
- **development**: GitHub, Stack Overflow, GitLab, Bitbucket
- **documentation**: Documentation sites, README files, API docs
- **search**: Google Search, Bing Search, DuckDuckGo
- **news**: News websites, BBC, CNN, Reuters
- **shopping**: Amazon, eBay, online stores
- **entertainment**: YouTube, Netflix, Spotify, Twitch
- **email**: Gmail, Outlook, Yahoo Mail
- **other**: Uncategorized websites

## Troubleshooting

### Chrome History Not Found
- Make sure Chrome is installed and has browsing history
- Check if the history file exists: `ls ~/.config/google-chrome/Default/History`
- Verify the volume mount in docker-compose.yml

### InfluxDB Connection Issues
- Check if InfluxDB is running: `docker ps`
- Verify InfluxDB credentials in environment variables
- Check InfluxDB logs: `docker logs youknow_influxdb`

### Permission Issues
- The Chrome history directory is mounted as read-only
- Make sure the Docker container can access your home directory

## Privacy & Security

- **Local Only**: Chrome history is read locally, never sent to external servers
- **Read-Only Access**: The application only reads history, never modifies it
- **Data Retention**: Data older than 30 days is automatically cleaned up
- **Secure Storage**: InfluxDB runs locally in Docker containers

## Performance

- **Efficient Reading**: Uses SQLite queries optimized for Chrome's schema
- **Background Processing**: Data collection runs in background threads
- **Caching**: InfluxDB provides fast query performance for historical data
- **Minimal Impact**: Chrome history reading takes only a few seconds

## Development

### Adding New Categories
Edit `chrome_history.py` and add new domain patterns to the `_categorize_url` method.

### Customizing Data Collection
Modify `data_manager.py` to change collection intervals or add new data sources.

### Extending Analytics
Add new query methods to `influxdb_service.py` for additional insights.
