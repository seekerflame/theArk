#!/usr/bin/env python3
"""
Simple QA Bot - No External Dependencies
Tests all routes and reports broken links/empty views
"""

import urllib.request
import urllib.error
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:3000"

class SimpleQA:
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passes = 0
        self.total = 0
        
    def test_route(self, path, desc=""):
        """Test if route is accessible"""
        self.total += 1
        try:
            response = urllib.request.urlopen(f"{API_BASE}{path}", timeout=5)
            content = response.read()
            size = len(content)
            
            if size == 0:
                print(f"⚠️  {desc or path}: EMPTY ({size} bytes)")
                self.warnings.append(f"{path} is empty")
            elif size < 200:
                print(f"⚠️  {desc or path}: Small ({size} bytes)")
                self.warnings.append(f"{path} suspiciously small")
            else:
                print(f"✅ {desc or path}: OK ({size} bytes)")
            
            self.passes += 1
            return True
            
        except urllib.error.HTTPError as e:
            print(f"❌ {desc or path}: HTTP {e.code}")
            self.failures.append(f"{path} returned {e.code}")
            return False
        except Exception as e:
            print(f"❌ {desc or path}: {str(e)}")
            self.failures.append(f"{path}: {e}")
            return False
    
    def run_qa(self):
        print("=" * 70)
        print("QA BOT - Application Quality Control")
        print("=" * 70)
        
        # Core pages
        print("\n[1] Core HTML Pages")
        self.test_route("/", "Dashboard")
        self.test_route("/gaia.html", "Gaia Control Center")
        self.test_route("/console.html", "Terminal Console")
        self.test_route("/verifier.html", "Verifier Station")
        
        # Data files
        print("\n[2] JSON Data")
        self.test_route("/ui_config.json", "UI Config")
        self.test_route("/seh7_quests.json", "SEH7 Quests")
        self.test_route("/api/graph", "Ledger Graph")
        self.test_route("/api/state", "App State")
        
        # JavaScript
        print("\n[3] JavaScript Files")
        self.test_route("/app.js", "Main App")
        self.test_route("/engagement.js", "Engagement System")
        self.test_route("/activity_feed.js", "Activity Feed")
        
        # Report
        print("\n" + "=" * 70)
        pass_rate = (self.passes / self.total * 100) if self.total > 0 else 0
        print(f"Total: {self.total} | Passed: {self.passes} | Failed: {len(self.failures)}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"   • {w}")
        
        if self.failures:
            print(f"\n❌ Failures ({len(self.failures)}):")
            for f in self.failures:
                print(f"   • {f}")
            return False
        
        print("\n🎉 ALL QA CHECKS PASSED")
        return True

if __name__ == "__main__":
    qa = SimpleQA()
    success = qa.run_qa()
    sys.exit(0 if success else 1)
