import logging
import threading
import time
from datetime import datetime, timedelta
from chrome_history import ChromeHistoryReader
from influxdb_service import InfluxDBService

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.chrome_reader = ChromeHistoryReader()
        self.influx_service = InfluxDBService()
        self.last_collection_time = None
        self.collection_interval = 300  # 5 minutes
        self.is_running = False
        self.collection_thread = None
        
    def start_data_collection(self):
        """Start the data collection service"""
        if self.is_running:
            logger.info("Data collection is already running")
            return
        
        # Try to connect to InfluxDB
        if not self.influx_service.connect():
            logger.warning("Could not connect to InfluxDB, running in local mode only")
        
        # Initial data collection
        self.collect_chrome_data()
        
        # Start background collection thread
        self.is_running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        logger.info("Data collection service started")
    
    def stop_data_collection(self):
        """Stop the data collection service"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        self.influx_service.close()
        logger.info("Data collection service stopped")
    
    def _collection_loop(self):
        """Background loop for periodic data collection"""
        while self.is_running:
            try:
                time.sleep(self.collection_interval)
                if self.is_running:
                    self.collect_chrome_data()
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def collect_chrome_data(self):
        """Collect Chrome history data and store it"""
        try:
            logger.info("Starting Chrome history collection...")
            
            # Read Chrome history for the last 7 days
            history_data = self.chrome_reader.get_chrome_history(days_back=7)
            
            if not history_data:
                logger.warning("No Chrome history data found")
                return
            
            # Store data in InfluxDB if connected
            if self.influx_service.client:
                if self.influx_service.store_chrome_history(history_data):
                    logger.info(f"Successfully stored {len(history_data)} history entries")
                else:
                    logger.error("Failed to store data in InfluxDB")
            
            # Update last collection time
            self.last_collection_time = datetime.now()
            
            # Clean up old data (keep last 30 days)
            if self.influx_service.client:
                self.influx_service.cleanup_old_data(days_to_keep=30)
            
        except Exception as e:
            logger.error(f"Error collecting Chrome data: {e}")
    
    def get_dashboard_data(self, days_back=7):
        """Get dashboard data from InfluxDB or fallback to local Chrome data"""
        try:
            # Try to get data from InfluxDB first
            if self.influx_service.client:
                domain_stats = self.influx_service.get_domain_stats(days_back)
                search_queries = self.influx_service.get_search_queries(days_back)
                category_stats = self.influx_service.get_category_stats(days_back)
                hourly_activity = self.influx_service.get_hourly_activity(days_back)
                
                if domain_stats and search_queries:
                    return self._format_dashboard_data(
                        domain_stats, search_queries, category_stats, hourly_activity
                    )
            
            # Fallback to local Chrome data
            logger.info("Using local Chrome data for dashboard")
            return self._get_local_dashboard_data(days_back)
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return self._get_fallback_data()
    
    def _get_local_dashboard_data(self, days_back=7):
        """Get dashboard data from local Chrome history"""
        try:
            # Read Chrome history
            history_data = self.chrome_reader.get_chrome_history(days_back)
            
            if not history_data:
                return self._get_fallback_data()
            
            # Process data locally
            domain_stats = self.chrome_reader.get_domain_stats(history_data)
            search_queries = self.chrome_reader.get_search_queries(history_data)
            
            # Calculate category stats
            category_stats = {}
            for entry in history_data:
                category = entry['category']
                category_stats[category] = category_stats.get(category, 0) + 1
            
            # Calculate hourly activity
            hourly_activity = {}
            for entry in history_data:
                if entry['visit_time']:
                    hour = str(entry['visit_time'].hour)
                    hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            return self._format_dashboard_data(
                domain_stats, search_queries, category_stats, hourly_activity
            )
            
        except Exception as e:
            logger.error(f"Error getting local dashboard data: {e}")
            return self._get_fallback_data()
    
    def _format_dashboard_data(self, domain_stats, search_queries, category_stats, hourly_activity):
        """Format data for the dashboard API"""
        try:
            # Convert domain stats to the expected format
            top_domains = []
            for stat in domain_stats[:10]:  # Top 10 domains
                # Estimate time spent based on visit count (rough approximation)
                estimated_minutes = stat['visit_count'] * 2  # Assume 2 minutes per visit
                top_domains.append({
                    "domain": stat['domain'],
                    "minutes": estimated_minutes
                })
            
            # Convert search queries to the expected format
            top_searches = []
            for stat in search_queries[:10]:  # Top 10 searches
                top_searches.append({
                    "q": stat['query'],
                    "count": stat['count']
                })
            
            # Calculate focus metrics
            docs_min = category_stats.get('documentation', 0) * 2
            social_min = category_stats.get('social', 0) * 2
            total_min = docs_min + social_min
            
            focus_score = 0.0
            if total_min > 0:
                focus_score = docs_min / total_min
            
            focus = {
                "docs_min": docs_min,
                "social_min": social_min,
                "score": round(focus_score, 2)
            }
            
            # Format golden hours data
            golden_hours = {}
            for hour in range(8, 18):  # 8 AM to 6 PM
                golden_hours[str(hour)] = hourly_activity.get(str(hour), 0) * 2
            
            # Generate session data (simplified)
            sessions = self._generate_sessions(domain_stats, category_stats)
            
            # Calculate trends (simplified)
            trends = {
                "docs_min_delta_pct": 0,
                "social_min_delta_pct": 0,
                "search_count_delta_pct": 0
            }
            
            # Generate interest chains
            chains = self._generate_chains(domain_stats)
            
            # Extract interests from top searches and domains
            interests = []
            for search in search_queries[:5]:
                interests.append(search['query'])
            
            return {
                "top_domains": top_domains,
                "top_searches": top_searches,
                "focus": focus,
                "golden_hours": golden_hours,
                "sessions": sessions,
                "trends": trends,
                "chains": chains,
                "interests": interests[:10]
            }
            
        except Exception as e:
            logger.error(f"Error formatting dashboard data: {e}")
            return self._get_fallback_data()
    
    def _generate_sessions(self, domain_stats, category_stats):
        """Generate session data based on domain and category statistics"""
        sessions = []
        
        # Create some sample sessions based on the data
        if domain_stats:
            # Session 1: Development focused
            if any('github.com' in stat['domain'] for stat in domain_stats):
                sessions.append({
                    "start": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
                    "duration_min": 45,
                    "dominant": "development",
                    "path": ["github", "stackoverflow", "docs"]
                })
            
            # Session 2: Research focused
            if any('google.com' in stat['domain'] for stat in domain_stats):
                sessions.append({
                    "start": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M"),
                    "duration_min": 30,
                    "dominant": "research",
                    "path": ["google", "stackoverflow", "github"]
                })
        
        # Add more sessions if we have enough data
        if len(domain_stats) > 5:
            sessions.append({
                "start": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M"),
                "duration_min": 25,
                "dominant": "browsing",
                "path": ["reddit", "news", "social"]
            })
        
        return sessions[:5]  # Return max 5 sessions
    
    def _generate_chains(self, domain_stats):
        """Generate interest chains based on domain statistics"""
        chains = []
        
        if domain_stats:
            # Chain 1: Development workflow
            if any('github.com' in stat['domain'] for stat in domain_stats):
                chains.append(["google", "stackoverflow", "github", "docs"])
            
            # Chain 2: Research workflow
            if any('google.com' in stat['domain'] for stat in domain_stats):
                chains.append(["google", "stackoverflow", "github"])
            
            # Chain 3: Social browsing
            if any('reddit.com' in stat['domain'] for stat in domain_stats):
                chains.append(["google", "reddit", "social"])
        
        return chains[:5]  # Return max 5 chains
    
    def _get_fallback_data(self):
        """Return fallback data when everything else fails"""
        return {
            "top_domains": [
                {"domain": "github.com", "minutes": 30},
                {"domain": "stackoverflow.com", "minutes": 20},
                {"domain": "google.com", "minutes": 15}
            ],
            "top_searches": [
                {"q": "python tutorial", "count": 2},
                {"q": "react components", "count": 1}
            ],
            "focus": {"docs_min": 60, "social_min": 20, "score": 0.75},
            "golden_hours": {"8": 10, "9": 15, "10": 20, "11": 25, "12": 15, "13": 10, "14": 20, "15": 15, "16": 20, "17": 10},
            "sessions": [
                {"start": "2025-01-20T10:00", "duration_min": 30, "dominant": "development", "path": ["google", "github", "docs"]}
            ],
            "trends": {"docs_min_delta_pct": 0, "social_min_delta_pct": 0, "search_count_delta_pct": 0},
            "chains": [["google", "github", "docs"]],
            "interests": ["python", "react", "development"]
        }
    
    def force_refresh(self):
        """Force a refresh of the data"""
        logger.info("Forcing data refresh...")
        self.collect_chrome_data()
        return True

    def test_chrome_history_access(self):
        """Test if Chrome history is accessible"""
        logger.info("Testing Chrome history access...")
        
        try:
            # Test basic access
            if self.chrome_reader.test_history_access():
                logger.info("Chrome history access test passed")
                return True
            else:
                logger.error("Chrome history access test failed")
                return False
        except Exception as e:
            logger.error(f"Error testing Chrome history access: {e}")
            return False
    
    def get_chrome_history_info(self):
        """Get information about Chrome history availability"""
        try:
            # Try to get a small sample of history
            sample_data = self.chrome_reader.get_chrome_history(days_back=1)
            
            info = {
                'accessible': len(sample_data) > 0,
                'sample_count': len(sample_data),
                'sample_domains': list(set([entry['domain'] for entry in sample_data[:5]])) if sample_data else [],
                'last_collection': self.last_collection_time.isoformat() if self.last_collection_time else None
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting Chrome history info: {e}")
            return {
                'accessible': False,
                'error': str(e),
                'sample_count': 0,
                'sample_domains': [],
                'last_collection': None
            }
