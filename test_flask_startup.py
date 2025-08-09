#!/usr/bin/env python3
"""
Test script to verify Flask app startup without deprecated decorator errors
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    # Try to import the main module
    from main import app
    print("✅ Successfully imported Flask app")
    print(f"✅ App name: {app.name}")
    print(f"✅ App instance: {app}")
    
    # Check if the app has the expected routes
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    print(f"✅ App has {len(routes)} routes:")
    for route in routes:
        print(f"   - {route}")
    
    print("\n✅ Flask app startup test passed!")
    
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
