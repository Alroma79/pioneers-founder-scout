#!/usr/bin/env python3
"""
Quick validation script to verify the system works end-to-end
"""
import asyncio
import sys
import os
import json
import pandas as pd
sys.path.append('backend')

from backend.app.clients.harvest_client import HarvestClient
from backend.app.models import Criteria
from backend.app.services.normalize import normalize_person
from backend.app.services.scoring import score_candidate
from backend.app.services.utils import dedupe
from backend.app.storage.repository import save_candidates_csv

async def validate_system():
    print("🎯 Pioneers Founder Scout - System Validation")
    print("=" * 50)
    
    # Test 1: HarvestAPI connectivity
    print("\n1. Testing HarvestAPI connectivity...")
    client = HarvestClient()
    
    # Test geo lookup
    geo_id = await client.lookup_geo_id('Portugal')
    print(f"   ✅ Portugal geo_id: {geo_id}")
    
    # Test search
    results = await client.search_people(search='founder', limit=5)
    print(f"   ✅ Search returned {len(results)} results")
    
    if not results:
        print("   ⚠️  No results from HarvestAPI - using mock data")
        results = [
            {
                "name": "Test Founder",
                "position": "CTO & Co-Founder",
                "publicIdentifier": "test-founder",
                "linkedinUrl": "https://linkedin.com/in/test-founder"
            }
        ]
    
    # Test 2: Data processing pipeline
    print("\n2. Testing data processing pipeline...")
    
    # Deduplication
    deduped = dedupe(results)
    print(f"   ✅ Deduplication: {len(results)} -> {len(deduped)} candidates")
    
    # Normalization
    normalized = [normalize_person(p) for p in deduped]
    print(f"   ✅ Normalized {len(normalized)} candidates")
    
    # Scoring
    criteria = {"technical_signal": True, "founder_signal": True, "sector": "ai"}
    scored = [score_candidate(p, criteria) for p in normalized]
    print(f"   ✅ Scored {len(scored)} candidates")
    
    # Show score distribution
    scores = [p["score"] for p in scored]
    tiers = [p["tier"] for p in scored]
    print(f"   📊 Score range: {min(scores)}-{max(scores)}")
    print(f"   📊 Tier distribution: A={tiers.count('A')}, B={tiers.count('B')}, C={tiers.count('C')}")
    
    # Test 3: CSV export
    print("\n3. Testing CSV export...")
    csv_path = save_candidates_csv(scored)
    print(f"   ✅ Saved to: {csv_path}")
    
    # Verify CSV
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"   ✅ CSV contains {len(df)} rows")
        print(f"   📋 Columns: {list(df.columns)}")
    
    # Test 4: Unit tests
    print("\n4. Running unit tests...")
    import subprocess
    
    test_files = ['tests.test_normalize', 'tests.test_scoring', 'tests.test_utils']
    all_passed = True
    
    for test_file in test_files:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'unittest', test_file, '-v'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"   ✅ {test_file}: PASSED")
            else:
                print(f"   ❌ {test_file}: FAILED")
                print(f"      {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {test_file}: ERROR - {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 System validation PASSED!")
        print("\nNext steps:")
        print("1. Start backend: uvicorn backend.app.main:app --reload")
        print("2. Start frontend: streamlit run frontend/streamlit_app.py")
        print("3. Test search: POST /search with Portugal criteria")
    else:
        print("❌ System validation FAILED!")
        print("Please check the errors above and fix before proceeding.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(validate_system())
    sys.exit(0 if success else 1)
