#!/usr/bin/env python3
"""
Simple test script for Chrome history reading
This script demonstrates basic Chrome history access functionality
"""

import sqlite3
import shutil
import os
import sys

def test_chrome_history():
    """Test basic Chrome history reading"""
    
    # مسیر فایل History
    history_path = os.path.expanduser("~/.config/google-chrome/Default/History")
    temp_path = "/tmp/History_copy"
    
    print(f"Looking for Chrome history at: {history_path}")
    
    # Check if Chrome history file exists
    if not os.path.exists(history_path):
        print(f"❌ Chrome history not found at {history_path}")
        print("Make sure Chrome is installed and has been used at least once")
        return False
    
    print("✅ Chrome history file found")
    
    try:
        # کپی گرفتن از فایل (برای جلوگیری از قفل شدن)
        print("📋 Copying history file to temporary location...")
        shutil.copy2(history_path, temp_path)
        print("✅ History file copied successfully")
        
        # اتصال به دیتابیس
        print("🔌 Connecting to database...")
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        print("✅ Database connection established")
        
        # گرفتن 10 رکورد آخر
        print("\n📊 Fetching last 10 history records...")
        query = """
        SELECT url, title, datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime') as visit_time
        FROM urls
        ORDER BY last_visit_time DESC
        LIMIT 10
        """
        cursor.execute(query)
        
        rows = cursor.fetchall()
        if rows:
            print(f"✅ Found {len(rows)} history records:")
            print("-" * 80)
            for i, row in enumerate(rows, 1):
                url, title, visit_time = row
                print(f"{i:2d}. {visit_time}")
                print(f"    Title: {title[:60]}{'...' if len(title) > 60 else ''}")
                print(f"    URL:   {url[:80]}{'...' if len(url) > 80 else ''}")
                print()
        else:
            print("⚠️  No history records found")
        
        conn.close()
        print("✅ Database connection closed")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("✅ Temporary file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_advanced_features():
    """Test advanced features from the ChromeHistoryReader class"""
    print("\n" + "="*80)
    print("TESTING ADVANCED FEATURES")
    print("="*80)
    
    try:
        from app.chrome_history import ChromeHistoryReader
        
        print("📚 Testing ChromeHistoryReader class...")
        reader = ChromeHistoryReader()
        
        # Test basic history reading
        print("🔍 Reading last 7 days of history...")
        history_data = reader.get_chrome_history(days_back=7)
        
        if history_data:
            print(f"✅ Successfully read {len(history_data)} history entries")
            
            # Test domain statistics
            print("📊 Generating domain statistics...")
            domain_stats = reader.get_domain_stats(history_data)
            print(f"✅ Found {len(domain_stats)} unique domains")
            
            if domain_stats:
                print("\nTop 5 domains by visit count:")
                for i, domain in enumerate(domain_stats[:5], 1):
                    print(f"  {i}. {domain['domain']} - {domain['visit_count']} visits")
            
            # Test search queries
            print("\n🔍 Extracting search queries...")
            search_queries = reader.get_search_queries(history_data)
            print(f"✅ Found {len(search_queries)} search queries")
            
            if search_queries:
                print("\nTop 5 search queries:")
                for i, query in enumerate(search_queries[:5], 1):
                    print(f"  {i}. '{query['query']}' - {query['count']} times")
        
        else:
            print("⚠️  No history data returned")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import ChromeHistoryReader: {e}")
        print("Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Error testing advanced features: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Chrome History Test Script")
    print("="*80)
    
    # Test basic functionality
    basic_success = test_chrome_history()
    
    # Test advanced features
    advanced_success = test_advanced_features()
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Advanced features:  {'✅ PASS' if advanced_success else '❌ FAIL'}")
    
    if basic_success and advanced_success:
        print("\n🎉 All tests passed! Your Chrome history integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 You can now use the ChromeHistoryReader class in your application!")
