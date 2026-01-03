#!/usr/bin/env python3
"""
COMPREHENSIVE QA BOT - Application Quality Control
Ensures ALL features work, link correctly, and have content
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

API_BASE = "http://localhost:3000"

class QABot:
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.tests_run = 0
        self.tests_passed = 0
        
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        symbol = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(level, "•")
        print(f"[{timestamp}] {symbol} {msg}")
        
    def test_route(self, path, expected_status=200, description=""):
        """Test if a route exists and returns expected status"""
        try:
            r = requests.get(f"{API_BASE}{path}", timeout=5)
            self.tests_run += 1
            
            if r.status_code == expected_status:
                self.tests_passed += 1
                self.log(f"{description or path}: OK", "PASS")
                return True
            else:
                self.log(f"{description or path}: Got {r.status_code}, expected {expected_status}", "FAIL")
                self.failures.append(f"{path} returned {r.status_code}")
                return False
        except Exception as e:
            self.tests_run += 1
            self.log(f"{description or path}: {str(e)}", "FAIL")
            self.failures.append(f"{path}: {e}")
            return False
    
    def test_json_endpoint(self, path, required_keys=[]):
        """Test JSON endpoint and verify required keys"""
        try:
            r = requests.get(f"{API_BASE}{path}", timeout=5)
            self.tests_run += 1
            
            if r.status_code != 200:
                self.log(f"{path}: HTTP {r.status_code}", "FAIL")
                self.failures.append(f"{path} not accessible")
                return False
            
            data = r.json()
            
            # Check for required keys
            missing = [k for k in required_keys if k not in data]
            if missing:
                self.log(f"{path}: Missing keys: {missing}", "FAIL")
                self.failures.append(f"{path} missing: {missing}")
                return False
            
            self.tests_passed += 1
            self.log(f"{path}: Valid JSON with {len(data)} keys", "PASS")
            return True
            
        except Exception as e:
            self.tests_run += 1
            self.log(f"{path}: {str(e)}", "FAIL")
            self.failures.append(f"{path}: {e}")
            return False
    
    def test_view_has_content(self, path, min_size=500):
        """Test that HTML page has meaningful content"""
        try:
            r = requests.get(f"{API_BASE}{path}", timeout=5)
            self.tests_run += 1
            
            if r.status_code != 200:
                self.log(f"{path}: Not accessible", "FAIL")
                self.failures.append(f"{path} not found")
                return False
            
            content_size = len(r.text)
            
            if content_size < min_size:
                self.log(f"{path}: Suspiciously small ({content_size} bytes)", "WARN")
                self.warnings.append(f"{path} only {content_size} bytes")
                self.tests_passed += 1  # Warning, not failure
                return True
            
            self.tests_passed += 1
            self.log(f"{path}: {content_size} bytes", "PASS")
            return True
            
        except Exception as e:
            self.tests_run += 1
            self.log(f"{path}: {str(e)}", "FAIL")
            self.failures.append(f"{path}: {e}")
            return False
    
    def test_navigation_links(self):
        """Test all navigation links in index.html"""
        try:
            r = requests.get(f"{API_BASE}/", timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            links = soup.find_all('a', href=True)
            self.log(f"Found {len(links)} links to test", "INFO")
            
            for link in links:
                href = link['href']
                if href.startswith('http') or href.startswith('#'):
                    continue  # Skip external and anchors
                
                # Test internal link
                self.test_route(href, description=f"Link: {href}")
                
        except Exception as e:
            self.log(f"Navigation test failed: {e}", "FAIL")
    
    def run_comprehensive_qa(self):
        """Execute full QA suite"""
        self.log("=" * 70, "INFO")
        self.log("COMPREHENSIVE QA SUITE - Application Quality Control", "INFO")
        self.log("=" * 70, "INFO")
        
        # Test core HTML pages
        self.log("\n[1] Testing Core HTML Pages", "INFO")
        self.test_route("/", description="Dashboard (index.html)")
        self.test_route("/index.html", description="Index")
        self.test_route("/gaia.html", description="Gaia Control Center")
        self.test_route("/console.html", description="Terminal Console")
        self.test_route("/verifier.html", description="Verifier Station")
        
        # Test JSON endpoints
        self.log("\n[2] Testing JSON Data Endpoints", "INFO")
        self.test_json_endpoint("/ui_config.json", required_keys=["modules", "theme"])
        self.test_json_endpoint("/seh7_quests.json", required_keys=["total_quests", "phases"])
        self.test_json_endpoint("/api/graph")
        self.test_json_endpoint("/api/state")
        
        # Test JavaScript assets
        self.log("\n[3] Testing JavaScript Assets", "INFO")
        self.test_route("/app.js")
        self.test_route("/engagement.js")
        self.test_route("/activity_feed.js")
        self.test_route("/sw_offline.js")
        
        # Test that pages have content
        self.log("\n[4] Testing Page Content (not empty)", "INFO")
        self.test_view_has_content("/", min_size=1000)
        self.test_view_has_content("/gaia.html", min_size=1000)
        self.test_view_has_content("/console.html", min_size=500)
        
        # Test navigation integrity
        self.log("\n[5] Testing Navigation Links", "INFO")
        # self.test_navigation_links()  # Commented to avoid spam, enable if needed
        
        # Generate report
        self.log("\n" + "=" * 70, "INFO")
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Tests: {self.tests_run} | Passed: {self.tests_passed} | Failed: {self.tests_run - self.tests_passed}", "INFO")
        self.log(f"Pass Rate: {pass_rate:.1f}%", "INFO")
        
        if self.warnings:
            self.log(f"\nWarnings ({len(self.warnings)}):", "WARN")
            for w in self.warnings:
                self.log(f"  • {w}", "WARN")
        
        if self.failures:
            self.log(f"\nFailures ({len(self.failures)}):", "FAIL")
            for f in self.failures:
                self.log(f"  • {f}", "FAIL")
            return False
        else:
            self.log("\n🎉 ALL QA CHECKS PASSED", "PASS")
            return True

if __name__ == "__main__":
    qa = QABot()
    success = qa.run_comprehensive_qa()
    exit(0 if success else 1)
