import sqlite3
import shutil
import os
import re
import tempfile
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromeHistoryReader:
    def __init__(self):
        # First check for custom paths from environment variables
        custom_paths = os.getenv("CHROME_HISTORY_PATHS", "")
        extra_paths = [p.strip() for p in custom_paths.split(";") if p.strip()]
        
        # Try multiple possible Chrome history paths
        self.history_paths = extra_paths + [
            # Host-mounted paths (from docker-compose)
            "/host_chrome/Default/History",
            "/host_chrome/Profile 1/History", 
            "/host_chrome/Profile 2/History",
            "/host_chrome/Profile 3/History",
            "/host_chromium/Default/History",
            "/host_chromium/Profile 1/History",
            "/host_chromium/Profile 2/History",
            # Container paths (fallback)
            "/root/.config/google-chrome/Default/History",
            "/root/.config/google-chrome/Profile 1/History",
            "/root/.config/google-chrome/Profile 2/History",
            "/root/.config/chromium/Default/History",
            "/root/.config/chromium/Profile 1/History",
            "/root/.config/chromium/Profile 2/History",
            # Local user paths (for development)
            os.path.expanduser("~/.config/google-chrome/Default/History"),
            os.path.expanduser("~/.config/google-chrome/Profile 1/History"),
            os.path.expanduser("~/.config/google-chrome/Profile 2/History"),
            os.path.expanduser("~/.config/chromium/Default/History"),
            os.path.expanduser("~/.config/chromium/Profile 1/History"),
            os.path.expanduser("~/.config/chromium/Profile 2/History"),
        ]
        
        logger.info(f"ChromeHistoryReader initialized with {len(self.history_paths)} potential paths")
        if extra_paths:
            logger.info(f"Custom paths from environment: {extra_paths}")
        
    def get_chrome_history(self, days_back=7):
        """Read Chrome history for the last N days"""
        temp_path = None
        
        try:
            # Find an accessible Chrome history file
            history_path = self._find_history_file()
            if not history_path:
                logger.warning("No accessible Chrome history file found")
                return []
            
            logger.info(f"Found Chrome history at: {history_path}")
            
            # Create a temporary file in a writable directory
            temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
            os.close(temp_fd)
            
            # Try to copy the history file
            try:
                # First try a simple copy
                shutil.copy2(history_path, temp_path)
                logger.info("Successfully copied Chrome history file")
            except PermissionError:
                logger.warning("Permission denied, trying alternative copy method...")
                # If that fails, try using cp command
                import subprocess
                try:
                    subprocess.run(['cp', history_path, temp_path], check=True)
                    logger.info("Successfully copied Chrome history file using cp")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.error("Failed to copy Chrome history file")
                    return []
            except Exception as e:
                logger.error(f"Error copying Chrome history file: {e}")
                return []
            
            # Verify the copy was successful
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                logger.error("Failed to create valid copy of Chrome history file")
                return []
            
            # Connect to the copied database
            try:
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                logger.info("Successfully connected to Chrome history database")
            except Exception as e:
                logger.error(f"Failed to connect to Chrome history database: {e}")
                return []
            
            # Calculate timestamp for N days ago
            days_ago = datetime.now() - timedelta(days=days_back)
            days_ago_timestamp = int((days_ago.timestamp() + 11644473600) * 1000000)
            
            logger.info(f"Querying for visits after: {days_ago} (timestamp: {days_ago_timestamp})")
            
            # Query for recent history
            query = """
            SELECT 
                url, 
                title, 
                last_visit_time,
                visit_count,
                typed_count
            FROM urls 
            WHERE last_visit_time > ? 
            ORDER BY last_visit_time DESC
            """
            
            try:
                cursor.execute(query, (days_ago_timestamp,))
                rows = cursor.fetchall()
                logger.info(f"Found {len(rows)} raw history entries")
            except Exception as e:
                logger.error(f"Failed to execute query: {e}")
                conn.close()
                return []
            
            history_data = []
            processed_count = 0
            error_count = 0
            
            for row in rows:
                try:
                    url, title, visit_time, visit_count, typed_count = row
                    
                    # Convert Chrome timestamp to datetime
                    if visit_time:
                        timestamp = (visit_time / 1000000) - 11644473600
                        visit_datetime = datetime.fromtimestamp(timestamp)
                    else:
                        visit_datetime = None
                    
                    # Extract domain from URL
                    try:
                        domain = urlparse(url).netloc
                        if domain.startswith('www.'):
                            domain = domain[4:]
                    except:
                        domain = "unknown"
                    
                    # Categorize the visit
                    category = self._categorize_url(url, title)
                    
                    history_data.append({
                        'url': url,
                        'title': title,
                        'domain': domain,
                        'visit_time': visit_datetime,
                        'visit_count': visit_count or 0,
                        'typed_count': typed_count or 0,
                        'category': category
                    })
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    logger.warning(f"Error processing history entry {processed_count + error_count}: {e}")
                    continue
            
            conn.close()
            
            logger.info(f"Successfully processed {processed_count} history entries (errors: {error_count})")
            return history_data
            
        except Exception as e:
            logger.error(f"Error reading Chrome history: {e}")
            return []
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.debug("Cleaned up temporary Chrome history file")
                except Exception as e:
                    logger.warning(f"Could not remove temporary file {temp_path}: {e}")
    
    def _find_history_file(self):
        """Find an accessible Chrome history file"""
        logger.info("Searching for Chrome history files...")
        
        for path in self.history_paths:
            logger.debug(f"Checking path: {path}")
            if os.path.exists(path):
                try:
                    # Check if we can read the file
                    if os.access(path, os.R_OK):
                        # Check if file is not empty
                        file_size = os.path.getsize(path)
                        if file_size > 0:
                            logger.info(f"Found accessible Chrome history file: {path} (size: {file_size} bytes)")
                            return path
                        else:
                            logger.debug(f"Chrome history file is empty: {path}")
                    else:
                        logger.debug(f"Cannot read Chrome history file: {path}")
                except Exception as e:
                    logger.debug(f"Error checking file {path}: {e}")
            else:
                logger.debug(f"Path does not exist: {path}")
        
        logger.warning("No accessible Chrome history files found")
        return None
    
    def _categorize_url(self, url, title):
        """Categorize URLs based on domain and content"""
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        
        # Social media
        if any(social in url_lower for social in ['facebook.com', 'twitter.com', 'instagram.com', 'reddit.com', 'tiktok.com']):
            return 'social'
        
        # Development/Programming
        if any(dev in url_lower for dev in ['github.com', 'stackoverflow.com', 'gitlab.com', 'bitbucket.org']):
            return 'development'
        
        # Documentation
        if any(doc in url_lower for doc in ['docs.', 'documentation', 'readme', 'api.']):
            return 'documentation'
        
        # Search engines
        if any(search in url_lower for search in ['google.com/search', 'bing.com/search', 'duckduckgo.com']):
            return 'search'
        
        # News/Information
        if any(news in url_lower for news in ['news.', 'bbc.com', 'cnn.com', 'reuters.com']):
            return 'news'
        
        # Shopping
        if any(shop in url_lower for shop in ['amazon.com', 'ebay.com', 'shop.', 'store.']):
            return 'shopping'
        
        # Entertainment
        if any(ent in url_lower for ent in ['youtube.com', 'netflix.com', 'spotify.com', 'twitch.tv']):
            return 'entertainment'
        
        # Email
        if any(mail in url_lower for mail in ['gmail.com', 'outlook.com', 'yahoo.com/mail']):
            return 'email'
        
        return 'other'
    
    def get_domain_stats(self, history_data):
        """Calculate domain statistics from history data"""
        domain_stats = {}
        
        for entry in history_data:
            domain = entry['domain']
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'visit_count': 0,
                    'total_time': 0,
                    'category': entry['category'],
                    'last_visit': None
                }
            
            domain_stats[domain]['visit_count'] += entry['visit_count']
            if entry['visit_time']:
                if not domain_stats[domain]['last_visit'] or entry['visit_time'] > domain_stats[domain]['last_visit']:
                    domain_stats[domain]['last_visit'] = entry['visit_time']
        
        # Convert to list and sort by visit count
        domain_list = [
            {
                'domain': domain,
                'visit_count': stats['visit_count'],
                'category': stats['category'],
                'last_visit': stats['last_visit']
            }
            for domain, stats in domain_stats.items()
        ]
        
        domain_list.sort(key=lambda x: x['visit_count'], reverse=True)
        return domain_list
    
    def get_search_queries(self, history_data):
        """Extract search queries from history data"""
        search_queries = {}
        
        for entry in history_data:
            url = entry['url']
            if 'google.com/search' in url or 'bing.com/search' in url:
                # Extract search query from URL
                try:
                    if 'google.com/search' in url:
                        query_start = url.find('q=') + 2
                        query_end = url.find('&', query_start)
                        if query_end == -1:
                            query_end = len(url)
                        query = url[query_start:query_end]
                    else:
                        query_start = url.find('q=') + 2
                        query_end = url.find('&', query_start)
                        if query_end == -1:
                            query_end = len(url)
                        query = url[query_start:query_end]
                    
                    # Decode URL encoding
                    query = query.replace('+', ' ').replace('%20', ' ')
                    
                    if query and len(query) > 2:  # Filter out very short queries
                        search_queries[query] = search_queries.get(query, 0) + 1
                        
                except Exception as e:
                    logger.debug(f"Could not extract query from {url}: {e}")
                    continue
        
        # Convert to list and sort by count
        search_list = [
            {'query': query, 'count': count}
            for query, count in search_queries.items()
        ]
        
        search_list.sort(key=lambda x: x['count'], reverse=True)
        return search_list[:20]  # Return top 20 searches

    def test_history_access(self):
        """Test if we can access and read Chrome history files"""
        logger.info("Testing Chrome history access...")
        
        # Find accessible files
        history_path = self._find_history_file()
        if not history_path:
            logger.error("No accessible Chrome history files found")
            return False
        
        # Test file copy
        temp_path = None
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
            os.close(temp_fd)
            
            # Try to copy
            shutil.copy2(history_path, temp_path)
            
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                logger.info("Successfully copied Chrome history file")
                
                # Test database connection
                try:
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    
                    # Test basic query
                    cursor.execute("SELECT COUNT(*) FROM urls")
                    count = cursor.fetchone()[0]
                    logger.info(f"Database connection successful, found {count} total URLs")
                    
                    conn.close()
                    return True
                    
                except Exception as e:
                    logger.error(f"Database connection failed: {e}")
                    return False
            else:
                logger.error("File copy failed or resulted in empty file")
                return False
                
        except Exception as e:
            logger.error(f"File copy test failed: {e}")
            return False
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
        
        return False
