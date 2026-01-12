#!/usr/bin/env python3
"""Test script to find Superfly's API endpoint."""

import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

# Test various endpoints
endpoints = [
    "https://superfly.fm/api/now-playing",
    "https://www.superfly.fm/api/now-playing",
    "https://api.superfly.fm/now-playing",
    "https://superfly.fm/now-playing.json",
    "https://superfly.fm/api/current-track",
    "https://superfly.fm/player/api/now-playing",
]

print("Testing Superfly API endpoints...\n")

for endpoint in endpoints:
    try:
        response = session.get(endpoint, timeout=5)
        print(f"✓ {endpoint}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"  Response (text): {response.text[:200]}")
        print()
    except Exception as e:
        print(f"✗ {endpoint}: {e}\n")

# Also try scraping the player page
print("Testing player page scraping...")
try:
    response = session.get("https://superfly.fm/player/", timeout=5)
    if response.status_code == 200:
        html = response.text
        # Look for common patterns
        if 'artist' in html.lower() or 'title' in html.lower():
            print("  Page contains artist/title keywords")
            # Try to find JSON in script tags
            import re
            script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for i, script in enumerate(script_tags[:5]):  # Check first 5 scripts
                if 'artist' in script.lower() or 'title' in script.lower():
                    print(f"  Found potential data in script tag {i+1}")
                    print(f"    Preview: {script[:300]}")
except Exception as e:
    print(f"  Error: {e}")
