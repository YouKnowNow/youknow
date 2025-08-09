from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class InfluxDBService:
    def __init__(self):
        # InfluxDB configuration - can be overridden by environment variables
        self.url = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'your-token-here')
        self.org = os.getenv('INFLUXDB_ORG', 'your-org')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'chrome_history')
        
        self.client = None
        self.write_api = None
        self.query_api = None
        
    def connect(self):
        """Connect to InfluxDB"""
        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org
            )
            
            # Test connection
            self.client.ping()
            
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            logger.info("Successfully connected to InfluxDB")
            logger.info(f"InfluxDB URL: {self.url}")
            logger.info(f"InfluxDB Org: {self.org}")
            logger.info(f"InfluxDB Bucket: {self.bucket}")
            
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                logger.warning("Could not ensure bucket exists, some operations may fail")
            
            # Test a simple query
            if not self.test_query():
                logger.warning("InfluxDB test query failed, connection may have issues")
            
            # Test basic functionality
            if not self.test_basic_functionality():
                logger.warning("InfluxDB basic functionality test failed")
            
            # Get server information
            info = self.get_info()
            if info:
                logger.info(f"InfluxDB server info: {info}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            logger.error(f"InfluxDB URL: {self.url}")
            logger.error(f"InfluxDB Org: {self.org}")
            logger.error(f"InfluxDB Bucket: {self.bucket}")
            return False
    
    def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
    
    def store_chrome_history(self, history_data):
        """Store Chrome history data in InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return False
        
        try:
            points = []
            
            for entry in history_data:
                if entry['visit_time']:
                    point = Point("chrome_history") \
                        .tag("domain", entry['domain']) \
                        .tag("category", entry['category']) \
                        .tag("url", entry['url']) \
                        .field("title", entry['title']) \
                        .field("visit_count", entry['visit_count']) \
                        .field("typed_count", entry['typed_count']) \
                        .time(entry['visit_time'])
                    
                    points.append(point)
            
            if points:
                self.write_api.write(bucket=self.bucket, record=points)
                logger.info(f"Stored {len(points)} history entries in InfluxDB")
                return True
                
        except Exception as e:
            logger.error(f"Error storing data in InfluxDB: {e}")
            return False
        
        return False
    
    def get_domain_stats(self, days_back=7):
        """Get domain statistics from InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return []
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            # Format datetime as RFC3339 string for InfluxDB (UTC)
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            logger.debug(f"Time range: {start_str} to {end_str}")
            
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_str}, stop: {end_str})
              |> filter(fn: (r) => r._measurement == "chrome_history" and r._field == "visit_count")
              |> group(columns: ["domain"])
              |> sum()
              |> rename(columns: {{_value: "visit_count"}})
              |> sort(columns: ["visit_count"], desc: true)
              |> limit(n: 50)
            '''
            
            logger.debug(f"Executing InfluxDB query: {query}")
            result = self.query_api.query(query)
            
            domain_stats = []
            for table in result:
                for record in table.records:
                    domain_stats.append({
                        'domain': record.values.get("domain", "unknown"),
                        'visit_count': int(record.values.get("visit_count", 0)),
                        'category': record.values.get("category", "unknown")
                    })
            
            return domain_stats
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB (domains): {e}")
            return []
    
    def get_search_queries(self, days_back=7):
        """Get search query statistics from InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return []
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            # Format datetime as RFC3339 string for InfluxDB (UTC)
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Pull urls and times; we don't aggregate in Flux here
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_str}, stop: {end_str})
              |> filter(fn: (r) => r._measurement == "chrome_history")
              |> keep(columns: ["_time","url"])
            '''
            
            logger.debug(f"Executing InfluxDB query: {query}")
            result = self.query_api.query(query)
            
            counts = {}
            for table in result:
                for record in table.records:
                    url = record.values.get("url")
                    if not url:
                        continue
                    q = self._extract_search_query(url)
                    if q:
                        counts[q] = counts.get(q, 0) + 1
            
            top = [{"query": k, "count": v} for k, v in counts.items()]
            top.sort(key=lambda x: x["count"], reverse=True)
            return top[:50]
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB (searches): {e}")
            return []
    
    def get_category_stats(self, days_back=7):
        """Get category statistics from InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return {}
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            # Format datetime as RFC3339 string for InfluxDB (UTC)
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Option A: count points by category
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_str}, stop: {end_str})
              |> filter(fn: (r) => r._measurement == "chrome_history")
              |> group(columns: ["category"])
              |> count()
              |> rename(columns: {{_value: "count"}})
            '''
            
            logger.debug(f"Executing InfluxDB query: {query}")
            result = self.query_api.query(query)
            
            category_stats = {}
            for table in result:
                for record in table.records:
                    cat = record.values.get("category", "other")
                    category_stats[cat] = int(record.values.get("count", 0))
            
            return category_stats
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB (categories): {e}")
            return {}
    
    def get_hourly_activity(self, days_back=7):
        """Get hourly activity patterns from InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return {}
        
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days_back)
            
            # Format datetime as RFC3339 string for InfluxDB (UTC)
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            query = f'''
            import "date"
            from(bucket: "{self.bucket}")
              |> range(start: {start_str}, stop: {end_str})
              |> filter(fn: (r) => r._measurement == "chrome_history")
              |> map(fn: (r) => ({{
                  r with hour: string(v: date.hour(t: r._time))
              }}))
              |> keep(columns: ["hour","_time"])
              |> group(columns: ["hour"])
              |> count(column: "_time")
              |> rename(columns: {{_value: "count"}})
            '''
            
            logger.debug(f"Executing InfluxDB query: {query}")
            result = self.query_api.query(query)
            
            hourly_stats = {}
            for table in result:
                for record in table.records:
                    hour = record.values.get("hour", "0")
                    hourly_stats[str(hour)] = int(record.values.get("count", 0))
            
            return hourly_stats
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB (hourly): {e}")
            return {}
    
    def _extract_search_query(self, url):
        """Extract search query from URL"""
        try:
            if 'google.com/search' in url:
                query_start = url.find('q=') + 2
                query_end = url.find('&', query_start)
                if query_end == -1:
                    query_end = len(url)
                query = url[query_start:query_end]
            elif 'bing.com/search' in url:
                query_start = url.find('q=') + 2
                query_end = url.find('&', query_start)
                if query_end == -1:
                    query_end = len(url)
                query = url[query_start:query_end]
            else:
                return None
            
            # Decode URL encoding
            query = query.replace('+', ' ').replace('%20', ' ')
            return query if query and len(query) > 2 else None
            
        except Exception:
            return None
    
    def cleanup_old_data(self, days_to_keep=30):
        """Clean up old data from InfluxDB"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return False
        
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            # Format datetime as RFC3339 string for InfluxDB (UTC)
            cutoff_str = cutoff_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: 0, stop: {cutoff_str})
                |> filter(fn: (r) => r._measurement == "chrome_history")
                |> count()
            '''
            
            logger.debug(f"Executing InfluxDB cleanup query: {query}")
            result = self.query_api.query(query)
            
            # Count records that would be deleted
            record_count = 0
            for table in result:
                for record in table.records:
                    record_count += record.get_value()
            
            logger.info(f"Found {record_count} records older than {days_to_keep} days")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False

    def test_query(self):
        """Test a simple query to verify InfluxDB connection and syntax"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return False
        
        try:
            # Simple test query
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1h)
                |> limit(n: 1)
            '''
            
            logger.info(f"Testing InfluxDB query: {query}")
            result = self.query_api.query(query)
            
            # Count results
            record_count = 0
            for table in result:
                for record in table.records:
                    record_count += 1
            
            logger.info(f"InfluxDB test query successful, found {record_count} records")
            return True
            
        except Exception as e:
            logger.error(f"InfluxDB test query failed: {e}")
            return False

    def ensure_bucket_exists(self):
        """Ensure the bucket exists, create it if it doesn't"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return False
        
        try:
            # Get buckets API
            buckets_api = self.client.buckets_api()
            
            # Check if bucket exists
            try:
                bucket = buckets_api.find_bucket_by_name(self.bucket)
                logger.info(f"Bucket '{self.bucket}' already exists")
                return True
            except Exception:
                # Bucket doesn't exist, create it
                logger.info(f"Creating bucket '{self.bucket}'...")
                bucket = buckets_api.create_bucket(
                    bucket_name=self.bucket,
                    org=self.org
                )
                logger.info(f"Successfully created bucket '{self.bucket}'")
                return True
                
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            return False

    def _validate_query(self, query):
        """Validate InfluxDB query syntax"""
        try:
            # Basic validation - check for common syntax issues
            if not query.strip():
                return False, "Empty query"
            
            # Check for proper bucket reference
            if f'from(bucket: "{self.bucket}")' not in query:
                return False, "Missing or incorrect bucket reference"
            
            # Check for proper range syntax
            if '|> range(' not in query:
                return False, "Missing range operator"
            
            return True, "Query appears valid"
            
        except Exception as e:
            return False, f"Validation error: {e}"

    def get_info(self):
        """Get InfluxDB server information (JSON-serializable)"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return None
        try:
            health = self.client.health()
            # health is a HealthCheck object -> make it serializable
            health_info = {
                "status": getattr(health, "status", None),
                "message": getattr(health, "message", None),
                "name": getattr(health, "name", None),
                "version": getattr(health, "version", None),
                "commit": getattr(health, "commit", None),
            }

            ping_ok = bool(self.client.ping())

            return {
                "health": health_info,
                "ping": ping_ok,
                "url": self.url,
                "org": self.org,
                "bucket": self.bucket,
            }
        except Exception as e:
            logger.error(f"Error getting InfluxDB info: {e}")
            return None


    def test_basic_functionality(self):
        """Test basic InfluxDB functionality with simple queries"""
        if not self.client:
            logger.error("Not connected to InfluxDB")
            return False
        
        try:
            # Test 1: Simple count query
            query1 = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1h)
                |> count()
            '''
            
            logger.info("Testing basic count query...")
            result1 = self.query_api.query(query1)
            logger.info(f"Count query successful, result: {result1}")
            
            # Test 2: Simple filter query
            query2 = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -1h)
                |> filter(fn: (r) => r._measurement == "chrome_history")
                |> count()
            '''
            
            logger.info("Testing filter query...")
            result2 = self.query_api.query(query2)
            logger.info(f"Filter query successful, result: {result2}")
            
            return True
            
        except Exception as e:
            logger.error(f"Basic functionality test failed: {e}")
            return False
